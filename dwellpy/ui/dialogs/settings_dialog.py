"""Settings dialog for the Dwellpy application."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QSlider, QCheckBox, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

try:
    from ...config.constants import Colors, BORDER_RADIUS, Fonts
    from ...utils.helpers import center_window, format_time_display, format_percentage_display
    from ...__init__ import __version__
except ImportError:
    # Fallback constants
    class Colors:
        DARK_BG = "#1a1a1a"
        DARK_BUTTON_BG = "#2d2d2d"
        TEXT_COLOR = "#ffffff"
        BLUE_ACCENT = "#0078d7"
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


class SettingsDialog(QDialog):
    """Settings dialog for Dwellpy configuration."""
    
    def __init__(self, settings_manager, button_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.button_manager = button_manager
        
        # Initialize timers
        self.setup_timers()
        
        # Setup the dialog
        self.setup_ui()
        
        # Connect signals
        self.connect_signals()
    
    def setup_timers(self):
        """Initialize all hover timers."""
        # Initial delay timers
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
        
        self.scroll_speed_minus_timer = QTimer()
        self.scroll_speed_minus_timer.setSingleShot(True)
        self.scroll_speed_minus_timer.timeout.connect(self.start_minus_scroll_speed_repeat)
        
        self.scroll_speed_plus_timer = QTimer()
        self.scroll_speed_plus_timer.setSingleShot(True)
        self.scroll_speed_plus_timer.timeout.connect(self.start_plus_scroll_speed_repeat)
        
        # Repeat timers
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
        
        self.scroll_speed_minus_repeat = QTimer()
        self.scroll_speed_minus_repeat.timeout.connect(self.on_hover_minus_scroll_speed)
        
        self.scroll_speed_plus_repeat = QTimer()
        self.scroll_speed_plus_repeat.timeout.connect(self.on_hover_plus_scroll_speed)
    
    def setup_ui(self):
        """Setup the dialog UI."""
        self.setFixedSize(350, 580)  # Increased height for scroll settings
        
        # Set window flags for frameless window
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        
        # Make dialog non-modal
        self.setModal(False)
        
        # Apply dark theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.DARK_BG};
                color: {Colors.TEXT_COLOR};
                border: 1px solid {Colors.BORDER_COLOR};
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 10)
        main_layout.setSpacing(8)
        
        # Title area with close button
        title_frame = self.create_title_frame()
        main_layout.addWidget(title_frame)
        
        # Move Limit section
        self.create_move_limit_section(main_layout)
        
        # Add separator
        self.add_separator(main_layout)
        
        # Dwell Time section
        self.create_dwell_time_section(main_layout)
        
        # Add separator
        self.add_separator(main_layout)
        
        # Transparency section
        self.create_transparency_section(main_layout)
        
        # Add separator
        self.add_separator(main_layout)
        
        # Scroll Widget section
        self.create_scroll_widget_section(main_layout)
        
        # Default active state
        self.create_active_state_section(main_layout)
        
        # OK button
        self.create_ok_button(main_layout)
        
        # Bottom section with version
        self.create_bottom_section(main_layout)
        
        # Center the dialog
        center_window(self)
    
    def create_title_frame(self):
        """Create title frame with close button."""
        title_frame = QFrame()
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title label
        title_label = QLabel("Dwellpy Settings")
        title_label.setStyleSheet(f"""
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 16pt;
            font-weight: bold;
            color: {Colors.TEXT_COLOR};
        """)
        title_layout.addWidget(title_label)
        
        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(24, 24)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_COLOR};
                border: none;
                font-size: 16pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                color: #aaaaaa;
            }}
        """)
        close_button.clicked.connect(self.accept)
        title_layout.addWidget(close_button)
        
        return title_frame
    
    def create_move_limit_section(self, main_layout):
        """Create move limit adjustment section."""
        # Label
        move_label = QLabel("Move Limit (px):")
        move_label.setFont(QFont("Helvetica Neue", 11))
        move_label.setStyleSheet(f"color: {Colors.TEXT_COLOR}; font-weight: bold;")
        main_layout.addWidget(move_label)
        
        # Controls frame
        move_frame = QFrame()
        move_layout = QHBoxLayout(move_frame)
        move_layout.setContentsMargins(0, 0, 0, 0)
        move_layout.setSpacing(5)
        
        # Minus button
        move_minus_btn = self.create_adjustment_button("-")
        move_minus_btn.enterEvent = lambda e: self.on_enter_minus_move()
        move_minus_btn.leaveEvent = lambda e: self.on_leave_minus_move()
        move_layout.addWidget(move_minus_btn)
        
        # Slider
        self.move_limit_slider = QSlider(Qt.Orientation.Horizontal)
        self.move_limit_slider.setRange(3, 20)
        self.move_limit_slider.setValue(self.settings_manager.get_setting('move_limit', 5))
        self.move_limit_slider.setStyleSheet(self.get_slider_style())
        move_layout.addWidget(self.move_limit_slider)
        
        # Plus button
        move_plus_btn = self.create_adjustment_button("+")
        move_plus_btn.enterEvent = lambda e: self.on_enter_plus_move()
        move_plus_btn.leaveEvent = lambda e: self.on_leave_plus_move()
        move_layout.addWidget(move_plus_btn)
        
        # Value label
        self.move_limit_value = QLabel(str(self.settings_manager.get_setting('move_limit', 5)))
        self.move_limit_value.setStyleSheet(f"""
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 12pt;
            font-weight: bold;
            color: {Colors.TEXT_COLOR};
        """)
        self.move_limit_value.setFixedWidth(30)
        move_layout.addWidget(self.move_limit_value)
        
        main_layout.addWidget(move_frame)
    
    def create_dwell_time_section(self, main_layout):
        """Create dwell time adjustment section."""
        # Label
        time_label = QLabel("Dwell Time (s):")
        time_label.setFont(QFont("Helvetica Neue", 11))
        time_label.setStyleSheet(f"color: {Colors.TEXT_COLOR}; font-weight: bold;")
        main_layout.addWidget(time_label)
        
        # Controls frame
        time_frame = QFrame()
        time_layout = QHBoxLayout(time_frame)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(5)
        
        # Minus button
        time_minus_btn = self.create_adjustment_button("-")
        time_minus_btn.enterEvent = lambda e: self.on_enter_minus_time()
        time_minus_btn.leaveEvent = lambda e: self.on_leave_minus_time()
        time_layout.addWidget(time_minus_btn)
        
        # Slider
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(1, 20)
        self.time_slider.setValue(int(self.settings_manager.get_setting('dwell_time', 1.0) * 10))
        self.time_slider.setStyleSheet(self.get_slider_style())
        time_layout.addWidget(self.time_slider)
        
        # Plus button
        time_plus_btn = self.create_adjustment_button("+")
        time_plus_btn.enterEvent = lambda e: self.on_enter_plus_time()
        time_plus_btn.leaveEvent = lambda e: self.on_leave_plus_time()
        time_layout.addWidget(time_plus_btn)
        
        # Value label
        self.time_value = QLabel(format_time_display(self.settings_manager.get_setting('dwell_time', 1.0)))
        self.time_value.setStyleSheet(f"""
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 12pt;
            font-weight: bold;
            color: {Colors.TEXT_COLOR};
        """)
        self.time_value.setFixedWidth(30)
        time_layout.addWidget(self.time_value)
        
        main_layout.addWidget(time_frame)
    
    def create_transparency_section(self, main_layout):
        """Create transparency adjustment section."""
        # Enable checkbox
        transparency_enable_frame = QFrame()
        transparency_enable_layout = QHBoxLayout(transparency_enable_frame)
        transparency_enable_layout.setContentsMargins(0, 0, 0, 0)
        transparency_enable_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.transparency_check = QCheckBox("Enable window transparency")
        self.transparency_check.setChecked(self.settings_manager.get_setting('transparency_enabled', False))
        self.transparency_check.setFont(QFont("Helvetica Neue", 11))
        self.transparency_check.setStyleSheet(self.get_checkbox_style())
        transparency_enable_layout.addWidget(self.transparency_check)
        
        main_layout.addWidget(transparency_enable_frame)
        
        # Transparency level label
        transparency_label = QLabel("Transparency (%):")
        transparency_label.setFont(QFont("Helvetica Neue", 11))
        transparency_label.setStyleSheet(f"color: {Colors.TEXT_COLOR}; font-weight: bold;")
        main_layout.addWidget(transparency_label)
        
        # Controls frame
        transparency_frame = QFrame()
        transparency_layout = QHBoxLayout(transparency_frame)
        transparency_layout.setContentsMargins(0, 0, 0, 0)
        transparency_layout.setSpacing(5)
        
        # Minus button
        transparency_minus_btn = self.create_adjustment_button("-")
        transparency_minus_btn.enterEvent = lambda e: self.on_enter_minus_transparency()
        transparency_minus_btn.leaveEvent = lambda e: self.on_leave_minus_transparency()
        transparency_layout.addWidget(transparency_minus_btn)
        
        # Slider
        self.transparency_slider = QSlider(Qt.Orientation.Horizontal)
        self.transparency_slider.setRange(10, 90)
        self.transparency_slider.setValue(self.settings_manager.get_setting('transparency_level', 70))
        transparency_layout.addWidget(self.transparency_slider)
        
        # Plus button
        transparency_plus_btn = self.create_adjustment_button("+")
        transparency_plus_btn.enterEvent = lambda e: self.on_enter_plus_transparency()
        transparency_plus_btn.leaveEvent = lambda e: self.on_leave_plus_transparency()
        transparency_layout.addWidget(transparency_plus_btn)
        
        # Value label
        self.transparency_value = QLabel(format_percentage_display(self.settings_manager.get_setting('transparency_level', 70)))
        self.transparency_value.setStyleSheet(f"""
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 12pt;
            font-weight: bold;
            color: {Colors.TEXT_COLOR};
        """)
        self.transparency_value.setFixedWidth(40)
        transparency_layout.addWidget(self.transparency_value)
        
        main_layout.addWidget(transparency_frame)
        
        # Update controls state
        self.update_transparency_controls_state()
    
    def create_scroll_widget_section(self, main_layout):
        """Create scroll widget settings section."""
        # Enable checkbox
        scroll_enable_frame = QFrame()
        scroll_enable_layout = QHBoxLayout(scroll_enable_frame)
        scroll_enable_layout.setContentsMargins(0, 0, 0, 0)
        scroll_enable_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.scroll_check = QCheckBox("Enable scroll widget")
        self.scroll_check.setChecked(self.settings_manager.get_setting('scroll_enabled', True))
        self.scroll_check.setFont(QFont("Helvetica Neue", 11))
        self.scroll_check.setStyleSheet(self.get_checkbox_style())
        scroll_enable_layout.addWidget(self.scroll_check)
        
        main_layout.addWidget(scroll_enable_frame)
        
        # Scroll speed label
        scroll_speed_label = QLabel("Scroll Speed:")
        scroll_speed_label.setFont(QFont("Helvetica Neue", 11))
        scroll_speed_label.setStyleSheet(f"color: {Colors.TEXT_COLOR}; font-weight: bold;")
        main_layout.addWidget(scroll_speed_label)
        
        # Controls frame
        scroll_speed_frame = QFrame()
        scroll_speed_layout = QHBoxLayout(scroll_speed_frame)
        scroll_speed_layout.setContentsMargins(0, 0, 0, 0)
        scroll_speed_layout.setSpacing(5)
        
        # Minus button
        scroll_speed_minus_btn = self.create_adjustment_button("-")
        scroll_speed_minus_btn.enterEvent = lambda e: self.on_enter_minus_scroll_speed()
        scroll_speed_minus_btn.leaveEvent = lambda e: self.on_leave_minus_scroll_speed()
        scroll_speed_layout.addWidget(scroll_speed_minus_btn)
        
        # Slider (1-10, where 1 is slowest, 10 is fastest)
        self.scroll_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.scroll_speed_slider.setRange(1, 10)
        # Convert interval to speed (lower interval = faster speed)
        current_interval = self.settings_manager.get_setting('scroll_speed', 100)
        speed_value = 11 - (current_interval // 20)  # 200ms=1, 180ms=2, ..., 20ms=10
        self.scroll_speed_slider.setValue(max(1, min(10, speed_value)))
        scroll_speed_layout.addWidget(self.scroll_speed_slider)
        
        # Plus button
        scroll_speed_plus_btn = self.create_adjustment_button("+")
        scroll_speed_plus_btn.enterEvent = lambda e: self.on_enter_plus_scroll_speed()
        scroll_speed_plus_btn.leaveEvent = lambda e: self.on_leave_plus_scroll_speed()
        scroll_speed_layout.addWidget(scroll_speed_plus_btn)
        
        # Value label
        self.scroll_speed_value = QLabel(str(self.scroll_speed_slider.value()))
        self.scroll_speed_value.setStyleSheet(f"""
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 12pt;
            font-weight: bold;
            color: {Colors.TEXT_COLOR};
        """)
        self.scroll_speed_value.setFixedWidth(30)
        scroll_speed_layout.addWidget(self.scroll_speed_value)
        
        main_layout.addWidget(scroll_speed_frame)
        
        # Update controls state
        self.update_scroll_controls_state()
    
    def create_active_state_section(self, main_layout):
        """Create default active state section."""
        active_frame = QFrame()
        active_layout = QHBoxLayout(active_frame)
        active_layout.setContentsMargins(0, 0, 0, 0)
        active_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.active_check = QCheckBox("Start active on launch")
        self.active_check.setChecked(self.settings_manager.get_setting('default_active', False))
        self.active_check.setFont(QFont("Helvetica Neue", 11))
        self.active_check.setStyleSheet(self.get_checkbox_style())
        active_layout.addWidget(self.active_check)
        
        main_layout.addWidget(active_frame)
    
    def create_ok_button(self, main_layout):
        """Create OK button."""
        ok_button = QPushButton("OK")
        ok_button.setFixedSize(250, 35)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setFont(QFont("Helvetica Neue", 12, QFont.Weight.Bold))
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BLUE_ACCENT};
                color: {Colors.TEXT_COLOR};
                border: none;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: #0069c0;
            }}
        """)
        ok_button.clicked.connect(self.accept)
        
        main_layout.addWidget(ok_button, 0, Qt.AlignmentFlag.AlignCenter)
    
    def create_bottom_section(self, main_layout):
        """Create bottom section with version info."""
        bottom_frame = QFrame()
        bottom_layout = QVBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(0, 5, 0, 0)
        bottom_layout.setSpacing(5)
        
        # Separator
        bottom_separator = QFrame()
        bottom_separator.setFrameShape(QFrame.Shape.HLine)
        bottom_separator.setFrameShadow(QFrame.Shadow.Sunken)
        bottom_separator.setStyleSheet(f"background-color: {Colors.BORDER_COLOR};")
        bottom_layout.addWidget(bottom_separator)
        
        # Version info
        version_label = QLabel(f"Dwellpy v{__version__}")
        version_label.setStyleSheet("""
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 9pt;
            color: #999999;
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        bottom_layout.addWidget(version_label)
        
        main_layout.addWidget(bottom_frame)
    
    def create_adjustment_button(self, text):
        """Create a +/- adjustment button."""
        button = QPushButton(text)
        button.setFixedSize(20, 20)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.DARK_BUTTON_BG};
                color: {Colors.TEXT_COLOR};
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: 10px;
                font-weight: bold;
            }}
        """)
        return button
    
    def add_separator(self, layout):
        """Add a visual separator line."""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setMaximumHeight(1)
        separator.setStyleSheet(f"background-color: {Colors.BORDER_COLOR};")
        layout.addWidget(separator)
    
    def get_slider_style(self):
        """Get slider stylesheet."""
        return f"""
            QSlider::groove:horizontal {{
                background: {Colors.SLIDER_TRACK};
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {Colors.BLUE_ACCENT};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: {Colors.BLUE_ACCENT};
                height: 4px;
                border-radius: 2px;
            }}
        """
    
    def get_checkbox_style(self):
        """Get checkbox stylesheet."""
        return f"""
            QCheckBox {{
                color: {Colors.TEXT_COLOR};
                spacing: 10px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                background-color: {Colors.DARK_BG};
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {Colors.BLUE_ACCENT};
                border: 1px solid {Colors.BLUE_ACCENT};
            }}
        """
    
    def connect_signals(self):
        """Connect all widget signals."""
        self.move_limit_slider.valueChanged.connect(self.update_move_limit_value)
        self.time_slider.valueChanged.connect(self.update_time_value)
        self.transparency_slider.valueChanged.connect(self.update_transparency_value)
        self.transparency_check.stateChanged.connect(self.on_transparency_toggle)
        self.scroll_speed_slider.valueChanged.connect(self.update_scroll_speed_value)
        self.scroll_check.stateChanged.connect(self.on_scroll_toggle)
        self.active_check.stateChanged.connect(self.on_active_toggle)
    
    # Hover timer methods for move limit
    def on_enter_minus_move(self):
        self.move_minus_timer.start(500)

    def on_leave_minus_move(self):
        self.move_minus_timer.stop()
        self.move_minus_repeat.stop()

    def on_enter_plus_move(self):
        self.move_plus_timer.start(500)

    def on_leave_plus_move(self):
        self.move_plus_timer.stop()
        self.move_plus_repeat.stop()

    def start_minus_move_repeat(self):
        self.on_hover_minus_move_limit()
        self.move_minus_repeat.start(500)

    def start_plus_move_repeat(self):
        self.on_hover_plus_move_limit()
        self.move_plus_repeat.start(500)

    def on_hover_minus_move_limit(self):
        if self.move_limit_slider.value() > self.move_limit_slider.minimum():
            self.move_limit_slider.setValue(self.move_limit_slider.value() - 1)

    def on_hover_plus_move_limit(self):
        if self.move_limit_slider.value() < self.move_limit_slider.maximum():
            self.move_limit_slider.setValue(self.move_limit_slider.value() + 1)
    
    # Hover timer methods for dwell time
    def on_enter_minus_time(self):
        self.time_minus_timer.start(500)

    def on_leave_minus_time(self):
        self.time_minus_timer.stop()
        self.time_minus_repeat.stop()

    def on_enter_plus_time(self):
        self.time_plus_timer.start(500)

    def on_leave_plus_time(self):
        self.time_plus_timer.stop()
        self.time_plus_repeat.stop()

    def start_minus_time_repeat(self):
        self.on_hover_minus_dwell_time()
        self.time_minus_repeat.start(500)

    def start_plus_time_repeat(self):
        self.on_hover_plus_dwell_time()
        self.time_plus_repeat.start(500)

    def on_hover_minus_dwell_time(self):
        if self.time_slider.value() > self.time_slider.minimum():
            self.time_slider.setValue(self.time_slider.value() - 1)

    def on_hover_plus_dwell_time(self):
        if self.time_slider.value() < self.time_slider.maximum():
            self.time_slider.setValue(self.time_slider.value() + 1)
    
    # Hover timer methods for transparency
    def on_enter_minus_transparency(self):
        if self.transparency_check.isChecked():
            self.transparency_minus_timer.start(500)

    def on_leave_minus_transparency(self):
        self.transparency_minus_timer.stop()
        self.transparency_minus_repeat.stop()

    def on_enter_plus_transparency(self):
        if self.transparency_check.isChecked():
            self.transparency_plus_timer.start(500)

    def on_leave_plus_transparency(self):
        self.transparency_plus_timer.stop()
        self.transparency_plus_repeat.stop()

    def start_minus_transparency_repeat(self):
        self.on_hover_minus_transparency()
        self.transparency_minus_repeat.start(500)

    def start_plus_transparency_repeat(self):
        self.on_hover_plus_transparency()
        self.transparency_plus_repeat.start(500)

    def on_hover_minus_transparency(self):
        if self.transparency_slider.value() > self.transparency_slider.minimum():
            self.transparency_slider.setValue(self.transparency_slider.value() - 5)

    def on_hover_plus_transparency(self):
        if self.transparency_slider.value() < self.transparency_slider.maximum():
            self.transparency_slider.setValue(self.transparency_slider.value() + 5)
    
    # Hover timer methods for scroll speed
    def on_enter_minus_scroll_speed(self):
        if self.scroll_check.isChecked():
            self.scroll_speed_minus_timer.start(500)

    def on_leave_minus_scroll_speed(self):
        self.scroll_speed_minus_timer.stop()
        self.scroll_speed_minus_repeat.stop()

    def on_enter_plus_scroll_speed(self):
        if self.scroll_check.isChecked():
            self.scroll_speed_plus_timer.start(500)

    def on_leave_plus_scroll_speed(self):
        self.scroll_speed_plus_timer.stop()
        self.scroll_speed_plus_repeat.stop()

    def start_minus_scroll_speed_repeat(self):
        self.on_hover_minus_scroll_speed()
        self.scroll_speed_minus_repeat.start(500)

    def start_plus_scroll_speed_repeat(self):
        self.on_hover_plus_scroll_speed()
        self.scroll_speed_plus_repeat.start(500)

    def on_hover_minus_scroll_speed(self):
        if self.scroll_speed_slider.value() > self.scroll_speed_slider.minimum():
            self.scroll_speed_slider.setValue(self.scroll_speed_slider.value() - 1)

    def on_hover_plus_scroll_speed(self):
        if self.scroll_speed_slider.value() < self.scroll_speed_slider.maximum():
            self.scroll_speed_slider.setValue(self.scroll_speed_slider.value() + 1)
    
    # Value update methods
    def update_move_limit_value(self, value):
        """Update move limit value and apply setting."""
        self.move_limit_value.setText(str(value))
        self.settings_manager.update_move_limit(value)

    def update_time_value(self, value):
        """Update dwell time value and apply setting."""
        seconds = value / 10.0
        self.time_value.setText(format_time_display(seconds))
        self.settings_manager.update_dwell_time(seconds)

    def update_transparency_value(self, value):
        """Update transparency value and apply setting."""
        self.transparency_value.setText(format_percentage_display(value))
        self.settings_manager.update_transparency_level(value)

    def on_transparency_toggle(self, state):
        """Handle transparency checkbox toggle."""
        is_enabled = state == 2  # Qt.CheckState.Checked is 2
        self.settings_manager.update_transparency_enabled(is_enabled)
        self.update_transparency_controls_state()

    def update_scroll_speed_value(self, value):
        """Update scroll speed value and apply setting."""
        self.scroll_speed_value.setText(str(value))
        # Convert speed value to interval (1=200ms, 10=20ms)
        interval = 220 - (value * 20)
        self.settings_manager.update_scroll_speed(interval)

    def on_scroll_toggle(self, state):
        """Handle scroll widget checkbox toggle."""
        is_enabled = state == 2  # Qt.CheckState.Checked is 2
        self.settings_manager.update_scroll_enabled(is_enabled)
        self.update_scroll_controls_state()

    def on_active_toggle(self, state):
        """Handle active checkbox toggle."""
        is_active = state == 2  # Qt.CheckState.Checked is 2
        self.settings_manager.update_default_active(is_active)

    def update_transparency_controls_state(self):
        """Enable/disable transparency controls based on checkbox state."""
        enabled = self.transparency_check.isChecked()
        self.transparency_slider.setEnabled(enabled)
        
        if enabled:
            self.transparency_slider.setStyleSheet(self.get_slider_style())
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

    def update_scroll_controls_state(self):
        """Enable/disable scroll controls based on checkbox state."""
        enabled = self.scroll_check.isChecked()
        self.scroll_speed_slider.setEnabled(enabled)
        
        if enabled:
            self.scroll_speed_slider.setStyleSheet(self.get_slider_style())
        else:
            self.scroll_speed_slider.setStyleSheet(f"""
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

    def accept(self):
        """Handle dialog acceptance."""
        # Stop all timers
        timers_to_stop = [
            self.move_minus_timer, self.move_plus_timer, 
            self.time_minus_timer, self.time_plus_timer,
            self.transparency_minus_timer, self.transparency_plus_timer,
            self.scroll_speed_minus_timer, self.scroll_speed_plus_timer,
            self.move_minus_repeat, self.move_plus_repeat, 
            self.time_minus_repeat, self.time_plus_repeat,
            self.transparency_minus_repeat, self.transparency_plus_repeat,
            self.scroll_speed_minus_repeat, self.scroll_speed_plus_repeat
        ]
        
        for timer in timers_to_stop:
            if timer:
                timer.stop()
        
        # Save settings
        self.settings_manager.save_settings()
        
        # Close dialog
        super().accept()