# settings.py
import configparser
import os
import tkinter as tk
from tkinter import ttk

class Settings:
    def open_settings(self):
        if self.settings_window is not None:
            # Settings window is already open
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.attributes('-topmost', True)
        # remove window decorations
        self.settings_window.overrideredirect(True)

        # Dwell Time Slider
        tk.Label(self.settings_window, text="Dwell Time (0.2 - 2.0 sec):").pack(pady=5)
        self.dwell_time_slider = tk.Scale(
            self.settings_window, from_=0.2, to=2.0, orient='horizontal',
            resolution=0.1, length=200, command=self.update_dwell_time
        )
        self.dwell_time_slider.set(self.dwell_time)
        self.dwell_time_slider.pack(pady=5)

        # Radius Slider
        tk.Label(self.settings_window, text="Radius (2 - 20 px):").pack(pady=5)
        self.radius_slider = tk.Scale(
            self.settings_window, from_=2, to=20, orient='horizontal',
            resolution=1, length=200, command=self.update_radius
        )
        self.radius_slider.set(self.radius)
        self.radius_slider.pack(pady=5)

        # Close Button
        close_button = ttk.Button(self.settings_window, text="Close", command=self.close_settings)
        close_button.pack(pady=10)

        # Center the window on the screen
        self.settings_window.update_idletasks()  # Update window size information
        window_width = self.settings_window.winfo_reqwidth()
        window_height = self.settings_window.winfo_reqheight()
        screen_width = self.settings_window.winfo_screenwidth()
        screen_height = self.settings_window.winfo_screenheight()
        position_right = int(screen_width / 2 - window_width / 2)
        position_down = int(screen_height / 2 - window_height / 2)
        self.settings_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

        # Handle settings window close event
        self.settings_window.protocol("WM_DELETE_WINDOW", self.close_settings)

    def update_dwell_time(self, value):
        self.dwell_time = float(value)
        print(f"Dwell time set to {self.dwell_time} seconds.")

    def update_radius(self, value):
        self.radius = int(value)
        print(f"Radius set to {self.radius} pixels.")

    def close_settings(self):
        self.settings_window.destroy()
        self.save_settings()
        self.settings_window = None

    def load_settings(self):
        config = configparser.ConfigParser()
        if os.path.exists('config.ini'):
            config.read('config.ini')
            self.dwell_time = float(config.get('Settings', 'dwell_time', fallback='0.4'))
            self.radius = int(config.get('Settings', 'radius', fallback='10'))
            self.geometry = config.get('Settings', 'geometry', fallback='+100+100')
            print("Settings loaded.")
        else:
            print("No settings file found. Using default settings.")
            self.geometry = '+100+100'

    def save_settings(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'dwell_time': str(self.dwell_time),
            'radius': str(self.radius),
            'geometry': self.root.wm_geometry()
        }
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        print("Settings saved.")