from PyQt6.QtWidgets import QFrame, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QColorDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

# Section header helper

def create_section_header(title, description, Colors):
    header_frame = QFrame()
    header_layout = QVBoxLayout(header_frame)
    header_layout.setContentsMargins(0, 0, 0, 0)
    header_layout.setSpacing(2)
    # Title
    title_label = QLabel(title)
    title_label.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {Colors.BLUE_ACCENT}; qproperty-alignment: 'AlignLeft';")
    header_layout.addWidget(title_label)
    # Description
    desc_label = QLabel(description)
    desc_label.setFont(QFont("Arial", 9))
    desc_label.setStyleSheet("color: #999999; margin-bottom: 8px;")
    desc_label.setWordWrap(True)
    header_layout.addWidget(desc_label)
    # Separator
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.HLine)
    separator.setFrameShadow(QFrame.Shadow.Sunken)
    separator.setStyleSheet(f"background-color: {Colors.BORDER_COLOR};")
    header_layout.addWidget(separator)
    return header_frame

# Adjustment button helper

def create_adjustment_button(text, Colors):
    button = QPushButton(text)
    button.setFixedSize(30, 30)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    font = QFont("Arial", 12)
    font.setBold(True)
    button.setFont(font)
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: {Colors.DARK_BUTTON_BG};
            color: {Colors.TEXT_COLOR};
            border: 1px solid {Colors.BORDER_COLOR};
            border-radius: 15px;
        }}
        QPushButton:hover {{
            background-color: {Colors.BLUE_ACCENT};
            border: 1px solid {Colors.BLUE_ACCENT};
            color: {Colors.TEXT_COLOR};
        }}
    """)
    return button

# Color button helper

def create_color_button(click_type, display_name, default_color, settings_manager, Colors, parent, update_color_button_style):
    current_color = settings_manager.get_setting(f'click_color_{click_type}', default_color)
    color_btn = create_adjustment_button("", Colors)
    color_btn.setFixedSize(40, 30)
    color_btn.setToolTip(display_name)
    update_color_button_style(color_btn, current_color, Colors)
    color_btn.clicked.connect(lambda: open_color_picker(click_type, color_btn, settings_manager, Colors, parent, update_color_button_style))
    return color_btn

def update_color_button_style(button, color_hex, Colors):
    text_color = "#ffffff" if is_light_color(color_hex) else "#000000"
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: {color_hex};
            color: {text_color};
            border: 1px solid {Colors.BORDER_COLOR};
            border-radius: 15px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            border: 2px solid {Colors.TEXT_COLOR};
        }}
    """)

def is_light_color(color_hex):
    color_hex = color_hex.lstrip('#')
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return brightness > 128

def open_color_picker(click_type, button, settings_manager, Colors, parent, update_color_button_style):
    current_color = settings_manager.get_setting(f'click_color_{click_type}', "#00e676")
    color = QColor(current_color)
    new_color = QColorDialog.getColor(color, parent, "Choose Color")
    if new_color.isValid():
        new_color_hex = new_color.name()
        settings_manager.set_setting(f'click_color_{click_type}', new_color_hex)
        update_color_button_style(button, new_color_hex, Colors) 