"""Button management for the Dwell Clicker application."""

class ButtonManager:
    """
    Manages button commands and hover state tracking.
    This centralizes button interaction logic.
    """
    
    def __init__(self):
        # Dictionary of button commands: button_id -> function
        self.button_commands = {}
        
        # Track which button is being hovered over
        self.current_hover_button = None
        
        # Buttons that should only respond to physical clicks, not dwell clicks
        self.physical_click_only_buttons = ["EXIT_YES", "EXIT_NO"]
    
    def register_command(self, button_id, command):
        """Register a command for a button."""
        self.button_commands[button_id] = command
    
    def execute_command(self, button_id):
        """Execute the command for a button if available."""
        if button_id in self.button_commands:
            print(f"Executing command for button: {button_id}")
            self.button_commands[button_id]()
            return True
        return False
    
    def set_hover(self, button_id):
        """Set the current hover button."""
        # Don't track hover for buttons that should only respond to physical clicks
        if button_id not in self.physical_click_only_buttons:
            self.current_hover_button = button_id
            print(f"Hovering over: {button_id}")
        else:
            print(f"Hovering over physical-click-only button: {button_id}")
    
    def clear_hover(self, button_id=None):
        """Clear hover state if it matches the given button_id or if none given."""
        if button_id is None or self.current_hover_button == button_id:
            self.current_hover_button = None
    
    def get_current_hover(self):
        """Get the ID of the currently hovered button."""
        return self.current_hover_button
    
    def mark_as_physical_click_only(self, button_ids):
        """Mark buttons that should only respond to physical clicks, not dwells."""
        if isinstance(button_ids, list):
            self.physical_click_only_buttons.extend(button_ids)
        else:
            self.physical_click_only_buttons.append(button_ids)
