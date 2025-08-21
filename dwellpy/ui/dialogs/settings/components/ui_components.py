"""UI components for settings dialog."""

from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QSlider, QCheckBox, QFrame, QComboBox, QColorDialog, QRadioButton, QButtonGroup, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QIcon
import os

try:
    from dwellpy.config.constants import Colors, BORDER_RADIUS, Fonts, MENU_ITEM_SIZE_MIN, MENU_ITEM_SIZE_MAX
    from dwellpy.utils.helpers import center_window, format_time_display, format_percentage_display, get_asset_path
    from dwellpy import __version__
except ImportError:
    # Fallback constants
    BORDER_RADIUS = 5
    __version__ = "0.1.0"
    
    class Fonts:
        PRIMARY_FAMILY = "'Helvetica Neue', Helvetica, Arial, sans-serif"
        TITLE_SIZE = 16
        REGULAR_SIZE = 11
        BUTTON_SIZE = 9
        VERSION_SIZE = 9
    
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


def get_focus_style():
    """Get consistent focus styling for various widgets."""
    return f"""
        QWidget:focus {{
            outline: 2px solid {Colors.BLUE_ACCENT};
            outline-offset: 2px;
        }}
        
        QSlider:focus {{
            outline: 2px solid {Colors.BLUE_ACCENT};
            outline-offset: 4px;
        }}
        
        QCheckBox:focus {{
            outline: 2px solid {Colors.BLUE_ACCENT};
            outline-offset: 2px;
        }}
        
        QRadioButton:focus {{
            outline: 2px solid {Colors.BLUE_ACCENT};
            outline-offset: 2px;
        }}
        
        QPushButton:focus {{
            outline: 2px solid {Colors.BLUE_ACCENT};
            outline-offset: 2px;
        }}
    """


