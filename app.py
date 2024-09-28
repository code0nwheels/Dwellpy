# app.py
from pynput.mouse import Controller
from gui import GUI
from monitor import Monitor
from actions import Actions
from settings import Settings
import os

class DwellClickerApp(GUI, Monitor, Actions, Settings):
    def __init__(self, root):
        self.root = root

        self.load_settings()
        self.root.title("")
        self.root.geometry(self.geometry)  # Use the geometry from settings
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.wm_attributes("-topmost", True)  # Always on top

        # Set window background color to match button color
        self.root.config(bg="lightgrey")

        # For transparency on Windows
        if os.name == 'nt':  # Check if OS is Windows
            self.root.wm_attributes('-transparentcolor', 'lightgrey')
        else:  # For Linux
            self.root.wm_attributes('-transparent', True)

        # Initialize variables
        self.is_running = True  # On/Off state
        # self.dwell_time and self.radius are already set from load_settings()
        self.dwell_triggered = False
        self.dragging = False  # Drag state
        self.moving = False    # Move mode state
        self.mouse_controller = Controller()
        self.dwell_start_time = None
        self.default_action = 'left'  # Default Click State (DCS)
        self.current_action = 'left'  # Temporary Click State (TCS)
        self.settings_window = None   # Reference to settings window
        self.move_offset_x = 0
        self.move_offset_y = 0
        self.initial_dwell_position = None

        self.create_styles()
        self.create_widgets()
        self.start_monitoring()

        # Handle window close event to save settings
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
