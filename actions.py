# actions.py
from pynput.mouse import Button

class Actions:
    def set_default_action(self, action):
        self.default_action = action
        self.current_action = action
        self.update_button_styles()

    def set_temporary_action(self, action):
        self.current_action = action
        self.update_button_styles()

    def trigger_action(self):
        if self.is_cursor_over_app():
            # Over application window, perform left click
            self.mouse_controller.click(Button.left, 1)
            print("Left click performed over app window.")
        else:
            # Perform the action based on current_action
            if self.current_action == 'left':
                self.mouse_controller.click(Button.left, 1)
                print("Left click performed.")
            elif self.current_action == 'double':
                self.mouse_controller.click(Button.left, 2)
                print("Double click performed.")
            elif self.current_action == 'right':
                self.mouse_controller.click(Button.right, 1)
                print("Right click performed.")
            elif self.current_action == 'drag':
                if not self.dragging:
                    # Start drag
                    self.mouse_controller.press(Button.left)
                    self.dragging = True
                    print("Drag started.")
                else:
                    # Stop drag
                    self.mouse_controller.release(Button.left)
                    self.dragging = False
                    print("Drag stopped.")
        # Reset current_action to default if it's a TCS and not currently dragging
        if self.current_action != self.default_action:
            if self.current_action != 'drag' or (self.current_action == 'drag' and not self.dragging):
                self.current_action = self.default_action
                self.update_button_styles()
        # Do not reset dwell detection variables here

    def trigger_button_action(self, action_type):
        if action_type == 'move':
            self.toggle_move_mode()
        elif self.current_action == action_type:
            # If the same action is selected twice in a row, set it as default
            self.set_default_action(action_type)
            print(f"{action_type.capitalize()} set as Default Action.")
        else:
            # Set as temporary action
            self.set_temporary_action(action_type)
            print(f"Temporary Action: {action_type.capitalize()}")

    def toggle_move_mode(self):
        if not self.moving:
            # Start move mode
            self.moving = True
            # Calculate offset between cursor and window position
            cursor_x, cursor_y = self.mouse_controller.position
            window_x = self.root.winfo_rootx()
            window_y = self.root.winfo_rooty()
            self.move_offset_x = cursor_x - window_x
            self.move_offset_y = cursor_y - window_y
            self.update_button_styles()
            print("Move mode activated.")
        else:
            # End move mode
            self.moving = False
            self.update_button_styles()
            print("Move mode deactivated.")

    def toggle_running(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.toggle_button.config(text="Turn Off")
            buttons = [button for button in self.buttons if button.action_type != 'toggle']
            for i, button in enumerate(buttons):
                button.grid(row=0, column=i+1, padx=2)
            print("Application turned ON.")
        else:
            self.toggle_button.config(text="Turn On")
            print("Application turned OFF.")
            # Reset variables
            self.dwell_start_time = None
            self.dwell_triggered = False

            buttons = [button for button in self.buttons if button.action_type != 'toggle']
            for button in buttons:
                button.grid_forget()
