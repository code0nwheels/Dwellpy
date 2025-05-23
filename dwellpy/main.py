"""Main application entry point for Dwellpy."""

import sys
from PyQt6.QtWidgets import QApplication

from .core.dwell_algorithm import DwellDetector
from .core.input_manager import InputManager
from .core.click_manager import ClickManager
from .managers.settings_manager import SettingsManager
from .managers.exit_manager import ExitManager
from .managers.button_manager import ButtonManager
from .ui.ui_manager import DwellClickerUI
from .ui.window_manager import WindowManager
from .config.constants import DEFAULT_MOVE_LIMIT, DEFAULT_DWELL_TIME
from .__version__ import __version__


class DwellpyApplication:
    """Main dwell clicker application with UI."""
    
    def __init__(self):
        """Initialize the Dwellpy application."""
        # Create the Qt application first
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Dwellpy")
        self.app.setApplicationVersion(__version__)
        
        # Initialize core managers
        self._initialize_managers()
        
        # Create UI components
        self._initialize_ui()
        
        # Connect all components
        self._connect_components()
        
        # Setup application state
        self.running = False
        
        print(f"Dwellpy v{__version__} initialized")
    
    def _initialize_managers(self) -> None:
        """Initialize core managers and components."""
        # Create core managers
        self.button_manager = ButtonManager()
        self.detector = DwellDetector(
            radius=DEFAULT_MOVE_LIMIT, 
            dwell_time=DEFAULT_DWELL_TIME
        )
        self.input_manager = InputManager()
        self.click_manager = ClickManager()
        
        # Create settings manager (must be created before UI)
        self.settings_manager = SettingsManager(self.detector)
        
        # Create window manager
        self.window_manager = WindowManager(self.settings_manager)
    
    def _initialize_ui(self) -> None:
        """Initialize UI components."""
        # Create main UI
        self.ui = DwellClickerUI(
            self.click_manager, 
            self.detector,
            self.button_manager,
            self.window_manager
        )
        
        # Create exit manager after UI is created
        self.exit_manager = ExitManager(
            self.settings_manager, 
            self.button_manager,
            self.ui.window
        )
    
    def _connect_components(self) -> None:
        """Connect all application components together."""
        # Connect UI to managers
        self.ui.connect_managers(self.settings_manager, self.exit_manager)
        
        # Register settings manager command with button manager
        self.button_manager.register_command(
            "SETUP", 
            lambda: self.settings_manager.open_setup(
                self.button_manager, 
                self.ui.window
            )
        )
        
        # Setup input callback for position updates
        self.input_manager.on_position_update = self._on_position_update
        # Give input manager reference to UI for scroll widget updates
        self.input_manager.ui_manager = self.ui
    
    def _on_position_update(self, position: tuple[int, int]) -> None:
        """
        Handle new mouse position data at regular intervals.
        
        This method is called by the InputManager every 100ms with the
        current mouse position. It processes the position through the dwell
        detection algorithm and handles any dwell events.
        
        Args:
            position: Current mouse position as (x, y) tuple
        """
        # Add position to detector's tracking history
        self.detector.add_position(position)
        
        # Check if a dwell event has been detected
        is_dwelling, dwell_center = self.detector.check_dwell()
        
        # Process dwell event if one occurred
        if is_dwelling and dwell_center:
            # Delegate dwell processing to the UI manager
            self.ui.process_dwell_event(dwell_center)
    
    def start(self) -> None:
        """Start the dwell clicker application."""
        print("Starting Dwellpy application...")
        
        try:
            # Load and apply saved window position
            self.window_manager.load_position(self.ui.window)
            
            # Start core services
            self.running = True
            self.input_manager.start()
            
            # Show the main window
            self.ui.window.show()
            
            print("Dwellpy is now running. Use dwell clicks to interact.")
            
            # Start the Qt event loop (this blocks until app exits)
            exit_code = self.app.exec()
            sys.exit(exit_code)
            
        except KeyboardInterrupt:
            print("\nShutdown requested by user...")
        except Exception as e:
            print(f"Application error: {e}")
            raise
        finally:
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Clean up application resources."""
        print("Cleaning up application resources...")
        
        # Stop core services
        self.running = False
        if self.input_manager:
            self.input_manager.stop()
        
        # Save settings before exit
        if self.settings_manager:
            self.settings_manager.save_settings()
        
        print("Dwellpy stopped.")
    
    def stop(self) -> None:
        """Stop the application gracefully."""
        self._cleanup()
        if self.app:
            self.app.quit()


def main() -> None:
    """Main entry point for the application."""
    try:
        # Create and start the dwell clicker application
        app = DwellpyApplication()
        app.start()
    except Exception as e:
        print(f"Failed to start Dwellpy: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
