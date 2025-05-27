"""Exit confirmation dialog for the Dwellpy application."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame)
from PyQt6.QtCore import Qt

try:
    from ...config.constants import Colors, Fonts
    from ...utils.helpers import center_window
    # Use constants from config
    DARK_BG = Colors.DARK_BG
    TEXT_COLOR = Colors.TEXT_COLOR
    BLUE_ACCENT = Colors.BLUE_ACCENT
    RED_ACCENT = Colors.RED_ACCENT
except ImportError:
    # Fallback constants
    DARK_BG = "#222222"
    TEXT_COLOR = "#ffffff"
    BLUE_ACCENT = "#0078d7"
    RED_ACCENT = "#d83638"
    
    def center_window(window):
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        window_size = window.frameGeometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        window.move(x, y)


class ExitDialog(QDialog):
    """Exit confirmation dialog for Dwellpy."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        self.setFixedSize(350, 180)
        
        # Set window flags to frameless
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        
        # Make dialog non-modal to allow dwell clicking to continue
        self.setModal(False)
        
        # Apply dark theme with red border
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {DARK_BG};
                color: {TEXT_COLOR};
                border: 1px solid {RED_ACCENT};
                border-radius: 3px;
            }}
            QLabel {{
                color: {TEXT_COLOR};
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 25, 20, 20)
        main_layout.setSpacing(20)
        
        # Message
        message = QLabel("Are you sure you want to exit?")
        message.setStyleSheet(f"""
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 14pt;
            color: {TEXT_COLOR};
        """)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(message)
        
        # Buttons
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(20)
        buttons_frame.setStyleSheet(f"background-color: {DARK_BG};")
        
        # Yes button - red styling
        self.yes_button = QPushButton("Yes")
        self.yes_button.setFixedSize(100, 40)
        self.yes_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.yes_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED_ACCENT};
                color: {TEXT_COLOR};
                border: none;
                border-radius: 3px;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 12pt;
                font-weight: bold;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
        """)
        buttons_layout.addWidget(self.yes_button)
        
        # No button - blue styling
        self.no_button = QPushButton("No")
        self.no_button.setFixedSize(100, 40)
        self.no_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.no_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BLUE_ACCENT};
                color: {TEXT_COLOR};
                border: none;
                border-radius: 3px;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 12pt;
                font-weight: bold;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: #0069c0;
            }}
        """)
        buttons_layout.addWidget(self.no_button)
        
        main_layout.addWidget(buttons_frame, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Connect signals
        self.yes_button.clicked.connect(self.accept)
        self.no_button.clicked.connect(self.reject)
        
        # Center the dialog on screen
        center_window(self)
    
    def show_and_center(self):
        """Show the dialog and ensure it's centered."""
        center_window(self)
        self.show()
