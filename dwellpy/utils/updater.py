"""Platform-independent helpers for the Dwellpy auto-updater.

This module has no Qt dependency so it can be unit tested in isolation.
It knows how to:

- parse and compare release versions,
- turn a GitHub "latest release" API response into a ``ReleaseInfo``,
- work out how this copy of Dwellpy was installed (and so how to update it),
- pick the matching release asset for this platform,
- verify a downloaded file against GitHub's published SHA-256 digest,
- hand off to the platform installer once the download is ready.
"""

from __future__ import annotations

import hashlib
import os
import platform
import re
import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

GITHUB_REPO = "code0nwheels/Dwellpy"
LATEST_RELEASE_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASES_PAGE_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"

# Where the .deb package installs the executable (see build-executables.yml)
LINUX_DEB_EXECUTABLE = "/usr/local/bin/dwellpy"

# Settings file that lives next to the executable and must survive an update
SETTINGS_FILENAME = "dwell_settings.json"


class InstallMethod(Enum):
    """How this copy of Dwellpy was installed, which decides how to update it."""

    WINDOWS_INSTALLER = "windows_installer"  # NSIS installer .exe
    MACOS_DMG = "macos_dmg"                  # Dwellpy.app copied from a .dmg
    LINUX_DEB = "linux_deb"                  # .deb package in /usr/local/bin
    MANUAL = "manual"                        # pip / source checkout / unknown

    @property
    def can_self_install(self) -> bool:
        return self is not InstallMethod.MANUAL


@dataclass
class ReleaseAsset:
    name: str
    download_url: str
    size: int = 0
    digest: Optional[str] = None  # e.g. "sha256:abc123..."


@dataclass
class ReleaseInfo:
    version: str
    tag: str
    html_url: str
    notes: str = ""
    assets: list[ReleaseAsset] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Versions
# --------------------------------------------------------------------------- #

_VERSION_RE = re.compile(r"^v?(\d+(?:\.\d+)*)(.*)$")


def parse_version(version: str) -> tuple[tuple[int, ...], bool]:
    """Parse ``"v1.2.3"`` / ``"1.2.3-rc1"`` into ``((1, 2, 3), is_prerelease)``.

    Raises ``ValueError`` for strings that do not start with a numeric version.
    """
    match = _VERSION_RE.match(version.strip())
    if not match:
        raise ValueError(f"Unrecognised version string: {version!r}")
    numbers = tuple(int(part) for part in match.group(1).split("."))
    # Pad to three components so "1.2" == "1.2.0"
    numbers = numbers + (0,) * max(0, 3 - len(numbers))
    is_prerelease = bool(match.group(2).strip())
    return numbers, is_prerelease


def is_newer_version(candidate: str, current: str) -> bool:
    """Return True if ``candidate`` is strictly newer than ``current``."""
    cand_nums, cand_pre = parse_version(candidate)
    curr_nums, curr_pre = parse_version(current)
    if cand_nums != curr_nums:
        return cand_nums > curr_nums
    # Same numbers: a final release beats a pre-release of the same version
    return curr_pre and not cand_pre


# --------------------------------------------------------------------------- #
# GitHub release parsing
# --------------------------------------------------------------------------- #

def parse_release(data: dict[str, Any]) -> ReleaseInfo:
    """Build a ``ReleaseInfo`` from a GitHub ``/releases/latest`` response."""
    tag = data.get("tag_name") or ""
    if not tag:
        raise ValueError("Release response has no tag_name")
    if data.get("draft") or data.get("prerelease"):
        raise ValueError(f"Release {tag} is a draft or pre-release")

    version = tag[1:] if tag.startswith("v") else tag
    parse_version(version)  # validate

    assets = [
        ReleaseAsset(
            name=asset.get("name", ""),
            download_url=asset.get("browser_download_url", ""),
            size=int(asset.get("size") or 0),
            digest=asset.get("digest") or None,
        )
        for asset in data.get("assets") or []
        if asset.get("browser_download_url")
    ]

    return ReleaseInfo(
        version=version,
        tag=tag,
        html_url=data.get("html_url") or RELEASES_PAGE_URL,
        notes=data.get("body") or "",
        assets=assets,
    )


# --------------------------------------------------------------------------- #
# Install detection / asset selection
# --------------------------------------------------------------------------- #

