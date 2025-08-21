"""Visual Feedback tab for settings dialog."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSlider, QCheckBox, QPushButton, QGridLayout
from PyQt6.QtCore import Qt
from dwellpy.config.constants import Colors, Fonts, BORDER_RADIUS
from dwellpy.ui.dialogs.settings.components.ui_components import (
    create_section_header, create_adjustment_button, get_slider_style, get_checkbox_style,
    get_label_style, get_small_label_style, create_color_button, format_percentage_display
)


class VisualFeedbackTab:
    """Visual Feedback tab creation and management."""
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.settings_manager = dialog.settings_manager
        self.event_handlers = dialog.event_handlers
    
    def create_tab(self):
        """Create visual feedback tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 10, 15, 10)  # Reduced margins
        layout.setSpacing(8)  # Reduced spacing
        
        # Interface Appearance Section
        appearance_header = create_section_header("Interface Appearance",
                                                 "Control how the Dwellpy interface looks and behaves")
        layout.addWidget(appearance_header)
        
        self.create_transparency_section(layout)
        
        # Click Feedback Section
        feedback_header = create_section_header("Click Feedback",
                                               "Visual indicators to show where and what type of clicks are performed")
        layout.addWidget(feedback_header)
        
        self.create_visible_clicks_section(layout)
        self.create_click_colors_section(layout)
        
        # Add minimal stretch to push content to the top
        layout.addStretch(1)
        
        return tab
    
    def create_transparency_section(self, layout):
        """Create transparency adjustment section."""
        # Enable checkbox
        transparency_enable_frame = QFrame()
        transparency_enable_layout = QHBoxLayout(transparency_enable_frame)
        transparency_enable_layout.setContentsMargins(0, 0, 0, 0)
        transparency_enable_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.dialog.transparency_check = QCheckBox("Enable window transparency")
        self.dialog.transparency_check.setChecked(self.settings_manager.get_setting('transparency_enabled', False))
        self.dialog.transparency_check.setStyleSheet(get_checkbox_style())
        self.dialog.transparency_check.setToolTip("Make the Dwellpy toolbar semi-transparent")
        transparency_enable_layout.addWidget(self.dialog.transparency_check)
        
        layout.addWidget(transparency_enable_frame)
        
        # Transparency level controls in a compact layout
        transparency_frame = QFrame()
        transparency_layout = QVBoxLayout(transparency_frame)  # Changed to vertical layout
        transparency_layout.setContentsMargins(0, 0, 0, 0)
        transparency_layout.setSpacing(4)  # Reduced spacing for vertical layout
        
        # Label on top
        transparency_label = QLabel("Transparency (%):")
        transparency_label.setStyleSheet(get_small_label_style())
        transparency_layout.addWidget(transparency_label)
        
        # Controls below in horizontal layout
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)
        
        # Minus button
        transparency_minus_btn = create_adjustment_button("◀")
        transparency_minus_btn.setToolTip("Decrease transparency")
        transparency_minus_btn.setAccessibleName("Decrease Transparency")
        transparency_minus_btn.setAccessibleDescription("Click to decrease transparency by 1%")
        transparency_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_transparency()
        transparency_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_transparency()
        controls_layout.addWidget(transparency_minus_btn)
        
        # Slider
        self.dialog.transparency_slider = QSlider(Qt.Orientation.Horizontal)
        self.dialog.transparency_slider.setRange(10, 90)
        self.dialog.transparency_slider.setValue(self.settings_manager.get_setting('transparency_level', 70))
        self.dialog.transparency_slider.setStyleSheet(get_slider_style())
        self.dialog.transparency_slider.setToolTip("Adjust the transparency level of the Dwellpy toolbar")
        self.dialog.transparency_slider.setAccessibleName("Transparency Slider")
        self.dialog.transparency_slider.setAccessibleDescription("Controls how transparent the toolbar appears")
        controls_layout.addWidget(self.dialog.transparency_slider)
        
        # Plus button
        transparency_plus_btn = create_adjustment_button("▶")
        transparency_plus_btn.setToolTip("Increase transparency")
        transparency_plus_btn.setAccessibleName("Increase Transparency")
        transparency_plus_btn.setAccessibleDescription("Click to increase transparency by 1%")
        transparency_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_transparency()
        transparency_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_transparency()
        controls_layout.addWidget(transparency_plus_btn)
        
        # Value label
        self.dialog.transparency_label = QLabel(format_percentage_display(self.settings_manager.get_setting('transparency_level', 70)))
        self.dialog.transparency_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
            font-weight: bold;
            min-width: 35px;
            background: rgba(0, 120, 215, 0.1);
            border: 1px solid rgba(0, 120, 215, 0.3);
            border-radius: 3px;
            padding: 2px 4px;
        """)
        self.dialog.transparency_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.addWidget(self.dialog.transparency_label)
        
        # Add controls layout to main layout
        transparency_layout.addLayout(controls_layout)
        
        layout.addWidget(transparency_frame)
    
    def create_visible_clicks_section(self, layout):
        """Create visible clicks section."""
        # Enable checkbox
        visible_clicks_frame = QFrame()
        visible_clicks_layout = QHBoxLayout(visible_clicks_frame)
        visible_clicks_layout.setContentsMargins(0, 0, 0, 0)
        visible_clicks_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.dialog.visible_clicks_check = QCheckBox("Enable visible clicks")
        self.dialog.visible_clicks_check.setChecked(self.settings_manager.get_setting('visible_clicks_enabled', False))
        self.dialog.visible_clicks_check.setStyleSheet(get_checkbox_style())
        self.dialog.visible_clicks_check.setToolTip("Show visual feedback when clicks are performed")
        self.dialog.visible_clicks_check.setAccessibleName("Visible Clicks")
        self.dialog.visible_clicks_check.setAccessibleDescription("Enable visual indicators to show where and what type of clicks are performed")
        visible_clicks_layout.addWidget(self.dialog.visible_clicks_check)
        
        layout.addWidget(visible_clicks_frame)
    
    def create_click_colors_section(self, layout):
        """Create click colors customization section."""
        # Section title
        colors_label = QLabel("Click Colors:")
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
        
        # Create color picker buttons in a compact grid layout
        color_grid_frame = QFrame()
        color_grid_layout = QHBoxLayout(color_grid_frame)
        color_grid_layout.setContentsMargins(0, 0, 0, 0)
        color_grid_layout.setSpacing(6)
        color_grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Group colors logically: Primary clicks, Drag operations, Middle click
        primary_colors = ['left', 'right', 'double']
        drag_colors = ['drag_down', 'drag_up']
        other_colors = ['middle']
        
        # Add primary click colors
        for click_type in primary_colors:
            color_btn = create_color_button(click_type, color_names[click_type], default_colors[click_type])
            color_btn.setToolTip(f"Click to change {color_names[click_type]} color")
            color_btn.setAccessibleName(f"{color_names[click_type]} Color")
            color_btn.setAccessibleDescription(f"Click to customize the color for {color_names[click_type]} feedback")
            color_grid_layout.addWidget(color_btn)
        
        # Add a small spacer between groups
        spacer = QFrame()
        spacer.setFixedWidth(10)
        color_grid_layout.addWidget(spacer)
        
        # Add drag operation colors
        for click_type in drag_colors:
            color_btn = create_color_button(click_type, color_names[click_type], default_colors[click_type])
            color_btn.setToolTip(f"Click to change {color_names[click_type]} color")
            color_btn.setAccessibleName(f"{color_names[click_type]} Color")
            color_btn.setAccessibleDescription(f"Click to customize the color for {color_names[click_type]} feedback")
            color_grid_layout.addWidget(color_btn)
        
        # Add another spacer
        spacer2 = QFrame()
        spacer2.setFixedWidth(10)
        color_grid_layout.addWidget(spacer2)
        
        # Add other colors
        for click_type in other_colors:
            color_btn = create_color_button(click_type, color_names[click_type], default_colors[click_type])
            color_btn.setToolTip(f"Click to change {color_names[click_type]} color")
            color_btn.setAccessibleName(f"{color_names[click_type]} Color")
            color_btn.setAccessibleDescription(f"Click to customize the color for {color_names[click_type]} feedback")
            color_grid_layout.addWidget(color_btn)
        
        # Now connect all color buttons to their event handlers
        # We need to find the buttons by their text since we can't store references in the loop
        for child in color_grid_frame.children():
            if hasattr(child, 'text') and child.text():
                button_text = child.text()
                if button_text == "Left Click":
                    self.dialog.left_click_color_button = child
                    child.clicked.connect(
                        lambda checked, btn=child: self.event_handlers.open_color_picker('left', btn)
                    )
                elif button_text == "Right Click":
                    self.dialog.right_click_color_button = child
                    child.clicked.connect(
                        lambda checked, btn=child: self.event_handlers.open_color_picker('right', btn)
                    )
                elif button_text == "Double Click":
                    self.dialog.double_click_color_button = child
                    child.clicked.connect(
                        lambda checked, btn=child: self.event_handlers.open_color_picker('double', btn)
                    )
                elif button_text == "Drag Start":
                    self.dialog.drag_start_color_button = child
                    child.clicked.connect(
                        lambda checked, btn=child: self.event_handlers.open_color_picker('drag_down', btn)
                    )
                elif button_text == "Drag End":
                    self.dialog.drag_end_color_button = child
                    child.clicked.connect(
                        lambda checked, btn=child: self.event_handlers.open_color_picker('drag_up', btn)
                    )
                elif button_text == "Middle Click":
                    self.dialog.middle_click_color_button = child
                    child.clicked.connect(
                        lambda checked, btn=child: self.event_handlers.open_color_picker('middle', btn)
                    )
        
        layout.addWidget(color_grid_frame) 