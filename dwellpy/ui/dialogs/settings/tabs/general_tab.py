"""General tab for settings dialog."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QCheckBox, QRadioButton, QButtonGroup
from PyQt6.QtCore import Qt
import os

try:
    from ....config.constants import Colors
except ImportError:
    class Colors:
        TEXT_COLOR = "#ffffff"

from ..components.ui_components import create_section_header, get_checkbox_style, get_radio_style


class GeneralTab:
    """General tab creation and management."""
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.settings_manager = dialog.settings_manager
        self.event_handlers = dialog.event_handlers
    
    def create_tab(self):
        """Create general tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Startup Behavior Section
        startup_header = create_section_header("Startup Behavior",
                                              "How Dwellpy should behave when first launched")
        layout.addWidget(startup_header)
        
        self.create_active_state_section(layout)
        
        # UI Behavior Section
        ui_header = create_section_header("UI Behavior",
                                         "How the toolbar behaves when you're not using it")
        layout.addWidget(ui_header)
        
        self.create_ui_contraction_section(layout)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        return tab
    
    def create_active_state_section(self, layout):
        """Create default active state section."""
        # Active on launch
        active_frame = QFrame()
        active_layout = QHBoxLayout(active_frame)
        active_layout.setContentsMargins(0, 0, 0, 0)
        active_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.dialog.active_check = QCheckBox("Active on launch")
        self.dialog.active_check.setChecked(self.settings_manager.get_setting('active_on_launch', True))
        self.dialog.active_check.setStyleSheet(get_checkbox_style())
        active_layout.addWidget(self.dialog.active_check)
        
        layout.addWidget(active_frame)
        
        # Auto-start with system
        auto_start_frame = QFrame()
        auto_start_layout = QHBoxLayout(auto_start_frame)
        auto_start_layout.setContentsMargins(0, 0, 0, 0)
        auto_start_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.dialog.auto_start_check = QCheckBox("Automatically start with system")
        self.dialog.auto_start_check.setChecked(self.settings_manager.get_setting('auto_start_enabled', False))
        self.dialog.auto_start_check.setStyleSheet(get_checkbox_style())
        auto_start_layout.addWidget(self.dialog.auto_start_check)
        
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
        
        self.dialog.contract_ui_check = QCheckBox("Contract UI when idle")
        self.dialog.contract_ui_check.setChecked(self.settings_manager.get_setting('contract_ui_enabled', True))
        self.dialog.contract_ui_check.setStyleSheet(get_checkbox_style())
        contract_ui_layout.addWidget(self.dialog.contract_ui_check)
        
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
        self.dialog.expansion_button_group = QButtonGroup()
        
        # Auto radio button
        self.dialog.expansion_auto_radio = QRadioButton("Auto (detects available space)")
        self.dialog.expansion_auto_radio.setStyleSheet(get_radio_style())
        self.dialog.expansion_button_group.addButton(self.dialog.expansion_auto_radio, 0)
        radio_layout.addWidget(self.dialog.expansion_auto_radio)
        
        # Horizontal radio button
        self.dialog.expansion_horizontal_radio = QRadioButton("Horizontal (left-to-right)")
        self.dialog.expansion_horizontal_radio.setStyleSheet(get_radio_style())
        self.dialog.expansion_button_group.addButton(self.dialog.expansion_horizontal_radio, 1)
        radio_layout.addWidget(self.dialog.expansion_horizontal_radio)
        
        # Vertical radio button
        self.dialog.expansion_vertical_radio = QRadioButton("Vertical (top-to-bottom)")
        self.dialog.expansion_vertical_radio.setStyleSheet(get_radio_style())
        self.dialog.expansion_button_group.addButton(self.dialog.expansion_vertical_radio, 2)
        radio_layout.addWidget(self.dialog.expansion_vertical_radio)
        
        expansion_direction_layout.addWidget(radio_container)
        
        # Set current selection based on settings
        current_direction = self.settings_manager.get_setting('expansion_direction', 'auto')
        if current_direction == 'auto':
            self.dialog.expansion_auto_radio.setChecked(True)
        elif current_direction == 'horizontal':
            self.dialog.expansion_horizontal_radio.setChecked(True)
        elif current_direction == 'vertical':
            self.dialog.expansion_vertical_radio.setChecked(True)
        
        layout.addWidget(expansion_direction_frame) 