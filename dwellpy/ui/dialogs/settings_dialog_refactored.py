"""Refactored settings dialog for the Dwellpy application."""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QTabWidget, QWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
import os

try:
    from ...config.constants import Colors, BORDER_RADIUS, Fonts
    from ...utils.helpers import center_window, get_asset_path
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
from .settings.components import SettingsEventHandlers
from .settings.tabs import (DwellMovementTab, VisualFeedbackTab, 
                           ScrollWidgetTab, MenuWidgetTab, GeneralTab)


class SettingsDialog(QDialog):
    """Refactored settings dialog for Dwellpy configuration."""
    
    def __init__(self, settings_manager, button_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.button_manager = button_manager
        
        # For frameless window dragging
        self.drag_pos = None
        
        # Initialize event handlers
        self.event_handlers = SettingsEventHandlers(self)
        
        # Initialize tab creators
        self.dwell_tab = DwellMovementTab(self)
        self.visual_tab = VisualFeedbackTab(self)
        self.scroll_tab = ScrollWidgetTab(self)
        self.menu_tab = MenuWidgetTab(self)
        self.general_tab = GeneralTab(self)
        
        # Setup the dialog
        self.setup_ui()
        
        # Connect signals
        self.connect_signals()
    
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
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: {BORDER_RADIUS}px;
                border-top-right-radius: {BORDER_RADIUS}px;
                border: 1px solid {Colors.BORDER_COLOR};
                border-bottom: none;
                font-family: {Fonts.MAIN_FONT};
                font-size: 11px;
                font-weight: bold;
                min-width: 80px;
            }}
            QTabBar::tab:selected {{
                background-color: {Colors.BLUE_ACCENT};
                border-color: {Colors.BLUE_ACCENT};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {Colors.BLUE_HOVER};
                border-color: {Colors.BLUE_HOVER};
            }}
            QTabBar::tab:disabled {{
                background-color: {Colors.DARK_BG};
                color: #666666;
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Title bar
        title_frame = self.create_title_frame()
        main_layout.addWidget(title_frame)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs using modularized components
        self.create_tabs()
        
        # Bottom section with OK button
        self.create_bottom_section(main_layout)
        
        # Set dialog size and position
        self.resize(800, 600)
        center_window(self)
    
    def create_title_frame(self):
        """Create the title bar frame."""
        title_frame = QFrame()
        title_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BLUE_ACCENT};
                border-bottom: 1px solid {Colors.BORDER_COLOR};
                padding: 10px;
            }}
        """)
        
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(15, 10, 15, 10)
        
        # Title
        title_label = QLabel("Dwellpy Settings")
        title_label.setFont(QFont(Fonts.MAIN_FONT, 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        title_layout.addWidget(title_label)
        
        # Version
        version_label = QLabel(f"v{__version__}")
        version_label.setFont(QFont(Fonts.MAIN_FONT, 10))
        version_label.setStyleSheet(f"color: {Colors.TEXT_COLOR}; opacity: 0.8;")
        title_layout.addWidget(version_label)
        
        # Spacer
        title_layout.addStretch()
        
        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(30, 30)
        close_button.setFont(QFont(Fonts.MAIN_FONT, 16, QFont.Weight.Bold))
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_COLOR};
                border: none;
                border-radius: 15px;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.2);
            }}
        """)
        close_button.clicked.connect(self.close)
        title_layout.addWidget(close_button)
        
        return title_frame
    
    def create_tabs(self):
        """Create all tabs using modularized components."""
        # Dwell Movement Tab
        dwell_tab = self.dwell_tab.create_tab()
        self.tab_widget.addTab(dwell_tab, "Dwell")
        
        # Visual Feedback Tab
        visual_tab = self.visual_tab.create_tab()
        self.tab_widget.addTab(visual_tab, "Visual")
        
        # Scroll Widget Tab
        scroll_tab = self.scroll_tab.create_tab()
        self.tab_widget.addTab(scroll_tab, "Scroll")
        
        # Menu Widget Tab
        menu_tab = self.menu_tab.create_tab()
        self.tab_widget.addTab(menu_tab, "Menu")
        
        # General Tab
        general_tab = self.general_tab.create_tab()
        self.tab_widget.addTab(general_tab, "General")
    
    def create_bottom_section(self, main_layout):
        """Create the bottom section with OK button."""
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.DARK_BUTTON_BG};
                border-top: 1px solid {Colors.BORDER_COLOR};
                padding: 15px;
            }}
        """)
        
        bottom_layout = QHBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(20, 15, 20, 15)
        
        # Spacer
        bottom_layout.addStretch()
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.setFixedSize(80, 35)
        ok_button.setFont(QFont(Fonts.MAIN_FONT, 11, QFont.Weight.Bold))
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BLUE_ACCENT};
                color: {Colors.TEXT_COLOR};
                border: 1px solid {Colors.BLUE_ACCENT};
                border-radius: {BORDER_RADIUS}px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BLUE_HOVER};
                border-color: {Colors.BLUE_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Colors.BLUE_ACCENT};
            }}
        """)
        ok_button.clicked.connect(self.accept)
        bottom_layout.addWidget(ok_button)
        
        main_layout.addWidget(bottom_frame)
    
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
        
        # Radio button changes
        self.expansion_button_group.buttonClicked.connect(
            lambda button: self.event_handlers.on_expansion_direction_toggle(button)
        )
        
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
        self.settings_manager.set_setting('active_on_launch', self.active_check.isChecked())
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
    
    def mousePressEvent(self, event):
        """Handle mouse press event for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move event for window dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            diff = event.globalPosition().toPoint() - self.drag_pos
            new_pos = self.pos() + diff
            self.move(new_pos)
            self.drag_pos = event.globalPosition().toPoint()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release event for window dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = None
    
    def closeEvent(self, event):
        """Handle close event."""
        # Clean up timers
        self.event_handlers.cleanup_timers()
        super().closeEvent(event) 