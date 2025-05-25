"""Utility functions for the Dwellpy application."""

import os
import sys
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QWidget


def center_window(window: QWidget) -> None:
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


def get_application_directory() -> str:
    """
    Get the directory where the application is running from.
    
    Works in both development and PyInstaller environments.
    
    Returns:
        str: Path to the application directory
    """
    try:
        # Get the base directory (works in both dev and PyInstaller)
        if getattr(sys, 'frozen', False):
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        return base_dir
    except Exception as e:
        return os.getcwd()  # Fallback to current directory


def get_settings_file_path(filename: str = "dwell_settings.json") -> str:
    """
    Get the full path to a settings file.
    
    Args:
        filename: Name of the settings file
        
    Returns:
        str: Full path to the settings file
    """
    base_dir = get_application_directory()
    return os.path.join(base_dir, filename)


def calculate_opacity_from_transparency(transparency_percent: int) -> float:
    """
    Convert transparency percentage to opacity value.
    
    Args:
        transparency_percent: Transparency as percentage (0-100)
        
    Returns:
        float: Opacity value (0.0-1.0)
    """
    # 70% transparent = 30% opaque = 0.3 opacity
    return (100 - transparency_percent) / 100.0


def create_button_stylesheet(base_style: dict, color_style: dict = None, 
                           hover_style: dict = None, disabled: bool = False) -> str:
    """
    Create a complete Qt stylesheet for buttons.
    
    Args:
        base_style: Base button styling dict
        color_style: Color-specific styling dict
        hover_style: Hover state styling dict
        disabled: Whether button is disabled
        
    Returns:
        str: Complete Qt stylesheet
    """
    # Start with base style
    style_dict = base_style.copy()
    
    # Apply color style if provided
    if color_style:
        style_dict.update(color_style)
    
    # Convert dict to CSS-like properties
    properties = []
    hover_properties = []
    
    for key, value in style_dict.items():
        if key.startswith('hover-'):
            # Extract hover properties
            css_key = key.replace('hover-', '').replace('_', '-')
            hover_properties.append(f"{css_key}: {value};")
        else:
            css_key = key.replace('_', '-')
            properties.append(f"{css_key}: {value};")
    
    # Build the complete stylesheet
    stylesheet_parts = [
        "QPushButton {",
        "    " + "\n    ".join(properties),
        "}"
    ]
    
    # Add hover state if there are hover properties
    if hover_properties or hover_style:
        if hover_style:
            for key, value in hover_style.items():
                css_key = key.replace('_', '-')
                hover_properties.append(f"{css_key}: {value};")
                
        stylesheet_parts.extend([
            "QPushButton:hover {",
            "    " + "\n    ".join(hover_properties),
            "}"
        ])
    
    return "\n".join(stylesheet_parts)


def format_time_display(seconds: float) -> str:
    """
    Format time in seconds for display.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        str: Formatted time string
    """
    return f"{seconds:.1f}"


def format_distance_display(pixels: int) -> str:
    """
    Format distance in pixels for display.
    
    Args:
        pixels: Distance in pixels
        
    Returns:
        str: Formatted distance string
    """
    return str(pixels)


def format_percentage_display(percent: int) -> str:
    """
    Format percentage for display.
    
    Args:
        percent: Percentage value
        
    Returns:
        str: Formatted percentage string
    """
    return f"{percent}%"


def clamp_value(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        float: Clamped value
    """
    return max(min_val, min(value, max_val))


def get_screen_center() -> tuple[int, int]:
    """
    Get the center point of the primary screen.
    
    Returns:
        tuple: (x, y) coordinates of screen center
    """
    primary_screen = QGuiApplication.primaryScreen()
    if primary_screen:
        screen_geometry = primary_screen.geometry()
        center_x = screen_geometry.width() // 2
        center_y = screen_geometry.height() // 2
        return (center_x, center_y)
    return (800, 600)  # Fallback

def get_asset_path(asset_name):
    """Get path to asset file, works in dev and PyInstaller"""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running in development
        base_path = os.path.dirname(os.path.dirname(__file__))
    
    return os.path.join(base_path, 'assets', 'icons', asset_name)
