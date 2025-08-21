"""Event handlers for settings dialog."""

from PyQt6.QtWidgets import QColorDialog
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QPushButton


class SettingsEventHandlers:
    """Event handlers for settings dialog interactions."""
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.settings_manager = dialog.settings_manager
        self.button_manager = dialog.button_manager
        
        # Hover timer management
        self.hover_timer = QTimer()
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.process_hover_action)
        
        self.repeat_timer = QTimer()
        self.repeat_timer.timeout.connect(self.process_repeat_action)
        
        self.current_hover_action = None
        self.current_hover_direction = None
        self.hover_delay = 300
        self.repeat_interval = 100
    
    def process_hover_action(self):
        """Process the hover action after the initial delay."""
        if not self.current_hover_action or not self.current_hover_direction:
            return
            
        self.perform_action(self.current_hover_action, self.current_hover_direction)
        self.repeat_timer.start(self.repeat_interval)
    
    def process_repeat_action(self):
        """Process the repeated hover action."""
        if not self.current_hover_action or not self.current_hover_direction:
            self.repeat_timer.stop()
            return
            
        self.perform_action(self.current_hover_action, self.current_hover_direction)
    
    def perform_action(self, action, direction):
        """Perform the specified action in the specified direction."""
        if action == "move_limit":
            if direction == "minus":
                self.dialog.move_limit_slider.setValue(self.dialog.move_limit_slider.value() - 1)
            else:  # plus
                self.dialog.move_limit_slider.setValue(self.dialog.move_limit_slider.value() + 1)
        elif action == "dwell_time":
            if direction == "minus":
                self.dialog.time_slider.setValue(self.dialog.time_slider.value() - 1)
            else:  # plus
                self.dialog.time_slider.setValue(self.dialog.time_slider.value() + 1)
        elif action == "transparency":
            if direction == "minus":
                self.dialog.transparency_slider.setValue(self.dialog.transparency_slider.value() - 1)
            else:  # plus
                self.dialog.transparency_slider.setValue(self.dialog.transparency_slider.value() + 1)
        elif action == "scroll_speed":
            if direction == "minus":
                self.dialog.scroll_speed_slider.setValue(self.dialog.scroll_speed_slider.value() - 1)
            else:  # plus
                self.dialog.scroll_speed_slider.setValue(self.dialog.scroll_speed_slider.value() + 1)
        elif action == "widget_delay":
            if direction == "minus":
                self.dialog.widget_delay_slider.setValue(self.dialog.widget_delay_slider.value() - 1)
            else:  # plus
                self.dialog.widget_delay_slider.setValue(self.dialog.widget_delay_slider.value() + 1)
        elif action == "unlock_threshold":
            if direction == "minus":
                self.dialog.unlock_threshold_slider.setValue(self.dialog.unlock_threshold_slider.value() - 1)
            else:  # plus
                self.dialog.unlock_threshold_slider.setValue(self.dialog.unlock_threshold_slider.value() + 1)
        elif action == "menu_size":
            if direction == "minus":
                self.dialog.menu_size_slider.setValue(self.dialog.menu_size_slider.value() - 1)
            else:  # plus
                self.dialog.menu_size_slider.setValue(self.dialog.menu_size_slider.value() + 1)
    
    def set_hover_action(self, action, direction):
        """Set the current hover action and start the hover timer."""
        self.current_hover_action = action
        self.current_hover_direction = direction
        self.hover_timer.start(self.hover_delay)
    
    def clear_hover_action(self, action=None):
        """Clear the current hover action and stop timers."""
        if action is None or action == self.current_hover_action:
            self.hover_timer.stop()
            self.repeat_timer.stop()
            self.current_hover_action = None
            self.current_hover_direction = None
    
    # Value update handlers
    def update_move_limit_value(self, value):
        """Update move limit value display."""
        self.dialog.move_limit_label.setText(f"{value}px")
    
    def update_time_value(self, value):
        """Update dwell time value display."""
        from .ui_components import format_time_display
        self.dialog.time_label.setText(f"{format_time_display(value)}s")
    
    def update_transparency_value(self, value):
        """Update transparency value display."""
        self.dialog.transparency_label.setText(f"{value}%")
    
    def update_scroll_speed_value(self, value):
        """Update scroll speed value display."""
        self.dialog.scroll_speed_label.setText(f"{value}%")
    
    def update_widget_delay_value(self, value):
        """Update widget delay value display."""
        from .ui_components import format_time_display
        self.dialog.widget_delay_label.setText(f"{format_time_display(value)}s")
    
    def update_unlock_threshold_value(self, value):
        """Update unlock threshold value display."""
        self.dialog.unlock_threshold_label.setText(f"{value}px")
    
    def update_unlock_threshold_setting(self, value):
        """Update unlock threshold setting in real-time."""
        self.settings_manager.set_setting('widget_unlock_threshold', value)
    
    def update_menu_size_value(self, value):
        """Update menu size value display."""
        self.dialog.menu_size_label.setText(f"{value}px")
    
    # Toggle handlers
    def on_transparency_toggle(self, state):
        """Handle transparency toggle."""
        self.dialog.transparency_slider.setEnabled(state)
        self.dialog.transparency_label.setEnabled(state)
    
    def on_scroll_toggle(self, checked):
        """Handle scroll widget toggle."""
        # Enable/disable scroll-specific controls
        self.dialog.scroll_speed_slider.setEnabled(checked)
        self.dialog.scroll_speed_label.setEnabled(checked)
        
        # Find and enable/disable scroll speed minus/plus buttons
        for child in self.dialog.findChildren(QPushButton):
            if hasattr(child, 'toolTip') and child.toolTip() in ["Decrease scroll speed", "Increase scroll speed"]:
                child.setEnabled(checked)
    
    def on_menu_toggle(self, checked):
        """Handle menu widget toggle."""
        # Enable/disable menu-specific controls
        self.dialog.menu_size_slider.setEnabled(checked)
        self.dialog.menu_size_label.setEnabled(checked)
        
        # Find and enable/disable menu size minus/plus buttons
        for child in self.dialog.findChildren(QPushButton):
            if hasattr(child, 'toolTip') and child.toolTip() in ["Decrease icon size", "Increase icon size"]:
                child.setEnabled(checked)
    
    def on_visible_clicks_toggle(self, state):
        """Handle visible clicks toggle."""
        # Enable/disable color buttons
        for button in [self.dialog.left_click_color_button, 
                      self.dialog.right_click_color_button, 
                      self.dialog.double_click_color_button]:
            button.setEnabled(state)
    
    def on_active_toggle(self, state):
        """Handle active state toggle."""
        self.dialog.unlock_threshold_slider.setEnabled(state)
        self.dialog.unlock_threshold_label.setEnabled(state)
    
    def on_contract_ui_toggle(self, state):
        """Handle UI contraction toggle."""
        # Enable/disable expansion direction dropdown
        self.dialog.expansion_direction_combo.setEnabled(state)
    
    def on_expansion_direction_changed(self, index):
        """Handle expansion direction dropdown change."""
        direction = self.dialog.expansion_direction_combo.itemData(index)
        self.settings_manager.set_setting('expansion_direction', direction)
    
    def on_auto_start_toggle(self, state):
        """Handle auto-start toggle."""
        # This would typically involve system-level changes
        # For now, just update the setting
        self.settings_manager.set_setting('auto_start', state)
    
    # Hover event handlers for adjustment buttons
    def on_enter_minus_move(self):
        self.set_hover_action("move_limit", "minus")
    
    def on_leave_minus_move(self):
        self.clear_hover_action("move_limit")
    
    def on_enter_plus_move(self):
        self.set_hover_action("move_limit", "plus")
    
    def on_leave_plus_move(self):
        self.clear_hover_action("move_limit")
    
    def on_enter_minus_time(self):
        self.set_hover_action("dwell_time", "minus")
    
    def on_leave_minus_time(self):
        self.clear_hover_action("dwell_time")
    
    def on_enter_plus_time(self):
        self.set_hover_action("dwell_time", "plus")
    
    def on_leave_plus_time(self):
        self.clear_hover_action("dwell_time")
    
    def on_enter_minus_transparency(self):
        self.set_hover_action("transparency", "minus")
    
    def on_leave_minus_transparency(self):
        self.clear_hover_action("transparency")
    
    def on_enter_plus_transparency(self):
        self.set_hover_action("transparency", "plus")
    
    def on_leave_plus_transparency(self):
        self.clear_hover_action("transparency")
    
    def on_enter_minus_scroll_speed(self):
        self.set_hover_action("scroll_speed", "minus")
    
    def on_leave_minus_scroll_speed(self):
        self.clear_hover_action("scroll_speed")
    
    def on_enter_plus_scroll_speed(self):
        self.set_hover_action("scroll_speed", "plus")
    
    def on_leave_plus_scroll_speed(self):
        self.clear_hover_action("scroll_speed")
    
    def on_enter_minus_widget_delay(self):
        self.set_hover_action("widget_delay", "minus")
    
    def on_leave_minus_widget_delay(self):
        self.clear_hover_action("widget_delay")
    
    def on_enter_plus_widget_delay(self):
        self.set_hover_action("widget_delay", "plus")
    
    def on_leave_plus_widget_delay(self):
        self.clear_hover_action("widget_delay")
    
    def on_enter_minus_unlock_threshold(self):
        self.set_hover_action("unlock_threshold", "minus")
    
    def on_leave_minus_unlock_threshold(self):
        self.clear_hover_action("unlock_threshold")
    
    def on_enter_plus_unlock_threshold(self):
        self.set_hover_action("unlock_threshold", "plus")
    
    def on_leave_plus_unlock_threshold(self):
        self.clear_hover_action("unlock_threshold")
    
    def on_enter_minus_menu_size(self):
        self.set_hover_action("menu_size", "minus")
    
    def on_leave_minus_menu_size(self):
        self.clear_hover_action("menu_size")
    
    def on_enter_plus_menu_size(self):
        self.set_hover_action("menu_size", "plus")
    
    def on_leave_plus_menu_size(self):
        self.clear_hover_action("menu_size")
    
    # Color picker functionality
    def open_color_picker(self, click_type, button):
        """Open color picker dialog for click type."""
        from PyQt6.QtGui import QColor
        current_color = self.settings_manager.get_setting(f'{click_type}_click_color')
        color = QColorDialog.getColor(QColor(current_color), self.dialog, f"Select {click_type} click color")
        
        if color.isValid():
            color_hex = color.name()
            self.settings_manager.set_setting(f'{click_type}_click_color', color_hex)
            from .ui_components import update_color_button_style
            update_color_button_style(button, color_hex)
    
    def cleanup_timers(self):
        """Clean up timers when dialog closes."""
        self.hover_timer.stop()
        self.repeat_timer.stop() 