"""Visual Feedback tab for settings dialog."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSlider, QCheckBox, QPushButton
from PyQt6.QtCore import Qt

try:
    from ....config.constants import Colors
except ImportError:
    class Colors:
        TEXT_COLOR = "#ffffff"

from ..components.ui_components import (create_section_header, create_adjustment_button, 
                                       get_slider_style, get_checkbox_style, create_color_button,
                                       format_percentage_display)


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
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Window Appearance Section
        appearance_header = create_section_header("Window Appearance",
                                                 "Control how the Dwellpy toolbar looks and behaves")
        layout.addWidget(appearance_header)
        
        self.create_transparency_section(layout)
        
        # Click Feedback Section
        feedback_header = create_section_header("Click Feedback",
                                               "Visual indicators to show where and what type of clicks are performed")
        layout.addWidget(feedback_header)
        
        self.create_visible_clicks_section(layout)
        self.create_click_colors_section(layout)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
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
        transparency_enable_layout.addWidget(self.dialog.transparency_check)
        
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
        transparency_minus_btn = create_adjustment_button("◀")
        transparency_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_transparency()
        transparency_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_transparency()
        transparency_layout.addWidget(transparency_minus_btn)
        
        # Slider
        self.dialog.transparency_slider = QSlider(Qt.Orientation.Horizontal)
        self.dialog.transparency_slider.setRange(10, 90)
        self.dialog.transparency_slider.setValue(self.settings_manager.get_setting('transparency_level', 70))
        self.dialog.transparency_slider.setStyleSheet(get_slider_style())
        transparency_layout.addWidget(self.dialog.transparency_slider)
        
        # Plus button
        transparency_plus_btn = create_adjustment_button("▶")
        transparency_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_transparency()
        transparency_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_transparency()
        transparency_layout.addWidget(transparency_plus_btn)
        
        # Value label
        self.dialog.transparency_label = QLabel(format_percentage_display(self.settings_manager.get_setting('transparency_level', 70)))
        self.dialog.transparency_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
        """)
        self.dialog.transparency_label.setFixedWidth(40)
        transparency_layout.addWidget(self.dialog.transparency_label)
        
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
        visible_clicks_layout.addWidget(self.dialog.visible_clicks_check)
        
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
        
        # Create color picker buttons in a grid layout
        color_grid_frame = QFrame()
        color_grid_layout = QHBoxLayout(color_grid_frame)
        color_grid_layout.setContentsMargins(0, 0, 0, 0)
        color_grid_layout.setSpacing(8)
        
        for click_type in ['left', 'right', 'double', 'drag_down', 'drag_up', 'middle']:
            color_btn = create_color_button(click_type, color_names[click_type], default_colors[click_type])
            color_grid_layout.addWidget(color_btn)
            
            # Store button references for event handling and connect color picker
            if click_type == 'left':
                self.dialog.left_click_color_button = color_btn
                color_btn.clicked.connect(
                    lambda checked, btn=color_btn: self.event_handlers.open_color_picker('left', btn)
                )
            elif click_type == 'right':
                self.dialog.right_click_color_button = color_btn
                color_btn.clicked.connect(
                    lambda checked, btn=color_btn: self.event_handlers.open_color_picker('right', btn)
                )
            elif click_type == 'double':
                self.dialog.double_click_color_button = color_btn
                color_btn.clicked.connect(
                    lambda checked, btn=color_btn: self.event_handlers.open_color_picker('double', btn)
                )
        
        layout.addWidget(color_grid_frame) 