"""Settings management for the Dwellpy application."""

import tkinter as tk
import json
import os
import sys
from utils import center_window

class SettingsManager:
    """
    Manages settings UI and persistence for Dwellpy.
    
    This class handles:
    - Loading and saving settings to disk
    - Generating and managing the settings UI dialog
    - Applying settings to the dwell detector
    """
    
    def __init__(self, root, dwell_detector):
        """
        Initialize the settings manager.
        
        Args:
            root: The main Tkinter window
            dwell_detector: The DwellDetector instance to configure
        """
        self.root = root
        self.dwell_detector = dwell_detector
        self.setup_window = None  # Track settings window
        
        # All application settings stored here
        self.settings = {
            'window_position': (100, 100),
            'move_limit': 5,
            'dwell_time': 1.0,
            'default_active': False,
            'default_mode': 'LEFT'
        }
        
        # Load settings
        self.load_settings()
        
        # Apply settings to detector
        self.apply_detector_settings()
    
    def get_setting(self, key, default=None):
        """Get a setting value with a default fallback."""
        return self.settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set a setting value."""
        self.settings[key] = value
    
    def apply_detector_settings(self):
        """Apply settings to the dwell detector."""
        self.dwell_detector.move_limit = self.settings['move_limit']
        dwell_time_seconds = self.settings['dwell_time']
        self.dwell_detector.dwell_time = dwell_time_seconds
        self.dwell_detector.click_time = int(dwell_time_seconds / 0.1)
    
    def get_settings_path(self):
        """Get the path to the settings file."""
        try:
            # Get the base directory (works in both dev and PyInstaller)
            if getattr(sys, 'frozen', False):
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                
            # Create a settings file in the same directory as the executable/script
            return os.path.join(base_dir, "dwell_settings.json")
        except Exception as e:
            print(f"Error determining settings path: {e}")
            return "dwell_settings.json"  # Fallback to current directory
    
    def load_settings(self):
        """
        Load settings from JSON file and apply them to the dwell detector.
        """
        try:
            settings_file = self.get_settings_path()
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                
                # Update our settings dict with loaded values
                for key, value in loaded_settings.items():
                    self.settings[key] = value
                
                print(f"Settings loaded successfully: {self.settings}")
            else:
                # Default position near center of screen
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                self.settings['window_position'] = (screen_width // 2 - 150, screen_height // 2 - 25)
                print("Settings file not found, using defaults")
                
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Set fallback defaults if loading fails
            self.settings['move_limit'] = 5
            self.settings['dwell_time'] = 1.0
            print("Using fallback defaults due to error")
    
    def save_settings(self):
        """Save all settings to JSON file."""
        try:
            settings_file = self.get_settings_path()
            
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f)
                
            print(f"Settings saved: {self.settings}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def open_setup(self, button_manager):
        """
        Open the setup dialog if not already open.
        
        Args:
            button_manager: ButtonManager instance for button hover tracking
        """
        # Check if setup window is already open
        if self.setup_window is not None and self.setup_window.winfo_exists():
            # Bring it to front
            self.setup_window.lift()
            return
        
        # Pre-define window size with more room for improved UI
        width = 380
        height = 280
        
        # Create new setup window
        self.setup_window = tk.Toplevel(self.root)
        self.setup_window.geometry(f"{width}x{height}")
        
        # Configure window
        self.setup_window.title("Dwellpy Setup")
        self.setup_window.resizable(False, False)
        self.setup_window.transient(self.root)
        self.setup_window.attributes('-topmost', True)
        self.setup_window.configure(background='#f0f0f0')  # Light gray background
        
        # Hide window until all elements are added
        self.setup_window.withdraw()
        
        # Bind close event to clear reference
        self.setup_window.protocol("WM_DELETE_WINDOW", self.on_setup_window_close)
        
        # Main frame with padding
        main_frame = tk.Frame(self.setup_window, padx=25, pady=20, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Settings title with improved typography
        title_label = tk.Label(main_frame, text="Dwellpy Settings", font=("Segoe UI", 16, "bold"), 
                              bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=(0, 20))
        
        # Movement threshold setting
        move_limit_frame = tk.Frame(main_frame, bg='#f0f0f0')
        move_limit_frame.pack(fill=tk.X, pady=8)
        
        move_limit_label = tk.Label(move_limit_frame, text="Move Limit (px):", anchor=tk.W, 
                             font=("Segoe UI", 10), bg='#f0f0f0', fg='#333333',
                             width=12)
        move_limit_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Get the current move limit from settings
        move_limit_var = tk.IntVar(value=self.settings['move_limit'])
        
        move_limit_slider = tk.Scale(
            move_limit_frame, 
            from_=3,    # Minimum sensitivity
            to=20,      # Maximum sensitivity
            variable=move_limit_var,
            orient=tk.HORIZONTAL,
            length=180,
            showvalue=0,
            bd=0,
            highlightthickness=0,
            sliderrelief=tk.FLAT,
            bg='#f0f0f0',
            troughcolor='#d0d0d0',
            activebackground='#3498db'
        )
        move_limit_slider.pack(side=tk.LEFT, padx=5)
        
        # Value label to show current setting
        move_limit_value = tk.Label(move_limit_frame, text=str(move_limit_var.get()), width=3, 
                               font=("Segoe UI", 10, "bold"), bg='#f0f0f0', fg='#333333')
        move_limit_value.pack(side=tk.LEFT, padx=5)
        
        # Update value label when slider moves and apply settings immediately
        def update_move_limit_value(val):
            val = int(float(val))
            move_limit_value.config(text=str(val))
            # Apply setting immediately
            self.settings['move_limit'] = val
            self.dwell_detector.move_limit = val
            print(f"Move limit updated to: {val}")
        
        move_limit_slider.config(command=update_move_limit_value)
        
        # Dwell time setting
        time_frame = tk.Frame(main_frame, bg='#f0f0f0')
        time_frame.pack(fill=tk.X, pady=8)
        
        time_label = tk.Label(time_frame, text="Dwell Time (s):", anchor=tk.W, 
                             font=("Segoe UI", 10), bg='#f0f0f0', fg='#333333',
                             width=12)
        time_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Get dwell time from settings
        time_var = tk.DoubleVar(value=self.settings['dwell_time'])
        
        time_slider = tk.Scale(
            time_frame, 
            from_=0.1,   # Minimum dwell time
            to=2.0,      # Maximum dwell time
            resolution=0.1,
            variable=time_var,
            orient=tk.HORIZONTAL,
            length=180,
            showvalue=0,
            bd=0,
            highlightthickness=0,
            sliderrelief=tk.FLAT,
            bg='#f0f0f0',
            troughcolor='#d0d0d0',
            activebackground='#3498db'
        )
        time_slider.pack(side=tk.LEFT, padx=5)
        
        # Value label for dwell time
        time_value = tk.Label(time_frame, text=f"{time_var.get():.1f}", width=3, 
                             font=("Segoe UI", 10, "bold"), bg='#f0f0f0', fg='#333333')
        time_value.pack(side=tk.LEFT, padx=5)
        
        # Update time value when slider moves and apply settings immediately
        def update_time_value(val):
            val = float(val)
            time_value.config(text=f"{val:.1f}")
            # Apply setting immediately
            self.settings['dwell_time'] = val
            self.dwell_detector.dwell_time = val
            self.dwell_detector.click_time = int(val / 0.1)
            print(f"Dwell time updated to: {val}s")
        
        time_slider.config(command=update_time_value)
        
        # Default on state
        active_frame = tk.Frame(main_frame, bg='#f0f0f0')
        active_frame.pack(fill=tk.X, pady=15)
        
        active_var = tk.BooleanVar(value=self.settings['default_active'])
        active_check = tk.Checkbutton(
            active_frame, 
            text="Start active on launch", 
            variable=active_var,
            font=("Segoe UI", 10),
            bg='#f0f0f0',
            fg='#333333',
            activebackground='#f0f0f0',
            selectcolor='#f0f0f0',
            highlightthickness=0
        )
        
        # Add a callback for the checkbutton
        def on_active_toggle():
            is_active = active_var.get()
            self.settings['default_active'] = is_active
            print(f"Default active state updated to: {is_active}")
            
        active_check.config(command=on_active_toggle)
        active_check.pack(padx=5)
        
        # OK button - just closes the dialog and saves settings
        def ok_button_click():
            # Save settings
            self.save_settings()
            print(f"Settings saved")
                
            self.setup_window.destroy()
            self.setup_window = None
        
        ok_frame = tk.Frame(main_frame, bg='#f0f0f0')
        ok_frame.pack(pady=15)
        
        ok_button = tk.Button(
            ok_frame, 
            text="OK", 
            command=ok_button_click, 
            width=12,
            font=("Segoe UI", 10),
            bg='#3498db',
            fg='white',
            activebackground='#2980b9',
            activeforeground='white',
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        ok_button.pack()
        
        # Register OK command
        button_manager.register_command("OK_SETTINGS", ok_button_click)
        
        # Separator for visual appeal
        separator = tk.Frame(main_frame, height=1, bg='#d0d0d0')
        separator.pack(fill=tk.X, pady=10)
        
        # Version info with subtle styling
        version_label = tk.Label(main_frame, text="Dwellpy v1.0", 
                                font=("Segoe UI", 8), bg='#f0f0f0', fg='#999999')
        version_label.pack(side=tk.RIGHT, pady=(5, 0))
        
        # Update initial values
        update_move_limit_value(move_limit_var.get())
        update_time_value(time_var.get())
        
        # Force the window to update and calculate its true size after all widgets are added
        self.setup_window.update_idletasks()
        
        # Center the window on screen
        center_window(self.setup_window)
        
        # Now make the window visible
        self.setup_window.deiconify()
    
    def on_setup_window_close(self):
        """Handle setup window closing."""
        if self.setup_window:
            # Save settings when closing the window
            self.save_settings()
            self.setup_window.destroy()
            self.setup_window = None