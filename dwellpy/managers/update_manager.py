"""Auto-update support for Dwellpy.

Checks GitHub Releases for a newer version, asks the user, downloads the
matching installer, verifies its SHA-256 digest, hands off to the platform
installer and quits so the installer can replace the running executable.

Networking uses QtNetwork so it runs on the Qt event loop and uses the
operating system's TLS stack and certificate store (a frozen Python's own
``ssl`` module can't always find CA certificates, notably on macOS).
"""

import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, QProcess, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt6.QtWidgets import QApplication

from .. import __version__
from ..ui.dialogs.update_dialog import UpdateDialog
from ..utils import updater
from ..utils.updater import InstallLaunchError, InstallMethod, ReleaseAsset, ReleaseInfo

# How long after launch the first automatic check runs
STARTUP_CHECK_DELAY_MS = 15_000
# Minimum time between automatic checks (also the re-check interval while running)
CHECK_INTERVAL_SECONDS = 24 * 60 * 60
# Give up on a stalled request after this long without data
TRANSFER_TIMEOUT_MS = 30_000
# Hard exit if Qt does not shut down promptly after handing off to the installer
FORCE_EXIT_AFTER_SECONDS = 5.0


class UpdateManager(QObject):
    """Coordinates update checks, the update dialog, download and install."""

    def __init__(self, settings_manager, parent_window=None, current_version: str = __version__):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.settings_manager = settings_manager
        self.parent_window = parent_window
        self.current_version = current_version
        self.install_method = updater.detect_install_method()

        self._network = QNetworkAccessManager(self)
        self._network.setRedirectPolicy(QNetworkRequest.RedirectPolicy.NoLessSafeRedirectPolicy)

        self._dialog: Optional[UpdateDialog] = None
        self._check_reply: Optional[QNetworkReply] = None
        self._download_reply: Optional[QNetworkReply] = None
        self._download_file = None
        self._download_path: Optional[Path] = None
        self._release: Optional[ReleaseInfo] = None
        self._asset: Optional[ReleaseAsset] = None
        self._manual_check = False
        self._install_process: Optional[QProcess] = None

        self._periodic_timer = QTimer(self)
        self._periodic_timer.setInterval(CHECK_INTERVAL_SECONDS * 1000)
        self._periodic_timer.timeout.connect(self._automatic_check)

        self.logger.info(f"Update manager ready (install method: {self.install_method.value})")

    # ------------------------------------------------------------ public --
    def start(self) -> None:
        """Schedule automatic checks. Call once at startup."""
        QTimer.singleShot(STARTUP_CHECK_DELAY_MS, self._automatic_check)
        self._periodic_timer.start()

    def check_for_updates(self, manual: bool = True) -> None:
        """Query GitHub for the latest release.

        A manual check always reports its result; an automatic check stays
        silent unless there is a new version the user has not skipped.
        """
        if self._check_reply is not None or self._download_reply is not None:
            if manual and self._dialog:
                self._dialog.raise_()
            return

        self._manual_check = manual
        if manual:
            self._get_dialog().show_checking()

        request = QNetworkRequest(QUrl(updater.LATEST_RELEASE_API_URL))
        request.setRawHeader(b"Accept", b"application/vnd.github+json")
        request.setRawHeader(b"User-Agent", f"Dwellpy/{self.current_version}".encode())
        request.setTransferTimeout(TRANSFER_TIMEOUT_MS)

        self.logger.info("Checking for updates...")
        self._check_reply = self._network.get(request)
        self._check_reply.finished.connect(self._on_check_finished)

    # ------------------------------------------------------------ checks --
    def _automatic_check(self) -> None:
        if not self.settings_manager.get_setting('auto_update_check', True):
            return
        last = float(self.settings_manager.get_setting('update_last_check', 0) or 0)
        # Small slack so the 24h timer isn't skipped by a few seconds of drift
        if time.time() - last < CHECK_INTERVAL_SECONDS - 60:
            self.logger.debug("Skipping automatic update check (checked recently)")
            return
        self.check_for_updates(manual=False)

    def _on_check_finished(self) -> None:
        reply, self._check_reply = self._check_reply, None
        if reply is None:
            return
        reply.deleteLater()

        if reply.error() != QNetworkReply.NetworkError.NoError:
            self.logger.warning(f"Update check failed: {reply.errorString()}")
            if self._manual_check:
                self._get_dialog().show_error(
                    f"Couldn't reach GitHub to check for updates.<br>{reply.errorString()}")
            return

        self.settings_manager.set_setting('update_last_check', time.time())

        try:
            release = updater.parse_release(json.loads(bytes(reply.readAll()).decode("utf-8")))
            newer = updater.is_newer_version(release.version, self.current_version)
        except (ValueError, json.JSONDecodeError) as e:
            self.logger.warning(f"Could not understand update response: {e}")
            if self._manual_check:
                self._get_dialog().show_error("GitHub returned an unexpected response.")
            return

        self.logger.info(f"Latest release: {release.version} (current: {self.current_version})")

        if not newer:
            if self._manual_check:
                self._get_dialog().show_up_to_date(self.current_version)
            return

        skipped = self.settings_manager.get_setting('update_skipped_version', '')
        if not self._manual_check and skipped == release.version:
            self.logger.info(f"Update {release.version} was skipped by the user")
            return

        self._release = release
        self._asset = updater.select_asset(release, self.install_method)
        can_install = self.install_method.can_self_install and self._asset is not None
        if self.install_method.can_self_install and self._asset is None:
            self.logger.warning(f"Release {release.version} has no asset for {self.install_method.value}")

        self._get_dialog().show_available(
            release.version, self.current_version, release.html_url, can_install)

    # ---------------------------------------------------------- download --
    def _start_download(self) -> None:
        if not self._release or not self._asset or self._download_reply is not None:
            return

        dest_dir = updater.updates_dir()
        self._download_path = dest_dir / self._asset.name
        partial = self._download_path.with_suffix(self._download_path.suffix + ".part")
        try:
            self._download_file = open(partial, "wb")
        except OSError as e:
            self._get_dialog().show_error(f"Couldn't save the download: {e}")
            return

        request = QNetworkRequest(QUrl(self._asset.download_url))
        request.setRawHeader(b"User-Agent", f"Dwellpy/{self.current_version}".encode())
        request.setTransferTimeout(TRANSFER_TIMEOUT_MS)

        self.logger.info(f"Downloading {self._asset.download_url}")
        self._get_dialog().show_downloading(self._release.version)
        self._download_reply = self._network.get(request)
        self._download_reply.readyRead.connect(self._on_download_ready_read)
        self._download_reply.downloadProgress.connect(self._on_download_progress)
        self._download_reply.finished.connect(self._on_download_finished)

    def _on_download_ready_read(self) -> None:
        if self._download_reply and self._download_file:
            self._download_file.write(bytes(self._download_reply.readAll()))

    def _on_download_progress(self, received: int, total: int) -> None:
        if self._dialog:
            self._dialog.set_progress(received, total or (self._asset.size if self._asset else 0))

    def _on_download_finished(self) -> None:
        reply, self._download_reply = self._download_reply, None
        if reply is None:
            return
        reply.deleteLater()

        # Flush anything still buffered, then close
        if self._download_file:
            self._download_file.write(bytes(reply.readAll()))
            partial = Path(self._download_file.name)
            self._download_file.close()
            self._download_file = None
        else:
            return

        if reply.error() == QNetworkReply.NetworkError.OperationCanceledError:
            self.logger.info("Update download cancelled")
            partial.unlink(missing_ok=True)
            return
        if reply.error() != QNetworkReply.NetworkError.NoError:
            self.logger.warning(f"Update download failed: {reply.errorString()}")
            partial.unlink(missing_ok=True)
            self._get_dialog().show_error(f"The download failed.<br>{reply.errorString()}")
            return

        asset = self._asset
        size = partial.stat().st_size
        if asset.size and size != asset.size:
            self.logger.warning(f"Downloaded size {size} != expected {asset.size}")
            partial.unlink(missing_ok=True)
            self._get_dialog().show_error("The download was incomplete. Please try again.")
            return
        if not asset.digest:
            self.logger.warning(f"Release asset {asset.name} has no published digest; skipping hash check")
        elif not updater.verify_digest(partial, asset.digest):
            self.logger.error(f"Checksum mismatch for {asset.name}")
            partial.unlink(missing_ok=True)
            self._get_dialog().show_error(
                "The downloaded file didn't match its published checksum, so it was not installed.")
            return

        os.replace(partial, self._download_path)
        if self.install_method is InstallMethod.LINUX_DEB:
            # Only needs to be readable by dpkg; keep it private otherwise
            os.chmod(self._download_path, 0o644)
        self.logger.info(f"Update downloaded and verified: {self._download_path}")
        self._install()

    def _cancel_download(self) -> None:
        if self._download_reply:
            self._download_reply.abort()  # finished() handles cleanup
        self._close_dialog()

    # ----------------------------------------------------------- install --
    def _install(self) -> None:
        if self.install_method is InstallMethod.LINUX_DEB:
            self._install_linux_deb()
            return

        dialog = self._get_dialog()
        note = ""
        if self.install_method is InstallMethod.WINDOWS_INSTALLER:
            note = ("Windows will ask for permission to install. "
                    "Press <b>Alt+Y</b> (or click Yes) to allow it.")
        dialog.show_installing(note)
        # Paint the dialog before ShellExecute blocks on the UAC prompt
        QApplication.processEvents()

        try:
            updater.launch_installer(self.install_method, str(self._download_path))
        except InstallLaunchError as e:
            self.logger.warning(f"Could not start installer: {e}")
            dialog.show_error(
                "The update could not be installed automatically. "
                "You can download and install it yourself from GitHub.")
            return
        except Exception as e:
            self.logger.error(f"Unexpected error starting installer: {e}", exc_info=True)
            dialog.show_error("Something went wrong starting the installer.")
            return

        self.logger.info("Installer started; quitting so it can replace Dwellpy")
        self._quit_for_update()

    def _install_linux_deb(self) -> None:
        """Install the .deb with pkexec while Dwellpy keeps running.

        The polkit password prompt appears while dwell clicking is still
        available; Dwellpy only quits once the package is installed.
        """
        dialog = self._get_dialog()
        try:
            command = updater.linux_deb_install_command(str(self._download_path))
        except InstallLaunchError as e:
            self.logger.warning(f"Cannot install .deb: {e}")
            dialog.show_error("The update could not be installed automatically. "
                              "You can download and install it yourself from GitHub.")
            return

        dialog.show_installing("Enter your password in the window that appears to install the update.")
        process = QProcess(self)
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        process.finished.connect(self._on_linux_install_finished)
        process.errorOccurred.connect(self._on_linux_install_error)
        self._install_process = process
        self.logger.info(f"Running: {' '.join(command)}")
        process.start(command[0], command[1:])

    def _on_linux_install_error(self, error) -> None:
        if error != QProcess.ProcessError.FailedToStart:
            return  # crashes etc. are reported through finished()
        self.logger.warning("pkexec failed to start")
        self._install_process = None
        self._get_dialog().show_error("The installer could not be started.")

    def _on_linux_install_finished(self, exit_code: int, exit_status) -> None:
        process, self._install_process = self._install_process, None
        output = bytes(process.readAll()).decode(errors="replace").strip() if process else ""
        if output:
            self.logger.info(f"Installer output: {output}")
        if process:
            process.deleteLater()

        if exit_status == QProcess.ExitStatus.NormalExit and exit_code == 0:
            self.logger.info("Update installed; restarting Dwellpy")
            try:
                updater.relaunch_after_exit(updater.LINUX_DEB_EXECUTABLE)
            except InstallLaunchError as e:
                self.logger.warning(f"Could not schedule restart: {e}")
            self._quit_for_update()
            return

        if self._download_path:
            self._download_path.unlink(missing_ok=True)
        if exit_code in updater.PKEXEC_AUTH_FAILED_CODES:
            self.logger.info(f"Install not authorised (pkexec exit {exit_code})")
            self._get_dialog().show_error(
                "The update wasn't installed because permission wasn't given. "
                "Dwellpy will offer it again later.", offer_download_page=False)
        else:
            self.logger.warning(f"dpkg failed (exit {exit_code})")
            self._get_dialog().show_error("The update package failed to install.")

    def _quit_for_update(self) -> None:
        try:
            self.settings_manager.save_settings()
        except Exception:
            pass

        # Make sure the process really exits so the installer can replace the
        # executable, even if a background thread keeps the interpreter alive.
        # Deliberately not using ExitManager: it kills child processes, which
        # would include the installer we just started.
        killer = threading.Timer(FORCE_EXIT_AFTER_SECONDS, os._exit, args=(0,))
        killer.daemon = True
        killer.start()

        app = QApplication.instance()
        if app:
            app.quit()

    # ------------------------------------------------------------ dialog --
    def _get_dialog(self) -> UpdateDialog:
        if self._dialog is None:
            self._dialog = UpdateDialog(self.parent_window)
            self._dialog.update_clicked.connect(self._start_download)
            self._dialog.download_page_clicked.connect(self._open_download_page)
            self._dialog.later_clicked.connect(self._close_dialog)
            self._dialog.skip_clicked.connect(self._skip_version)
            self._dialog.cancel_clicked.connect(self._cancel_download)
        return self._dialog

    def _close_dialog(self) -> None:
        if self._dialog:
            self._dialog.hide()

    def _skip_version(self) -> None:
        if self._release:
            self.settings_manager.set_setting('update_skipped_version', self._release.version)
            self.logger.info(f"User skipped update {self._release.version}")
        self._close_dialog()

    def _open_download_page(self) -> None:
        url = self._release.html_url if self._release else updater.RELEASES_PAGE_URL
        QDesktopServices.openUrl(QUrl(url))
        self._close_dialog()
