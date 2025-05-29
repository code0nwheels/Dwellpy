"""Settings dialog for the Dwellpy application."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QSlider, QCheckBox, QFrame, QComboBox, QColorDialog, QTabWidget, QWidget, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

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
        """Setup the dialog UI with left-side wide tabs for dwell-friendly navigation."""
        self.setFixedSize(550, 550)  # Much taller to accommodate all content
        
        # Set window flags for frameless window
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        
        # Make dialog non-modal
        self.setModal(False)
        
        # Apply dark theme with left-side tab styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.DARK_BG};
                color: {Colors.TEXT_COLOR};
                border: 1px solid {Colors.BORDER_COLOR};
            }}
            QTabWidget::pane {{
                border: 1px solid {Colors.BORDER_COLOR};
                background-color: {Colors.DARK_BG};
                margin-top: 0px;
            }}
            QTabBar::tab {{
                background-color: {Colors.DARK_BUTTON_BG};
                color: {Colors.TEXT_COLOR};
                padding: 8px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 100px;
                min-height: 20px;
                font-size: 10pt;
                font-weight: bold;
            }}
            QTabBar[tabPosition="2"]::tab {{
                writing-mode: horizontal-tb;
                text-orientation: mixed;
                padding: 8px 12px;
            }}
            QTabBar::tab:selected {{
                background-color: {Colors.BLUE_ACCENT};
                color: {Colors.TEXT_COLOR};
            }}
            QTabBar::tab:hover {{
                background-color: {Colors.BLUE_HOVER};
            }}
            QTabWidget::tab-bar {{
                alignment: center;
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(8)
        
        # Title area with close button
        title_frame = self.create_title_frame()
        main_layout.addWidget(title_frame)
        
        # Create tab widget with top tabs and shorter names
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)  # Top tabs
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_dwell_movement_tab()
        self.create_visual_feedback_tab()
        self.create_scroll_widget_tab()
        self.create_general_tab()
        
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
    
    def create_dwell_movement_tab(self):
        """Create dwell movement tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Movement Detection Section
        movement_header = self.create_section_header("Movement Detection", 
                                                   "How much your cursor can move while still counting as 'dwelling' in one spot")
        layout.addWidget(movement_header)
        
        self.create_move_limit_section(layout)
        
        # Timing Section  
        timing_header = self.create_section_header("Dwell Timing",
                                                 "How long you must hold your cursor still before a click happens")
        layout.addWidget(timing_header)
        
        self.create_dwell_time_section(layout)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Dwell")
    
    def create_visual_feedback_tab(self):
        """Create visual feedback tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Window Appearance Section
        appearance_header = self.create_section_header("Window Appearance",
                                                     "Control how the Dwellpy toolbar looks and behaves")
        layout.addWidget(appearance_header)
        
        self.create_transparency_section(layout)
        
        # Click Feedback Section
        feedback_header = self.create_section_header("Click Feedback",
                                                   "Visual indicators to show where and what type of clicks are performed")
        layout.addWidget(feedback_header)
        
        self.create_visible_clicks_section(layout)
        self.create_click_colors_section(layout)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Visual")
    
    def create_scroll_widget_tab(self):
        """Create scroll widget tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Scroll Widget Section
        scroll_header = self.create_section_header("Scroll Widget",
                                                 "A floating scroll widget that appears near your cursor for easy scrolling")
        layout.addWidget(scroll_header)
        
        self.create_scroll_widget_section(layout)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Scroll")
    
    def create_general_tab(self):
        """Create general tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Startup Behavior Section
        startup_header = self.create_section_header("Startup Behavior",
                                                  "How Dwellpy should behave when first launched")
        layout.addWidget(startup_header)
        
        self.create_active_state_section(layout)
        
        # UI Behavior Section
        ui_header = self.create_section_header("UI Behavior",
                                             "How the toolbar behaves when you're not using it")
        layout.addWidget(ui_header)
        
        self.create_ui_contraction_section(layout)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "General")
    
    def create_move_limit_section(self, layout):
        """Create move limit adjustment section."""
        # Label
        move_label = QLabel("Move Limit (px):")
        move_label.setFont(QFont("Helvetica Neue", 11))
        move_label.setStyleSheet(f"color: {Colors.TEXT_COLOR}; font-weight: bold;")
        layout.addWidget(move_label)
        
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
        
        layout.addWidget(move_frame)
    
    def create_dwell_time_section(self, layout):
        """Create dwell time adjustment section."""
        # Label
        time_label = QLabel("Dwell Time (s):")
        time_label.setFont(QFont("Helvetica Neue", 11))
        time_label.setStyleSheet(f"color: {Colors.TEXT_COLOR}; font-weight: bold;")
        layout.addWidget(time_label)
        
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
        
        layout.addWidget(time_frame)
    
    def create_transparency_section(self, layout):
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
        
        layout.addWidget(transparency_enable_frame)
        
        # Transparency level label
        transparency_label = QLabel("Transparency (%):")
        transparency_label.setFont(QFont("Helvetica Neue", 11))
        transparency_label.setStyleSheet(f"color: {Colors.TEXT_COLOR}; font-weight: bold;")
        layout.addWidget(transparency_label)
        
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
        self.transparency_slider.setStyleSheet(self.get_slider_style())
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
        
        layout.addWidget(transparency_frame)
    
    def create_visible_clicks_section(self, layout):
        """Create visible clicks section."""
        # Enable checkbox
        visible_clicks_frame = QFrame()
        visible_clicks_layout = QHBoxLayout(visible_clicks_frame)
        visible_clicks_layout.setContentsMargins(0, 0, 0, 0)
        visible_clicks_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.visible_clicks_check = QCheckBox("Enable visible clicks")
        self.visible_clicks_check.setChecked(self.settings_manager.get_setting('visible_clicks_enabled', False))
        self.visible_clicks_check.setFont(QFont("Helvetica Neue", 11))
        self.visible_clicks_check.setStyleSheet(self.get_checkbox_style())
        visible_clicks_layout.addWidget(self.visible_clicks_check)
        
        layout.addWidget(visible_clicks_frame)
    
    def create_click_colors_section(self, layout):
        """Create click colors customization section."""
        # Section title
        colors_label = QLabel("Click Colors:")
        colors_label.setFont(QFont("Helvetica Neue", 11))
        colors_label.setStyleSheet(f"color: {Colors.TEXT_COLOR}; font-weight: bold;")
        layout.addWidget(colors_label)
        
        # Default colors to use if not set in settings
        default_colors = {
            'left': "#00e676",
            'right': "#ff9800", 
            'double': "#e91e63",
            'drag_down': "#9c27b0",
            'drag_up': "#673ab7",
            'middle': "#00bcd4"
        }
        
        # Color names for display
        color_names = {
            'left': "Left Click",
            'right': "Right Click", 
            'double': "Double Click",
            'drag_down': "Drag Start",
            'drag_up': "Drag End",
            'middle': "Middle Click"
        }
        
        # Create color picker buttons in a single row for wider dialog
        color_row_frame = QFrame()
        color_row_layout = QHBoxLayout(color_row_frame)
        color_row_layout.setContentsMargins(0, 0, 0, 0)
        color_row_layout.setSpacing(8)
        
        for click_type in ['left', 'right', 'double', 'drag_down', 'drag_up', 'middle']:
            color_btn = self.create_color_button(click_type, color_names[click_type], default_colors[click_type])
            color_row_layout.addWidget(color_btn)
        
        layout.addWidget(color_row_frame)
    
    def create_scroll_widget_section(self, layout):
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
        
        layout.addWidget(scroll_enable_frame)
        
        # Scroll speed label
        scroll_speed_label = QLabel("Scroll Speed:")
        scroll_speed_label.setFont(QFont("Helvetica Neue", 11))
        scroll_speed_label.setStyleSheet(f"color: {Colors.TEXT_COLOR}; font-weight: bold;")
        layout.addWidget(scroll_speed_label)
        
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
        self.scroll_speed_slider.setStyleSheet(self.get_slider_style())
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
        
        layout.addWidget(scroll_speed_frame)
    
    def create_active_state_section(self, layout):
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
        
        layout.addWidget(active_frame)
    
    def create_ui_contraction_section(self, layout):
        """Create UI contraction section."""
        # Enable checkbox
        contraction_frame = QFrame()
        contraction_layout = QHBoxLayout(contraction_frame)
        contraction_layout.setContentsMargins(0, 0, 0, 0)
        contraction_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.contract_ui_check = QCheckBox("Contract UI when cursor is outside")
        self.contract_ui_check.setChecked(self.settings_manager.get_setting('contract_ui_enabled', False))
        self.contract_ui_check.setFont(QFont("Helvetica Neue", 11))
        self.contract_ui_check.setStyleSheet(self.get_checkbox_style())
        contraction_layout.addWidget(self.contract_ui_check)
        
        layout.addWidget(contraction_frame)
        
        # Expansion direction section with radio buttons
        expansion_direction_frame = QFrame()
        expansion_direction_layout = QVBoxLayout(expansion_direction_frame)
        expansion_direction_layout.setContentsMargins(0, 0, 0, 0)
        expansion_direction_layout.setSpacing(8)
        
        # Label
        expansion_label = QLabel("Expansion direction:")
        expansion_label.setFont(QFont("Helvetica Neue", 11))
        expansion_label.setStyleSheet(f"color: {Colors.TEXT_COLOR}; font-weight: bold;")
        expansion_direction_layout.addWidget(expansion_label)
        
        # Create button group for radio buttons
        self.expansion_button_group = QButtonGroup()
        
        # Radio buttons container
        radio_container = QFrame()
        radio_layout = QVBoxLayout(radio_container)
        radio_layout.setContentsMargins(20, 0, 0, 0)
        radio_layout.setSpacing(4)
        
        # Auto radio button
        self.expansion_auto_radio = QRadioButton("Auto (recommended)")
        self.expansion_auto_radio.setFont(QFont("Helvetica Neue", 10))
        self.expansion_auto_radio.setStyleSheet(self.get_radio_style())
        self.expansion_button_group.addButton(self.expansion_auto_radio, 0)
        radio_layout.addWidget(self.expansion_auto_radio)
        
        # Horizontal radio button
        self.expansion_horizontal_radio = QRadioButton("Horizontal (left-to-right)")
        self.expansion_horizontal_radio.setFont(QFont("Helvetica Neue", 10))
        self.expansion_horizontal_radio.setStyleSheet(self.get_radio_style())
        self.expansion_button_group.addButton(self.expansion_horizontal_radio, 1)
        radio_layout.addWidget(self.expansion_horizontal_radio)
        
        # Vertical radio button
        self.expansion_vertical_radio = QRadioButton("Vertical (top-to-bottom)")
        self.expansion_vertical_radio.setFont(QFont("Helvetica Neue", 10))
        self.expansion_vertical_radio.setStyleSheet(self.get_radio_style())
        self.expansion_button_group.addButton(self.expansion_vertical_radio, 2)
        radio_layout.addWidget(self.expansion_vertical_radio)
        
        expansion_direction_layout.addWidget(radio_container)
        
        # Set current selection based on settings
        current_direction = self.settings_manager.get_setting('expansion_direction', 'auto')
        if current_direction == 'auto':
            self.expansion_auto_radio.setChecked(True)
        elif current_direction == 'horizontal':
            self.expansion_horizontal_radio.setChecked(True)
        elif current_direction == 'vertical':
            self.expansion_vertical_radio.setChecked(True)
        
        layout.addWidget(expansion_direction_frame)
    
    def create_adjustment_button(self, text):
        """Create a +/- adjustment button."""
        button = QPushButton(text)
        button.setFixedSize(30, 30)  # Larger for dwell clicking
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.DARK_BUTTON_BG};
                color: {Colors.TEXT_COLOR};
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: 15px;
                font-weight: bold;
                font-size: 14pt;
            }}
            QPushButton:hover {{
                background-color: {Colors.BLUE_ACCENT};
                border: 1px solid {Colors.BLUE_ACCENT};
                color: {Colors.TEXT_COLOR};
            }}
        """)
        return button
    
    def create_color_button(self, click_type, display_name, default_color):
        """Create a color picker button for a specific click type."""
        # Get current color from settings or use default
        current_color = self.settings_manager.get_setting(f'click_color_{click_type}', default_color)
        
        # Create button frame
        btn_frame = QFrame()
        btn_layout = QVBoxLayout(btn_frame)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(2)
        
        # Label
        label = QLabel(display_name)
        label.setFont(QFont("Helvetica Neue", 9))
        label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(label)
        
        # Color button
        color_btn = QPushButton()
        color_btn.setFixedSize(70, 22)
        color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        color_btn.setProperty('click_type', click_type)  # Store click type for reference
        
        # Style the button with current color
        self.update_color_button_style(color_btn, current_color)
        
        # Connect click event
        color_btn.clicked.connect(lambda: self.open_color_picker(click_type, color_btn))
        
        btn_layout.addWidget(color_btn)
        
        return btn_frame
    
    def update_color_button_style(self, button, color_hex):
        """Update a color button's style to show the selected color."""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_hex};
                border: 2px solid {Colors.BORDER_COLOR};
                border-radius: 3px;
                color: {'#000000' if self.is_light_color(color_hex) else '#ffffff'};
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 8pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border: 2px solid {Colors.TEXT_COLOR};
            }}
        """)
        button.setText(color_hex.upper())
    
    def is_light_color(self, color_hex):
        """Check if a color is light (for text contrast)."""
        try:
            # Convert hex to RGB
            color_hex = color_hex.lstrip('#')
            r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            # Calculate luminance
            luminance = (0.299 * r + 0.587 * g + 0.114 * b)
            return luminance > 128
        except:
            return False
    
    def open_color_picker(self, click_type, button):
        """Open color picker dialog for a specific click type."""
        # Get current color
        current_color_hex = self.settings_manager.get_setting(f'click_color_{click_type}', '#ffffff')
        current_color = QColor(current_color_hex)
        
        # Open color dialog
        color = QColorDialog.getColor(current_color, self, f"Choose {click_type.replace('_', ' ').title()} Color")
        
        if color.isValid():
            color_hex = color.name()
            # Update settings
            self.settings_manager.set_setting(f'click_color_{click_type}', color_hex)
            # Update button appearance
            self.update_color_button_style(button, color_hex)
    
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
    
    def get_radio_style(self):
        """Get radio button stylesheet."""
        return f"""
            QRadioButton {{
                color: {Colors.TEXT_COLOR};
                spacing: 10px;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                background-color: {Colors.DARK_BG};
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: 8px;
            }}
            QRadioButton::indicator:checked {{
                background-color: {Colors.BLUE_ACCENT};
                border: 1px solid {Colors.BLUE_ACCENT};
            }}
        """
    
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
    
    def connect_signals(self):
        """Connect all widget signals."""
        self.move_limit_slider.valueChanged.connect(self.update_move_limit_value)
        self.time_slider.valueChanged.connect(self.update_time_value)
        self.transparency_slider.valueChanged.connect(self.update_transparency_value)
        self.transparency_check.stateChanged.connect(self.on_transparency_toggle)
        self.scroll_speed_slider.valueChanged.connect(self.update_scroll_speed_value)
        self.scroll_check.stateChanged.connect(self.on_scroll_toggle)
        self.visible_clicks_check.stateChanged.connect(self.on_visible_clicks_toggle)
        self.active_check.stateChanged.connect(self.on_active_toggle)
        self.contract_ui_check.stateChanged.connect(self.on_contract_ui_toggle)
        self.expansion_button_group.buttonClicked.connect(self.on_expansion_direction_toggle)
    
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

    def on_visible_clicks_toggle(self, state):
        """Handle visible clicks checkbox toggle."""
        is_enabled = state == 2  # Qt.CheckState.Checked is 2
        self.settings_manager.update_visible_clicks_enabled(is_enabled)

    def on_active_toggle(self, state):
        """Handle active checkbox toggle."""
        is_active = state == 2  # Qt.CheckState.Checked is 2
        self.settings_manager.update_default_active(is_active)

    def on_contract_ui_toggle(self, state):
        """Handle contract UI checkbox toggle."""
        is_enabled = state == 2  # Qt.CheckState.Checked is 2
        self.settings_manager.update_contract_ui_enabled(is_enabled)

    def on_expansion_direction_toggle(self, button):
        """Handle expansion direction radio button toggle."""
        # Map button text to setting value
        if button == self.expansion_auto_radio:
            direction = 'auto'
        elif button == self.expansion_horizontal_radio:
            direction = 'horizontal'
        elif button == self.expansion_vertical_radio:
            direction = 'vertical'
        else:
            direction = 'auto'  # fallback
        
        # Update settings
        self.settings_manager.update_expansion_direction(direction)
    
    # Hover enter/leave methods for +/- buttons
    def on_enter_minus_move(self):
        self.move_minus_timer.start(300)  # 300ms initial delay
        
    def on_leave_minus_move(self):
        self.move_minus_timer.stop()
        self.move_minus_repeat.stop()
        
    def on_enter_plus_move(self):
        self.move_plus_timer.start(300)
        
    def on_leave_plus_move(self):
        self.move_plus_timer.stop()
        self.move_plus_repeat.stop()
        
    def on_enter_minus_time(self):
        self.time_minus_timer.start(300)
        
    def on_leave_minus_time(self):
        self.time_minus_timer.stop()
        self.time_minus_repeat.stop()
        
    def on_enter_plus_time(self):
        self.time_plus_timer.start(300)
        
    def on_leave_plus_time(self):
        self.time_plus_timer.stop()
        self.time_plus_repeat.stop()
        
    def on_enter_minus_transparency(self):
        self.transparency_minus_timer.start(300)
        
    def on_leave_minus_transparency(self):
        self.transparency_minus_timer.stop()
        self.transparency_minus_repeat.stop()
        
    def on_enter_plus_transparency(self):
        self.transparency_plus_timer.start(300)
        
    def on_leave_plus_transparency(self):
        self.transparency_plus_timer.stop()
        self.transparency_plus_repeat.stop()
        
    def on_enter_minus_scroll_speed(self):
        self.scroll_speed_minus_timer.start(300)
        
    def on_leave_minus_scroll_speed(self):
        self.scroll_speed_minus_timer.stop()
        self.scroll_speed_minus_repeat.stop()
        
    def on_enter_plus_scroll_speed(self):
        self.scroll_speed_plus_timer.start(300)
        
    def on_leave_plus_scroll_speed(self):
        self.scroll_speed_plus_timer.stop()
        self.scroll_speed_plus_repeat.stop()
    
    # Timer start methods that begin the repeat action
    def start_minus_move_repeat(self):
        self.on_hover_minus_move_limit()  # First action
        self.move_minus_repeat.start(500)  # Then repeat every 500ms
        
    def start_plus_move_repeat(self):
        self.on_hover_plus_move_limit()
        self.move_plus_repeat.start(500)
        
    def start_minus_time_repeat(self):
        self.on_hover_minus_dwell_time()
        self.time_minus_repeat.start(500)
        
    def start_plus_time_repeat(self):
        self.on_hover_plus_dwell_time()
        self.time_plus_repeat.start(500)
        
    def start_minus_transparency_repeat(self):
        self.on_hover_minus_transparency()
        self.transparency_minus_repeat.start(500)
        
    def start_plus_transparency_repeat(self):
        self.on_hover_plus_transparency()
        self.transparency_plus_repeat.start(500)
        
    def start_minus_scroll_speed_repeat(self):
        self.on_hover_minus_scroll_speed()
        self.scroll_speed_minus_repeat.start(500)
        
    def start_plus_scroll_speed_repeat(self):
        self.on_hover_plus_scroll_speed()
        self.scroll_speed_plus_repeat.start(500)
    
    # The actual value adjustment methods
    def on_hover_minus_move_limit(self):
        current = self.move_limit_slider.value()
        if current > self.move_limit_slider.minimum():
            self.move_limit_slider.setValue(current - 1)
        
    def on_hover_plus_move_limit(self):
        current = self.move_limit_slider.value()
        if current < self.move_limit_slider.maximum():
            self.move_limit_slider.setValue(current + 1)
        
    def on_hover_minus_dwell_time(self):
        current = self.time_slider.value()
        if current > self.time_slider.minimum():
            self.time_slider.setValue(current - 1)
        
    def on_hover_plus_dwell_time(self):
        current = self.time_slider.value()
        if current < self.time_slider.maximum():
            self.time_slider.setValue(current + 1)
        
    def on_hover_minus_transparency(self):
        current = self.transparency_slider.value()
        if current > self.transparency_slider.minimum():
            self.transparency_slider.setValue(current - 5)  # Move by 5% steps
        
    def on_hover_plus_transparency(self):
        current = self.transparency_slider.value()
        if current < self.transparency_slider.maximum():
            self.transparency_slider.setValue(current + 5)
        
    def on_hover_minus_scroll_speed(self):
        current = self.scroll_speed_slider.value()
        if current > self.scroll_speed_slider.minimum():
            self.scroll_speed_slider.setValue(current - 1)
        
    def on_hover_plus_scroll_speed(self):
        current = self.scroll_speed_slider.value()
        if current < self.scroll_speed_slider.maximum():
            self.scroll_speed_slider.setValue(current + 1)
    
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

    def create_section_header(self, title, description):
        """Create a section header with title and description."""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 10, 0, 10)
        header_layout.setSpacing(5)
        
        # Title label
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 12pt;
            font-weight: bold;
            color: {Colors.BLUE_ACCENT};
            margin-bottom: 3px;
        """)
        header_layout.addWidget(title_label)
        
        # Description label
        description_label = QLabel(description)
        description_label.setStyleSheet(f"""
            color: #aaaaaa; 
            font-size: 9pt;
            margin-bottom: 8px;
        """)
        description_label.setWordWrap(True)
        header_layout.addWidget(description_label)
        
        # Add subtle separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {Colors.BORDER_COLOR}; max-height: 1px; margin: 5px 0px;")
        header_layout.addWidget(separator)
        
        return header_frame