#!/usr/bin/env python3
"""Main application entry point for Dwellpy."""

import sys
import signal
import os

# Add the dwellpy package to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Set DPI awareness as early as possible for Windows multi-monitor support
if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes
        
        # Set DPI awareness before any Qt initialization
        try:
            # Try the newer SetProcessDpiAwarenessContext first (Windows 10 1703+)
            ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
        except:
            try:
                # Fallback to SetProcessDpiAwareness (Windows 8.1+)
                ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
            except:
                try:
                    # Final fallback to SetProcessDPIAware (Windows Vista+)
                    ctypes.windll.user32.SetProcessDPIAware()
                except:
                    pass  # DPI awareness not available
    except ImportError:
        pass  # ctypes not available

# Now import PyQt and other modules
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer
import logging

# Import application components
from .core.dwell_algorithm import DwellDetector
from .core.input_manager import InputManager
from .core.click_manager import ClickManager
from .managers.button_manager import ButtonManager  
from .managers.settings_manager import SettingsManager
from .managers.window_manager import WindowManager
from .managers.exit_manager import ExitManager
from .ui.ui_manager import DwellClickerUI
from .ui.click_feedback import ClickFeedbackManager
from .config.constants import DEFAULT_MOVE_LIMIT, DEFAULT_DWELL_TIME, APP_NAME
from .__init__ import __version__, __title__, __description__, __author__
from .utils.logging_config import (
    setup_logging, 
    get_logger, 
    log_application_start,
    log_application_shutdown
)


class DwellpyApplication:
    """Main application class that coordinates all components."""
    
    def __init__(self):
        """Initialize the application."""
        # Setup logging first
        setup_logging()
        self.logger = get_logger(__name__)
        log_application_start(__version__)
        
        self.logger.info("Initializing Dwellpy application...")
        
        # Create Qt application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(__version__)
        
        # Setup signal handlers for clean exit
        self._setup_signal_handlers()
        
        # Initialize core managers
        self._initialize_managers()
        
        # Create UI components
        self._initialize_ui()
        
        # Connect all components
        self._connect_components()
        
        # Setup application state
        self.running = False
        
        self.logger.info("Application initialization completed")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for clean shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown...")
            try:
                self._cleanup()
                self.app.quit()
            except:
                os._exit(1)
        
        # Handle common termination signals
        signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler)  # Termination request
        
        # Windows-specific signal handling
        if sys.platform == "win32":
            try:
                signal.signal(signal.SIGBREAK, signal_handler)  # Ctrl+Break on Windows
            except AttributeError:
                pass  # SIGBREAK not available on all Windows versions
    
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
        
        # Create click feedback manager
        self.feedback_manager = ClickFeedbackManager()
        
        # Connect feedback manager to click manager
        self.click_manager.feedback_manager = self.feedback_manager
        
        # Create settings manager (must be created before UI)
        self.settings_manager = SettingsManager(self.detector)
        
        # Connect settings manager to feedback manager
        self.feedback_manager.set_settings_manager(self.settings_manager)
        
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
        # Give input manager reference to UI for scroll widget updates
        self.input_manager.ui_manager = self.ui
        
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
        
        try:
            # Set running flag to false first
            self.running = False
            
            # Clean up feedback manager first
            if hasattr(self, 'feedback_manager') and self.feedback_manager:
                try:
                    self.feedback_manager.cleanup()
                    self.logger.info("Click feedback manager cleaned up")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up feedback manager: {e}")
            
            # Clean up scroll widget
            if hasattr(self, 'ui') and self.ui:
                try:
                    self.ui.cleanup_scroll_widget()
                    self.logger.info("Scroll widget cleaned up")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up scroll widget: {e}")
            
            # Stop input manager
            if hasattr(self, 'input_manager') and self.input_manager:
                try:
                    self.input_manager.stop()
                    self.logger.info("Input manager stopped")
                except Exception as e:
                    self.logger.warning(f"Error stopping input manager: {e}")
            
            # Save settings before exit
            if hasattr(self, 'settings_manager') and self.settings_manager:
                try:
                    self.settings_manager.save_settings()
                    self.logger.info("Settings saved")
                except Exception as e:
                    self.logger.warning(f"Error saving settings: {e}")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
        finally:
            # Always log shutdown
            try:
                log_application_shutdown()
            except:
                pass  # Don't let logging errors prevent shutdown
    
    def stop(self) -> None:
        """Stop the application gracefully."""
        self.logger.info("Graceful application stop requested")
        try:
            self._cleanup()
            if hasattr(self, 'app') and self.app:
                self.app.quit()
        except Exception as e:
            self.logger.error(f"Error during graceful stop: {e}")
            # Force exit if graceful stop fails
            import os
            os._exit(1)


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
