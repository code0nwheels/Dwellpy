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
        # Initialize core components
        self.detector = DwellDetector(radius=8, dwell_time=0.2)
        self.input_manager = InputManager(sample_rate=0.01)
        self.click_manager = ClickManager()
        
        # Create UI
        self.root = tk.Tk()
        
        # Create shared button commands dictionary
        self.button_commands = {}
        self.current_hover_button = None
        
        # Initialize UI first without managers
        self.ui = DwellClickerUI(self.root, self.click_manager, self.detector, self)
        
        # Initialize managers
        self.settings_manager = SettingsManager(self.root, self.detector, self)
        self.exit_manager = ExitManager(self.root, self.settings_manager, self)
        
        # Connect managers to UI
        self.ui.connect_managers(self.settings_manager, self.exit_manager)
        
        # Register callback for position updates
        self.input_manager.on_position_update = self.on_position_update
        
        self.running = False
    
    def on_position_update(self, position):
        """Handle new mouse position data."""
        # Add position to detector
        self.detector.add_position(position)
        
        # Check for dwell
        is_dwelling, center = self.detector.check_dwell()
        
        # Process dwell event if detected
        if is_dwelling and center:
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