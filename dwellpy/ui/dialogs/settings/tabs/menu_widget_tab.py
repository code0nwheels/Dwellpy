"""Menu Widget tab for settings dialog."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSlider
from PyQt6.QtCore import Qt

try:
    from ....config.constants import Colors
except ImportError:
    class Colors:
        TEXT_COLOR = "#ffffff"

from ..components.ui_components import create_section_header, create_adjustment_button, get_slider_style


class MenuWidgetTab:
    """Menu Widget tab creation and management."""
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.settings_manager = dialog.settings_manager
        self.event_handlers = dialog.event_handlers
    
    def create_tab(self):
        """Create menu widget settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Menu Item Size Section
        self.create_menu_item_size_section(layout)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        return tab
    
    def create_menu_item_size_section(self, layout):
        """Create menu item size adjustment section."""
        # Header
        menu_size_header = create_section_header(
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
        menu_size_minus_btn = create_adjustment_button("◀")
        menu_size_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_menu_size()
        menu_size_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_menu_size()
        size_layout.addWidget(menu_size_minus_btn)

        # Slider for menu item size
        self.dialog.menu_size_slider = QSlider(Qt.Orientation.Horizontal)
        # Use constants if available, otherwise fallback values
        try:
            from ....config.constants import MENU_ITEM_SIZE_MIN, MENU_ITEM_SIZE_MAX
            self.dialog.menu_size_slider.setRange(MENU_ITEM_SIZE_MIN, MENU_ITEM_SIZE_MAX)
        except ImportError:
            self.dialog.menu_size_slider.setRange(40, 100)  # Fallback range
        
        self.dialog.menu_size_slider.setValue(self.settings_manager.get_setting('menu_item_size', 60))
        self.dialog.menu_size_slider.setStyleSheet(get_slider_style())
        size_layout.addWidget(self.dialog.menu_size_slider)

        # Plus button
        menu_size_plus_btn = create_adjustment_button("▶")
        menu_size_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_menu_size()
        menu_size_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_menu_size()
        size_layout.addWidget(menu_size_plus_btn)

        # Value label
        self.dialog.menu_size_label = QLabel(str(self.settings_manager.get_setting('menu_item_size', 60)))
        self.dialog.menu_size_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
        """)
        self.dialog.menu_size_label.setFixedWidth(40)
        size_layout.addWidget(self.dialog.menu_size_label)
        
        layout.addWidget(size_frame) 