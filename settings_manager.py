"""Settings management for the Dwellpy application."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QSlider, QCheckBox, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QGuiApplication, QFont
import json
import os
import sys
from utils import center_window
from __version__ import __version__  # Add this at the top

# Dark theme color constants
DARK_BG = "#1a1a1a"         # Dark background - darker for contrast
DARK_BUTTON_BG = "#2d2d2d"  # Dark button background
TEXT_COLOR = "#ffffff"      # White text
BLUE_ACCENT = "#0078d7"     # Blue accent color
SLIDER_TRACK = "#444444"    # Slider track color
BORDER_COLOR = "#3c3c3c"    # Slight border color for depth

class SettingsManager:
    """
    Manages settings UI and persistence for Dwellpy.
    
    This class handles:
    - Loading and saving settings to disk
    - Generating and managing the settings UI dialog
    - Applying settings to the dwell detector
    """
    
    def __init__(self, dwell_detector):
        """
        Initialize the settings manager.
        
        Args:
            dwell_detector: The DwellDetector instance to configure
        """
        self.dwell_detector = dwell_detector
        self.setup_dialog = None  # Track settings dialog
        
        # Initialize timers to None
        self.move_minus_timer = None
        self.move_plus_timer = None
        self.time_minus_timer = None
        self.time_plus_timer = None
        self.transparency_minus_timer = None
        self.transparency_plus_timer = None
        self.move_minus_repeat = None
        self.move_plus_repeat = None
        self.time_minus_repeat = None
        self.time_plus_repeat = None
        self.transparency_minus_repeat = None
        self.transparency_plus_repeat = None
        
        # All application settings stored here
        self.settings = {
            'window_position': (100, 100),
            'move_limit': 5,
            'dwell_time': 1.0,
            'default_active': False,
            'default_mode': 'LEFT',
            'transparency_enabled': False,  # Disabled by default
            'transparency_level': 70  # Percentage (70% = 70% transparent, 30% opaque)
        }
        
        # Reference to UI manager for immediate transparency updates (set by UI manager)
        self.ui_manager = None
        
        # Load settings
        self.load_settings()
        
        # Apply settings to detector
        self.apply_detector_settings()
    
    def get_setting(self, key, default=None):
        """Get a setting value with a default fallback."""
        return self.settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set a setting value."""
        self.settings[key] = value
    
    def apply_detector_settings(self):
        """Apply settings to the dwell detector."""
        self.dwell_detector.move_limit = self.settings['move_limit']
        dwell_time_seconds = self.settings['dwell_time']
        self.dwell_detector.dwell_time = dwell_time_seconds
        self.dwell_detector.click_time = int(dwell_time_seconds / 0.1)
    
    def get_settings_path(self):
        """Get the path to the settings file."""
        try:
            # Get the base directory (works in both dev and PyInstaller)
            if getattr(sys, 'frozen', False):
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                
            # Create a settings file in the same directory as the executable/script
            return os.path.join(base_dir, "dwell_settings.json")
        except Exception as e:
            print(f"Error determining settings path: {e}")
            return "dwell_settings.json"  # Fallback to current directory
    
    def load_settings(self):
        """
        Load settings from JSON file and apply them to the dwell detector.
        """
        try:
            settings_file = self.get_settings_path()
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                
                # Update our settings dict with loaded values
                for key, value in loaded_settings.items():
                    self.settings[key] = value
                
                print(f"Settings loaded successfully: {self.settings}")
            else:
                # Default position near center of screen
                # In PyQt6, QDesktopWidget is removed, use QScreen instead
                primary_screen = QGuiApplication.primaryScreen()
                if primary_screen:
                    screen_geometry = primary_screen.geometry()
                    screen_width = screen_geometry.width()
                    screen_height = screen_geometry.height()
                    self.settings['window_position'] = (screen_width // 2 - 150, screen_height // 2 - 25)
                print("Settings file not found, using defaults")
                
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Set fallback defaults if loading fails
            self.settings['move_limit'] = 5
            self.settings['dwell_time'] = 1.0
            self.settings['transparency_enabled'] = False
            self.settings['transparency_level'] = 70
            print("Using fallback defaults due to error")
    
    def save_settings(self):
        """Save all settings to JSON file."""
        try:
            settings_file = self.get_settings_path()
            
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f)
                
            print(f"Settings saved: {self.settings}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def open_setup(self, button_manager, parent_window=None):
        """
        Open the setup dialog if not already open.
        
        Args:
            button_manager: ButtonManager instance for button hover tracking
            parent_window: Parent window for the dialog
        """
        # Check if setup dialog is already open
        if self.setup_dialog is not None and self.setup_dialog.isVisible():
            # Bring it to front
            self.setup_dialog.raise_()
            self.setup_dialog.activateWindow()
            return
        
        # Create timers for hover delay functionality
        self.move_minus_timer = QTimer()
        self.move_minus_timer.setSingleShot(True)
        self.move_minus_timer.timeout.connect(self.start_minus_move_repeat)
        
        self.move_plus_timer = QTimer()
        self.move_plus_timer.setSingleShot(True)
        self.move_plus_timer.timeout.connect(self.start_plus_move_repeat)
        
        self.time_minus_timer = QTimer()
        self.time_minus_timer.setSingleShot(True)
        self.time_minus_timer.timeout.connect(self.start_minus_time_repeat)
        
        self.time_plus_timer = QTimer()
        self.time_plus_timer.setSingleShot(True)
        self.time_plus_timer.timeout.connect(self.start_plus_time_repeat)
        
        self.transparency_minus_timer = QTimer()
        self.transparency_minus_timer.setSingleShot(True)
        self.transparency_minus_timer.timeout.connect(self.start_minus_transparency_repeat)
        
        self.transparency_plus_timer = QTimer()
        self.transparency_plus_timer.setSingleShot(True)
        self.transparency_plus_timer.timeout.connect(self.start_plus_transparency_repeat)
        
        # Repeat timers (will trigger repeatedly after initial delay)
        self.move_minus_repeat = QTimer()
        self.move_minus_repeat.timeout.connect(self.on_hover_minus_move_limit)
        
        self.move_plus_repeat = QTimer()
        self.move_plus_repeat.timeout.connect(self.on_hover_plus_move_limit)
        
        self.time_minus_repeat = QTimer()
        self.time_minus_repeat.timeout.connect(self.on_hover_minus_dwell_time)
        
        self.time_plus_repeat = QTimer()
        self.time_plus_repeat.timeout.connect(self.on_hover_plus_dwell_time)
        
        self.transparency_minus_repeat = QTimer()
        self.transparency_minus_repeat.timeout.connect(self.on_hover_minus_transparency)
        
        self.transparency_plus_repeat = QTimer()
        self.transparency_plus_repeat.timeout.connect(self.on_hover_plus_transparency)
        
        # Create new setup dialog
        self.setup_dialog = QDialog(parent_window)
        self.setup_dialog.setFixedSize(350, 450)  # Increased height for transparency settings
        
        # Set window flags for frameless window
        self.setup_dialog.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint  # No title bar
        )
        
        # Make dialog non-modal to allow dwell clicking to continue
        self.setup_dialog.setModal(False)
        
        # Apply dark theme with subtle border
        self.setup_dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {DARK_BG};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self.setup_dialog)
        main_layout.setContentsMargins(20, 15, 20, 10)
        main_layout.setSpacing(8)  # Reduced spacing to fit more elements
        
        # Title area with close button
        title_frame = QFrame(self.setup_dialog)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title label
        title_label = QLabel("Dwellpy Settings", title_frame)
        title_label.setStyleSheet(f"""
            font-family: 'Segoe UI', Arial;
            font-size: 16pt;
            font-weight: bold;
            color: {TEXT_COLOR};
        """)
        title_layout.addWidget(title_label)
        
        # Close button
        close_button = QPushButton("×", title_frame)
        close_button.setFixedSize(24, 24)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_COLOR};
                border: none;
                font-size: 16pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: #aaaaaa;
            }}
        """)
        close_button.clicked.connect(self.on_ok_button_click)
        title_layout.addWidget(close_button)
        
        main_layout.addWidget(title_frame)
        
        # Move Limit label
        move_label = QLabel("Move Limit (px):", self.setup_dialog)
        move_label.setFont(QFont("Segoe UI", 11))
        move_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold;")
        main_layout.addWidget(move_label)
        
        # First slider group - Move Limit
        move_limit_frame = QFrame(self.setup_dialog)
        move_limit_layout = QHBoxLayout(move_limit_frame)
        move_limit_layout.setContentsMargins(0, 0, 0, 0)
        move_limit_layout.setSpacing(5)
        
        # Minus button
        move_minus_btn = QPushButton("-", move_limit_frame)
        move_minus_btn.setFixedSize(20, 20)
        move_minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        move_minus_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_BUTTON_BG};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
                font-weight: bold;
            }}
        """)
        move_minus_btn.enterEvent = lambda e: self.on_enter_minus_move()
        move_minus_btn.leaveEvent = lambda e: self.on_leave_minus_move()
        move_limit_layout.addWidget(move_minus_btn)
        
        # Slider
        self.move_limit_slider = QSlider(Qt.Orientation.Horizontal, move_limit_frame)
        self.move_limit_slider.setRange(3, 20)
        self.move_limit_slider.setValue(self.settings['move_limit'])
        self.move_limit_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {SLIDER_TRACK};
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {BLUE_ACCENT};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: {BLUE_ACCENT};
                height: 4px;
                border-radius: 2px;
            }}
        """)
        move_limit_layout.addWidget(self.move_limit_slider)
        
        # Plus button
        move_plus_btn = QPushButton("+", move_limit_frame)
        move_plus_btn.setFixedSize(20, 20)
        move_plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        move_plus_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_BUTTON_BG};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
                font-weight: bold;
            }}
        """)
        move_plus_btn.enterEvent = lambda e: self.on_enter_plus_move()
        move_plus_btn.leaveEvent = lambda e: self.on_leave_plus_move()
        move_limit_layout.addWidget(move_plus_btn)
        
        # Value label
        self.move_limit_value = QLabel(str(self.settings['move_limit']), move_limit_frame)
        self.move_limit_value.setStyleSheet(f"""
            font-family: 'Segoe UI', Arial;
            font-size: 12pt;
            font-weight: bold;
            color: {TEXT_COLOR};
        """)
        self.move_limit_value.setFixedWidth(30)
        move_limit_layout.addWidget(self.move_limit_value)
        
        main_layout.addWidget(move_limit_frame)
        
        # Add visual separator
        separator = QFrame(self.setup_dialog)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setMaximumHeight(1)
        separator.setStyleSheet(f"background-color: {BORDER_COLOR};")
        main_layout.addWidget(separator)
        
        # Dwell Time label
        time_label = QLabel("Dwell Time (s):", self.setup_dialog)
        time_label.setFont(QFont("Segoe UI", 11))
        time_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold;")
        main_layout.addWidget(time_label)
        
        # Second slider group - Dwell Time
        time_frame = QFrame(self.setup_dialog)
        time_layout = QHBoxLayout(time_frame)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(5)
        
        # Minus button
        time_minus_btn = QPushButton("-", time_frame)
        time_minus_btn.setFixedSize(20, 20)
        time_minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        time_minus_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_BUTTON_BG};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
                font-weight: bold;
            }}
        """)
        time_minus_btn.enterEvent = lambda e: self.on_enter_minus_time()
        time_minus_btn.leaveEvent = lambda e: self.on_leave_minus_time()
        time_layout.addWidget(time_minus_btn)
        
        # Slider
        self.time_slider = QSlider(Qt.Orientation.Horizontal, time_frame)
        self.time_slider.setRange(1, 20)  # 0.1 to 2.0 seconds (x10 for smoother slider)
        self.time_slider.setValue(int(self.settings['dwell_time'] * 10))
        self.time_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {SLIDER_TRACK};
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {BLUE_ACCENT};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: {BLUE_ACCENT};
                height: 4px;
                border-radius: 2px;
            }}
        """)
        time_layout.addWidget(self.time_slider)
        
        # Plus button
        time_plus_btn = QPushButton("+", time_frame)
        time_plus_btn.setFixedSize(20, 20)
        time_plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        time_plus_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_BUTTON_BG};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
                font-weight: bold;
            }}
        """)
        time_plus_btn.enterEvent = lambda e: self.on_enter_plus_time()
        time_plus_btn.leaveEvent = lambda e: self.on_leave_plus_time()
        time_layout.addWidget(time_plus_btn)
        
        # Value label
        self.time_value = QLabel(f"{self.settings['dwell_time']:.1f}", time_frame)
        self.time_value.setStyleSheet(f"""
            font-family: 'Segoe UI', Arial;
            font-size: 12pt;
            font-weight: bold;
            color: {TEXT_COLOR};
        """)
        self.time_value.setFixedWidth(30)
        time_layout.addWidget(self.time_value)
        
        main_layout.addWidget(time_frame)
        
        # Add another visual separator
        separator2 = QFrame(self.setup_dialog)
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setMaximumHeight(1)
        separator2.setStyleSheet(f"background-color: {BORDER_COLOR};")
        main_layout.addWidget(separator2)
        
        # Transparency enable checkbox
        transparency_enable_frame = QFrame(self.setup_dialog)
        transparency_enable_layout = QHBoxLayout(transparency_enable_frame)
        transparency_enable_layout.setContentsMargins(0, 0, 0, 0)
        transparency_enable_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.transparency_check = QCheckBox("Enable window transparency", transparency_enable_frame)
        self.transparency_check.setChecked(self.settings['transparency_enabled'])
        self.transparency_check.setFont(QFont("Segoe UI", 11))
        self.transparency_check.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_COLOR};
                spacing: 10px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                background-color: {DARK_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {BLUE_ACCENT};
                border: 1px solid {BLUE_ACCENT};
            }}
        """)
        self.transparency_check.stateChanged.connect(self.on_transparency_toggle)
        transparency_enable_layout.addWidget(self.transparency_check)
        
        main_layout.addWidget(transparency_enable_frame)
        
        # Transparency level label
        transparency_label = QLabel("Transparency (%):", self.setup_dialog)
        transparency_label.setFont(QFont("Segoe UI", 11))
        transparency_label.setStyleSheet(f"color: {TEXT_COLOR}; font-weight: bold;")
        main_layout.addWidget(transparency_label)
        
        # Third slider group - Transparency Level
        transparency_frame = QFrame(self.setup_dialog)
        transparency_layout = QHBoxLayout(transparency_frame)
        transparency_layout.setContentsMargins(0, 0, 0, 0)
        transparency_layout.setSpacing(5)
        
        # Minus button
        transparency_minus_btn = QPushButton("-", transparency_frame)
        transparency_minus_btn.setFixedSize(20, 20)
        transparency_minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        transparency_minus_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_BUTTON_BG};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
                font-weight: bold;
            }}
        """)
        transparency_minus_btn.enterEvent = lambda e: self.on_enter_minus_transparency()
        transparency_minus_btn.leaveEvent = lambda e: self.on_leave_minus_transparency()
        transparency_layout.addWidget(transparency_minus_btn)
        
        # Slider
        self.transparency_slider = QSlider(Qt.Orientation.Horizontal, transparency_frame)
        self.transparency_slider.setRange(10, 90)  # 10% to 90% transparency
        self.transparency_slider.setValue(self.settings['transparency_level'])
        self.transparency_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {SLIDER_TRACK};
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {BLUE_ACCENT};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: {BLUE_ACCENT};
                height: 4px;
                border-radius: 2px;
            }}
        """)
        transparency_layout.addWidget(self.transparency_slider)
        
        # Plus button
        transparency_plus_btn = QPushButton("+", transparency_frame)
        transparency_plus_btn.setFixedSize(20, 20)
        transparency_plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        transparency_plus_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {DARK_BUTTON_BG};
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
                font-weight: bold;
            }}
        """)
        transparency_plus_btn.enterEvent = lambda e: self.on_enter_plus_transparency()
        transparency_plus_btn.leaveEvent = lambda e: self.on_leave_plus_transparency()
        transparency_layout.addWidget(transparency_plus_btn)
        
        # Value label
        self.transparency_value = QLabel(f"{self.settings['transparency_level']}%", transparency_frame)
        self.transparency_value.setStyleSheet(f"""
            font-family: 'Segoe UI', Arial;
            font-size: 12pt;
            font-weight: bold;
            color: {TEXT_COLOR};
        """)
        self.transparency_value.setFixedWidth(40)
        transparency_layout.addWidget(self.transparency_value)
        
        main_layout.addWidget(transparency_frame)
        
        # Update transparency controls enabled state
        self.update_transparency_controls_state()
        
        # Default on state
        active_frame = QFrame(self.setup_dialog)
        active_layout = QHBoxLayout(active_frame)
        active_layout.setContentsMargins(0, 0, 0, 0)
        active_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.active_check = QCheckBox("Start active on launch", active_frame)
        self.active_check.setChecked(self.settings['default_active'])
        self.active_check.setFont(QFont("Segoe UI", 11))
        self.active_check.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_COLOR};
                spacing: 10px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                background-color: {DARK_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {BLUE_ACCENT};
                border: 1px solid {BLUE_ACCENT};
            }}
        """)
        active_layout.addWidget(self.active_check)
        
        main_layout.addWidget(active_frame)
        
        # OK button
        ok_button = QPushButton("OK", self.setup_dialog)
        ok_button.setFixedSize(250, 35)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BLUE_ACCENT};
                color: {TEXT_COLOR};
                border: none;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: #0069c0;
            }}
        """)
        ok_button.clicked.connect(self.on_ok_button_click)
        
        main_layout.addWidget(ok_button, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Bottom separator and version
        bottom_frame = QFrame(self.setup_dialog)
        bottom_layout = QVBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(0, 5, 0, 0)
        bottom_layout.setSpacing(5)
        
        # Separator
        bottom_separator = QFrame(self.setup_dialog)
        bottom_separator.setFrameShape(QFrame.Shape.HLine)
        bottom_separator.setFrameShadow(QFrame.Shadow.Sunken)
        bottom_separator.setStyleSheet(f"background-color: {BORDER_COLOR};")
        bottom_layout.addWidget(bottom_separator)
        
        # Version info
        version_label = QLabel(f"Dwellpy v{__version__}", self.setup_dialog)
        version_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial;
            font-size: 9pt;
            color: #999999;
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        bottom_layout.addWidget(version_label)
        
        main_layout.addWidget(bottom_frame)
        
        # Connect signals
        self.move_limit_slider.valueChanged.connect(self.update_move_limit_value)
        self.time_slider.valueChanged.connect(self.update_time_value)
        self.transparency_slider.valueChanged.connect(self.update_transparency_value)
        self.active_check.stateChanged.connect(self.on_active_toggle)
        
        # Register button command
        button_manager.register_command("OK_SETTINGS", self.on_ok_button_click)
        
        # Center the dialog on screen
        center_window(self.setup_dialog)
        
        # Show the dialog (non-modal)
        self.setup_dialog.show()
    
    def update_transparency_controls_state(self):
        """Enable/disable transparency controls based on checkbox state."""
        enabled = self.transparency_check.isChecked()
        
        # Enable/disable slider and buttons
        self.transparency_slider.setEnabled(enabled)
        
        # Update styling to show disabled state
        if enabled:
            self.transparency_slider.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    background: {SLIDER_TRACK};
                    height: 4px;
                    border-radius: 2px;
                }}
                QSlider::handle:horizontal {{
                    background: {BLUE_ACCENT};
                    width: 16px;
                    height: 16px;
                    margin: -6px 0;
                    border-radius: 8px;
                }}
                QSlider::sub-page:horizontal {{
                    background: {BLUE_ACCENT};
                    height: 4px;
                    border-radius: 2px;
                }}
            """)
        else:
            self.transparency_slider.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    background: #333333;
                    height: 4px;
                    border-radius: 2px;
                }}
                QSlider::handle:horizontal {{
                    background: #666666;
                    width: 16px;
                    height: 16px;
                    margin: -6px 0;
                    border-radius: 8px;
                }}
                QSlider::sub-page:horizontal {{
                    background: #666666;
                    height: 4px;
                    border-radius: 2px;
                }}
            """)
    
    # New hover enter/leave methods for transparency
    def on_enter_minus_transparency(self):
        """Start the timer when mouse enters minus transparency button."""
        if self.transparency_check.isChecked():
            self.transparency_minus_timer.start(500)

    def on_leave_minus_transparency(self):
        """Stop all timers when mouse leaves minus transparency button."""
        self.transparency_minus_timer.stop()
        self.transparency_minus_repeat.stop()

    def on_enter_plus_transparency(self):
        """Start the timer when mouse enters plus transparency button."""
        if self.transparency_check.isChecked():
            self.transparency_plus_timer.start(500)

    def on_leave_plus_transparency(self):
        """Stop all timers when mouse leaves plus transparency button."""
        self.transparency_plus_timer.stop()
        self.transparency_plus_repeat.stop()

    def start_minus_transparency_repeat(self):
        """After initial delay, start repeating."""
        self.on_hover_minus_transparency()
        self.transparency_minus_repeat.start(500)

    def start_plus_transparency_repeat(self):
        """After initial delay, start repeating."""
        self.on_hover_plus_transparency()
        self.transparency_plus_repeat.start(500)
    
    def on_hover_minus_transparency(self):
        """Handle hover over minus button for transparency."""
        if self.transparency_slider.value() > self.transparency_slider.minimum():
            self.transparency_slider.setValue(self.transparency_slider.value() - 5)
    
    def on_hover_plus_transparency(self):
        """Handle hover over plus button for transparency."""
        if self.transparency_slider.value() < self.transparency_slider.maximum():
            self.transparency_slider.setValue(self.transparency_slider.value() + 5)
    
    def update_transparency_value(self, value):
        """Update transparency value and apply setting."""
        self.transparency_value.setText(f"{value}%")
        self.settings['transparency_level'] = value
        
        # Apply transparency change immediately
        if self.ui_manager:
            self.ui_manager.apply_transparency_settings()
        
        print(f"Transparency level updated to: {value}%")
    
    def on_transparency_toggle(self, state):
        """Handle transparency checkbox toggle."""
        is_enabled = state == 2  # Qt.CheckState.Checked is 2
        self.settings['transparency_enabled'] = is_enabled
        self.update_transparency_controls_state()
        
        # Apply transparency change immediately
        if self.ui_manager:
            self.ui_manager.apply_transparency_settings()
        
        print(f"Transparency enabled: {is_enabled}")
    
    # Existing hover enter/leave methods
    def on_enter_minus_move(self):
        """Start the timer when mouse enters minus move button."""
        self.move_minus_timer.start(500)  # 500 ms = 0.5 seconds

    def on_leave_minus_move(self):
        """Stop all timers when mouse leaves minus move button."""
        self.move_minus_timer.stop()
        self.move_minus_repeat.stop()

    def on_enter_plus_move(self):
        """Start the timer when mouse enters plus move button."""
        self.move_plus_timer.start(500)

    def on_leave_plus_move(self):
        """Stop all timers when mouse leaves plus move button."""
        self.move_plus_timer.stop()
        self.move_plus_repeat.stop()

    def on_enter_minus_time(self):
        """Start the timer when mouse enters minus time button."""
        self.time_minus_timer.start(500)

    def on_leave_minus_time(self):
        """Stop all timers when mouse leaves minus time button."""
        self.time_minus_timer.stop()
        self.time_minus_repeat.stop()

    def on_enter_plus_time(self):
        """Start the timer when mouse enters plus time button."""
        self.time_plus_timer.start(500)

    def on_leave_plus_time(self):
        """Stop all timers when mouse leaves plus time button."""
        self.time_plus_timer.stop()
        self.time_plus_repeat.stop()

    # New methods to start repeating timers
    def start_minus_move_repeat(self):
        """After initial delay, start repeating."""
        self.on_hover_minus_move_limit()  # Trigger once immediately
        self.move_minus_repeat.start(500)  # Then repeat every 0.5 seconds

    def start_plus_move_repeat(self):
        """After initial delay, start repeating."""
        self.on_hover_plus_move_limit()  # Trigger once immediately
        self.move_plus_repeat.start(500)  # Then repeat every 0.5 seconds

    def start_minus_time_repeat(self):
        """After initial delay, start repeating."""
        self.on_hover_minus_dwell_time()  # Trigger once immediately
        self.time_minus_repeat.start(500)  # Then repeat every 0.5 seconds

    def start_plus_time_repeat(self):
        """After initial delay, start repeating."""
        self.on_hover_plus_dwell_time()  # Trigger once immediately
        self.time_plus_repeat.start(500)  # Then repeat every 0.5 seconds
    
    def on_hover_minus_move_limit(self):
        """Handle hover over minus button for move limit."""
        if self.move_limit_slider.value() > self.move_limit_slider.minimum():
            # Decrement the slider value
            self.move_limit_slider.setValue(self.move_limit_slider.value() - 1)
    
    def on_hover_plus_move_limit(self):
        """Handle hover over plus button for move limit."""
        if self.move_limit_slider.value() < self.move_limit_slider.maximum():
            # Increment the slider value
            self.move_limit_slider.setValue(self.move_limit_slider.value() + 1)
    
    def on_hover_minus_dwell_time(self):
        """Handle hover over minus button for dwell time."""
        if self.time_slider.value() > self.time_slider.minimum():
            # Decrement the slider value
            self.time_slider.setValue(self.time_slider.value() - 1)
    
    def on_hover_plus_dwell_time(self):
        """Handle hover over plus button for dwell time."""
        if self.time_slider.value() < self.time_slider.maximum():
            # Increment the slider value
            self.time_slider.setValue(self.time_slider.value() + 1)
    
    def update_move_limit_value(self, value):
        """Update move limit value and apply setting."""
        self.move_limit_value.setText(str(value))
        # Apply setting immediately
        self.settings['move_limit'] = value
        self.dwell_detector.move_limit = value
        print(f"Move limit updated to: {value}")
    
    def update_time_value(self, value):
        """Update dwell time value and apply setting."""
        # Convert slider value (1-20) to seconds (0.1-2.0)
        seconds = value / 10.0
        self.time_value.setText(f"{seconds:.1f}")
        # Apply setting immediately
        self.settings['dwell_time'] = seconds
        self.dwell_detector.dwell_time = seconds
        self.dwell_detector.click_time = int(seconds / 0.1)
        print(f"Dwell time updated to: {seconds}s")
    
    def on_active_toggle(self, state):
        """Handle active checkbox toggle."""
        is_active = state == 2  # Qt.CheckState.Checked is 2
        self.settings['default_active'] = is_active
        print(f"Default active state updated to: {is_active}")
    
    def on_ok_button_click(self):
        """Handle OK button click."""
        # Stop all timers if they exist
        timers_to_stop = [
            'move_minus_timer', 'move_plus_timer', 'time_minus_timer', 'time_plus_timer',
            'transparency_minus_timer', 'transparency_plus_timer',
            'move_minus_repeat', 'move_plus_repeat', 'time_minus_repeat', 'time_plus_repeat',
            'transparency_minus_repeat', 'transparency_plus_repeat'
        ]
        
        for timer_name in timers_to_stop:
            if hasattr(self, timer_name) and getattr(self, timer_name):
                getattr(self, timer_name).stop()
        
        # Save settings
        self.save_settings()
        print(f"Settings saved")
        
        # Close dialog
        if self.setup_dialog and self.setup_dialog.isVisible():
            self.setup_dialog.close()
            self.setup_dialog = None