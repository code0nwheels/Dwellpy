"""UI management for the Dwell Clicker application."""

import tkinter as tk
from tkinter import ttk
import pyautogui
import threading
import time

class DwellClickerUI:
    """UI Manager for the Dwell Clicker application with temporary/default modes."""
    
    def __init__(self, root, click_manager, dwell_detector, button_manager, window_manager):
        self.root = root
        self.click_manager = click_manager
        self.dwell_detector = dwell_detector
        self.button_manager = button_manager
        self.window_manager = window_manager
        
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
        
        # Window dragging handled by WindowManager
        
        # Store original button frames for color changes
        self.button_frames = {}
        
        # UI setup
        self.setup_ui()
        
        # Register button commands
        self.register_button_commands()
    
    def connect_managers(self, settings_manager, exit_manager):
        """Connect to the settings and exit managers after initialization."""
        self.settings_manager = settings_manager
        self.exit_manager = exit_manager
        
        # Apply default active state if configured
        if self.settings_manager.get_setting('default_active', False):
            self.is_active = True
            self.update_button_states()
            print("Starting with active state due to settings")
    
    def register_button_commands(self):
        """Register button commands with the button manager."""
        # Register basic button commands
        self.button_manager.register_command("ON_OFF", self.toggle_active)
        self.button_manager.register_command("LEFT", lambda: self.set_mode("LEFT"))
        self.button_manager.register_command("DOUBLE", lambda: self.set_mode("DOUBLE"))
        self.button_manager.register_command("DRAG", lambda: self.set_mode("DRAG"))
        self.button_manager.register_command("RIGHT", lambda: self.set_mode("RIGHT"))
        # SETUP and EXIT will be set by the respective managers
    
    def setup_ui(self):
        """Set up the main UI components."""
        # Remove title bar
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)  # Always on top
        
        # Add this code to periodically lift the window to the top
        def keep_on_top():
            self.root.lift()
            self.root.attributes('-topmost', True)
            # Schedule the function to run again after 100ms
            self.root.after(100, keep_on_top)
        
        # Start the keep_on_top loop
        keep_on_top()
        
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
        # Create a frame with the background color and fixed pixel dimensions
        frame = tk.Frame(self.button_frame, bg=color, bd=1, width=45, height=50)
        frame.pack(side=tk.LEFT, padx=1, fill=tk.Y)
        frame.pack_propagate(False)  # Force frame to keep specified dimensions
        
        # Store frame for color changes
        self.button_frames[button_id] = frame
        
        # Create button inside the frame using tk.Button with modern styling
        button = tk.Button(
            frame,
            text=text,
            font=("Segoe UI", 10),  # Smaller font to fit in tiny button
            bg='#3498db' if color == 'lightblue' else color,
            fg='white' if color in ['lightblue', 'green', 'salmon'] else '#333333',
            activebackground='#2980b9' if color == 'lightblue' else color,
            activeforeground='white' if color in ['lightblue', 'green', 'salmon'] else '#333333',
            relief=tk.FLAT,
            padx=0,
            pady=0
        )
        
        # Add command for all buttons except MOVE
        if button_id != "MOVE":
            # Only allow certain buttons when clicker is off
            button.config(command=lambda b=button_id: self.on_button_click(b))
        else:
            # Special handling for MOVE button - bind to window manager
            button.bind("<ButtonPress-1>", self.window_manager.start_drag)
        
        # Fill the entire frame
        button.pack(fill=tk.BOTH, expand=True)
        
        # Store button_id as an attribute of the button
        button.button_id = button_id
        
        # Add hover event bindings for all buttons
        button.bind("<Enter>", lambda event, b=button_id: self.on_button_hover(b))
        button.bind("<Leave>", lambda event, b=button_id: self.on_button_leave(b))
        
        return button
    
    def on_button_click(self, button_id):
        """Handle physical clicks on buttons."""
        # For ON/OFF button, always allow regardless of active state
        if button_id == "ON_OFF":
            self.toggle_active()
            return
            
        # Don't allow other buttons if clicker is off
        if not self.is_active and button_id not in ["ON_OFF"]:
            print(f"Button {button_id} disabled when clicker is off")
            return
            
        # Execute the appropriate command via button manager
        self.button_manager.execute_command(button_id)

    def on_button_hover(self, button_id):
        """Handle when mouse hovers over a button - visual feedback only."""
        # Store the current hover button in button manager
        self.button_manager.set_hover(button_id)
        
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
            elif button_id == "ON_OFF" and current_bg == '#bdc3c7':  # OFF state
                button.config(bg='#95a5a6')  # Darker gray when hovering
    
    def on_button_leave(self, button_id):
        """Handle when mouse leaves a button - visual feedback only."""
        # Clear the hover button in the button manager
        self.button_manager.clear_hover(button_id)
        
        # Don't clear MOVE button hover status while dragging
        if button_id == "MOVE" and self.window_manager.is_dragging:
            return
            
        # Remove highlight unless it's the selected mode
        if button_id in self.buttons:
            button = self.buttons[button_id]
            
            # Restore the appropriate background based on button role and state
            if button_id == "ON_OFF":
                # ON/OFF button
                button.config(bg='#2ecc71' if self.is_active else '#bdc3c7')
            
            elif button_id in ["LEFT", "DOUBLE", "DRAG", "RIGHT", "MOVE"]:
                # Mode buttons - need to check if permanent or temporary
                if button_id == self.current_mode:
                    if self.is_temporary_mode:
                        # Temporary current mode - red
                        button.config(bg='#e74c3c')
                    else:
                        # Permanent current mode - blue
                        button.config(bg='#3498db')
                elif button_id == self.default_mode:
                    # Default mode (but not current) - blue
                    button.config(bg='#3498db')
                else:
                    # Inactive mode - light gray
                    button.config(bg='#f0f0f0')
            
            elif button_id == "SETUP":
                # Setup button
                button.config(bg='#bdc3c7' if self.is_active else '#95a5a6')
            
            elif button_id == "EXIT":
                # Exit button
                button.config(bg='#e74c3c' if self.is_active else '#95a5a6')
    
    def update_button_states(self):
        """Update button appearances to show temporary vs default modes."""
        # Reset all click type buttons
        for button_name in ["LEFT", "DOUBLE", "DRAG", "RIGHT", "MOVE"]:
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
        """
        Set click mode with improved temporary/default behavior.
        
        Logic:
        - If selecting a different mode than current, it becomes temporary (red)
        - If selecting a temporary mode again, it becomes permanent (blue)
        - If selecting a permanent mode again, it stays permanent (no change)
        """
        current_time = time.time()
        
        # If selecting the current mode...
        if mode == self.current_mode:
            # If it's already permanent, do nothing (keep it permanent)
            if not self.is_temporary_mode:
                print(f"Mode {mode} is already the permanent default - ignoring")
                return
                
            # If it's temporary, make it permanent
            if self.is_temporary_mode:
                self.default_mode = mode
                self.is_temporary_mode = False
                print(f"Mode set to: {mode} (DEFAULT/PERMANENT)")
        else:
            # Selecting a different mode - make it temporary
            self.current_mode = mode
            self.is_temporary_mode = True
            print(f"Mode set to: {mode} (TEMPORARY)")
        
        # Update tracking variables
        self.last_mode_selection = mode
        self.last_selection_time = current_time
        
        # Reset any active drag state
        self.drag_state = None
        
        # Update UI to reflect new state
        self.update_button_states()
    
    def process_dwell_event(self, center):
        """
        Process a dwell event with selective button handling.
        
        Implements the following rules:
        1. When active (ON/OFF=on), override current click method with left click on all buttons except MOVE
        2. When deactivated, only the ON/OFF button responds to dwell
        """
        # Get current hover button from button manager
        current_hover = self.button_manager.get_current_hover()
        
        # Check if we're hovering over a button
        if current_hover is not None:
            button_id = current_hover
            print(f"Dwell detected on button: {button_id}")
            
            # Always allow ON/OFF button to be toggled regardless of active state
            if button_id == "ON_OFF":
                print("Toggling ON/OFF via dwell")
                self.toggle_active()
                return
                
            # For all other buttons (except MOVE), only act if clicker is active
            if self.is_active and button_id != "MOVE":
                # Execute the command via button manager
                self.button_manager.execute_command(button_id)
                # Don't reset mode for UI button clicks
                return
            
            # If clicker is inactive, don't process other buttons
            if not self.is_active:
                print(f"Button {button_id} ignored - clicker not active")
                return
        
        # No button detected or button handling complete, process normal dwell clicks
        # Only process if clicker is active
        if not self.is_active:
            return
        
        #print(f"Processing dwell in {self.current_mode} mode")
        
        # Handle DRAG mode
        if self.current_mode == "DRAG":
            self.handle_drag(center)
            return  # Don't reset temporary mode for drag operations
        
        # Perform the appropriate click action for other modes
        if self.current_mode == "LEFT":
            self.click_manager.perform_left_click(center)
        elif self.current_mode == "RIGHT":
            self.click_manager.perform_right_click(center)
        elif self.current_mode == "DOUBLE":
            self.click_manager.perform_double_click(center)
        
        # If this was a temporary mode, switch back to default
        if self.is_temporary_mode:
            self.current_mode = self.default_mode
            self.is_temporary_mode = False
            print(f"Returned to default mode: {self.default_mode}")
            self.update_button_states()
    
    def handle_drag(self, center):
        """Handle drag operations that require two dwells."""
        
        # Regular drag operation for mouse
        if self.drag_state is None:
            # First dwell - mouse down
            success = self.click_manager.mouse_down()
            
            if success:
                self.drag_state = "down"
                print("Mouse DOWN at", center)
        
        elif self.drag_state == "down":
            # Second dwell - mouse up
            success = self.click_manager.mouse_up()
            
            if success:
                self.drag_state = None
                print("Mouse UP at", center)
                
                # After completing drag, switch back to default if temporary
                if self.is_temporary_mode:
                    self.current_mode = self.default_mode
                    self.is_temporary_mode = False
                    print(f"Drag completed, returned to default mode: {self.default_mode}")
        
        self.update_button_states()
