"""Utility functions for the Dwellpy application."""

from PyQt6.QtGui import QGuiApplication

def center_window(window):
    """
    Center a window on the screen.
    
    Args:
        window: QWidget/QMainWindow/QDialog to center
    """
    # In PyQt6, QDesktopWidget is removed, use QScreen instead
    screen = QGuiApplication.primaryScreen().geometry()
    
    # Get window size
    window_size = window.frameGeometry()
    
    # Calculate position
    x = (screen.width() - window_size.width()) // 2
    y = (screen.height() - window_size.height()) // 2
    
    # Set window position
    window.move(x, y)