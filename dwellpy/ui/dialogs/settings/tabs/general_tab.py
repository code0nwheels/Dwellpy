"""General tab for settings dialog."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QCheckBox, QRadioButton, QButtonGroup, QComboBox
from PyQt6.QtCore import Qt
from dwellpy.config.constants import Colors, Fonts, BORDER_RADIUS
from dwellpy.ui.dialogs.settings.components.ui_components import (
    create_section_header, get_checkbox_style, get_radio_style, 
    get_label_style, get_small_label_style
)
import os


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
        layout.setContentsMargins(20, 15, 20, 15)  # Increased from 15,10,15,10
        layout.setSpacing(18)  # Increased from 15
        
        # Application Behavior Section
        app_header = create_section_header("Application Behavior",
                                          "How Dwellpy behaves when launched and during operation")
        layout.addWidget(app_header)
        
        self.create_active_state_section(layout)
        
        # Interface Behavior Section
        ui_header = create_section_header("Interface Behavior",
                                         "How the toolbar and interface elements behave")
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
        self.dialog.active_check.setChecked(self.settings_manager.get_setting('default_active', True))
        self.dialog.active_check.setStyleSheet(get_checkbox_style())
        self.dialog.active_check.setToolTip("Start Dwellpy in active mode when launched")
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
        self.dialog.auto_start_check.setToolTip("Launch Dwellpy automatically when your system starts up")
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
        self.dialog.contract_ui_check.setToolTip("Automatically hide the toolbar when not in use to save screen space")
        contract_ui_layout.addWidget(self.dialog.contract_ui_check)
        
        layout.addWidget(contract_ui_frame)
        
        # Expansion Direction Section
        expansion_frame = QFrame()
        expansion_layout = QVBoxLayout(expansion_frame)
        expansion_layout.setContentsMargins(0, 0, 0, 0)
        expansion_layout.setSpacing(4)
        
        # Label on top
        expansion_direction_label = QLabel("Expansion Direction:")
        expansion_direction_label.setStyleSheet(get_small_label_style())
        expansion_layout.addWidget(expansion_direction_label)
        
        # Dropdown below the label
        self.expansion_direction_combo = QComboBox()
        self.expansion_direction_combo.addItem("Auto (detects available space)", "auto")
        self.expansion_direction_combo.addItem("Expand Up", "up")
        self.expansion_direction_combo.addItem("Expand Down", "down")
        self.expansion_direction_combo.addItem("Expand Left", "left")
        self.expansion_direction_combo.addItem("Expand Right", "right")
        
        # Set current value
        current_direction = self.settings_manager.get_setting('expansion_direction', 'auto')
        index = self.expansion_direction_combo.findData(current_direction)
        if index >= 0:
            self.expansion_direction_combo.setCurrentIndex(index)
        
        # Style the dropdown
        self.expansion_direction_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {Colors.DARK_BUTTON_BG};
                color: {Colors.TEXT_COLOR};
                border: 1px solid {Colors.BORDER_COLOR};
                border-radius: {BORDER_RADIUS}px;
                padding: 6px 12px;
                font-size: 11px;
                min-width: 200px;
            }}
            QComboBox:hover {{
                border-color: {Colors.BLUE_HOVER};
            }}
            QComboBox:focus {{
                border-color: {Colors.BLUE_ACCENT};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {Colors.TEXT_COLOR};
                margin-right: 5px;
            }}
        """)
        
        expansion_layout.addWidget(self.expansion_direction_combo)
        layout.addWidget(expansion_frame)
        
        # Connect the dropdown signal to save changes
        self.expansion_direction_combo.currentIndexChanged.connect(
            lambda index: self.dialog.event_handlers.on_expansion_direction_changed(index)
        ) 