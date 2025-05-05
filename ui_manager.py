import tkinter as tk
from tkinter import ttk
import pyautogui
import threading
import time

class DwellClickerUI:
    """UI Manager for the Dwell Clicker application with temporary/default modes."""
    
    def __init__(self, root, click_manager, dwell_detector, button_commander):
        self.root = root
        self.click_manager = click_manager
        self.dwell_detector = dwell_detector
        self.button_commander = button_commander
        
        # Create a custom style for taller buttons with better proportions
        self.style = ttk.Style()
        self.style.configure("Tall.TButton", padding=(3, 8))
        
        # These will be set later
        self.settings_manager = None
        self.exit_manager = None
        
        # State variables
        self.is_active = False
        
        # Mode tracking
        self.current_mode = "LEFT"       # Currently active mode
        self.default_mode = "LEFT"       # Mode to return to after temporary use
        self.is_temporary_mode = False   # Flag for temporary mode
        self.last_mode_selection = None  # For tracking double selection
        self.last_selection_time = 0     # For timing double selection
        
        self.drag_state = None  # Can be None, "down", or "up"
        self.move_mode = False  # Track when in window move mode
        self.move_tracking_thread = None  # Thread for move tracking
        self.move_thread_running = False  # Flag to control the move thread
        
        # Track which button is being hovered over
        self.current_hover_button = None
        
        # Store original button frames for color changes
        self.button_frames = {}
        
        # UI setup
        self.setup_ui()
        
        # Button commands dictionary for hover clicks
        self.button_commands = {
            "ON_OFF": self.toggle_active,
            "LEFT": lambda: self.set_mode("LEFT"),
            "DOUBLE": lambda: self.set_mode("DOUBLE"),
            "DRAG": lambda: self.set_mode("DRAG"),
            "RIGHT": lambda: self.set_mode("RIGHT"),
            "MOVE": self.toggle_move_mode,
            # SETUP and EXIT will be set later
        }
        
        # Share the commands with the button commander
        self.button_commander.button_commands = self.button_commands
    
    def connect_managers(self, settings_manager, exit_manager):
        """Connect to the settings and exit managers after initialization."""
        self.settings_manager = settings_manager
        self.exit_manager = exit_manager
        
        # Connect manager commands to buttons
        self.button_commands["SETUP"] = self.settings_manager.open_setup
        self.button_commands["EXIT"] = self.exit_manager.show_exit_dialog
        
        # Apply loaded position
        if hasattr(self.settings_manager, 'window_position'):
            x, y = self.settings_manager.window_position
            self.root.geometry(f"+{x}+{y}")
            
        # Apply default active state if configured
        if self.settings_manager.default_active:
            self.is_active = True
            self.update_button_states()
            print("Starting with active state due to settings")
        
        # Share thread references with exit manager for cleanup
        self.exit_manager.set_move_thread(self.move_tracking_thread, self.move_thread_running)
    
    def setup_ui(self):
        """Set up the main UI components."""
        # Remove title bar
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)  # Always on top
        
        # Create main frame with slightly more padding for height
        self.main_frame = ttk.Frame(self.root, padding=(0, 2))
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create button frame with minimum height
        self.button_frame = ttk.Frame(self.main_frame, height=40)
        self.button_frame.pack(fill=tk.X)
        
        # Create buttons
        self.buttons = {}
        
        # ON/OFF button
        self.buttons["ON_OFF"] = self.create_button(
            "ON/OFF", "green", "ON_OFF"
        )
        
        # Click type buttons
        self.buttons["LEFT"] = self.create_button(
            "LEFT", "lightblue", "LEFT"
        )
        
        self.buttons["DOUBLE"] = self.create_button(
            "DOUBLE", "lightblue", "DOUBLE"
        )
        
        self.buttons["DRAG"] = self.create_button(
            "DRAG", "lightblue", "DRAG"
        )
        
        self.buttons["RIGHT"] = self.create_button(
            "RIGHT", "lightblue", "RIGHT"
        )
        
        # Utility buttons
        self.buttons["SETUP"] = self.create_button(
            "SETUP", "lightgray", "SETUP"
        )
        
        self.buttons["MOVE"] = self.create_button(
            "MOVE", "lightgray", "MOVE"
        )
        
        self.buttons["EXIT"] = self.create_button(
            "EXIT", "salmon", "EXIT"
        )
        
        # Highlight initial mode
        self.update_button_states()
    
    def create_button(self, text, color, button_id):
        """Create a styled button with hover behavior."""
        # Create a frame with the background color
        frame = tk.Frame(self.button_frame, bg=color, bd=1)
        frame.pack(side=tk.LEFT, padx=1, fill=tk.Y)
        
        # Store frame for color changes
        self.button_frames[button_id] = frame
        
        # Create button inside the frame using tk.Button with modern styling
        button = tk.Button(
            frame,
            text=text,
            width=6,
            font=("Segoe UI", 10),
            bg='#3498db' if color == 'lightblue' else color,
            fg='white' if color in ['lightblue', 'green', 'salmon'] else '#333333',
            activebackground='#2980b9' if color == 'lightblue' else color,
            activeforeground='white' if color in ['lightblue', 'green', 'salmon'] else '#333333',
            relief=tk.FLAT,
            padx=2,
            pady=5,
            cursor="hand2"
        )
        button.pack(padx=0, pady=0, fill=tk.BOTH, expand=True)
        
        # Store button_id as an attribute of the button
        button.button_id = button_id
        
        # Bind hover enter event
        def on_hover_enter(event, bid=button_id):
            self.on_button_hover(bid)
        
        # Bind hover leave event
        def on_hover_leave(event, bid=button_id):
            self.on_button_leave(bid)
        
        button.bind('<Enter>', on_hover_enter)
        button.bind('<Leave>', on_hover_leave)
        
        return button
    
    def on_button_hover(self, button_id):
        """Handle when mouse hovers over a button."""
        # Store the current hover button
        self.current_hover_button = button_id
        
        # Don't activate SETUP, MOVE or EXIT buttons when clicker is off
        if not self.is_active and button_id in ["SETUP", "MOVE", "EXIT"]:
            print(f"Button {button_id} disabled when clicker is off")
            return
        
        # Highlight the button visually by making it slightly darker
        if button_id in self.buttons:
            button = self.buttons[button_id]
            current_bg = button.cget("bg")
            
            # Make button appear pressed
            if current_bg == '#3498db':  # Blue button
                button.config(bg='#2980b9')
            elif current_bg == '#e74c3c':  # Red button
                button.config(bg='#c0392b')
            elif current_bg == '#2ecc71':  # Green button
                button.config(bg='#27ae60')
                
        print(f"Hovering over: {button_id}")
    
    def on_button_leave(self, button_id):
        """Handle when mouse leaves a button."""
        # Clear the hover button if it's this one
        if self.current_hover_button == button_id:
            self.current_hover_button = None
        
        # Remove highlight unless it's the selected mode
        if button_id in self.buttons:
            # Instead of using state(), restore the appropriate color based on the button type
            button = self.buttons[button_id]
            
            # Restore appropriate background based on button role and state
            if button_id == "ON_OFF":
                if self.is_active:
                    button.config(bg='#2ecc71')
                else:
                    button.config(bg='#bdc3c7')
            
            elif button_id in ["LEFT", "DOUBLE", "DRAG", "RIGHT"]:
                if button_id == self.current_mode:
                    if self.is_temporary_mode:
                        button.config(bg='#e74c3c')  # Red for temporary
                    else:
                        button.config(bg='#3498db')  # Blue for default
                else:
                    button.config(bg='#f0f0f0')  # Light gray for inactive
            
            elif button_id == "MOVE":
                if self.move_mode:
                    button.config(bg='#9b59b6')
                else:
                    button.config(bg='#bdc3c7')
            
            elif button_id == "SETUP":
                button.config(bg='#bdc3c7' if self.is_active else '#95a5a6')
            
            elif button_id == "EXIT":
                button.config(bg='#e74c3c' if self.is_active else '#95a5a6')

        print(f"Left button: {button_id}")
    
    def update_button_states(self):
        """Update button appearances to show temporary vs default modes."""
        # Reset all click type buttons
        for button_name in ["LEFT", "DOUBLE", "DRAG", "RIGHT"]:
            # Get the button
            button = self.buttons[button_name]
            
            # Set default styling
            if button_name == self.default_mode:
                # Default mode button - blue
                button.config(bg='#3498db', fg='white', activebackground='#2980b9', activeforeground='white')
            else:
                # Non-default modes - light gray
                button.config(bg='#f0f0f0', fg='#333333', activebackground='#e0e0e0', activeforeground='#333333')
        
        # Highlight current mode
        if self.is_temporary_mode:
            # Temporary mode - red
            self.buttons[self.current_mode].config(bg='#e74c3c', fg='white', activebackground='#c0392b', activeforeground='white')
        
        # Update ON/OFF button
        if self.is_active:
            self.buttons["ON_OFF"].config(bg='#2ecc71', fg='white', activebackground='#27ae60', activeforeground='white')
        else:
            self.buttons["ON_OFF"].config(bg='#bdc3c7', fg='#333333', activebackground='#95a5a6', activeforeground='#333333')
        
        # Update MOVE button if in move mode
        if self.move_mode:
            self.buttons["MOVE"].config(bg='#9b59b6', fg='white', activebackground='#8e44ad', activeforeground='white')
        else:
            self.buttons["MOVE"].config(bg='#bdc3c7', fg='#333333', activebackground='#95a5a6', activeforeground='#333333')
            
        # Style SETUP and EXIT buttons
        self.buttons["SETUP"].config(bg='#bdc3c7' if self.is_active else '#95a5a6', 
                                    fg='#333333' if self.is_active else '#555555')
        self.buttons["EXIT"].config(bg='#e74c3c' if self.is_active else '#95a5a6',
                                    fg='white' if self.is_active else '#555555')
    
    def toggle_active(self):
        """Toggle the active state of the dwell clicker."""
        self.is_active = not self.is_active
        self.update_button_states()
        
        if self.is_active:
            print("Dwell Clicker activated")
        else:
            print("Dwell Clicker deactivated")
    
    def set_mode(self, mode):
        """Set click mode with temporary/default behavior."""
        current_time = time.time()
        
        # Check if this is a double selection (same mode within 3 seconds)
        if (mode == self.last_mode_selection and 
                current_time - self.last_selection_time < 3.0):
            # Double selection - set as default mode
            self.default_mode = mode
            self.current_mode = mode
            self.is_temporary_mode = False
            print(f"Mode set to: {mode} (DEFAULT)")
        else:
            # Single selection - set as temporary mode
            self.current_mode = mode
            self.is_temporary_mode = True
            print(f"Mode set to: {mode} (TEMPORARY)")
        
        # Update tracking variables
        self.last_mode_selection = mode
        self.last_selection_time = current_time
        
        # Reset any active drag state
        self.drag_state = None
        
        # Update UI
        self.update_button_states()
    
    def toggle_move_mode(self):
        """Toggle window move mode - make window follow cursor until next click."""
        # Don't allow move mode when clicker is off
        if not self.is_active:
            print("Move mode not available when clicker is off")
            return
            
        self.move_mode = not self.move_mode
        self.update_button_states()
        
        if self.move_mode:
            print("Move mode activated - UI will follow cursor until next click")
            # Start the move tracking thread
            self.move_thread_running = True
            self.move_tracking_thread = threading.Thread(target=self.track_cursor)
            self.move_tracking_thread.daemon = True
            self.move_tracking_thread.start()
            
            # Update reference in exit manager
            if self.exit_manager:
                self.exit_manager.set_move_thread(self.move_tracking_thread, self.move_thread_running)
        else:
            # Stop the move tracking thread
            self.move_thread_running = False
            if self.move_tracking_thread:
                self.move_tracking_thread.join(timeout=1.0)
            print("Move mode deactivated")
            # Save the position
            if self.settings_manager:
                self.settings_manager.save_window_position()
    
    def track_cursor(self):
        """Track cursor position in a separate thread and update window position."""
        while self.move_thread_running:
            try:
                # Get cursor position using pyautogui
                x, y = pyautogui.position()
                
                # Calculate window position
                window_width = self.root.winfo_width()
                window_height = self.root.winfo_height()
                
                # Position window relative to cursor
                win_x = x - window_width // 2
                win_y = y - 30  # Position above cursor
                
                # Update window position in the main thread
                self.root.after(0, lambda x=win_x, y=win_y: self.root.geometry(f"+{x}+{y}"))
                
                # Small sleep to avoid high CPU usage
                time.sleep(0.01)
            except Exception as e:
                print(f"Error tracking cursor: {e}")
                time.sleep(0.1)
    
    def process_dwell_event(self, center):
        """Process a dwell event with temporary mode support."""
        # First check if we're hovering over a UI button and activate it if so
        if self.current_hover_button is not None:
            print(f"Activating button: {self.current_hover_button}")
            
            # Don't activate SETUP, MOVE or EXIT buttons when clicker is off
            if not self.is_active and self.current_hover_button in ["SETUP", "MOVE", "EXIT"]:
                print(f"Button {self.current_hover_button} not available when clicker is off")
                return
                
            # Call the appropriate command for the button
            if self.current_hover_button in self.button_commands:
                self.button_commands[self.current_hover_button]()
                return
        
        # If in move mode, exit move mode when dwell is detected (click)
        if self.move_mode:
            self.move_mode = False
            self.move_thread_running = False
            if self.move_tracking_thread:
                self.move_tracking_thread.join(timeout=1.0)
            self.update_button_states()
            if self.settings_manager:
                self.settings_manager.save_window_position()
            print("Move mode deactivated by dwell")
            return
            
        # Otherwise process normal click modes if active
        if not self.is_active:
            return
        
        print(f"Processing dwell in {self.current_mode} mode")
        
        # Perform the appropriate click action
        if self.current_mode == "LEFT":
            self.click_manager.perform_left_click(center)
        elif self.current_mode == "RIGHT":
            self.click_manager.perform_right_click(center)
        elif self.current_mode == "DOUBLE":
            self.click_manager.perform_double_click(center)
        elif self.current_mode == "DRAG":
            self.handle_drag(center)
            return  # Don't reset temporary mode for drag operations
        
        # If this was a temporary mode, switch back to default
        if self.is_temporary_mode and self.current_mode != "DRAG":
            self.current_mode = self.default_mode
            self.is_temporary_mode = False
            print(f"Returned to default mode: {self.default_mode}")
            self.update_button_states()
    
    def handle_drag(self, center):
        """Handle drag operations that require two dwells."""
        import pyautogui
        
        if self.drag_state is None:
            # First dwell - mouse down
            pyautogui.FAILSAFE = False
            pyautogui.mouseDown()
            pyautogui.FAILSAFE = True
            
            self.drag_state = "down"
            print("Mouse DOWN at", center)
            
        elif self.drag_state == "down":
            # Second dwell - mouse up
            pyautogui.FAILSAFE = False
            pyautogui.mouseUp()
            pyautogui.FAILSAFE = True
            
            self.drag_state = None
            print("Mouse UP at", center)
            
            # After completing drag, switch back to default if temporary
            if self.is_temporary_mode:
                self.current_mode = self.default_mode
                self.is_temporary_mode = False
                print(f"Drag completed, returned to default mode: {self.default_mode}")
        
        self.update_button_states()