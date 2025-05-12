import tkinter as tk
from dwell_algorithm import DwellDetector
from input_manager import InputManager
from click_manager import ClickManager
from settings_manager import SettingsManager
from exit_manager import ExitManager
from ui_manager import DwellClickerUI

class DwellClicker:
    """Main dwell clicker application with UI."""
    
    def __init__(self):
        # Initialize core components with reasonable defaults
        # The dwell detector uses:
        # - move_limit: How many pixels the cursor can move while still considering it "dwelling"
        # - dwell_time: How long (in seconds) the cursor must dwell to trigger an action
        self.detector = DwellDetector(radius=10, dwell_time=0.2)
        
        # The input manager tracks cursor position and sends updates at regular intervals
        self.input_manager = InputManager()
        
        # The click manager handles performing different types of mouse clicks
        self.click_manager = ClickManager()
        
        # Create UI
        self.root = tk.Tk()
        
        # Create shared button commands dictionary
        self.button_commands = {}
        self.current_hover_button = None
        
        # Initialize UI first without managers
        self.ui = DwellClickerUI(self.root, self.click_manager, self.detector, self)
        
        # Force reconnect button commands after UI initialization
        self.button_commands = self.ui.button_commands
        
        # Initialize managers
        self.settings_manager = SettingsManager(self.root, self.detector, self)
        self.exit_manager = ExitManager(self.root, self.settings_manager, self)
        
        # Connect managers to UI
        self.ui.connect_managers(self.settings_manager, self.exit_manager)
        
        # Register callback for position updates
        self.input_manager.on_position_update = self.on_position_update
        
        self.running = False
    
    def on_position_update(self, position):
        """
        Handle new mouse position data at regular intervals.
        
        This method is called by the InputManager every 100ms with the
        current mouse position. It adds the position to the dwell detector
        and processes any dwell events that might be triggered.
        
        Args:
            position: Tuple (x, y) representing cursor position
        """
        # Add position to detector's history
        self.detector.add_position(position)
        
        # Check if a dwell has been detected
        is_dwelling, center = self.detector.check_dwell()
        
        # Process dwell event if detected
        if is_dwelling and center:
            # Let the UI process the dwell event, which might
            # result in clicking, button activation, etc.
            self.ui.process_dwell_event(center)
    
    def start(self):
        """Start the dwell clicker application."""
        print("Starting Dwell Clicker application...")
        
        self.running = True
        self.input_manager.start()
        
        try:
            # Main loop - tkinter will handle events
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nStopping application...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the dwell clicker application."""
        self.running = False
        self.input_manager.stop()
        print("Application stopped.")

if __name__ == "__main__":
    # Create and start the dwell clicker application
    clicker = DwellClicker()
    clicker.start()