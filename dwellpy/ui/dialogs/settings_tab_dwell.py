from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from dwellpy.ui.dialogs.settings_ui_helpers import create_section_header, create_adjustment_button

def create_dwell_tab(self):
    Colors = self.Colors if hasattr(self, 'Colors') else self.settings_manager.Colors
    tab = QWidget()
    layout = QVBoxLayout(tab)
    layout.setContentsMargins(20, 15, 20, 15)
    layout.setSpacing(20)

    # Dwell Detection Section
    dwell_header = create_section_header(
        "Dwell Detection",
        "Configure how Dwellpy detects when you want to click",
        Colors
    )
    layout.addWidget(dwell_header)

    # Move Limit Section
    move_label = QLabel("Movement Limit:")
    move_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
    layout.addWidget(move_label)
    move_desc = QLabel("Maximum distance (in pixels) the cursor can move while dwelling")
    move_desc.setStyleSheet("color: #999999; margin-bottom: 8px;")
    move_desc.setWordWrap(True)
    layout.addWidget(move_desc)
    slider_frame = QFrame()
    slider_layout = QHBoxLayout(slider_frame)
    slider_layout.setContentsMargins(0, 0, 0, 0)
    slider_layout.setSpacing(10)
    minus_button = create_adjustment_button("-", Colors)
    minus_button.enterEvent = lambda event: self.on_enter_minus_move()
    minus_button.leaveEvent = lambda event: self.on_leave_minus_move()
    slider_layout.addWidget(minus_button)
    self.move_limit_slider = self.create_slider()
    self.move_limit_slider.setMinimum(self.MIN_MOVE_LIMIT)
    self.move_limit_slider.setMaximum(self.MAX_MOVE_LIMIT)
    self.move_limit_slider.setValue(self.settings_manager.get_setting('move_limit', 8))
    slider_layout.addWidget(self.move_limit_slider)
    plus_button = create_adjustment_button("+", Colors)
    plus_button.enterEvent = lambda event: self.on_enter_plus_move()
    plus_button.leaveEvent = lambda event: self.on_leave_plus_move()
    slider_layout.addWidget(plus_button)
    self.move_limit_value = QLabel(str(self.move_limit_slider.value()))
    self.move_limit_value.setStyleSheet(f"color: {Colors.TEXT_COLOR}; min-width: 30px;")
    slider_layout.addWidget(self.move_limit_value)
    layout.addWidget(slider_frame)

    # Dwell Time Section
    time_label = QLabel("Dwell Time:")
    time_label.setStyleSheet(f"color: {Colors.TEXT_COLOR};")
    layout.addWidget(time_label)
    time_desc = QLabel("How long to wait (in seconds) before performing a click")
    time_desc.setStyleSheet("color: #999999; margin-bottom: 8px;")
    time_desc.setWordWrap(True)
    layout.addWidget(time_desc)
    slider_frame = QFrame()
    slider_layout = QHBoxLayout(slider_frame)
    slider_layout.setContentsMargins(0, 0, 0, 0)
    slider_layout.setSpacing(10)
    minus_button = create_adjustment_button("-", Colors)
    minus_button.enterEvent = lambda event: self.on_enter_minus_time()
    minus_button.leaveEvent = lambda event: self.on_leave_minus_time()
    slider_layout.addWidget(minus_button)
    self.time_slider = self.create_slider()
    self.time_slider.setMinimum(int(self.MIN_DWELL_TIME * 10))
    self.time_slider.setMaximum(int(self.MAX_DWELL_TIME * 10))
    dwell_time = self.settings_manager.get_setting('dwell_time', 0.5)
    self.time_slider.setValue(int(dwell_time * 10))
    slider_layout.addWidget(self.time_slider)
    plus_button = create_adjustment_button("+", Colors)
    plus_button.enterEvent = lambda event: self.on_enter_plus_time()
    plus_button.leaveEvent = lambda event: self.on_leave_plus_time()
    slider_layout.addWidget(plus_button)
    self.time_value = QLabel(self.format_time_display(dwell_time))
    self.time_value.setStyleSheet(f"color: {Colors.TEXT_COLOR}; min-width: 30px;")
    slider_layout.addWidget(self.time_value)
    layout.addWidget(slider_frame)

    layout.addStretch()
    return tab 