def create_section_header(title_text, description=None):
    """Create a compact section header with title and optional description underneath."""
    header_widget = QWidget()
    header_layout = QVBoxLayout(header_widget)
    header_layout.setContentsMargins(0, 0, 0, 0)
    header_layout.setSpacing(2)  # Reduced spacing between title and description
    
    # Title
    title = QLabel(title_text)
    title.setStyleSheet(f"""
        color: {Colors.TEXT_COLOR};
        font-family: {Fonts.PRIMARY_FAMILY};
        font-size: 13pt;
        font-weight: bold;
        margin: 0;
        padding: 0;
    """)
    header_layout.addWidget(title)
    
    # Description underneath (if provided)
    if description:
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            color: {Colors.SUBTLE_TEXT};
            font-family: {Fonts.PRIMARY_FAMILY};
            font-size: 10px;
            margin: 0;
            padding: 0;
            opacity: 0.7;
        """)
        desc_label.setWordWrap(False)  # Prevent wrapping to save space
        header_layout.addWidget(desc_label)
    
    return header_widget


def create_adjustment_button(text, tooltip=""):
    """Create a modern, compact adjustment button."""
    button = QPushButton(text)
    button.setFixedSize(36, 36)  # Increased from 26x26
    button.setFont(QFont(Fonts.PRIMARY_FAMILY, 12, QFont.Weight.Bold))  # Increased from 10pt
    button.setToolTip(tooltip)
    button.setAccessibleName(f"Adjust {text}")
    button.setAccessibleDescription(f"Button to {tooltip.lower()}")
    button.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 {Colors.DARK_BUTTON_BG}, stop:1 #252525);
            color: {Colors.TEXT_COLOR};
            border: 1px solid {Colors.BORDER_COLOR};
            border-radius: 18px;
            font-family: {Fonts.PRIMARY_FAMILY};
            font-size: 12pt;
            font-weight: bold;
            padding: 4px;
            min-width: 36px;
            min-height: 36px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 {Colors.BLUE_HOVER}, stop:1 {Colors.BLUE_ACCENT});
            border-color: {Colors.BLUE_ACCENT};
        }}
        QPushButton:pressed {{
            background: {Colors.BLUE_ACCENT};
        }}
        QPushButton:disabled {{
            background-color: {Colors.DARK_BG};
            color: #666666;
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
    """Get consistent slider styling."""
    return f"""
        QSlider::groove:horizontal {{
            border: 1px solid {Colors.BORDER_COLOR};
            height: 12px;  /* Increased from 6px */
            background: {Colors.SLIDER_TRACK};
            border-radius: 6px;  /* Increased from 3px */
            margin: 2px 0px;
        }}
        
        QSlider::sub-page:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 {Colors.BLUE_ACCENT}, stop:1 {Colors.BLUE_HOVER});
            border-radius: 6px;  /* Increased from 3px */
        }}
        
        QSlider::handle:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 {Colors.TEXT_COLOR}, stop:1 #cccccc);
            border: 2px solid {Colors.BORDER_COLOR};  /* Increased from 1px */
            width: 22px;  /* Increased from 16px */
            margin: -5px 0px;  /* Increased from -1px */
            border-radius: 11px;  /* Increased from 8px */
        }}
        
        QSlider::handle:horizontal:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 {Colors.BLUE_ACCENT}, stop:1 {Colors.BLUE_HOVER});
            border-color: {Colors.BLUE_ACCENT};
        }}
    """


def get_consistent_font_style():
    """Get consistent font styling for all form controls."""
    return f"""
        font-family: {Fonts.PRIMARY_FAMILY};
        font-size: {Fonts.REGULAR_SIZE}px;
        color: {Colors.TEXT_COLOR};
    """

def get_label_style():
    """Get consistent label styling."""
    return f"""
        {get_consistent_font_style()}
        font-weight: bold;
    """

def get_small_label_style():
    """Get consistent small label styling."""
    return f"""
        font-family: {Fonts.PRIMARY_FAMILY};
        font-size: 12px;
        color: {Colors.TEXT_COLOR};
        font-weight: bold;
    """

def get_checkbox_style():
    """Get consistent checkbox styling with uniform fonts."""
    return f"""
        QCheckBox {{
            {get_consistent_font_style()}
            spacing: 10px;  /* Increased from 6px */
            padding: 3px;  /* Increased from 2px */
        }}
        
        QCheckBox::indicator {{
            width: 18px;  /* Increased from 14px */
            height: 18px;  /* Increased from 14px */
            border: 2px solid {Colors.BORDER_COLOR};  /* Increased from 1px */
            border-radius: 4px;  /* Increased from 2px */
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 {Colors.DARK_BUTTON_BG}, stop:1 #252525);
        }}
        
        QCheckBox::indicator:checked {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 {Colors.BLUE_ACCENT}, stop:1 {Colors.BLUE_HOVER});
            border-color: {Colors.BLUE_ACCENT};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {Colors.BLUE_HOVER};
        }}
        
        QCheckBox::indicator:disabled {{
            background-color: {Colors.DARK_BG};
            border-color: #666666;
        }}
    """


def get_radio_style():
    """Get consistent radio button styling with uniform fonts."""
    return f"""
        QRadioButton {{
            {get_consistent_font_style()}
            spacing: 10px;  /* Increased from 6px */
            padding: 3px;  /* Increased from 2px */
        }}
        
        QRadioButton::indicator {{
            width: 18px;  /* Increased from 14px */
            height: 18px;  /* Increased from 14px */
            border: 2px solid {Colors.BORDER_COLOR};  /* Increased from 1px */
            border-radius: 9px;  /* Increased from 7px */
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 {Colors.DARK_BUTTON_BG}, stop:1 #252525);
        }}
        
        QRadioButton::indicator:checked {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 {Colors.BLUE_ACCENT}, stop:1 {Colors.BLUE_HOVER});
            border-color: {Colors.BLUE_ACCENT};
        }}
        
        QRadioButton::indicator:hover {{
            border-color: {Colors.BLUE_HOVER};
        }}
        
        QRadioButton::indicator:disabled {{
            background-color: {Colors.DARK_BG};
            border-color: #666666;
        }}
    """ 