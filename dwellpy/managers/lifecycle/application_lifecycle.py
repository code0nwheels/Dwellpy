#!/usr/bin/env python3
"""Application lifecycle management for Dwellpy."""

import sys
import os
import logging
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from ...utils.helpers import get_asset_path
from ...utils.logging_config import log_application_start, log_application_shutdown
from ...config.constants import APP_NAME


class ApplicationLifecycle:
    """Manages the application lifecycle including startup, shutdown, and cleanup."""
    
    def __init__(self, app: QApplication, logger: logging.Logger):
        """Initialize the lifecycle manager."""
        self.app = app
        self.logger = logger
        self.running = False
    
    def setup_application_icon(self) -> None:
        """Set application icon for taskbar (works across all OS)."""
        try:
            # Use platform-appropriate icon format
            if sys.platform == "win32":
                icon_path = get_asset_path("Dwellpy.ico")
            else:
                # Linux/macOS: use PNG format
                icon_path = get_asset_path("Dwellpy.png")
                
            if os.path.exists(icon_path):
                app_icon = QIcon(icon_path)
                self.app.setWindowIcon(app_icon)
                self.logger.info(f"Application icon set from: {icon_path}")
            else:
                self.logger.warning(f"Icon file not found at: {icon_path}")
        except Exception as e:
            self.logger.error(f"Failed to set application icon: {e}")
    
    def start(self, ui, input_manager, window_manager, settings_manager, feedback_manager) -> None:
        """Start the dwell clicker application."""
        self.logger.info("Starting Dwellpy application...")
        
        try:
            # Load and apply saved window position
            window_manager.load_position(ui.window)
            self.logger.info("Window position loaded from settings")
            
            # Start core services
            self.running = True
            input_manager.start()
            self.logger.info("Input manager started")
            
            # Show the main window
            ui.window.show()
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
            self._cleanup(ui, input_manager, settings_manager, feedback_manager)
    
    def _cleanup(self, ui, input_manager, settings_manager, feedback_manager) -> None:
        """Clean up application resources."""
        self.logger.info("Starting application cleanup...")
        
        try:
            # Set running flag to false first
            self.running = False
            
            # Clean up feedback manager first
            if feedback_manager:
                try:
                    feedback_manager.cleanup()
                    self.logger.info("Click feedback manager cleaned up")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up feedback manager: {e}")
            
            # Clean up scroll widget
            if ui:
                try:
                    ui.cleanup_scroll_widget()
                    self.logger.info("Scroll widget cleaned up")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up scroll widget: {e}")
            
            # Stop input manager
            if input_manager:
                try:
                    input_manager.stop()
                    self.logger.info("Input manager stopped")
                except Exception as e:
                    self.logger.warning(f"Error stopping input manager: {e}")
            
            # Save settings before exit
            if settings_manager:
                try:
                    settings_manager.save_settings()
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
    
    def stop(self, ui, input_manager, settings_manager, feedback_manager) -> None:
        """Stop the application gracefully."""
        self.logger.info("Graceful application stop requested")
        try:
            self._cleanup(ui, input_manager, settings_manager, feedback_manager)
            if self.app:
                self.app.quit()
        except Exception as e:
            self.logger.error(f"Error during graceful stop: {e}")
            # Force exit if graceful stop fails
            os._exit(1) 