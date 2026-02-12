"""Refactored settings dialog for the Dwellpy application."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QTabWidget, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
import os

try:
    from ...config.constants import Colors, BORDER_RADIUS, Fonts
    from ...utils.helpers import center_window, get_asset_path
    from ... import __version__
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
    
    def get_asset_path(asset_name):
        """Fallback get_asset_path function"""
        import sys
        import os
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        return os.path.join(base_path, 'assets', 'icons', asset_name)

# Import modularized components
from dwellpy.ui.dialogs.settings.tabs.dwell_movement_tab import DwellMovementTab
from dwellpy.ui.dialogs.settings.tabs.visual_feedback_tab import VisualFeedbackTab
from dwellpy.ui.dialogs.settings.tabs.scroll_widget_tab import ScrollWidgetTab
from dwellpy.ui.dialogs.settings.tabs.menu_widget_tab import MenuWidgetTab
from dwellpy.ui.dialogs.settings.tabs.general_tab import GeneralTab
from dwellpy.ui.dialogs.settings.components.event_handlers import SettingsEventHandlers


class SettingsDialog(QDialog):
    """Refactored settings dialog for Dwellpy configuration."""
    
    def __init__(self, settings_manager, button_manager, parent=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        
        # Store references
        self.settings_manager = settings_manager
        self.button_manager = button_manager
        
        # Initialize drag position
        self.drag_pos = None
        
        # Initialize event handlers FIRST
        self.event_handlers = SettingsEventHandlers(self)
        
        # Initialize tab components AFTER event handlers
        self.dwell_tab = DwellMovementTab(self)
        self.visual_tab = VisualFeedbackTab(self)
        self.scroll_tab = ScrollWidgetTab(self)
        self.menu_tab = MenuWidgetTab(self)
        self.general_tab = GeneralTab(self)
        
        # Setup UI
        self.setup_ui()
        
        # Connect signals
        self.connect_signals()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        # Set window properties
        self.setWindowTitle("Dwellpy Settings")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Try to set window icon
        try:
            icon_path = get_asset_path("Dwellpy.ico")
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
                border-radius: {BORDER_RADIUS}px;
            }}
            QTabWidget::pane {{
                border: 1px solid {Colors.BORDER_COLOR};
                background-color: {Colors.DARK_BG};
                margin-top: 0px;
                border-radius: 0px 0px {BORDER_RADIUS}px {BORDER_RADIUS}px;
            }}
            QTabBar::tab {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 {Colors.DARK_BUTTON_BG}, stop:1 #252525);
                color: {Colors.TEXT_COLOR};
                padding: 12px 20px;  /* Increased from 8px 16px */
                margin-right: 2px;  /* Increased from 1px */
                border-top-left-radius: {BORDER_RADIUS}px;
                border-top-right-radius: {BORDER_RADIUS}px;
                border: 1px solid {Colors.BORDER_COLOR};
                border-bottom: none;
                font-family: {Fonts.PRIMARY_FAMILY};
                font-size: 11px;  /* Increased from 10px */
                font-weight: bold;
                min-width: 80px;  /* Increased from 70px */
            }}
            QTabBar::tab:selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 {Colors.BLUE_ACCENT}, stop:1 {Colors.BLUE_HOVER});
                border-color: {Colors.BLUE_ACCENT};
            }}
            QTabBar::tab:hover:!selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 {Colors.BLUE_HOVER}, stop:1 {Colors.BLUE_ACCENT});
                border-color: {Colors.BLUE_HOVER};
            }}
            QTabBar::tab:disabled {{
                background-color: {Colors.DARK_BG};
                color: #666666;
            }}
            QTabBar::tab:focus {{
                outline: 2px solid {Colors.BLUE_ACCENT};
                outline-offset: 2px;
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Tab widget (now at the top since no title bar)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMouseTracking(True)  # Enable mouse tracking for dragging
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs using modularized components
        self.create_tabs()
        
        # Add tooltips to tabs for better user experience
        self.tab_widget.setTabToolTip(0, "Core dwell clicking settings, startup behavior, and UI behavior")
        self.tab_widget.setTabToolTip(1, "Visual appearance and feedback settings")
        self.tab_widget.setTabToolTip(2, "Widget configuration - scroll and menu widgets")
        
        # Bottom section with OK button
        self.create_bottom_section(main_layout)
        
        # Set dialog size and position
        self.resize(700, 500)  # Reduced from 750x550 to minimize blank space
        center_window(self)
        
        # Set focus policy for better keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.tab_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Set accessibility properties
        self.setAccessibleName("Dwellpy Settings Dialog")
        self.setAccessibleDescription("Configure Dwellpy settings including dwell timing, visual feedback, and widget behavior")
        
        # Set tab order for better keyboard navigation
        self.setTabOrder(self.tab_widget, self.findChild(QPushButton, ""))  # OK button)
        
        # Install event filters on child widgets to enable dragging from anywhere
        self.install_drag_event_filters()
    
    def install_drag_event_filters(self):
        """Install event filters on child widgets to enable dragging from anywhere."""
        # Install event filter on tab widget
        self.tab_widget.installEventFilter(self)
        
        # Install event filter on bottom section
        bottom_widget = self.findChild(QFrame)
        if bottom_widget:
            bottom_widget.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Event filter to handle mouse events for dragging from child widgets."""
        if event.type() == event.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.drag_pos = event.globalPosition().toPoint()
                return True
        elif event.type() == event.Type.MouseMove:
            if event.buttons() & Qt.MouseButton.LeftButton and self.drag_pos:
                new_pos = event.globalPosition().toPoint() - self.drag_pos
                self.move(self.pos() + new_pos)
                self.drag_pos = event.globalPosition().toPoint()
                return True
        elif event.type() == event.Type.MouseButtonRelease:
            if event.button() == Qt.MouseButton.LeftButton:
                self.drag_pos = None
                return True
        return super().eventFilter(obj, event)
    
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging."""
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_pos:
            new_pos = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.pos() + new_pos)
            self.drag_pos = event.globalPosition().toPoint()
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = None
            event.accept()
        else:
            super().mouseReleaseEvent(event)
    
    def create_widgets_tab(self):
        """Create a combined widgets tab with scroll and menu settings."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QHBoxLayout, QSlider, QCheckBox
        from PyQt6.QtCore import Qt
        from dwellpy.ui.dialogs.settings.components.ui_components import (
            create_section_header, create_adjustment_button, get_slider_style, get_checkbox_style, get_small_label_style
        )
        from dwellpy.config.constants import Colors
        
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(12)
        
        # Scroll Widget Section
        scroll_header = create_section_header("Scroll Widget",
                                             "A floating scroll widget that appears near your cursor for easy scrolling")
        layout.addWidget(scroll_header)
        
        # Scroll Widget Enable
        scroll_enable_frame = QFrame()
        scroll_enable_layout = QHBoxLayout(scroll_enable_frame)
        scroll_enable_layout.setContentsMargins(0, 0, 0, 0)
        scroll_enable_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.scroll_check = QCheckBox("Enable scroll widget")
        self.scroll_check.setChecked(self.settings_manager.get_setting('scroll_enabled', True))
        self.scroll_check.setStyleSheet(get_checkbox_style())
        self.scroll_check.setToolTip("Show a floating scroll widget when you dwell")
        scroll_enable_layout.addWidget(self.scroll_check)
        layout.addWidget(scroll_enable_frame)
        
        # Scroll Speed Control (Label above, slider below)
        scroll_speed_frame = QFrame()
        scroll_speed_layout = QVBoxLayout(scroll_speed_frame)
        scroll_speed_layout.setContentsMargins(0, 0, 0, 0)
        scroll_speed_layout.setSpacing(4)
        
        # Label on top
        scroll_speed_label = QLabel("Scroll Speed:")
        scroll_speed_label.setStyleSheet(get_small_label_style())
        scroll_speed_layout.addWidget(scroll_speed_label)
        
        # Controls below in horizontal layout
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        
        # Minus button
        scroll_speed_minus_btn = create_adjustment_button("◀")
        scroll_speed_minus_btn.setToolTip("Decrease scroll speed")
        scroll_speed_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_scroll_speed()
        scroll_speed_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_scroll_speed()
        controls_layout.addWidget(scroll_speed_minus_btn)
        
        # Slider
        self.scroll_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.scroll_speed_slider.setRange(1, 10)
        current_interval = self.settings_manager.get_setting('scroll_speed', 100)
        speed_value = 11 - (current_interval // 20)
        self.scroll_speed_slider.setValue(max(1, min(10, speed_value)))
        self.scroll_speed_slider.setStyleSheet(get_slider_style())
        controls_layout.addWidget(self.scroll_speed_slider)
        
        # Plus button
        scroll_speed_plus_btn = create_adjustment_button("▶")
        scroll_speed_plus_btn.setToolTip("Increase scroll speed")
        scroll_speed_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_scroll_speed()
        scroll_speed_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_scroll_speed()
        controls_layout.addWidget(scroll_speed_plus_btn)
        
        # Value label
        self.scroll_speed_label = QLabel(str(self.scroll_speed_slider.value()))
        self.scroll_speed_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
            font-weight: bold;
            min-width: 25px;
            background: rgba(0, 120, 215, 0.1);
            border: 1px solid rgba(0, 120, 215, 0.3);
            border-radius: 3px;
            padding: 2px 4px;
        """)
        self.scroll_speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.addWidget(self.scroll_speed_label)
        
        scroll_speed_layout.addLayout(controls_layout)
        layout.addWidget(scroll_speed_frame)
        
        # Widget Appearance & Behavior Section (shared between both widgets)
        appearance_header = create_section_header("Widget Appearance & Behavior",
                                                "Control when and how widgets appear (applies to both scroll and menu widgets)")
        layout.addWidget(appearance_header)
        
        # Widget Appearance Delay Control (Label above, slider below)
        widget_delay_frame = QFrame()
        widget_delay_layout = QVBoxLayout(widget_delay_frame)
        widget_delay_layout.setContentsMargins(0, 0, 0, 0)
        widget_delay_layout.setSpacing(4)
        
        # Label on top
        widget_delay_label = QLabel("Widget Appearance Delay:")
        widget_delay_label.setStyleSheet(get_small_label_style())
        widget_delay_layout.addWidget(widget_delay_label)
        
        # Controls below in horizontal layout
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        
        # Minus button
        widget_delay_minus_btn = create_adjustment_button("◀")
        widget_delay_minus_btn.setToolTip("Decrease appearance delay")
        widget_delay_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_widget_delay()
        widget_delay_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_widget_delay()
        controls_layout.addWidget(widget_delay_minus_btn)
        
        # Slider
        self.widget_delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.widget_delay_slider.setRange(1, 10)
        current_delay = self.settings_manager.get_setting('widget_appearance_delay', 0.2)
        slider_value = int(current_delay * 10)
        self.widget_delay_slider.setValue(max(1, min(10, slider_value)))
        self.widget_delay_slider.setStyleSheet(get_slider_style())
        controls_layout.addWidget(self.widget_delay_slider)
        
        # Plus button
        widget_delay_plus_btn = create_adjustment_button("▶")
        widget_delay_plus_btn.setToolTip("Increase appearance delay")
        widget_delay_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_widget_delay()
        widget_delay_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_widget_delay()
        controls_layout.addWidget(widget_delay_plus_btn)
        
        # Value label - Fix: divide by 10 to get correct seconds
        delay_seconds = self.widget_delay_slider.value() / 10.0
        self.widget_delay_label = QLabel(f"{delay_seconds:.1f}s")
        self.widget_delay_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
            font-weight: bold;
            min-width: 35px;
            background: rgba(0, 120, 215, 0.1);
            border: 1px solid rgba(0, 120, 215, 0.3);
            border-radius: 3px;
            padding: 2px 4px;
        """)
        self.widget_delay_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.addWidget(self.widget_delay_label)
        
        widget_delay_layout.addLayout(controls_layout)
        layout.addWidget(widget_delay_frame)
        
        # Widget Unlock Threshold Control (Label above, slider below)
        unlock_threshold_frame = QFrame()
        unlock_threshold_layout = QVBoxLayout(unlock_threshold_frame)
        unlock_threshold_layout.setContentsMargins(0, 0, 0, 0)
        unlock_threshold_layout.setSpacing(4)
        
        # Label on top
        unlock_threshold_label = QLabel("Widget Unlock Threshold:")
        unlock_threshold_label.setStyleSheet(get_small_label_style())
        unlock_threshold_layout.addWidget(unlock_threshold_label)
        
        # Controls below in horizontal layout
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        
        # Minus button
        unlock_threshold_minus_btn = create_adjustment_button("◀")
        unlock_threshold_minus_btn.setToolTip("Decrease unlock threshold")
        unlock_threshold_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_unlock_threshold()
        unlock_threshold_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_unlock_threshold()
        controls_layout.addWidget(unlock_threshold_minus_btn)
        
        # Slider
        self.unlock_threshold_slider = QSlider(Qt.Orientation.Horizontal)
        try:
            from dwellpy.config.constants import WIDGET_UNLOCK_THRESHOLD_MIN, WIDGET_UNLOCK_THRESHOLD_MAX, WIDGET_UNLOCK_THRESHOLD_DEFAULT
            self.unlock_threshold_slider.setRange(WIDGET_UNLOCK_THRESHOLD_MIN, WIDGET_UNLOCK_THRESHOLD_MAX)
            default_value = WIDGET_UNLOCK_THRESHOLD_DEFAULT
        except ImportError:
            self.unlock_threshold_slider.setRange(100, 300)
            default_value = 150
        
        self.unlock_threshold_slider.setValue(self.settings_manager.get_setting('widget_unlock_threshold', default_value))
        self.unlock_threshold_slider.setStyleSheet(get_slider_style())
        controls_layout.addWidget(self.unlock_threshold_slider)
        
        # Plus button
        unlock_threshold_plus_btn = create_adjustment_button("▶")
        unlock_threshold_plus_btn.setToolTip("Increase unlock threshold")
        unlock_threshold_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_unlock_threshold()
        unlock_threshold_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_unlock_threshold()
        controls_layout.addWidget(unlock_threshold_plus_btn)
        
        # Value label
        try:
            from dwellpy.config.constants import WIDGET_UNLOCK_THRESHOLD_DEFAULT
            default_value = WIDGET_UNLOCK_THRESHOLD_DEFAULT
        except ImportError:
            default_value = 150
        
        self.unlock_threshold_label = QLabel(f"{self.settings_manager.get_setting('widget_unlock_threshold', default_value)}px")
        self.unlock_threshold_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
            font-weight: bold;
            min-width: 35px;
            background: rgba(0, 120, 215, 0.1);
            border: 1px solid rgba(0, 120, 215, 0.3);
            border-radius: 3px;
            padding: 2px 4px;
        """)
        self.unlock_threshold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.addWidget(self.unlock_threshold_label)
        
        unlock_threshold_layout.addLayout(controls_layout)
        layout.addWidget(unlock_threshold_frame)
        
        # Menu Widget Section
        menu_header = create_section_header("Menu Widget",
                                           "Customize the appearance of the menu widget")
        layout.addWidget(menu_header)
        
        # Menu Widget Enable
        menu_enable_frame = QFrame()
        menu_enable_layout = QHBoxLayout(menu_enable_frame)
        menu_enable_layout.setContentsMargins(0, 0, 0, 0)
        menu_enable_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.menu_check = QCheckBox("Enable menu widget")
        self.menu_check.setChecked(self.settings_manager.get_setting('menu_enabled', True))
        self.menu_check.setStyleSheet(get_checkbox_style())
        self.menu_check.setToolTip("Show a circular menu widget when you dwell")
        menu_enable_layout.addWidget(self.menu_check)
        layout.addWidget(menu_enable_frame)
        
        # Icon Size Control (Label above, slider below)
        icon_size_frame = QFrame()
        icon_size_layout = QVBoxLayout(icon_size_frame)
        icon_size_layout.setContentsMargins(0, 0, 0, 0)
        icon_size_layout.setSpacing(4)
        
        # Label on top
        icon_size_label = QLabel("Icon Size:")
        icon_size_label.setStyleSheet(get_small_label_style())
        icon_size_layout.addWidget(icon_size_label)
        
        # Controls below in horizontal layout
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        
        # Minus button
        icon_size_minus_btn = create_adjustment_button("◀")
        icon_size_minus_btn.setToolTip("Decrease icon size")
        icon_size_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_menu_size()
        icon_size_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_menu_size()
        controls_layout.addWidget(icon_size_minus_btn)
        
        # Slider
        self.menu_size_slider = QSlider(Qt.Orientation.Horizontal)
        try:
            from dwellpy.config.constants import MENU_ITEM_SIZE_MIN, MENU_ITEM_SIZE_MAX
            self.menu_size_slider.setRange(MENU_ITEM_SIZE_MIN, MENU_ITEM_SIZE_MAX)
        except ImportError:
            self.menu_size_slider.setRange(40, 100)
        
        self.menu_size_slider.setValue(self.settings_manager.get_setting('menu_item_size', 60))
        self.menu_size_slider.setStyleSheet(get_slider_style())
        controls_layout.addWidget(self.menu_size_slider)
        
        # Plus button
        icon_size_plus_btn = create_adjustment_button("▶")
        icon_size_plus_btn.setToolTip("Increase icon size")
        icon_size_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_menu_size()
        icon_size_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_menu_size()
        controls_layout.addWidget(icon_size_plus_btn)
        
        # Value label
        self.menu_size_label = QLabel(str(self.settings_manager.get_setting('menu_item_size', 60)))
        self.menu_size_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
            font-weight: bold;
            min-width: 35px;
            background: rgba(0, 120, 215, 0.1);
            border: 1px solid rgba(0, 120, 215, 0.3);
            border-radius: 3px;
            padding: 2px 4px;
        """)
        self.menu_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.addWidget(self.menu_size_label)
        
        icon_size_layout.addLayout(controls_layout)
        layout.addWidget(icon_size_frame)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        return tab
    
    def create_behavior_tab(self):
        """Create a combined behavior tab with core dwell settings and general behavior."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame
        
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)
        
        # Core Dwell Settings Section
        dwell_header = self.create_section_header("Core Dwell Settings", 
                                                 "Essential settings that control how dwell clicking works")
        layout.addWidget(dwell_header)
        
        # Create a frame for all dwell settings
        dwell_settings_frame = QFrame()
        dwell_settings_layout = QVBoxLayout(dwell_settings_frame)
        dwell_settings_layout.setContentsMargins(10, 8, 10, 8)
        dwell_settings_layout.setSpacing(12)
        
        # Add dwell settings
        self.dwell_tab.create_move_limit_section(dwell_settings_layout)
        self.dwell_tab.create_dwell_time_section(dwell_settings_layout)
        layout.addWidget(dwell_settings_frame)
        
        # Application Behavior Section
        app_header = self.create_section_header("Application Behavior",
                                               "General application settings and startup behavior")
        layout.addWidget(app_header)
        
        # Create a frame for app behavior settings
        app_settings_frame = QFrame()
        app_settings_layout = QVBoxLayout(app_settings_frame)
        app_settings_layout.setContentsMargins(10, 8, 10, 8)
        app_settings_layout.setSpacing(12)
        
        # Add app behavior content
        self.general_tab.create_active_state_section(app_settings_layout)
        self.general_tab.create_ui_contraction_section(app_settings_layout)
        layout.addWidget(app_settings_frame)
        
        # Add minimal stretch to push content to the top
        layout.addStretch(1)
        
        return tab
    
    def create_section_header(self, title, description):
        """Create a section header for the widgets tab."""
        from PyQt6.QtWidgets import QLabel
        from dwellpy.ui.dialogs.settings.components.ui_components import create_section_header
        return create_section_header(title, description)
    
    def create_tabs(self):
        """Create all tabs using modularized components."""
        # Behavior Tab (Core + General combined)
        behavior_tab = self.create_behavior_tab()
        self.tab_widget.addTab(behavior_tab, "Behavior")
        
        # Visual Feedback Tab
        visual_tab = self.visual_tab.create_tab()
        self.tab_widget.addTab(visual_tab, "Visual")
        
        # Widgets Tab (combines scroll and menu settings)
        widgets_tab = self.create_widgets_tab()
        self.tab_widget.addTab(widgets_tab, "Widgets")
        
        # Add tooltips to tabs for better user experience
        self.tab_widget.setTabToolTip(0, "Core dwell clicking settings, startup behavior, and UI behavior")
        self.tab_widget.setTabToolTip(1, "Visual appearance and feedback settings")
        self.tab_widget.setTabToolTip(2, "Widget configuration - scroll and menu widgets")
    
    def create_bottom_section(self, main_layout):
        """Create the bottom section with OK button."""
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 {Colors.DARK_BUTTON_BG}, stop:1 #252525);
                border-top: 1px solid {Colors.BORDER_COLOR};
                padding: 12px;
                border-bottom-left-radius: {BORDER_RADIUS}px;
                border-bottom-right-radius: {BORDER_RADIUS}px;
            }}
        """)
        
        bottom_layout = QVBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(15, 0, 15, 0)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # OK button (now just closes the dialog since settings apply immediately)
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Colors.BLUE_ACCENT}, stop:1 {Colors.BLUE_HOVER});
                color: white;
                border: none;
                border-radius: {BORDER_RADIUS}px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Colors.BLUE_HOVER}, stop:1 {Colors.BLUE_ACCENT});
            }}
            QPushButton:pressed {{
                background: {Colors.BLUE_ACCENT};
            }}
        """)
        ok_button.clicked.connect(self.close)
        button_layout.addWidget(ok_button)
        
        bottom_layout.addLayout(button_layout)
        
        main_layout.addWidget(bottom_frame)
    
    def keyPressEvent(self, event):
        """Handle key press events for accessibility."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.accept()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Tab:
            # Allow normal tab navigation
            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
    
    def connect_signals(self):
        """Connect all signal handlers."""
        # Slider value changes
        self.move_limit_slider.valueChanged.connect(self.event_handlers.update_move_limit_value)
        self.time_slider.valueChanged.connect(self.event_handlers.update_time_value)
        self.transparency_slider.valueChanged.connect(self.event_handlers.update_transparency_value)
        self.scroll_speed_slider.valueChanged.connect(self.event_handlers.update_scroll_speed_value)
        self.widget_delay_slider.valueChanged.connect(self.event_handlers.update_widget_delay_value)
        self.unlock_threshold_slider.valueChanged.connect(self.event_handlers.update_unlock_threshold_value)
        self.menu_size_slider.valueChanged.connect(self.event_handlers.update_menu_size_value)
        
        # Checkbox toggles
        self.transparency_check.toggled.connect(self.event_handlers.on_transparency_toggle)
        self.scroll_check.toggled.connect(self.event_handlers.on_scroll_toggle)
        self.menu_check.toggled.connect(self.event_handlers.on_menu_toggle)
        self.visible_clicks_check.toggled.connect(self.event_handlers.on_visible_clicks_toggle)
        self.active_check.toggled.connect(self.event_handlers.on_active_toggle)
        self.contract_ui_check.toggled.connect(self.event_handlers.on_contract_ui_toggle)
        self.auto_start_check.toggled.connect(self.event_handlers.on_auto_start_toggle)
        
        # Color button clicks are handled in the VisualFeedbackTab
    
    def showEvent(self, event):
        """Handle show event."""
        super().showEvent(event)
        # Ensure window stays on top
        self.raise_()
        self.activateWindow()
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click event for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.close()
    
    def closeEvent(self, event):
        """Handle close event."""
        # Clean up timers
        self.event_handlers.cleanup_timers()
        super().closeEvent(event) 