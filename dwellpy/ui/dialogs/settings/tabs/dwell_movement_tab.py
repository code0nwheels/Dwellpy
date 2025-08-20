"""Dwell Movement tab for settings dialog."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSlider
from PyQt6.QtCore import Qt

try:
    from ....config.constants import Colors
except ImportError:
    class Colors:
        TEXT_COLOR = "#ffffff"

from ..components.ui_components import create_section_header, create_adjustment_button, get_slider_style, format_time_display


class DwellMovementTab:
    """Dwell Movement tab creation and management."""
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.settings_manager = dialog.settings_manager
        self.event_handlers = dialog.event_handlers
    
    def create_tab(self):
        """Create dwell movement tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Movement Detection Section
        movement_header = create_section_header("Movement Detection", 
                                               "How much your cursor can move while still counting as 'dwelling' in one spot")
        layout.addWidget(movement_header)
        
        self.create_move_limit_section(layout)
        
        # Timing Section  
        timing_header = create_section_header("Dwell Timing",
                                             "How long you must hold your cursor still before a click happens")
        layout.addWidget(timing_header)
        
        self.create_dwell_time_section(layout)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        return tab
    
    def create_move_limit_section(self, layout):
        """Create move limit adjustment section."""
        # Label
        move_label = QLabel("Move Limit (px):")
        move_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        layout.addWidget(move_label)
        
        # Controls frame
        move_frame = QFrame()
        move_layout = QHBoxLayout(move_frame)
        move_layout.setContentsMargins(0, 0, 0, 0)
        move_layout.setSpacing(5)
        
        # Minus button
        move_minus_btn = create_adjustment_button("◀")
        move_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_move()
        move_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_move()
        move_layout.addWidget(move_minus_btn)
        
        # Slider
        self.dialog.move_limit_slider = QSlider(Qt.Orientation.Horizontal)
        self.dialog.move_limit_slider.setRange(3, 20)
        self.dialog.move_limit_slider.setValue(self.settings_manager.get_setting('move_limit', 5))
        self.dialog.move_limit_slider.setStyleSheet(get_slider_style())
        move_layout.addWidget(self.dialog.move_limit_slider)
        
        # Plus button
        move_plus_btn = create_adjustment_button("▶")
        move_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_move()
        move_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_move()
        move_layout.addWidget(move_plus_btn)
        
        # Value label
        self.dialog.move_limit_label = QLabel(str(self.settings_manager.get_setting('move_limit', 5)))
        self.dialog.move_limit_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
        """)
        self.dialog.move_limit_label.setFixedWidth(30)
        move_layout.addWidget(self.dialog.move_limit_label)
        
        layout.addWidget(move_frame)
    
    def create_dwell_time_section(self, layout):
        """Create dwell time adjustment section."""
        # Label
        time_label = QLabel("Dwell Time (s):")
        time_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        layout.addWidget(time_label)
        
        # Controls frame
        time_frame = QFrame()
        time_layout = QHBoxLayout(time_frame)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(5)
        
        # Minus button
        time_minus_btn = create_adjustment_button("◀")
        time_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_time()
        time_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_time()
        time_layout.addWidget(time_minus_btn)
        
        # Slider
        self.dialog.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.dialog.time_slider.setRange(1, 20)
        self.dialog.time_slider.setValue(int(self.settings_manager.get_setting('dwell_time', 1.0) * 10))
        self.dialog.time_slider.setStyleSheet(get_slider_style())
        time_layout.addWidget(self.dialog.time_slider)
        
        # Plus button
        time_plus_btn = create_adjustment_button("▶")
        time_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_time()
        time_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_time()
        time_layout.addWidget(time_plus_btn)
        
        # Value label
        self.dialog.time_label = QLabel(format_time_display(self.settings_manager.get_setting('dwell_time', 1.0)))
        self.dialog.time_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
        """)
        self.dialog.time_label.setFixedWidth(30)
        time_layout.addWidget(self.dialog.time_label)
        
        layout.addWidget(time_frame) 