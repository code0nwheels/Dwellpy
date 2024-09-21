# gui.py
from tkinter import ttk
import threading

class GUI:
    def create_styles(self):
        # Create styles for buttons
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('DCS.TButton', background='light blue', foreground='black', width=10, height=15)
        self.style.map('DCS.TButton', background=[('active', 'blue')])

        self.style.configure('TCS.TButton', background='light coral', foreground='black', width=10, height=15)
        self.style.map('TCS.TButton', background=[('active', 'red')])

        self.style.configure('MoveOn.TButton', background='yellow', foreground='black', width=10, height=15)
        self.style.map('MoveOn.TButton', background=[('active', 'gold')])

        self.style.configure('Normal.TButton', foreground='black', width=10, height=15)

    def create_widgets(self):
        # Main Frame
        self.main_frame = ttk.Frame(self.root, style='Custom.TFrame')
        self.main_frame.pack(pady=5, padx=5)

        # List to hold all buttons
        self.buttons = []

        # On/Off Button
        self.toggle_button = ttk.Button(self.main_frame, text="Turn Off", command=self.toggle_running)
        self.toggle_button.grid(row=0, column=0, padx=2)
        self.toggle_button.action_type = 'toggle'
        self.buttons.append(self.toggle_button)

        # Click Type Buttons
        self.left_click_button = ttk.Button(self.main_frame, text="Left", command=lambda: self.trigger_button_action('left'))
        self.left_click_button.grid(row=0, column=1, padx=2)
        self.left_click_button.action_type = 'left'
        self.buttons.append(self.left_click_button)

        self.double_click_button = ttk.Button(self.main_frame, text="Double", command=lambda: self.trigger_button_action('double'))
        self.double_click_button.grid(row=0, column=2, padx=2)
        self.double_click_button.action_type = 'double'
        self.buttons.append(self.double_click_button)

        self.right_click_button = ttk.Button(self.main_frame, text="Right", command=lambda: self.trigger_button_action('right'))
        self.right_click_button.grid(row=0, column=3, padx=2)
        self.right_click_button.action_type = 'right'
        self.buttons.append(self.right_click_button)

        self.drag_button = ttk.Button(self.main_frame, text="Drag", command=lambda: self.trigger_button_action('drag'))
        self.drag_button.grid(row=0, column=4, padx=2)
        self.drag_button.action_type = 'drag'
        self.buttons.append(self.drag_button)

        # Settings Button
        self.settings_button = ttk.Button(self.main_frame, text="Settings", command=self.open_settings)
        self.settings_button.grid(row=0, column=5, padx=2)
        self.settings_button.action_type = 'settings'
        self.buttons.append(self.settings_button)

        # Move Button
        self.move_button = ttk.Button(self.main_frame, text="Move", command=self.toggle_move_mode)
        self.move_button.grid(row=0, column=6, padx=2)
        self.move_button.action_type = 'move'
        self.buttons.append(self.move_button)

        # Exit Button
        self.exit_button = ttk.Button(self.main_frame, text="Exit", command=self.confirm_exit)
        self.exit_button.grid(row=0, column=7, padx=2)
        self.exit_button.action_type = 'exit'
        self.buttons.append(self.exit_button)

        # Update button styles initially
        self.update_button_styles()

    def update_button_styles(self):
        # Reset all buttons to normal style
        for button in self.buttons:
            button.configure(style='Normal.TButton')

        # Apply DCS style to default action button
        dcs_button = self.get_button_by_action(self.default_action)
        if dcs_button:
            dcs_button.configure(style='DCS.TButton')

        # Apply TCS style to temporary action button if it's different from DCS
        if self.current_action != self.default_action:
            tcs_button = self.get_button_by_action(self.current_action)
            if tcs_button:
                tcs_button.configure(style='TCS.TButton')

        # If move mode is active, update move button style
        if self.moving:
            self.move_button.configure(style='MoveOn.TButton')

    def get_button_by_action(self, action):
        action_to_button = {
            'left': self.left_click_button,
            'double': self.double_click_button,
            'right': self.right_click_button,
            'drag': self.drag_button,
            'move': self.move_button
        }
        return action_to_button.get(action, None)

    def confirm_exit(self):
        from tkinter import messagebox
        response = messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?")
        if response:
            self.on_closing()

        #threading.Thread(target=show_message_box).start()

    def on_closing(self):
        self.save_settings()
        self.root.destroy()