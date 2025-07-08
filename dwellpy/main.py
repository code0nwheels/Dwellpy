#!/usr/bin/env python3
"""Main application entry point for Dwellpy."""

import sys
import os

# Add the dwellpy package to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Set DPI awareness as early as possible for Windows multi-monitor support
from .bootstrap import setup_dpi_awareness, create_linux_desktop_file, setup_signal_handlers

# Now import PyQt and other modules
from PyQt6.QtWidgets import QApplication
import logging

# Import application components
from .__init__ import __version__, __title__, __description__, __author__
from .utils.logging_config import (
    setup_logging, 
    get_logger, 
    log_application_start
)
from .managers.lifecycle import ApplicationLifecycle, ComponentInitializer
from .config.constants import APP_NAME


class DwellpyApplication:
    """Main application class that coordinates all components."""
    
    def __init__(self):
        """Initialize the application."""
        # Setup logging first
        setup_logging()
        self.logger = get_logger(__name__)
        log_application_start(__version__)
        
        self.logger.info("Initializing Dwellpy application...")
        
        # Create Linux desktop file for system integration
        create_linux_desktop_file()
        
        # Create Qt application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(__version__)
        
        # Setup signal handlers for clean exit
        setup_signal_handlers(self._cleanup)
        
        # Initialize lifecycle and component managers
        self.lifecycle = ApplicationLifecycle(self.app, self.logger)
        self.component_initializer = ComponentInitializer(self.logger)
        
        # Initialize core managers
        self.components = self.component_initializer.initialize_managers()
        
        # Create UI components
        self.ui = self.component_initializer.initialize_ui(self.components)
        
        # Connect all components
        self.component_initializer.connect_components(self.ui, self.components)
        
        # Configure adaptive polling
        self.component_initializer.configure_adaptive_polling(
            self.components['input_manager'], 
            self.components['settings_manager']
        )
        
        # Setup application icon
        self.lifecycle.setup_application_icon()
        
        # Setup application state
        self.running = False
        
        self.logger.info("Application initialization completed")
    
    def _cleanup(self) -> None:
        """Clean up application resources."""
        self.lifecycle._cleanup(
            self.ui,
            self.components['input_manager'],
            self.components['settings_manager'],
            self.components['feedback_manager']
        )
    
    def start(self) -> None:
        """Start the dwell clicker application."""
        self.lifecycle.start(
            self.ui,
            self.components['input_manager'],
            self.components['window_manager'],
            self.components['settings_manager'],
            self.components['feedback_manager']
        )
    
    def stop(self) -> None:
        """Stop the application gracefully."""
        self.lifecycle.stop(
            self.ui,
            self.components['input_manager'],
            self.components['settings_manager'],
            self.components['feedback_manager']
        )


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
