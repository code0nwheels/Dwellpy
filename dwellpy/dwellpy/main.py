"""Main application entry point for Dwellpy."""

import sys
import logging
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
from .utils.logging_config import setup_logging, log_application_start, log_application_shutdown, get_logger


class DwellpyApplication:
    """Main dwell clicker application with UI."""
    
    def __init__(self):
        """Initialize the Dwellpy application."""
        # Initialize logging first
        self.log_dir = setup_logging()
        self.logger = get_logger(__name__)
        
        # Log application startup
        log_application_start(__version__)
        
        # Create the Qt application first
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Dwellpy")
        self.app.setApplicationVersion(__version__)
        
        self.logger.info("Qt application created")
        
        # Initialize core managers
        self._initialize_managers()
        
        # Create UI components
        self._initialize_ui()
        
        # Connect all components
        self._connect_components()
        
        # Setup application state
        self.running = False
        
        self.logger.info("Application initialization completed")
    
    def _initialize_managers(self) -> None:
        """Initialize core managers and components."""
        self.logger.info("Initializing core managers...")
        
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
        
        self.logger.info("Core managers initialized successfully")
    
    def _initialize_ui(self) -> None:
        """Initialize UI components."""
        self.logger.info("Initializing UI components...")
        
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
        
        self.logger.info("UI components initialized successfully")
    
    def _connect_components(self) -> None:
        """Connect all application components together."""
        self.logger.info("Connecting application components...")
        
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
        
        self.logger.info("Component connections established")
    
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
            self.logger.debug(f"Dwell event detected at position: {dwell_center}")
            # Delegate dwell processing to the UI manager
            self.ui.process_dwell_event(dwell_center)
    
    def start(self) -> None:
        """Start the dwell clicker application."""
        self.logger.info("Starting Dwellpy application...")
        
        try:
            # Load and apply saved window position
            self.window_manager.load_position(self.ui.window)
            self.logger.info("Window position loaded from settings")
            
            # Start core services
            self.running = True
            self.input_manager.start()
            self.logger.info("Input manager started")
            
            # Show the main window
            self.ui.window.show()
            self.logger.info("Main window displayed")
            
            # Start the Qt event loop (this blocks until app exits)
            self.logger.info("Starting Qt event loop...")
            exit_code = self.app.exec()
            self.logger.info(f"Qt event loop ended with exit code: {exit_code}")
            sys.exit(exit_code)
            
        except KeyboardInterrupt:
            # Silently handle keyboard interrupt
            self.logger.info("Application interrupted by user (Ctrl+C)")
            pass
        except Exception as e:
            self.logger.error(f"Unexpected error during application startup: {e}", exc_info=True)
            raise
        finally:
            self._cleanup()
    
    def _cleanup(self) -> None:
        """Clean up application resources."""
        self.logger.info("Starting application cleanup...")
        
        # Stop core services
        self.running = False
        if self.input_manager:
            self.input_manager.stop()
            self.logger.info("Input manager stopped")
        
        # Save settings before exit
        if self.settings_manager:
            self.settings_manager.save_settings()
            self.logger.info("Settings saved")
        
        log_application_shutdown()
    
    def stop(self) -> None:
        """Stop the application gracefully."""
        self.logger.info("Graceful application stop requested")
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
        # If logging isn't set up yet, fall back to basic error handling
        try:
            logger = get_logger(__name__)
            logger.critical(f"Fatal error in main(): {e}", exc_info=True)
        except:
            # Last resort - print to stderr
            import traceback
            print(f"FATAL ERROR: {e}", file=sys.stderr)
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
