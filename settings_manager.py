import tkinter as tk
import json
import os
import sys

class SettingsManager:
    """
    Manages settings UI and persistence for the Dwell Clicker.
    
    This class handles:
    - Loading and saving settings to disk
    - Generating and managing the settings UI dialog
    - Applying settings to the dwell detector
    """
    
    def __init__(self, root, dwell_detector, button_commander):
        """
        Initialize the settings manager.
        
        Args:
            root: The main Tkinter window
            dwell_detector: The DwellDetector instance to configure
            button_commander: Object tracking button hover events
        """
        self.root = root
        self.dwell_detector = dwell_detector
        self.button_commander = button_commander  # For handling button hover events
        self.setup_window = None  # Track settings window
        
        # Default settings
        self.default_active = False
        self.window_position = (100, 100)
        
        # Load settings
        self.load_settings()
    
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
        
        This method ensures settings are immediately applied to the detector
        with proper conversion between UI values and internal algorithm values.
        """
        try:
            settings_file = self.get_settings_path()
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                if 'window_position' in settings:
                    self.window_position = settings['window_position']
                
                # Handle move_limit (could be stored as radius in older versions)
                if 'move_limit' in settings:
                    self.dwell_detector.move_limit = int(settings['move_limit'])
                    print(f"Applied move_limit: {self.dwell_detector.move_limit}")
                elif 'radius' in settings:
                    self.dwell_detector.move_limit = int(settings['radius'])
                    print(f"Applied radius as move_limit: {self.dwell_detector.move_limit}")
                
                # Handle dwell_time with proper conversion to click_time
                if 'dwell_time' in settings:
                    # Store original value in seconds
                    dwell_time_seconds = float(settings['dwell_time'])
                    self.dwell_detector.dwell_time = dwell_time_seconds
                    
                    # Convert to counter ticks (each tick = 100ms)
                    self.dwell_detector.click_time = int(dwell_time_seconds / 0.1)
                    print(f"Applied dwell_time: {dwell_time_seconds}s (click_time: {self.dwell_detector.click_time})")
                
                # Default active setting
                if 'default_active' in settings:
                    self.default_active = bool(settings['default_active'])
                
                print(f"Settings loaded successfully: {settings}")
            else:
                # Default position near center of screen
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                self.window_position = (screen_width // 2 - 150, screen_height // 2 - 25)
                print("Settings file not found, using defaults")
                
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Set fallback defaults if loading fails
            self.dwell_detector.move_limit = 5
            self.dwell_detector.dwell_time = 1.0
            self.dwell_detector.click_time = 10  # 1.0 seconds / 0.1
            print("Using fallback defaults due to error")
    
    def save_settings(self, window_position=None):
        """
        Save all settings to JSON file.
        
        Args:
            window_position: Optional tuple (x, y) to save as window position,
                             defaults to current window position
        """
        try:
            settings_file = self.get_settings_path()
            
            if window_position is None:
                window_position = (self.root.winfo_x(), self.root.winfo_y())
            
            # Get the dwell time in seconds, either from stored value or calculated
            dwell_time = getattr(self.dwell_detector, 'dwell_time', 
                                 self.dwell_detector.click_time * 0.1)
            
            settings = {
                'window_position': window_position,
                'move_limit': self.dwell_detector.move_limit,
                'dwell_time': dwell_time,
                'default_active': self.default_active
            }
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f)
                
            print(f"Settings saved: {settings}")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def save_window_position(self):
        """Save just the window position."""
        self.save_settings((self.root.winfo_x(), self.root.winfo_y()))
    
    def center_window(self, window):
        """
        Center a window on the screen.
        
        Args:
            window: Tkinter window to center
        """
        window.update_idletasks()
        
        # Get window size
        width = window.winfo_width()
        height = window.winfo_height()
        
        # Get screen size
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Set window position
        window.geometry(f"+{x}+{y}")
    
    def open_setup(self):
        """
        Open the setup dialog if not already open.
        
        Creates and displays a settings window with controls for
        move_limit, dwell_time, and startup state.
        """
        # Check if setup window is already open
        if self.setup_window is not None and self.setup_window.winfo_exists():
            # Bring it to front
            self.setup_window.lift()
            return
        
        # Calculate center position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Pre-define window size with more room for improved UI
        width = 380
        height = 280
        
        # Calculate center position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Create new setup window WITH position
        self.setup_window = tk.Toplevel(self.root)
        self.setup_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configure window after positioning
        self.setup_window.title("Dwell Clicker Setup")
        self.setup_window.resizable(False, False)
        self.setup_window.transient(self.root)
        self.setup_window.attributes('-topmost', True)
        self.setup_window.configure(background='#f0f0f0')  # Light gray background
        
        # Bind close event to clear reference
        self.setup_window.protocol("WM_DELETE_WINDOW", self.on_setup_window_close)
        
        # Main frame with padding
        main_frame = tk.Frame(self.setup_window, padx=25, pady=20, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Settings title with improved typography
        title_label = tk.Label(main_frame, text="Dwell Settings", font=("Segoe UI", 16, "bold"), 
                              bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=(0, 20))
        
        # Movement threshold setting (how far cursor can move while still considering it a dwell)
        move_limit_frame = tk.Frame(main_frame, bg='#f0f0f0')
        move_limit_frame.pack(fill=tk.X, pady=8)
        
        move_limit_label = tk.Label(move_limit_frame, text="Move Limit (px):", anchor=tk.W, 
                             font=("Segoe UI", 10), bg='#f0f0f0', fg='#333333',
                             width=12)
        move_limit_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Get the current move limit from the detector
        move_limit_var = tk.IntVar(value=self.dwell_detector.move_limit)
        
        move_limit_slider = tk.Scale(
            move_limit_frame, 
            from_=3,    # Minimum sensitivity (small movement triggers reset)
            to=20,      # Maximum sensitivity (larger movements allowed while dwelling)
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
        
        # Update value label when slider moves
        def update_move_limit_value(val):
            move_limit_value.config(text=str(int(float(val))))
        
        move_limit_slider.config(command=update_move_limit_value)
        
        # Dwell time setting (how long cursor must stay in place)
        time_frame = tk.Frame(main_frame, bg='#f0f0f0')
        time_frame.pack(fill=tk.X, pady=8)
        
        time_label = tk.Label(time_frame, text="Dwell Time (s):", anchor=tk.W, 
                             font=("Segoe UI", 10), bg='#f0f0f0', fg='#333333',
                             width=12)
        time_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Get dwell time in seconds from the detector
        dwell_time_seconds = getattr(self.dwell_detector, 'dwell_time', 
                                    self.dwell_detector.click_time * 0.1)
        time_var = tk.DoubleVar(value=dwell_time_seconds)
        
        time_slider = tk.Scale(
            time_frame, 
            from_=0.1,   # Minimum dwell time (very fast)
            to=2.0,      # Maximum dwell time (very slow)
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
        
        # Update time value when slider moves
        def update_time_value(val):
            time_value.config(text=f"{float(val):.1f}")
        
        time_slider.config(command=update_time_value)
        
        # Default on state with better styling
        active_frame = tk.Frame(main_frame, bg='#f0f0f0')
        active_frame.pack(fill=tk.X, pady=15)
        
        active_var = tk.BooleanVar(value=self.default_active)
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
        active_check.pack(padx=5)
        
        # Apply button with improved styling
        def apply_settings():
            # Update detector settings from UI values
            self.dwell_detector.move_limit = move_limit_var.get()
            
            # Convert dwell time from seconds (UI) to counter ticks (internal)
            dwell_time_seconds = time_var.get()
            self.dwell_detector.click_time = int(dwell_time_seconds / 0.1)
            
            # Store original time value for UI representation and saving
            self.dwell_detector.dwell_time = dwell_time_seconds
            
            self.default_active = active_var.get()
            
            # Save settings
            self.save_settings()
            
            print(f"Settings applied - Move Limit: {self.dwell_detector.move_limit}, "
                f"Dwell Time: {self.dwell_detector.dwell_time}s, "
                f"Default Active: {self.default_active}")
                
            self.setup_window.destroy()
            self.setup_window = None
        
        apply_frame = tk.Frame(main_frame, bg='#f0f0f0')
        apply_frame.pack(pady=15)
        
        apply_button = tk.Button(
            apply_frame, 
            text="Apply", 
            command=apply_settings, 
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
        apply_button.pack()
        
        # Make button dwell-clickable by adding a hover handler
        apply_button.button_id = "APPLY_SETTINGS"
        
        def on_apply_hover(event):
            self.button_commander.current_hover_button = "APPLY_SETTINGS"
            apply_button.config(bg='#2980b9')
            print("Hovering over Apply button")
            
        def on_apply_leave(event):
            if self.button_commander.current_hover_button == "APPLY_SETTINGS":
                self.button_commander.current_hover_button = None
            apply_button.config(bg='#3498db')
            print("Left Apply button")
            
        apply_button.bind('<Enter>', on_apply_hover)
        apply_button.bind('<Leave>', on_apply_leave)
        
        # Add this button to button commands
        self.button_commander.button_commands["APPLY_SETTINGS"] = apply_settings
        
        # Separator for visual appeal
        separator = tk.Frame(main_frame, height=1, bg='#d0d0d0')
        separator.pack(fill=tk.X, pady=10)
        
        # Version info with subtle styling
        version_label = tk.Label(main_frame, text="Dwell Clicker v1.0", 
                                font=("Segoe UI", 8), bg='#f0f0f0', fg='#999999')
        version_label.pack(side=tk.RIGHT, pady=(5, 0))
        
        # Update initial values
        update_move_limit_value(move_limit_var.get())
        update_time_value(time_var.get())
        
        # First update to calculate geometry
        self.setup_window.update_idletasks()
        
        # Center the window on screen
        self.center_window(self.setup_window)
        
        # Now make the window visible
        self.setup_window.deiconify()
    
    def on_setup_window_close(self):
        """Handle setup window closing."""
        if self.setup_window:
            self.setup_window.destroy()
            self.setup_window = None