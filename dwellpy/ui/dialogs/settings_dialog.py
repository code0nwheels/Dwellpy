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
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame
        
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 10, 15, 10)  # Reduced margins
        layout.setSpacing(8)  # Reduced spacing
        
        # Scroll Widget Section
        scroll_header = self.create_section_header("Scroll Widget", 
                                                   "A floating scroll widget that appears near your cursor for easy scrolling")
        layout.addWidget(scroll_header)
        
        # Add scroll widget content
        scroll_content = self.scroll_tab.create_scroll_widget_section(layout)
        
        # Menu Widget Section
        menu_header = self.create_section_header("Menu Widget",
                                                "Configure the circular menu widget appearance and behavior")
        layout.addWidget(menu_header)
        
        # Create a frame for menu widget settings
        menu_settings_frame = QFrame()
        menu_settings_layout = QVBoxLayout(menu_settings_frame)
        menu_settings_layout.setContentsMargins(10, 8, 10, 8)
        menu_settings_layout.setSpacing(12)
        
        # Add menu widget content as options within the section
        self.menu_tab.create_menu_item_size_section(menu_settings_layout)
        layout.addWidget(menu_settings_frame)
        
        # Add minimal stretch to push content to the top
        layout.addStretch(1)
        
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
        
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(15, 0, 15, 0)
        
        # Spacer
        bottom_layout.addStretch()
        
        # Close button
        close_button = QPushButton("Cancel")
        close_button.setFixedSize(100, 40)  # Increased from 80x35
        close_button.setFont(QFont(Fonts.PRIMARY_FAMILY, 12, QFont.Weight.Bold))  # Increased from 11pt
        close_button.setAccessibleName("Cancel Settings")
        close_button.setAccessibleDescription("Close the settings dialog without saving changes")
        close_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 {Colors.DARK_BUTTON_BG}, stop:1 #252525);
                color: {Colors.TEXT_COLOR};
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: {BORDER_RADIUS}px;
                padding: 10px 20px;  /* Increased from 8px 16px */
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #353535, stop:1 #2a2a2a);
                border-color: {Colors.BLUE_HOVER};
            }}
            QPushButton:pressed {{
                background: {Colors.BLUE_ACCENT};
            }}
        """)
        close_button.clicked.connect(self.close)
        bottom_layout.addWidget(close_button)
        
        # Add spacing between buttons
        bottom_layout.addSpacing(15)  # Increased from 10
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.setFixedSize(100, 40)  # Increased from 80x35
        ok_button.setFont(QFont(Fonts.PRIMARY_FAMILY, 12, QFont.Weight.Bold))  # Increased from 11pt
        ok_button.setAccessibleName("Save Settings")
        ok_button.setAccessibleDescription("Save all settings and close the dialog")
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 {Colors.BLUE_ACCENT}, stop:1 {Colors.BLUE_HOVER});
                color: {Colors.TEXT_COLOR};
                border: 1px solid {Colors.BLUE_ACCENT};
                border-radius: {BORDER_RADIUS}px;
                padding: 10px 20px;  /* Increased from 8px 16px */
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 {Colors.BLUE_HOVER}, stop:1 {Colors.BLUE_ACCENT});
                border-color: {Colors.BLUE_HOVER};
            }}
            QPushButton:pressed {{
                background: {Colors.BLUE_ACCENT};
            }}
        """)
        ok_button.clicked.connect(self.accept)
        bottom_layout.addWidget(ok_button)
        
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
        self.visible_clicks_check.toggled.connect(self.event_handlers.on_visible_clicks_toggle)
        self.active_check.toggled.connect(self.event_handlers.on_active_toggle)
        self.contract_ui_check.toggled.connect(self.event_handlers.on_contract_ui_toggle)
        self.auto_start_check.toggled.connect(self.event_handlers.on_auto_start_toggle)
        
        # Color button clicks are handled in the VisualFeedbackTab
    
    def accept(self):
        """Save settings and close dialog."""
        # Save all slider values
        self.settings_manager.set_setting('move_limit', self.move_limit_slider.value())
        self.settings_manager.set_setting('dwell_time', self.time_slider.value() / 10.0)
        self.settings_manager.set_setting('transparency_enabled', self.transparency_check.isChecked())
        self.settings_manager.set_setting('transparency_level', self.transparency_slider.value())
        self.settings_manager.set_setting('visible_clicks_enabled', self.visible_clicks_check.isChecked())
        self.settings_manager.set_setting('scroll_enabled', self.scroll_check.isChecked())
        self.settings_manager.set_setting('widget_appearance_delay', self.widget_delay_slider.value() / 10.0)
        self.settings_manager.set_setting('widget_unlock_threshold', self.unlock_threshold_slider.value())
        self.settings_manager.set_setting('menu_item_size', self.menu_size_slider.value())
        self.settings_manager.set_setting('default_active', self.active_check.isChecked())
        self.settings_manager.set_setting('contract_ui_enabled', self.contract_ui_check.isChecked())
        
        # Save scroll speed (convert slider value back to interval)
        speed_value = self.scroll_speed_slider.value()
        interval = (11 - speed_value) * 20  # Convert back to milliseconds
        self.settings_manager.set_setting('scroll_speed', interval)
        
        super().accept()
    
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