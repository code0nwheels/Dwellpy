"""Update notification / progress dialog for Dwellpy."""

import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QDialog, QFrame, QHBoxLayout, QLabel, QProgressBar,
                             QPushButton, QVBoxLayout)

from ...config.constants import BORDER_RADIUS, Colors, Fonts
from ...utils.helpers import center_window, get_asset_path


def _button_style(top: str, bottom: str) -> str:
    return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {top}, stop:1 {bottom});
            color: {Colors.TEXT_COLOR};
            border: none;
            border-radius: {BORDER_RADIUS}px;
            font-family: {Fonts.PRIMARY_FAMILY};
            font-size: 11pt;
            font-weight: bold;
            padding: 5px 12px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {bottom}, stop:1 {top});
        }}
    """


PRIMARY_STYLE = _button_style(Colors.BLUE_ACCENT, Colors.BLUE_HOVER)
SECONDARY_STYLE = _button_style(Colors.DARK_BUTTON_BG, Colors.GRAY_HOVER)


class UpdateDialog(QDialog):
    """Non-modal, always-on-top dialog that walks the user through an update.

    The dialog only presents state; ``UpdateManager`` decides what happens when
    a button is pressed. Buttons are large so they are easy to dwell-click.
    """

    update_clicked = pyqtSignal()       # "Update now"
    download_page_clicked = pyqtSignal()  # "Open download page"
    later_clicked = pyqtSignal()        # "Later" / "Close" / "OK"
    skip_clicked = pyqtSignal()         # "Skip this version"
    cancel_clicked = pyqtSignal()       # "Cancel" while downloading

    def __init__(self, parent=None):
        super().__init__(parent)
        self._buttons: list[QPushButton] = []
        self._setup_ui()

    # ------------------------------------------------------------------ UI --
    def _setup_ui(self) -> None:
        self.setWindowTitle("Dwellpy Update")
        self.setMinimumWidth(460)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
        )
        # Non-modal so dwell clicking keeps working everywhere else
        self.setModal(False)

        try:
            icon_path = get_asset_path("Dwellpy.ico" if os.name == "nt" else "Dwellpy.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.DARK_BG};
                color: {Colors.TEXT_COLOR};
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: {BORDER_RADIUS}px;
            }}
            QLabel {{
                color: {Colors.TEXT_COLOR};
                font-family: {Fonts.PRIMARY_FAMILY};
            }}
            QProgressBar {{
                background-color: {Colors.DARK_BUTTON_BG};
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: {BORDER_RADIUS}px;
                color: {Colors.TEXT_COLOR};
                text-align: center;
                height: 22px;
            }}
            QProgressBar::chunk {{
                background-color: {Colors.BLUE_ACCENT};
                border-radius: {BORDER_RADIUS}px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        layout.setSpacing(14)

        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        self.message_label = QLabel()
        self.message_label.setStyleSheet("font-size: 11pt;")
        self.message_label.setWordWrap(True)
        self.message_label.setTextFormat(Qt.TextFormat.RichText)
        self.message_label.setOpenExternalLinks(True)
        layout.addWidget(self.message_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.buttons_frame = QFrame()
        self.buttons_layout = QHBoxLayout(self.buttons_frame)
        self.buttons_layout.setContentsMargins(0, 6, 0, 0)
        self.buttons_layout.setSpacing(14)
        layout.addWidget(self.buttons_frame, 0, Qt.AlignmentFlag.AlignCenter)

    def _set_buttons(self, buttons: list[tuple[str, str, pyqtSignal]]) -> None:
        """Replace the button row with ``(label, style, signal)`` entries."""
        for button in self._buttons:
            self.buttons_layout.removeWidget(button)
            button.deleteLater()
        self._buttons = []
        for label, style, signal in buttons:
            button = QPushButton(label)
            button.setMinimumSize(120, 44)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(style)
            button.clicked.connect(signal.emit)
            self.buttons_layout.addWidget(button)
            self._buttons.append(button)

    def _present(self, title: str, message: str) -> None:
        self.title_label.setText(title)
        self.message_label.setText(message)
        self.adjustSize()
        if not self.isVisible():
            center_window(self)
            self.show()
        self.raise_()
        self.activateWindow()

    # -------------------------------------------------------------- states --
    def show_checking(self) -> None:
        self.progress_bar.setVisible(False)
        self._set_buttons([("Close", SECONDARY_STYLE, self.later_clicked)])
        self._present("Checking for updates…", "Contacting GitHub for the latest Dwellpy release.")

    def show_available(self, new_version: str, current_version: str,
                       notes_url: str, can_install: bool) -> None:
        self.progress_bar.setVisible(False)
        link = f'<a style="color:{Colors.BLUE_ACCENT};" href="{notes_url}">See what\'s new</a>'
        if can_install:
            message = (f"You have version {current_version}. Dwellpy will download the update, "
                       f"close, install it and start again.<br><br>{link}")
            primary = ("Update now", PRIMARY_STYLE, self.update_clicked)
        else:
            message = (f"You have version {current_version}. This copy of Dwellpy can't update "
                       f"itself; download the new version from GitHub.<br><br>{link}")
            primary = ("Download", PRIMARY_STYLE, self.download_page_clicked)
        self._set_buttons([
            primary,
            ("Later", SECONDARY_STYLE, self.later_clicked),
            ("Skip version", SECONDARY_STYLE, self.skip_clicked),
        ])
        self._present(f"Dwellpy {new_version} is available", message)

    def show_downloading(self, version: str) -> None:
        self.progress_bar.setRange(0, 0)  # indeterminate until size is known
        self.progress_bar.setVisible(True)
        self._set_buttons([("Cancel", SECONDARY_STYLE, self.cancel_clicked)])
        self._present(f"Downloading Dwellpy {version}…", "You can keep using Dwellpy while this downloads.")

    def set_progress(self, received: int, total: int) -> None:
        if total > 0:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(received)
            self.progress_bar.setFormat(f"{received / 1_048_576:.1f} / {total / 1_048_576:.1f} MB")

    def show_installing(self, note: str = "") -> None:
        self.progress_bar.setVisible(False)
        self._set_buttons([])
        message = "Dwellpy will close and restart automatically."
        self._present("Installing update…", f"{note}<br><br>{message}" if note else message)

    def show_up_to_date(self, current_version: str) -> None:
        self.progress_bar.setVisible(False)
        self._set_buttons([("OK", PRIMARY_STYLE, self.later_clicked)])
        self._present("Dwellpy is up to date", f"You have the latest version ({current_version}).")

    def show_error(self, message: str, offer_download_page: bool = True) -> None:
        self.progress_bar.setVisible(False)
        buttons = []
        if offer_download_page:
            buttons.append(("Open download page", PRIMARY_STYLE, self.download_page_clicked))
        buttons.append(("Close", SECONDARY_STYLE, self.later_clicked))
        self._set_buttons(buttons)
        self._present("Update problem", message)