def _is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def get_macos_app_bundle(executable: Optional[str] = None) -> Optional[Path]:
    """Return the ``.app`` bundle containing ``executable`` (or None)."""
    exe = Path(executable or sys.executable).resolve()
    # .../Dwellpy.app/Contents/MacOS/Dwellpy
    if len(exe.parents) >= 3 and exe.parents[2].suffix == ".app":
        return exe.parents[2]
    return None


def detect_install_method(
    system: Optional[str] = None,
    frozen: Optional[bool] = None,
    executable: Optional[str] = None,
) -> InstallMethod:
    """Work out how this copy of Dwellpy was installed."""
    system = (system or platform.system()).lower()
    frozen = _is_frozen() if frozen is None else frozen
    executable = executable or sys.executable

    if not frozen:
        return InstallMethod.MANUAL

    if system == "windows":
        return InstallMethod.WINDOWS_INSTALLER
    if system == "darwin":
        return InstallMethod.MACOS_DMG if get_macos_app_bundle(executable) else InstallMethod.MANUAL
    if system == "linux":
        try:
            same = os.path.realpath(executable) == os.path.realpath(LINUX_DEB_EXECUTABLE)
        except OSError:
            same = False
        return InstallMethod.LINUX_DEB if same else InstallMethod.MANUAL
    return InstallMethod.MANUAL


def _linux_arch_tag(machine: str) -> Optional[str]:
    machine = machine.lower()
    if machine in ("x86_64", "amd64"):
        return "x64"
    if machine in ("aarch64", "arm64"):
        return "arm64"
    return None


def select_asset(
    release: ReleaseInfo,
    method: InstallMethod,
    machine: Optional[str] = None,
) -> Optional[ReleaseAsset]:
    """Pick the release asset that updates this install, or None."""
    machine = machine or platform.machine()

    def find(predicate) -> Optional[ReleaseAsset]:
        return next((a for a in release.assets if predicate(a.name.lower())), None)

    if method is InstallMethod.WINDOWS_INSTALLER:
        return find(lambda n: n.endswith(".exe") and "installer" in n and "windows" in n)
    if method is InstallMethod.MACOS_DMG:
        # Only an x64 build is published today; it runs on Apple Silicon via Rosetta.
        return find(lambda n: n.endswith(".dmg") and "macos" in n)
    if method is InstallMethod.LINUX_DEB:
        arch = _linux_arch_tag(machine)
        if not arch:
            return None
        return find(lambda n: n.endswith(f"-linux-debian-{arch}.deb"))
    return None


# --------------------------------------------------------------------------- #
# Verification
# --------------------------------------------------------------------------- #

def verify_digest(path: str | os.PathLike, digest: Optional[str]) -> bool:
    """Check ``path`` against a GitHub asset digest such as ``"sha256:<hex>"``.

    Returns True when the digest matches. Returns False when it does not match
    or the algorithm is not supported. ``digest=None`` (older releases that
    predate GitHub publishing digests) is treated as "nothing to verify".
    """
    if not digest:
        return True
    algorithm, _, expected = digest.partition(":")
    if algorithm.lower() != "sha256" or not expected:
        return False
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().lower() == expected.strip().lower()


# --------------------------------------------------------------------------- #
# Handing off to the installer
# --------------------------------------------------------------------------- #

class InstallLaunchError(Exception):
    """The installer could not be started (e.g. the user declined elevation)."""


def updates_dir() -> Path:
    """Temp directory used for downloads and helper scripts."""
    path = Path(tempfile.gettempdir()) / "dwellpy-update"
    path.mkdir(parents=True, exist_ok=True)
    return path


def launch_installer(method: InstallMethod, package_path: str) -> None:
    """Start the platform installer for ``package_path``.

    Handles Windows and macOS. On success the caller must quit Dwellpy
    promptly: the installer waits for this process to exit before replacing
    files, then relaunches Dwellpy. Linux .deb updates are driven by the update
    manager instead (see ``linux_deb_install_command``) so the password prompt
    appears while Dwellpy is still running.
    Raises ``InstallLaunchError`` if the installer could not be started.
    """
    if method is InstallMethod.WINDOWS_INSTALLER:
        _launch_windows_installer(package_path)
    elif method is InstallMethod.MACOS_DMG:
        _launch_macos_update(package_path)
    else:
        raise InstallLaunchError("This installation cannot update itself")


