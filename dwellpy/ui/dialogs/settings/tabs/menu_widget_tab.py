"""Menu Widget tab for settings dialog."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSlider
from PyQt6.QtCore import Qt
from dwellpy.config.constants import Colors, Fonts, BORDER_RADIUS
from dwellpy.ui.dialogs.settings.components.ui_components import (
    create_section_header, create_adjustment_button, get_slider_style,
    get_label_style, get_small_label_style
)


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
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(12)
        
        # Menu Item Size Section
        self.create_menu_item_size_section(layout)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        return tab
    
    def create_menu_item_size_section(self, layout):
        """Create menu item size adjustment section."""
        # Controls frame
        size_frame = QFrame()
        size_layout = QVBoxLayout(size_frame)  # Changed to vertical layout
        size_layout.setContentsMargins(0, 0, 0, 0)
        size_layout.setSpacing(4)  # Reduced spacing for vertical layout

        # Label on top
        size_label = QLabel("Icon Size:")
        size_label.setStyleSheet(get_small_label_style())
        size_layout.addWidget(size_label)
        
        # Controls below in horizontal layout
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)

        # Minus button
        menu_size_minus_btn = create_adjustment_button("◀")
        menu_size_minus_btn.setToolTip("Decrease menu item size")
        menu_size_minus_btn.setAccessibleName("Decrease Menu Item Size")
        menu_size_minus_btn.setAccessibleDescription("Click to decrease the size of menu items")
        menu_size_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_menu_size()
        menu_size_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_menu_size()
        controls_layout.addWidget(menu_size_minus_btn)

        # Slider for menu item size
        self.dialog.menu_size_slider = QSlider(Qt.Orientation.Horizontal)
        # Use constants if available, otherwise fallback values
        try:
            from dwellpy.config.constants import MENU_ITEM_SIZE_MIN, MENU_ITEM_SIZE_MAX
            self.dialog.menu_size_slider.setRange(MENU_ITEM_SIZE_MIN, MENU_ITEM_SIZE_MAX)
        except ImportError:
            self.dialog.menu_size_slider.setRange(40, 100)  # Fallback range
        
        self.dialog.menu_size_slider.setValue(self.settings_manager.get_setting('menu_item_size', 60))
        self.dialog.menu_size_slider.setStyleSheet(get_slider_style())
        self.dialog.menu_size_slider.setToolTip("Adjust the size of menu items in the circular menu")
        self.dialog.menu_size_slider.setAccessibleName("Menu Item Size Slider")
        self.dialog.menu_size_slider.setAccessibleDescription("Controls how large the menu items appear")
        controls_layout.addWidget(self.dialog.menu_size_slider)

        # Plus button
        menu_size_plus_btn = create_adjustment_button("▶")
        menu_size_plus_btn.setToolTip("Increase menu item size")
        menu_size_plus_btn.setAccessibleName("Increase Menu Item Size")
        menu_size_plus_btn.setAccessibleDescription("Click to increase the size of menu items")
        menu_size_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_menu_size()
        menu_size_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_menu_size()
        controls_layout.addWidget(menu_size_plus_btn)

        # Value label
        self.dialog.menu_size_label = QLabel(str(self.settings_manager.get_setting('menu_item_size', 60)))
        self.dialog.menu_size_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
            font-weight: bold;
            min-width: 35px;
            background: rgba(0, 120, 215, 0.1);
            border: 1px solid rgba(0, 120, 215, 0.3);
            border-radius: 3px;
            padding: 2px 4px;
        """)
        self.dialog.menu_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.addWidget(self.dialog.menu_size_label)
        
        # Add controls layout to main layout
        size_layout.addLayout(controls_layout)
        
        layout.addWidget(size_frame) 