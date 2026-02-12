"""Exit confirmation dialog for the Dwellpy application."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import os

try:
    from ...config.constants import Colors, BORDER_RADIUS, Fonts
    from ...utils.helpers import center_window, get_asset_path
    # Use constants from config
    DARK_BG = Colors.DARK_BG
    TEXT_COLOR = Colors.TEXT_COLOR
    BLUE_ACCENT = Colors.BLUE_ACCENT
    RED_ACCENT = Colors.RED_ACCENT
    BORDER_COLOR = Colors.BORDER_COLOR
    BORDER_RADIUS = BORDER_RADIUS
    PRIMARY_FONT = Fonts.PRIMARY_FAMILY
except ImportError:
    # Fallback constants - match exactly what settings dialog uses
    DARK_BG = "#1a1a1a"
    TEXT_COLOR = "#ffffff"
    BLUE_ACCENT = "#0078d7"
    RED_ACCENT = "#e74c3c"
    BORDER_COLOR = "#3c3c3c"
    BORDER_RADIUS = 5
    PRIMARY_FONT = "'Helvetica Neue', Helvetica, Arial, sans-serif"
    
    def center_window(window):
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        window_size = window.frameGeometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        window.move(x, y)
    
    def get_asset_path(asset_name):
        """Fallback get_asset_path function"""
        import sys
        import os
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        return os.path.join(base_path, 'assets', 'icons', asset_name)


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
        
        # Set window icon for taskbar display
        try:
            # Use platform-appropriate icon format
            if os.name == 'nt':  # Windows
                icon_path = get_asset_path("Dwellpy.ico")
            else:  # Linux/macOS
                icon_path = get_asset_path("Dwellpy.png")
                
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass  # Silently fail if icon can't be loaded
        
        # Apply dark theme with consistent border styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {DARK_BG};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: {BORDER_RADIUS}px;
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-family: {PRIMARY_FONT};
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 25, 20, 20)
        main_layout.setSpacing(20)
        
        # Message
        message = QLabel("Are you sure you want to exit?")
        message.setStyleSheet(f"""
            font-family: {PRIMARY_FONT};
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
        
        # Yes button - red styling with modern hover effects
        self.yes_button = QPushButton("Yes")
        self.yes_button.setFixedSize(100, 40)
        self.yes_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.yes_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 {RED_ACCENT}, stop:1 #c0392b);
                color: {TEXT_COLOR};
                border: none;
                border-radius: {BORDER_RADIUS}px;
                font-family: {PRIMARY_FONT};
                font-size: 12pt;
                font-weight: bold;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #c0392b, stop:1 {RED_ACCENT});
            }}
        """)
        buttons_layout.addWidget(self.yes_button)
        
        # No button - blue styling with modern hover effects
        self.no_button = QPushButton("No")
        self.no_button.setFixedSize(100, 40)
        self.no_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.no_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 {BLUE_ACCENT}, stop:1 #0069c0);
                color: {TEXT_COLOR};
                border: none;
                border-radius: {BORDER_RADIUS}px;
                font-family: {PRIMARY_FONT};
                font-size: 12pt;
                font-weight: bold;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #0069c0, stop:1 {BLUE_ACCENT});
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
