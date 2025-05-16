import tkinter as tk
from dwell_algorithm import DwellDetector
from input_manager import InputManager
from click_manager import ClickManager
from settings_manager import SettingsManager
from exit_manager import ExitManager
from ui_manager import DwellClickerUI
from button_manager import ButtonManager
from window_manager import WindowManager

class DwellClicker:
    """Main dwell clicker application with UI."""
    
    def __init__(self):
        # Create the root window
        self.root = tk.Tk()
        
        # Create managers first
        self.button_manager = ButtonManager()
        self.detector = DwellDetector(radius=10, dwell_time=0.2)
        self.input_manager = InputManager()
        self.click_manager = ClickManager()
        self.settings_manager = SettingsManager(self.root, self.detector)
        self.window_manager = WindowManager(self.root, self.settings_manager)
        
        # Create UI with references to managers
        self.ui = DwellClickerUI(
            self.root, 
            self.click_manager, 
            self.detector,
            self.button_manager,
            self.window_manager
        )
        
        # Create exit manager after UI
        self.exit_manager = ExitManager(
            self.root, 
            self.settings_manager, 
            self.button_manager
        )
        
        # Connect components
        self.ui.connect_managers(self.settings_manager, self.exit_manager)
        
        # Register settings manager open command with button manager
        self.button_manager.register_command(
            "SETUP", 
            lambda: self.settings_manager.open_setup(self.button_manager)
        )
        
        # Setup input callback
        self.input_manager.on_position_update = self.on_position_update
        
        self.running = False
    
    def on_position_update(self, position):
        """
        Handle new mouse position data at regular intervals.
        
        This method is called by the InputManager every 100ms with the
        current mouse position. It adds the position to the dwell detector
        and processes any dwell events that might be triggered.
        """
        # Add position to detector's history
        self.detector.add_position(position)
        
        # Check if a dwell has been detected
        is_dwelling, center = self.detector.check_dwell()
        
        # Process dwell event if detected
        if is_dwelling and center:
            # Let the UI process the dwell event
            self.ui.process_dwell_event(center)
    
    def start(self):
        """Start the dwell clicker application."""
        print("Starting Dwell Clicker application...")
        
        # Load window position
        self.window_manager.load_position()
        
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
        
        # Save settings before exit
        self.settings_manager.save_settings()
        
        print("Application stopped.")

if __name__ == "__main__":
    # Create and start the dwell clicker application
    clicker = DwellClicker()
    clicker.start()