def _launch_windows_installer(installer_path: str) -> None:
    import ctypes

    # /S = silent, /UPDATE = wait for Dwellpy to exit, keep shortcuts, relaunch.
    # "runas" triggers the UAC prompt; ShellExecuteW returns once the user answers.
    result = ctypes.windll.shell32.ShellExecuteW(  # type: ignore[attr-defined]
        None, "runas", installer_path, "/S /UPDATE", None, 1
    )
    if result <= 32:
        # 5 = access denied (UAC declined), 1223 = ERROR_CANCELLED
        raise InstallLaunchError(f"Installer did not start (ShellExecute code {result})")


_MACOS_SCRIPT = r"""#!/bin/sh
# Dwellpy macOS updater: wait for Dwellpy to quit, swap the .app bundle, relaunch.
PID="$1"; DMG="$2"; APP="$3"
LOG="$(dirname "$DMG")/update.log"
exec >>"$LOG" 2>&1
echo "=== $(date) updating $APP from $DMG"

i=0
while kill -0 "$PID" 2>/dev/null && [ $i -lt 120 ]; do sleep 0.5; i=$((i+1)); done

MNT="$(mktemp -d /tmp/dwellpy-dmg.XXXXXX)"
if hdiutil attach -nobrowse -noautoopen -readonly -mountpoint "$MNT" "$DMG"; then
  SRC="$(find "$MNT" -maxdepth 1 -name '*.app' -print -quit)"
  if [ -n "$SRC" ]; then
    OLD="$APP.old-$$"
    if mv "$APP" "$OLD"; then
      if ditto "$SRC" "$APP"; then
        # Settings are stored next to the executable; carry them over.
        if [ -f "$OLD/Contents/MacOS/__SETTINGS__" ]; then
          cp -p "$OLD/Contents/MacOS/__SETTINGS__" "$APP/Contents/MacOS/" || true
        fi
        xattr -dr com.apple.quarantine "$APP" 2>/dev/null || true
        rm -rf "$OLD"
        echo "update installed"
      else
        echo "copy failed, restoring previous version"
        rm -rf "$APP"; mv "$OLD" "$APP"
      fi
    fi
  else
    echo "no .app found in disk image"
  fi
  hdiutil detach "$MNT" -quiet || hdiutil detach "$MNT" -force -quiet
else
  echo "could not mount disk image"
fi
rmdir "$MNT" 2>/dev/null
rm -f "$DMG"
open "$APP"
"""


def _launch_macos_update(dmg_path: str) -> None:
    app = get_macos_app_bundle()
    if app is None:
        raise InstallLaunchError("Could not locate Dwellpy.app")
    if not os.access(app.parent, os.W_OK) or not os.access(app, os.W_OK):
        raise InstallLaunchError(f"No permission to replace {app}")

    script = updates_dir() / "install_update.sh"
    script.write_text(_MACOS_SCRIPT.replace("__SETTINGS__", SETTINGS_FILENAME))
    _spawn_detached(["/bin/sh", str(script), str(os.getpid()), dmg_path, str(app)])


def linux_deb_install_command(deb_path: str) -> list[str]:
    """Command that installs ``deb_path`` with admin rights via polkit.

    Dwellpy runs this while it is still running, so the user still has dwell
    clicking available for the password prompt. dpkg can safely replace the
    running executable.
    """
    if not _which("pkexec"):
        raise InstallLaunchError("pkexec is not available to install the update")
    return ["pkexec", "dpkg", "-i", deb_path]


# pkexec exit codes when authentication was dismissed or refused
PKEXEC_AUTH_FAILED_CODES = (126, 127)

_RELAUNCH_SCRIPT = (
    'PID="$1"; shift; i=0; '
    'while kill -0 "$PID" 2>/dev/null && [ $i -lt 120 ]; do sleep 0.5; i=$((i+1)); done; '
    'exec "$@"'
)


def relaunch_after_exit(executable: str) -> None:
    """Start ``executable`` once this process has exited (POSIX only)."""
    _spawn_detached(["/bin/sh", "-c", _RELAUNCH_SCRIPT, "dwellpy-relaunch",
                     str(os.getpid()), executable])


def _which(cmd: str) -> Optional[str]:
    from shutil import which
    return which(cmd)


def _spawn_detached(args: list[str]) -> None:
    """Start ``args`` in its own session so it outlives this process."""
    try:
        subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            close_fds=True,
        )
    except OSError as e:
        raise InstallLaunchError(f"Could not start updater: {shlex.join(args)}: {e}") from e
