"""Scroll Widget tab for settings dialog."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSlider, QCheckBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

try:
    from ....config.constants import Colors
except ImportError:
    class Colors:
        TEXT_COLOR = "#ffffff"

from ..components.ui_components import create_section_header, create_adjustment_button, get_slider_style, get_checkbox_style


class ScrollWidgetTab:
    """Scroll Widget tab creation and management."""
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.settings_manager = dialog.settings_manager
        self.event_handlers = dialog.event_handlers
    
    def create_tab(self):
        """Create scroll widget tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(20)
        
        # Scroll Widget Section
        scroll_header = create_section_header("Scroll Widget",
                                             "A floating scroll widget that appears near your cursor for easy scrolling")
        layout.addWidget(scroll_header)
        
        self.create_scroll_widget_section(layout)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
        return tab
    
    def create_scroll_widget_section(self, layout):
        """Create scroll widget settings section."""
        # Enable checkbox
        scroll_enable_frame = QFrame()
        scroll_enable_layout = QHBoxLayout(scroll_enable_frame)
        scroll_enable_layout.setContentsMargins(0, 0, 0, 0)
        scroll_enable_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.dialog.scroll_check = QCheckBox("Enable scroll widget")
        self.dialog.scroll_check.setChecked(self.settings_manager.get_setting('scroll_enabled', True))
        self.dialog.scroll_check.setStyleSheet(get_checkbox_style())
        scroll_enable_layout.addWidget(self.dialog.scroll_check)
        
        layout.addWidget(scroll_enable_frame)
        
        # Scroll speed label
        scroll_speed_label = QLabel("Scroll Speed:")
        scroll_speed_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        layout.addWidget(scroll_speed_label)
        
        # Controls frame
        scroll_speed_frame = QFrame()
        scroll_speed_layout = QHBoxLayout(scroll_speed_frame)
        scroll_speed_layout.setContentsMargins(0, 0, 0, 0)
        scroll_speed_layout.setSpacing(5)
        
        # Minus button
        scroll_speed_minus_btn = create_adjustment_button("◀")
        scroll_speed_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_scroll_speed()
        scroll_speed_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_scroll_speed()
        scroll_speed_layout.addWidget(scroll_speed_minus_btn)
        
        # Slider (1-10, where 1 is slowest, 10 is fastest)
        self.dialog.scroll_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.dialog.scroll_speed_slider.setRange(1, 10)
        # Convert interval to speed (lower interval = faster speed)
        current_interval = self.settings_manager.get_setting('scroll_speed', 100)
        speed_value = 11 - (current_interval // 20)  # 200ms=1, 180ms=2, ..., 20ms=10
        self.dialog.scroll_speed_slider.setValue(max(1, min(10, speed_value)))
        self.dialog.scroll_speed_slider.setStyleSheet(get_slider_style())
        scroll_speed_layout.addWidget(self.dialog.scroll_speed_slider)
        
        # Plus button
        scroll_speed_plus_btn = create_adjustment_button("▶")
        scroll_speed_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_scroll_speed()
        scroll_speed_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_scroll_speed()
        scroll_speed_layout.addWidget(scroll_speed_plus_btn)
        
        # Value label
        self.dialog.scroll_speed_label = QLabel(str(self.dialog.scroll_speed_slider.value()))
        self.dialog.scroll_speed_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
        """)
        self.dialog.scroll_speed_label.setFixedWidth(30)
        scroll_speed_layout.addWidget(self.dialog.scroll_speed_label)
        
        layout.addWidget(scroll_speed_frame)
        
        # Widget Appearance Delay
        appearance_delay_label = QLabel("Widget Appearance Delay:")
        appearance_delay_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        layout.addWidget(appearance_delay_label)
        
        # Description for widget delay
        delay_desc = QLabel("Time before scroll widget appears")
        delay_desc.setFont(QFont("Arial", 9))
        delay_desc.setStyleSheet("color: #999999; margin-top: 8px;")
        delay_desc.setWordWrap(True)
        layout.addWidget(delay_desc)
        
        # Controls frame
        widget_delay_frame = QFrame()
        widget_delay_layout = QHBoxLayout(widget_delay_frame)
        widget_delay_layout.setContentsMargins(0, 0, 0, 0)
        widget_delay_layout.setSpacing(5)
        
        # Minus button
        widget_delay_minus_btn = create_adjustment_button("◀")
        widget_delay_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_widget_delay()
        widget_delay_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_widget_delay()
        widget_delay_layout.addWidget(widget_delay_minus_btn)
        
        # Slider (1-10, representing 0.1s to 1.0s)
        self.dialog.widget_delay_slider = QSlider(Qt.Orientation.Horizontal)
        self.dialog.widget_delay_slider.setRange(1, 10)
        # Convert current delay (0.1-1.0) to slider value (1-10)
        current_delay = self.settings_manager.get_setting('widget_appearance_delay', 0.2)
        slider_value = int(current_delay * 10)
        self.dialog.widget_delay_slider.setValue(max(1, min(10, slider_value)))
        self.dialog.widget_delay_slider.setStyleSheet(get_slider_style())
        widget_delay_layout.addWidget(self.dialog.widget_delay_slider)
        
        # Plus button
        widget_delay_plus_btn = create_adjustment_button("▶")
        widget_delay_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_widget_delay()
        widget_delay_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_widget_delay()
        widget_delay_layout.addWidget(widget_delay_plus_btn)
        
        # Value label
        delay_seconds = self.dialog.widget_delay_slider.value() / 10.0
        self.dialog.widget_delay_label = QLabel(f"{delay_seconds:.1f}s")
        self.dialog.widget_delay_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
        """)
        self.dialog.widget_delay_label.setFixedWidth(40)
        widget_delay_layout.addWidget(self.dialog.widget_delay_label)
        
        layout.addWidget(widget_delay_frame)
        
        # Widget Unlock Threshold
        unlock_threshold_label = QLabel("Widget Unlock Threshold:")
        unlock_threshold_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
        layout.addWidget(unlock_threshold_label)
        
        # Description
        unlock_desc = QLabel("Distance (in pixels) cursor must move from widget before it starts following again")
        unlock_desc.setFont(QFont("Arial", 9))
        unlock_desc.setStyleSheet(f"color: #999999; margin-bottom: 8px;")
        unlock_desc.setWordWrap(True)
        layout.addWidget(unlock_desc)
        
        # Controls frame
        unlock_threshold_frame = QFrame()
        unlock_threshold_layout = QHBoxLayout(unlock_threshold_frame)
        unlock_threshold_layout.setContentsMargins(0, 0, 0, 0)
        unlock_threshold_layout.setSpacing(5)
        
        # Minus button
        unlock_threshold_minus_btn = create_adjustment_button("◀")
        unlock_threshold_minus_btn.enterEvent = lambda e: self.event_handlers.on_enter_minus_unlock_threshold()
        unlock_threshold_minus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_minus_unlock_threshold()
        unlock_threshold_layout.addWidget(unlock_threshold_minus_btn)
        
        # Slider (10-100 pixels)
        self.dialog.unlock_threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.dialog.unlock_threshold_slider.setRange(10, 100)
        self.dialog.unlock_threshold_slider.setValue(self.settings_manager.get_setting('widget_unlock_threshold', 30))
        self.dialog.unlock_threshold_slider.setStyleSheet(get_slider_style())
        unlock_threshold_layout.addWidget(self.dialog.unlock_threshold_slider)
        
        # Plus button
        unlock_threshold_plus_btn = create_adjustment_button("▶")
        unlock_threshold_plus_btn.enterEvent = lambda e: self.event_handlers.on_enter_plus_unlock_threshold()
        unlock_threshold_plus_btn.leaveEvent = lambda e: self.event_handlers.on_leave_plus_unlock_threshold()
        unlock_threshold_layout.addWidget(unlock_threshold_plus_btn)
        
        # Value label
        self.dialog.unlock_threshold_label = QLabel(f"{self.dialog.unlock_threshold_slider.value()}px")
        self.dialog.unlock_threshold_label.setStyleSheet(f"""
            color: {Colors.TEXT_COLOR};
        """)
        self.dialog.unlock_threshold_label.setFixedWidth(40)
        unlock_threshold_layout.addWidget(self.dialog.unlock_threshold_label)
        
        layout.addWidget(unlock_threshold_frame) 