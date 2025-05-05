import tkinter as tk
import json
import os

class SettingsManager:
    """Manages settings UI and persistence for the Dwell Clicker."""
    
    def __init__(self, root, dwell_detector, button_commander):
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
            script_dir = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(script_dir, "dwell_settings.json")
        except:
            # Fallback to current working directory
            return os.path.join(os.getcwd(), "dwell_settings.json")
    
    def load_settings(self):
        """Load settings from file."""
        try:
            settings_file = self.get_settings_path()
            
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                if 'window_position' in settings:
                    self.window_position = settings['window_position']
                
                if 'radius' in settings:
                    self.dwell_detector.radius = settings['radius']
                
                if 'dwell_time' in settings:
                    self.dwell_detector.dwell_time = settings['dwell_time']
                    
                if 'default_active' in settings:
                    self.default_active = settings['default_active']
                
                print(f"Settings loaded: {settings}")
            else:
                # Default position near center of screen
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                
                self.window_position = (screen_width // 2 - 150, screen_height // 2 - 25)
                
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self, window_position=None):
        """Save all settings to file."""
        try:
            settings_file = self.get_settings_path()
            
            if window_position is None:
                window_position = (self.root.winfo_x(), self.root.winfo_y())
            
            settings = {
                'window_position': window_position,
                'radius': self.dwell_detector.radius,
                'dwell_time': self.dwell_detector.dwell_time,
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
        """Center a window on the screen."""
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
        """Open the setup dialog if not already open."""
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
        
        # Radius setting with improved styling
        radius_frame = tk.Frame(main_frame, bg='#f0f0f0')
        radius_frame.pack(fill=tk.X, pady=8)
        
        radius_label = tk.Label(radius_frame, text="Radius (px):", anchor=tk.W, 
                               font=("Segoe UI", 10), bg='#f0f0f0', fg='#333333',
                               width=12)
        radius_label.pack(side=tk.LEFT, padx=(0, 5))
        
        radius_var = tk.IntVar(value=self.dwell_detector.radius)
        
        radius_slider = tk.Scale(
            radius_frame, 
            from_=3, 
            to=20, 
            variable=radius_var,
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
        radius_slider.pack(side=tk.LEFT, padx=5)
        
        # Value label with better styling
        radius_value = tk.Label(radius_frame, text=str(radius_var.get()), width=3, 
                               font=("Segoe UI", 10, "bold"), bg='#f0f0f0', fg='#333333')
        radius_value.pack(side=tk.LEFT, padx=5)
        
        # Update radius value when slider moves
        def update_radius_value(val):
            radius_value.config(text=str(int(float(val))))
        
        radius_slider.config(command=update_radius_value)
        
        # Dwell time setting with improved styling
        time_frame = tk.Frame(main_frame, bg='#f0f0f0')
        time_frame.pack(fill=tk.X, pady=8)
        
        time_label = tk.Label(time_frame, text="Dwell Time (s):", anchor=tk.W, 
                             font=("Segoe UI", 10), bg='#f0f0f0', fg='#333333',
                             width=12)
        time_label.pack(side=tk.LEFT, padx=(0, 5))
        
        time_var = tk.DoubleVar(value=self.dwell_detector.dwell_time)
        
        time_slider = tk.Scale(
            time_frame, 
            from_=0.1, 
            to=2.0, 
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
        
        # Value label with better styling
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
            self.dwell_detector.radius = radius_var.get()
            self.dwell_detector.dwell_time = time_var.get()
            self.default_active = active_var.get()
            
            # Save settings
            self.save_settings()
            
            print(f"Settings applied - Radius: {self.dwell_detector.radius}, "
                f"Dwell Time: {self.dwell_detector.dwell_time}, "
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
        update_radius_value(radius_var.get())
        update_time_value(time_var.get())
        
        # First update to calculate geometry
        self.setup_window.update_idletasks()
        
        # Center the window on screen
        width = self.setup_window.winfo_width()
        height = self.setup_window.winfo_height()
        
        screen_width = self.setup_window.winfo_screenwidth()
        screen_height = self.setup_window.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.setup_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Now make the window visible
        self.setup_window.deiconify()
    
    def on_setup_window_close(self):
        """Handle setup window closing."""
        if self.setup_window:
            self.setup_window.destroy()
            self.setup_window = None