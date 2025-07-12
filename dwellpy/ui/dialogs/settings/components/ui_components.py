"""UI components for settings dialog."""

from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QSlider, QCheckBox, QFrame, QComboBox, QColorDialog, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QIcon
import os

try:
    from ....config.constants import Colors, BORDER_RADIUS, Fonts, MENU_ITEM_SIZE_MIN, MENU_ITEM_SIZE_MAX
    from ....utils.helpers import center_window, format_time_display, format_percentage_display, get_asset_path
    from ....__init__ import __version__
except ImportError:
    # Fallback constants
    class Colors:
        DARK_BG = "#1a1a1a"
        DARK_BUTTON_BG = "#2d2d2d"
        TEXT_COLOR = "#ffffff"
        BLUE_ACCENT = "#0078d7"
        BLUE_HOVER = "#0069c0"
        SLIDER_TRACK = "#444444"
        BORDER_COLOR = "#3c3c3c"
    
    BORDER_RADIUS = 5
    __version__ = "0.1.0"
    
    def center_window(window):
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        window_size = window.frameGeometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        window.move(x, y)
    
    def format_time_display(seconds):
        return f"{seconds:.1f}"
    
    def format_percentage_display(percent):
        return f"{percent}%"

    def get_asset_path(asset_name):
        """Fallback get_asset_path function"""
        import sys
        import os
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        return os.path.join(base_path, 'assets', 'icons', asset_name)


def create_section_header(title, description):
    """Create a section header with title and description."""
    header_frame = QFrame()
    header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
    header_frame.setStyleSheet(f"""
        QFrame {{
            background-color: {Colors.DARK_BUTTON_BG};
            border: 1px solid {Colors.BORDER_COLOR};
            border-radius: {BORDER_RADIUS}px;
            padding: 10px;
            margin: 5px 0px;
        }}
    """)
    
    header_layout = QVBoxLayout(header_frame)
    header_layout.setContentsMargins(10, 10, 10, 10)
    header_layout.setSpacing(5)
    
    # Title
    title_label = QLabel(title)
    title_label.setFont(QFont(Fonts.MAIN_FONT, 12, QFont.Weight.Bold))
    title_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
    header_layout.addWidget(title_label)
    
    # Description
    if description:
        desc_label = QLabel(description)
        desc_label.setFont(QFont(Fonts.MAIN_FONT, 10))
        desc_label.setStyleSheet(f"color: {Colors.TEXT_COLOR}; opacity: 0.8;")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)
    
    return header_frame


def create_adjustment_button(text):
    """Create an adjustment button with consistent styling."""
    button = QPushButton(text)
    button.setFixedSize(30, 30)
    button.setFont(QFont(Fonts.MAIN_FONT, 12, QFont.Weight.Bold))
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: {Colors.DARK_BUTTON_BG};
            color: {Colors.TEXT_COLOR};
            border: 1px solid {Colors.BORDER_COLOR};
            border-radius: {BORDER_RADIUS}px;
            padding: 5px;
        }}
        QPushButton:hover {{
            background-color: {Colors.BLUE_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {Colors.BLUE_ACCENT};
        }}
    """)
    return button


def create_color_button(click_type, display_name, default_color):
    """Create a color selection button."""
    # Create color button
    color_btn = QPushButton(display_name)
    color_btn.setFixedSize(70, 22)
    color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    color_btn.setProperty('click_type', click_type)  # Store click type for reference
    
    # Style the button with default color (will be updated by settings)
    update_color_button_style(color_btn, default_color)
    
    return color_btn


def update_color_button_style(button, color_hex):
    """Update button style with the specified color."""
    # Determine text color based on background brightness
    text_color = "#000000" if is_light_color(color_hex) else "#ffffff"
    
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: {color_hex};
            color: {text_color};
            border: 2px solid {Colors.BORDER_COLOR};
            border-radius: {BORDER_RADIUS}px;
            padding: 5px 10px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            border-color: {Colors.BLUE_ACCENT};
        }}
    """)


def is_light_color(color_hex):
    """Check if a color is light (for determining text color)."""
    # Remove # if present
    color_hex = color_hex.lstrip('#')
    
    # Convert to RGB
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)
    
    # Calculate brightness
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return brightness > 128


def get_slider_style():
    """Get the consistent slider styling."""
    return f"""
        QSlider::groove:horizontal {{
            border: 1px solid {Colors.BORDER_COLOR};
            height: 8px;
            background: {Colors.SLIDER_TRACK};
            border-radius: 4px;
            margin: 2px 0;
        }}
        QSlider::handle:horizontal {{
            background: {Colors.BLUE_ACCENT};
            border: 1px solid {Colors.BORDER_COLOR};
            width: 18px;
            margin: -2px 0;
            border-radius: 9px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {Colors.BLUE_HOVER};
        }}
        QSlider::sub-page:horizontal {{
            background: {Colors.BLUE_ACCENT};
            border-radius: 4px;
        }}
    """


def get_checkbox_style():
    """Get the consistent checkbox styling."""
    return f"""
        QCheckBox {{
            color: {Colors.TEXT_COLOR};
            font-family: {Fonts.MAIN_FONT};
            font-size: 10px;
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 2px solid {Colors.BORDER_COLOR};
            border-radius: 3px;
            background-color: {Colors.DARK_BUTTON_BG};
        }}
        QCheckBox::indicator:checked {{
            background-color: {Colors.BLUE_ACCENT};
            border-color: {Colors.BLUE_ACCENT};
        }}
        QCheckBox::indicator:checked::after {{
            content: "✓";
            color: white;
            font-weight: bold;
            font-size: 12px;
        }}
        QCheckBox::indicator:hover {{
            border-color: {Colors.BLUE_HOVER};
        }}
    """


def get_radio_style():
    """Get the consistent radio button styling."""
    return f"""
        QRadioButton {{
            color: {Colors.TEXT_COLOR};
            font-family: {Fonts.MAIN_FONT};
            font-size: 10px;
            spacing: 8px;
        }}
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border: 2px solid {Colors.BORDER_COLOR};
            border-radius: 8px;
            background-color: {Colors.DARK_BUTTON_BG};
        }}
        QRadioButton::indicator:checked {{
            background-color: {Colors.BLUE_ACCENT};
            border-color: {Colors.BLUE_ACCENT};
        }}
        QRadioButton::indicator:checked::after {{
            content: "";
            width: 6px;
            height: 6px;
            border-radius: 3px;
            background-color: white;
            margin: 3px;
        }}
        QRadioButton::indicator:hover {{
            border-color: {Colors.BLUE_HOVER};
        }}
    """ 