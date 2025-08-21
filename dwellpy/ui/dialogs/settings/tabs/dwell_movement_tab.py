"""Dwell Movement tab for settings dialog."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSlider
from PyQt6.QtCore import Qt
from dwellpy.config.constants import Colors, Fonts, BORDER_RADIUS
from dwellpy.ui.dialogs.settings.components.ui_components import (
    create_section_header, create_adjustment_button, get_slider_style,
    get_label_style, get_small_label_style, format_time_display
)


class DwellMovementTab:
    """Dwell Movement tab creation and management."""
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.settings_manager = dialog.settings_manager
        self.event_handlers = dialog.event_handlers
    
    def create_tab(self):
        """Create core functionality tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 10, 15, 10)  # Reduced margins
        layout.setSpacing(8)  # Reduced spacing
        
        # Core Dwell Settings Section - Combined into one compact section
        core_header = create_section_header("Core Dwell Settings", 
                                           "Essential settings that control how dwell clicking works")
        layout.addWidget(core_header)
        
        # Create a single frame for all dwell settings
        dwell_settings_frame = QFrame()
        dwell_settings_layout = QVBoxLayout(dwell_settings_frame)
        dwell_settings_layout.setContentsMargins(10, 8, 10, 8)
        dwell_settings_layout.setSpacing(12)
        
        # Add both settings to the same frame
        self.create_move_limit_section(dwell_settings_layout)
        self.create_dwell_time_section(dwell_settings_layout)
        
        layout.addWidget(dwell_settings_frame)
        
        # Add minimal stretch to push content to the top
        layout.addStretch(1)
        
        return tab
    
    def create_move_limit_section(self, layout):
        """Create move limit adjustment section."""
        # Label and controls in a more compact layout
        move_frame = QFrame()
        move_layout = QHBoxLayout(move_frame)
        move_layout.setContentsMargins(0, 0, 0, 0)
        move_layout.setSpacing(8)
        
        # Label
        move_label = QLabel("Move Limit (px):")
        move_label.setStyleSheet(get_small_label_style())
        move_label.setFixedWidth(100)
        move_layout.addWidget(move_label)
        
        # Minus button
        move_minus_btn = create_adjustment_button("◀")
        move_minus_btn.setToolTip("Decrease movement limit")
        move_minus_btn.setAccessibleName("Decrease Movement Limit")
        move_minus_btn.setAccessibleDescription("Click to decrease the movement limit by 1 pixel")
        move_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_move()
        move_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_move()
        move_layout.addWidget(move_minus_btn)
        
        # Slider
        self.dialog.move_limit_slider = QSlider(Qt.Orientation.Horizontal)
        self.dialog.move_limit_slider.setRange(3, 20)
        self.dialog.move_limit_slider.setValue(self.settings_manager.get_setting('move_limit', 5))
        self.dialog.move_limit_slider.setStyleSheet(get_slider_style())
        self.dialog.move_limit_slider.setToolTip("Adjust the maximum distance (in pixels) the cursor can move while dwelling")
        self.dialog.move_limit_slider.setAccessibleName("Movement Limit Slider")
        self.dialog.move_limit_slider.setAccessibleDescription("Controls how much the cursor can move while dwelling")
        move_layout.addWidget(self.dialog.move_limit_slider)
        
        # Plus button
        move_plus_btn = create_adjustment_button("▶")
        move_plus_btn.setToolTip("Increase movement limit")
        move_plus_btn.setAccessibleName("Increase Movement Limit")
        move_plus_btn.setAccessibleDescription("Click to increase the movement limit by 1 pixel")
        move_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_move()
        move_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_move()
        move_layout.addWidget(move_plus_btn)
        
        # Value label
        self.dialog.move_limit_label = QLabel(str(self.settings_manager.get_setting('move_limit', 5)))
        self.dialog.move_limit_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
            font-weight: bold;
            min-width: 25px;
            background: rgba(0, 120, 215, 0.1);
            border: 1px solid rgba(0, 120, 215, 0.3);
            border-radius: 3px;
            padding: 2px 4px;
        """)
        self.dialog.move_limit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        move_layout.addWidget(self.dialog.move_limit_label)
        
        layout.addWidget(move_frame)
    
    def create_dwell_time_section(self, layout):
        """Create dwell time adjustment section."""
        # Label and controls in a more compact layout
        time_frame = QFrame()
        time_layout = QHBoxLayout(time_frame)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(8)
        
        # Label
        time_label = QLabel("Dwell Time (s):")
        time_label.setStyleSheet(get_small_label_style())
        time_label.setFixedWidth(100)
        time_layout.addWidget(time_label)
        
        # Minus button
        time_minus_btn = create_adjustment_button("◀")
        time_minus_btn.setToolTip("Decrease dwell time")
        time_minus_btn.setAccessibleName("Decrease Dwell Time")
        time_minus_btn.setAccessibleDescription("Click to decrease the dwell time by 1 second")
        time_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_time()
        time_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_time()
        time_layout.addWidget(time_minus_btn)
        
        # Slider
        self.dialog.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.dialog.time_slider.setRange(1, 20)
        self.dialog.time_slider.setValue(int(self.settings_manager.get_setting('dwell_time', 1.0) * 10))
        self.dialog.time_slider.setStyleSheet(get_slider_style())
        self.dialog.time_slider.setToolTip("Adjust the minimum time (in seconds) you must hold your cursor still")
        self.dialog.time_slider.setAccessibleName("Dwell Time Slider")
        self.dialog.time_slider.setAccessibleDescription("Controls how long you must hold your cursor still")
        time_layout.addWidget(self.dialog.time_slider)
        
        # Plus button
        time_plus_btn = create_adjustment_button("▶")
        time_plus_btn.setToolTip("Increase dwell time")
        time_plus_btn.setAccessibleName("Increase Dwell Time")
        time_plus_btn.setAccessibleDescription("Click to increase the dwell time by 1 second")
        time_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_time()
        time_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_time()
        time_layout.addWidget(time_plus_btn)
        
        # Value label
        self.dialog.time_label = QLabel(format_time_display(self.settings_manager.get_setting('dwell_time', 1.0)))
        self.dialog.time_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
            font-weight: bold;
            min-width: 25px;
            background: rgba(0, 120, 215, 0.1);
            border: 1px solid rgba(0, 120, 215, 0.3);
            border-radius: 3px;
            padding: 2px 4px;
        """)
        self.dialog.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_layout.addWidget(self.dialog.time_label)
        
        layout.addWidget(time_frame) 