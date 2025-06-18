"""Settings dialog for the Dwellpy application."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QSlider, QCheckBox, QFrame, QComboBox, QColorDialog, QTabWidget, QWidget, QRadioButton, QButtonGroup, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QIcon, QGuiApplication
import os

try:
    from ...config.constants import Colors, BORDER_RADIUS, Fonts, MENU_ITEM_SIZE_MIN, MENU_ITEM_SIZE_MAX
    from ...utils.helpers import center_window, format_time_display, format_percentage_display, get_asset_path
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

    def get_asset_path(asset_name):
        """Fallback get_asset_path function"""
        import sys
        import os
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        return os.path.join(base_path, 'assets', 'icons', asset_name)


class SettingsDialog(QDialog):
    """Settings dialog for Dwellpy configuration."""
    
    def __init__(self, settings_manager, button_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.button_manager = button_manager
        
        # For frameless window dragging
        self.drag_pos = None
        
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
        
        # Widget appearance delay timers
        self.widget_delay_minus_timer = QTimer()
        self.widget_delay_minus_timer.setSingleShot(True)
        self.widget_delay_minus_timer.timeout.connect(self.start_minus_widget_delay_repeat)
        
        self.widget_delay_plus_timer = QTimer()
        self.widget_delay_plus_timer.setSingleShot(True)
        self.widget_delay_plus_timer.timeout.connect(self.start_plus_widget_delay_repeat)
        
        self.widget_delay_minus_repeat = QTimer()
        self.widget_delay_minus_repeat.timeout.connect(self.on_hover_minus_widget_delay)
        
        self.widget_delay_plus_repeat = QTimer()
        self.widget_delay_plus_repeat.timeout.connect(self.on_hover_plus_widget_delay)
        
        # Widget unlock threshold timers
        self.unlock_threshold_minus_timer = QTimer()
        self.unlock_threshold_minus_timer.setSingleShot(True)
        self.unlock_threshold_minus_timer.timeout.connect(self.start_minus_unlock_threshold_repeat)
        
        self.unlock_threshold_plus_timer = QTimer()
        self.unlock_threshold_plus_timer.setSingleShot(True)
        self.unlock_threshold_plus_timer.timeout.connect(self.start_plus_unlock_threshold_repeat)
        
        self.unlock_threshold_minus_repeat = QTimer()
        self.unlock_threshold_minus_repeat.timeout.connect(self.on_hover_minus_unlock_threshold)
        
        self.unlock_threshold_plus_repeat = QTimer()
        self.unlock_threshold_plus_repeat.timeout.connect(self.on_hover_plus_unlock_threshold)
        
        # Menu item size timers
        self.menu_size_minus_timer = QTimer()
        self.menu_size_minus_timer.setSingleShot(True)
        self.menu_size_minus_timer.timeout.connect(self.start_minus_menu_size_repeat)
        
        self.menu_size_plus_timer = QTimer()
        self.menu_size_plus_timer.setSingleShot(True)
        self.menu_size_plus_timer.timeout.connect(self.start_plus_menu_size_repeat)
        
        self.menu_size_minus_repeat = QTimer()
        self.menu_size_minus_repeat.timeout.connect(self.on_hover_minus_menu_size)
        
        self.menu_size_plus_repeat = QTimer()
        self.menu_size_plus_repeat.timeout.connect(self.on_hover_plus_menu_size)
        
    def setup_ui(self):
        """Setup the dialog UI with left-side wide tabs for dwell-friendly navigation."""
        # Set window flags for frameless window
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint
        )
        
        # Make dialog non-modal
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
        font = QFont("Arial", 10)
        font.setBold(True)
        self.tab_widget.setFont(font)
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_dwell_movement_tab()
        self.create_visual_feedback_tab()
        self.create_scroll_widget_tab()
        self.create_menu_widget_tab()
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
            font-size: 18pt;
            font-weight: bold;
            color: {Colors.TEXT_COLOR};
        """)
        title_layout.addWidget(title_label)
        
        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(24, 24)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        font = QFont("Arial", 16)
        font.setBold(True)
        close_button.setFont(font)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_COLOR};
                border: none;
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

    def create_menu_widget_tab(self):
        """Create menu widget settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Menu Item Size Section
        self.create_menu_item_size_section(layout)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Menu")

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
        """Create move limit adjustment section."""        # Label
        move_label = QLabel("Move Limit (px):")
        move_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        layout.addWidget(move_label)
        
        # Controls frame
        move_frame = QFrame()
        move_layout = QHBoxLayout(move_frame)
        move_layout.setContentsMargins(0, 0, 0, 0)
        move_layout.setSpacing(5)
        
        # Minus button
        move_minus_btn = self.create_adjustment_button("◀")
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
        move_plus_btn = self.create_adjustment_button("▶")
        move_plus_btn.enterEvent = lambda e: self.on_enter_plus_move()
        move_plus_btn.leaveEvent = lambda e: self.on_leave_plus_move()
        move_layout.addWidget(move_plus_btn)
          # Value label
        self.move_limit_value = QLabel(str(self.settings_manager.get_setting('move_limit', 5)))
        self.move_limit_value.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
        """)
        self.move_limit_value.setFixedWidth(30)
        move_layout.addWidget(self.move_limit_value)
        
        layout.addWidget(move_frame)
    
    def create_dwell_time_section(self, layout):
        """Create dwell time adjustment section."""        # Label
        time_label = QLabel("Dwell Time (s):")
        time_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        layout.addWidget(time_label)
        
        # Controls frame
        time_frame = QFrame()
        time_layout = QHBoxLayout(time_frame)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(5)
        
        # Minus button
        time_minus_btn = self.create_adjustment_button("◀")
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
        time_plus_btn = self.create_adjustment_button("▶")
        time_plus_btn.enterEvent = lambda e: self.on_enter_plus_time()
        time_plus_btn.leaveEvent = lambda e: self.on_leave_plus_time()
        time_layout.addWidget(time_plus_btn)
          # Value label
        self.time_value = QLabel(format_time_display(self.settings_manager.get_setting('dwell_time', 1.0)))
        self.time_value.setStyleSheet(f"""
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
        self.transparency_check.setStyleSheet(self.get_checkbox_style())
        transparency_enable_layout.addWidget(self.transparency_check)
        
        layout.addWidget(transparency_enable_frame)
          # Transparency level label
        transparency_label = QLabel("Transparency (%):")
        transparency_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        layout.addWidget(transparency_label)
        
        # Controls frame
        transparency_frame = QFrame()
        transparency_layout = QHBoxLayout(transparency_frame)
        transparency_layout.setContentsMargins(0, 0, 0, 0)
        transparency_layout.setSpacing(5)
        
        # Minus button
        transparency_minus_btn = self.create_adjustment_button("◀")
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
        transparency_plus_btn = self.create_adjustment_button("▶")
        transparency_plus_btn.enterEvent = lambda e: self.on_enter_plus_transparency()
        transparency_plus_btn.leaveEvent = lambda e: self.on_leave_plus_transparency()
        transparency_layout.addWidget(transparency_plus_btn)
          # Value label
        self.transparency_value = QLabel(format_percentage_display(self.settings_manager.get_setting('transparency_level', 70)))
        self.transparency_value.setStyleSheet(f"""
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
        self.visible_clicks_check.setStyleSheet(self.get_checkbox_style())
        visible_clicks_layout.addWidget(self.visible_clicks_check)
        
        layout.addWidget(visible_clicks_frame)
    
    def create_click_colors_section(self, layout):
        """Create click colors customization section."""
        # Section title
        colors_label = QLabel("Click Colors:")
        colors_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
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
        self.scroll_check.setStyleSheet(self.get_checkbox_style())
        scroll_enable_layout.addWidget(self.scroll_check)
        
        layout.addWidget(scroll_enable_frame)
        
        # Scroll speed label
        scroll_speed_label = QLabel("Scroll Speed:")
        scroll_speed_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        layout.addWidget(scroll_speed_label)
        
        # Controls frame
        scroll_speed_frame = QFrame()
        scroll_speed_layout = QHBoxLayout(scroll_speed_frame)
        scroll_speed_layout.setContentsMargins(0, 0, 0, 0)
        scroll_speed_layout.setSpacing(5)
        
        # Minus button
        scroll_speed_minus_btn = self.create_adjustment_button("◀")
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
        scroll_speed_plus_btn = self.create_adjustment_button("▶")
        scroll_speed_plus_btn.enterEvent = lambda e: self.on_enter_plus_scroll_speed()
        scroll_speed_plus_btn.leaveEvent = lambda e: self.on_leave_plus_scroll_speed()
        scroll_speed_layout.addWidget(scroll_speed_plus_btn)
          # Value label
        self.scroll_speed_value = QLabel(str(self.scroll_speed_slider.value()))
        self.scroll_speed_value.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
        """)
        self.scroll_speed_value.setFixedWidth(30)
        scroll_speed_layout.addWidget(self.scroll_speed_value)
        
        layout.addWidget(scroll_speed_frame)
        
        # Widget Appearance Delay
        appearance_delay_label = QLabel("Widget Appearance Delay:")
        appearance_delay_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        layout.addWidget(appearance_delay_label)
        
        # Description for widget delay
        delay_desc = QLabel("Time before scroll widget appears")
        delay_desc.setFont(QFont("Arial", 9))
        delay_desc.setStyleSheet("color: #999999; margin-top: 8px;")
        delay_desc.setWordWrap(True)
        layout.addWidget(delay_desc)
        
        # Controls frame
        widget_delay_frame = QFrame()
        widget_delay_layout = QHBoxLayout(widget_delay_frame)
        widget_delay_layout.setContentsMargins(0, 0, 0, 0)
        widget_delay_layout.setSpacing(5)
        
        # Minus button
        widget_delay_minus_btn = self.create_adjustment_button("◀")
        widget_delay_minus_btn.enterEvent = lambda e: self.on_enter_minus_widget_delay()
        widget_delay_minus_btn.leaveEvent = lambda e: self.on_leave_minus_widget_delay()
        widget_delay_layout.addWidget(widget_delay_minus_btn)
        
        # Slider (1-10, representing 0.1s to 1.0s)
        self.widget_delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.widget_delay_slider.setRange(1, 10)
        # Convert current delay (0.1-1.0) to slider value (1-10)
        current_delay = self.settings_manager.get_setting('widget_appearance_delay', 0.2)
        slider_value = int(current_delay * 10)
        self.widget_delay_slider.setValue(max(1, min(10, slider_value)))
        self.widget_delay_slider.setStyleSheet(self.get_slider_style())
        widget_delay_layout.addWidget(self.widget_delay_slider)
        
        # Plus button
        widget_delay_plus_btn = self.create_adjustment_button("▶")
        widget_delay_plus_btn.enterEvent = lambda e: self.on_enter_plus_widget_delay()
        widget_delay_plus_btn.leaveEvent = lambda e: self.on_leave_plus_widget_delay()
        widget_delay_layout.addWidget(widget_delay_plus_btn)
          # Value label
        delay_seconds = self.widget_delay_slider.value() / 10.0
        self.widget_delay_value = QLabel(f"{delay_seconds:.1f}s")
        self.widget_delay_value.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
        """)
        self.widget_delay_value.setFixedWidth(40)
        widget_delay_layout.addWidget(self.widget_delay_value)
        
        layout.addWidget(widget_delay_frame)
        
        # Widget Unlock Threshold
        unlock_threshold_label = QLabel("Widget Unlock Threshold:")
        unlock_threshold_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        layout.addWidget(unlock_threshold_label)
        
        # Description
        unlock_desc = QLabel("Distance (in pixels) cursor must move from widget before it starts following again")
        unlock_desc.setFont(QFont("Arial", 9))
        unlock_desc.setStyleSheet(f"color: #999999; margin-bottom: 8px;")
        unlock_desc.setWordWrap(True)
        layout.addWidget(unlock_desc)
        
        # Controls frame
        unlock_threshold_frame = QFrame()
        unlock_threshold_layout = QHBoxLayout(unlock_threshold_frame)
        unlock_threshold_layout.setContentsMargins(0, 0, 0, 0)
        unlock_threshold_layout.setSpacing(5)
        
        # Minus button
        unlock_threshold_minus_btn = self.create_adjustment_button("◀")
        unlock_threshold_minus_btn.enterEvent = lambda e: self.on_enter_minus_unlock_threshold()
        unlock_threshold_minus_btn.leaveEvent = lambda e: self.on_leave_minus_unlock_threshold()
        unlock_threshold_layout.addWidget(unlock_threshold_minus_btn)
        
        # Slider (10-100 pixels)
        self.unlock_threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.unlock_threshold_slider.setRange(10, 100)
        self.unlock_threshold_slider.setValue(self.settings_manager.get_setting('widget_unlock_threshold', 30))
        self.unlock_threshold_slider.setStyleSheet(self.get_slider_style())
        unlock_threshold_layout.addWidget(self.unlock_threshold_slider)
        
        # Plus button
        unlock_threshold_plus_btn = self.create_adjustment_button("▶")
        unlock_threshold_plus_btn.enterEvent = lambda e: self.on_enter_plus_unlock_threshold()
        unlock_threshold_plus_btn.leaveEvent = lambda e: self.on_leave_plus_unlock_threshold()
        unlock_threshold_layout.addWidget(unlock_threshold_plus_btn)
          # Value label
        self.unlock_threshold_value = QLabel(f"{self.unlock_threshold_slider.value()}px")
        self.unlock_threshold_value.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
        """)
        self.unlock_threshold_value.setFixedWidth(40)
        unlock_threshold_layout.addWidget(self.unlock_threshold_value)
        
        layout.addWidget(unlock_threshold_frame)

    def create_menu_item_size_section(self, layout):
        """Create menu item size adjustment section."""
        # Header
        menu_size_header = self.create_section_header(
            "Menu Item Size",
            "Adjust the size of the circular menu items."
        )
        layout.addWidget(menu_size_header)

        # Controls frame
        size_frame = QFrame()
        size_layout = QHBoxLayout(size_frame)
        size_layout.setContentsMargins(0, 0, 0, 0)
        size_layout.setSpacing(10)

        # Minus button
        menu_size_minus_btn = self.create_adjustment_button("◀")
        menu_size_minus_btn.enterEvent = lambda e: self.on_enter_minus_menu_size()
        menu_size_minus_btn.leaveEvent = lambda e: self.on_leave_minus_menu_size()
        size_layout.addWidget(menu_size_minus_btn)

        # Slider for menu item size
        self.menu_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.menu_size_slider.setRange(MENU_ITEM_SIZE_MIN, MENU_ITEM_SIZE_MAX)
        self.menu_size_slider.setValue(self.settings_manager.get_setting('menu_item_size', 60))
        self.menu_size_slider.setStyleSheet(self.get_slider_style())
        size_layout.addWidget(self.menu_size_slider)

        # Plus button
        menu_size_plus_btn = self.create_adjustment_button("▶")
        menu_size_plus_btn.enterEvent = lambda e: self.on_enter_plus_menu_size()
        menu_size_plus_btn.leaveEvent = lambda e: self.on_leave_plus_menu_size()
        size_layout.addWidget(menu_size_plus_btn)

        # Value label
        self.menu_size_value = QLabel(str(self.settings_manager.get_setting('menu_item_size', 60)))
        self.menu_size_value.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
        """)
        self.menu_size_value.setFixedWidth(40)
        size_layout.addWidget(self.menu_size_value)
        
        layout.addWidget(size_frame)
    
    def create_active_state_section(self, layout):
        """Create default active state section."""
        # Active on launch
        active_frame = QFrame()
        active_layout = QHBoxLayout(active_frame)
        active_layout.setContentsMargins(0, 0, 0, 0)
        active_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.active_check = QCheckBox("Active on launch")
        self.active_check.setChecked(self.settings_manager.get_setting('active_on_launch', True))
        self.active_check.setStyleSheet(self.get_checkbox_style())
        active_layout.addWidget(self.active_check)
        
        layout.addWidget(active_frame)
        
        # Auto-start with system
        auto_start_frame = QFrame()
        auto_start_layout = QHBoxLayout(auto_start_frame)
        auto_start_layout.setContentsMargins(0, 0, 0, 0)
        auto_start_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.auto_start_check = QCheckBox("Automatically start with system")
        self.auto_start_check.setChecked(self.settings_manager.get_setting('auto_start_enabled', False))
        self.auto_start_check.setStyleSheet(self.get_checkbox_style())
        auto_start_layout.addWidget(self.auto_start_check)
        
        # Warning for non-Windows systems
        if os.name != 'nt':
            warning_label = QLabel(" (May require manual setup on macOS/Linux)")
            warning_label.setStyleSheet(f"color: #999999;")
            auto_start_layout.addWidget(warning_label)

        layout.addWidget(auto_start_frame)
    
    def create_ui_contraction_section(self, layout):
        """Create UI contraction settings section."""
        # Enable checkbox
        contract_ui_frame = QFrame()
        contract_ui_layout = QHBoxLayout(contract_ui_frame)
        contract_ui_layout.setContentsMargins(0, 0, 0, 0)
        contract_ui_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.contract_ui_check = QCheckBox("Contract UI when idle")
        self.contract_ui_check.setChecked(self.settings_manager.get_setting('contract_ui_enabled', True))
        self.contract_ui_check.setStyleSheet(self.get_checkbox_style())
        contract_ui_layout.addWidget(self.contract_ui_check)
        
        layout.addWidget(contract_ui_frame)
        
        # Expansion direction section
        expansion_direction_frame = QFrame()
        expansion_direction_layout = QHBoxLayout(expansion_direction_frame)
        expansion_direction_layout.setContentsMargins(20, 0, 0, 0) # Indent
        
        # Expansion direction
        expansion_direction_label = QLabel("Expansion Direction:")
        expansion_direction_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        expansion_direction_layout.addWidget(expansion_direction_label)

        # Radio button container
        radio_container = QFrame()
        radio_layout = QVBoxLayout(radio_container)
        radio_layout.setContentsMargins(0,0,0,0)
        self.expansion_button_group = QButtonGroup()
        
        # Auto radio button
        self.expansion_auto_radio = QRadioButton("Auto (detects available space)")
        self.expansion_auto_radio.setStyleSheet(self.get_radio_style())
        self.expansion_button_group.addButton(self.expansion_auto_radio, 0)
        radio_layout.addWidget(self.expansion_auto_radio)
        
        # Horizontal radio button
        self.expansion_horizontal_radio = QRadioButton("Horizontal (left-to-right)")
        self.expansion_horizontal_radio.setStyleSheet(self.get_radio_style())
        self.expansion_button_group.addButton(self.expansion_horizontal_radio, 1)
        radio_layout.addWidget(self.expansion_horizontal_radio)
        
        # Vertical radio button
        self.expansion_vertical_radio = QRadioButton("Vertical (top-to-bottom)")
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
        """Create a styled adjustment button (e.g., for increment/decrement)."""
        button = QPushButton(text)
        button.setFixedSize(30, 30)  # Larger for dwell clicking
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        font = QFont("Arial", 12)
        font.setBold(True)
        button.setFont(font)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.DARK_BUTTON_BG};
                color: {Colors.TEXT_COLOR};
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: 15px;
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
        label.setFont(QFont("Arial", 9))
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
        font = QFont("Arial", 13)
        font.setBold(True)
        ok_button.setFont(font)
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
        version_label.setStyleSheet(f"""
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
        self.auto_start_check.stateChanged.connect(self.on_auto_start_toggle)
        self.contract_ui_check.stateChanged.connect(self.on_contract_ui_toggle)
        self.expansion_button_group.buttonClicked.connect(self.on_expansion_direction_toggle)
        self.widget_delay_slider.valueChanged.connect(self.update_widget_delay_value)
        self.unlock_threshold_slider.valueChanged.connect(self.update_unlock_threshold_value)
        self.menu_size_slider.valueChanged.connect(self.update_menu_size_value)
    
    # Value update methods
    def update_move_limit_value(self, value):
        self.move_limit_value.setText(str(value))

    def update_time_value(self, value):
        seconds = value / 10.0
        self.time_value.setText(format_time_display(seconds))

    def update_transparency_value(self, value):
        self.transparency_value.setText(format_percentage_display(value))

    def on_transparency_toggle(self, state):
        is_enabled = state == 2  # Qt.CheckState.Checked is 2
        self.settings_manager.set_setting('transparency_enabled', is_enabled)
        
    def update_scroll_speed_value(self, value):
        self.scroll_speed_value.setText(str(value))
        interval = 220 - (value * 20)
        self.settings_manager.set_setting('scroll_speed', interval)

    def update_widget_delay_value(self, value):
        delay_seconds = value / 10.0
        self.widget_delay_value.setText(f"{delay_seconds:.1f}s")

    def update_unlock_threshold_value(self, value):
        self.unlock_threshold_value.setText(f"{value}px")

    def update_menu_size_value(self, value):
        self.menu_size_value.setText(str(value))

    def on_scroll_toggle(self, state):
        is_enabled = state == 2
        self.settings_manager.set_setting('scroll_enabled', is_enabled)

    def on_visible_clicks_toggle(self, state):
        is_enabled = state == 2
        self.settings_manager.set_setting('visible_clicks_enabled', is_enabled)

    def on_active_toggle(self, state):
        is_active = state == 2
        self.settings_manager.set_setting('active_on_launch', is_active)

    def on_contract_ui_toggle(self, state):
        is_enabled = state == 2
        self.settings_manager.set_setting('contract_ui_enabled', is_enabled)

    def on_expansion_direction_toggle(self, button):
        if button == self.expansion_auto_radio:
            direction = 'auto'
        elif button == self.expansion_horizontal_radio:
            direction = 'horizontal'
        else:
            direction = 'vertical'
        self.settings_manager.set_setting('expansion_direction', direction)
    
    def on_auto_start_toggle(self, state):
        is_enabled = state == 2
        success, error_message = self.settings_manager.update_auto_start_enabled(is_enabled)
        if not success:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Auto-start Configuration Error")
            msg_box.setText(error_message)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            self.auto_start_check.blockSignals(True)
            self.auto_start_check.setChecked(not is_enabled)
            self.auto_start_check.blockSignals(False)
            msg_box.exec()
    
    # Hover enter/leave methods for +/- buttons
    def on_enter_minus_move(self):
        self.move_minus_timer.start(300)
        
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
    
    def on_enter_minus_widget_delay(self):
        self.widget_delay_minus_timer.start(300)
        
    def on_leave_minus_widget_delay(self):
        self.widget_delay_minus_timer.stop()
        self.widget_delay_minus_repeat.stop()
        
    def on_enter_plus_widget_delay(self):
        self.widget_delay_plus_timer.start(300)
        
    def on_leave_plus_widget_delay(self):
        self.widget_delay_plus_timer.stop()
        self.widget_delay_plus_repeat.stop()
    
    def on_enter_minus_unlock_threshold(self):
        self.unlock_threshold_minus_timer.start(300)
    
    def on_leave_minus_unlock_threshold(self):
        self.unlock_threshold_minus_timer.stop()
        self.unlock_threshold_minus_repeat.stop()
    
    def on_enter_plus_unlock_threshold(self):
        self.unlock_threshold_plus_timer.start(300)
    
    def on_leave_plus_unlock_threshold(self):
        self.unlock_threshold_plus_timer.stop()
        self.unlock_threshold_plus_repeat.stop()
    
    def on_enter_minus_menu_size(self):
        self.menu_size_minus_timer.start(300)
    
    def on_leave_minus_menu_size(self):
        self.menu_size_minus_timer.stop()
        self.menu_size_minus_repeat.stop()
    
    def on_enter_plus_menu_size(self):
        self.menu_size_plus_timer.start(300)
    
    def on_leave_plus_menu_size(self):
        self.menu_size_plus_timer.stop()
        self.menu_size_plus_repeat.stop()
    
    # Timer start methods
    def start_minus_move_repeat(self):
        self.on_hover_minus_move_limit()
        self.move_minus_repeat.start(100)
        
    def start_plus_move_repeat(self):
        self.on_hover_plus_move_limit()
        self.move_plus_repeat.start(100)
        
    def start_minus_time_repeat(self):
        self.on_hover_minus_dwell_time()
        self.time_minus_repeat.start(100)
        
    def start_plus_time_repeat(self):
        self.on_hover_plus_dwell_time()
        self.time_plus_repeat.start(100)
        
    def start_minus_transparency_repeat(self):
        self.on_hover_minus_transparency()
        self.transparency_minus_repeat.start(100)
        
    def start_plus_transparency_repeat(self):
        self.on_hover_plus_transparency()
        self.transparency_plus_repeat.start(100)
        
    def start_minus_scroll_speed_repeat(self):
        self.on_hover_minus_scroll_speed()
        self.scroll_speed_minus_repeat.start(100)
        
    def start_plus_scroll_speed_repeat(self):
        self.on_hover_plus_scroll_speed()
        self.scroll_speed_plus_repeat.start(100)
    
    def start_minus_widget_delay_repeat(self):
        self.on_hover_minus_widget_delay()
        self.widget_delay_minus_repeat.start(100)
        
    def start_plus_widget_delay_repeat(self):
        self.on_hover_plus_widget_delay()
        self.widget_delay_plus_repeat.start(100)
    
    def start_minus_unlock_threshold_repeat(self):
        self.on_hover_minus_unlock_threshold()
        self.unlock_threshold_minus_repeat.start(100)
        
    def start_plus_unlock_threshold_repeat(self):
        self.on_hover_plus_unlock_threshold()
        self.unlock_threshold_plus_repeat.start(100)
    
    def start_minus_menu_size_repeat(self):
        self.on_hover_minus_menu_size()
        self.menu_size_minus_repeat.start(100)
    
    def start_plus_menu_size_repeat(self):
        self.on_hover_plus_menu_size()
        self.menu_size_plus_repeat.start(100)
    
    # Hover actions
    def on_hover_minus_move_limit(self):
        self.move_limit_slider.setValue(self.move_limit_slider.value() - 1)
        
    def on_hover_plus_move_limit(self):
        self.move_limit_slider.setValue(self.move_limit_slider.value() + 1)
        
    def on_hover_minus_dwell_time(self):
        self.time_slider.setValue(self.time_slider.value() - 1)
        
    def on_hover_plus_dwell_time(self):
        self.time_slider.setValue(self.time_slider.value() + 1)
        
    def on_hover_minus_transparency(self):
        self.transparency_slider.setValue(self.transparency_slider.value() - 1)
        
    def on_hover_plus_transparency(self):
        self.transparency_slider.setValue(self.transparency_slider.value() + 1)
        
    def on_hover_minus_scroll_speed(self):
        self.scroll_speed_slider.setValue(self.scroll_speed_slider.value() - 1)
        
    def on_hover_plus_scroll_speed(self):
        self.scroll_speed_slider.setValue(self.scroll_speed_slider.value() + 1)
    
    def on_hover_minus_widget_delay(self):
        self.widget_delay_slider.setValue(self.widget_delay_slider.value() - 1)
        
    def on_hover_plus_widget_delay(self):
        self.widget_delay_slider.setValue(self.widget_delay_slider.value() + 1)
    
    def on_hover_minus_unlock_threshold(self):
        self.unlock_threshold_slider.setValue(self.unlock_threshold_slider.value() - 1)
        
    def on_hover_plus_unlock_threshold(self):
        self.unlock_threshold_slider.setValue(self.unlock_threshold_slider.value() + 1)
    
    def on_hover_minus_menu_size(self):
        self.menu_size_slider.setValue(self.menu_size_slider.value() - 1)
        
    def on_hover_plus_menu_size(self):
        self.menu_size_slider.setValue(self.menu_size_slider.value() + 1)
    
    def accept(self):
        """Handle dialog acceptance."""
        # Stop all timers
        timers_to_stop = [
            self.move_minus_timer, self.move_plus_timer, self.time_minus_timer, self.time_plus_timer,
            self.transparency_minus_timer, self.transparency_plus_timer, self.scroll_speed_minus_timer,
            self.scroll_speed_plus_timer, self.widget_delay_minus_timer, self.widget_delay_plus_timer,
            self.unlock_threshold_minus_timer, self.unlock_threshold_plus_timer, self.menu_size_minus_timer,
            self.menu_size_plus_timer, self.move_minus_repeat, self.move_plus_repeat,
            self.time_minus_repeat, self.time_plus_repeat, self.transparency_minus_repeat,
            self.transparency_plus_repeat, self.scroll_speed_minus_repeat, self.scroll_speed_plus_repeat,
            self.widget_delay_minus_repeat, self.widget_delay_plus_repeat, self.unlock_threshold_minus_repeat,
            self.unlock_threshold_plus_repeat, self.menu_size_minus_repeat, self.menu_size_plus_repeat
        ]
        for timer in timers_to_stop:
            if timer and timer.isActive():
                timer.stop()
        
        # Save all settings at once
        settings = {
            'move_limit': self.move_limit_slider.value(),
            'dwell_time': self.time_slider.value() / 10.0,
            'transparency_enabled': self.transparency_check.isChecked(),
            'transparency_level': self.transparency_slider.value(),
            'scroll_enabled': self.scroll_check.isChecked(),
            'scroll_speed': 220 - (self.scroll_speed_slider.value() * 20),
            'widget_appearance_delay': self.widget_delay_slider.value() / 10.0,
            'widget_unlock_threshold': self.unlock_threshold_slider.value(),
            'menu_item_size': self.menu_size_slider.value(),
            'visible_clicks_enabled': self.visible_clicks_check.isChecked(),
            'active_on_launch': self.active_check.isChecked(),
            'contract_ui_enabled': self.contract_ui_check.isChecked(),
            'expansion_direction': self.expansion_button_group.checkedButton().text().split(' ')[0].lower()
        }
        for key, value in settings.items():
            self.settings_manager.set_setting(key, value)

        super().accept()

    def create_section_header(self, title, description):
        """Create a styled section header with title and description."""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(2)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 14pt;
            font-weight: bold;
            color: {Colors.BLUE_ACCENT};
            qproperty-alignment: 'AlignLeft';
        """)
        header_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 9))
        desc_label.setStyleSheet("color: #999999; margin-bottom: 8px;")
        desc_label.setWordWrap(True)
        header_layout.addWidget(desc_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"background-color: {Colors.BORDER_COLOR};")
        header_layout.addWidget(separator)
        
        return header_frame

    def showEvent(self, event):
        """Center the dialog when shown."""
        super().showEvent(event)
        center_window(self)

    def mouseDoubleClickEvent(self, event):
        """Center the window on double-click."""
        super().mouseDoubleClickEvent(event)
        center_window(self)

    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release for dragging."""
        self.drag_pos = None
        event.accept()