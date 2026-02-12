"""Exit functionality for the Dwellpy application."""

import os
import sys
import signal
import psutil
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Import the ExitDialog class
from ..ui.dialogs.exit_dialog import ExitDialog

class ExitManager:
    """Manages exit confirmation dialog and exit functionality."""
    
    def __init__(self, settings_manager, button_manager, parent_window=None):
        self.settings_manager = settings_manager
        self.button_manager = button_manager
        self.parent_window = parent_window
        self.confirm_dialog = None  # Track confirmation dialog
        
        # Register button commands
        self.button_manager.register_command("EXIT", self.show_exit_dialog)
        self.button_manager.register_command("EXIT_YES", self.confirm_exit)
        self.button_manager.register_command("EXIT_NO", self.cancel_exit)
    
    def _force_kill_process_tree(self):
        """Forcefully kill the current process and all its children."""
        try:
            current_pid = os.getpid()
            parent_process = psutil.Process(current_pid)
            
            # Get all child processes
            children = parent_process.children(recursive=True)
            
            # Terminate children first
            for child in children:
                try:
                    child.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Wait a bit for graceful termination
            gone, alive = psutil.wait_procs(children, timeout=1)
            
            # Force kill any remaining children
            for p in alive:
                try:
                    p.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Finally, kill the parent process
            if sys.platform == "win32":
                os.kill(current_pid, signal.SIGTERM)
            else:
                os.kill(current_pid, signal.SIGKILL)
                
        except Exception as e:
            # Last resort - force exit
            os._exit(1)
    
    def show_exit_dialog(self):
        """Show exit confirmation dialog."""
        # Check if dialog is already open
        if self.confirm_dialog is not None and self.confirm_dialog.isVisible():
            self.confirm_dialog.raise_()
            self.confirm_dialog.activateWindow()
            return
        
        # Create confirmation dialog using the ExitDialog class
        self.confirm_dialog = ExitDialog(self.parent_window)
        
        # Connect signals
        self.confirm_dialog.yes_button.clicked.connect(self.confirm_exit)
        self.confirm_dialog.no_button.clicked.connect(self.cancel_exit)
        
        # Show the dialog
        self.confirm_dialog.show()
    
    def confirm_exit(self):
        """Exit the application after confirmation with force kill."""
        try:
            # Close confirmation dialog first
            if self.confirm_dialog and self.confirm_dialog.isVisible():
                self.confirm_dialog.close()
            
            # Try to save settings quickly
            if self.settings_manager:
                try:
                    self.settings_manager.save_settings()
                except:
                    pass  # Don't let save errors prevent exit
            
            # Clean up feedback manager if available in main app
            app = QApplication.instance()
            if app and hasattr(app, 'feedback_manager'):
                try:
                    app.feedback_manager.cleanup()
                except:
                    pass
            
            # Close parent window if available
            if self.parent_window:
                try:
                    self.parent_window.close()
                except:
                    pass
            
            # Quit the Qt application
            if app:
                try:
                    app.quit()
                except:
                    pass
            
        except:
            pass  # Don't let cleanup errors prevent exit
        
        # Force kill the process tree after a brief delay
        self._force_kill_process_tree()
    
    def cancel_exit(self):
        """Cancel exit and close confirmation dialog."""
        if self.confirm_dialog and self.confirm_dialog.isVisible():
            self.confirm_dialog.close()
            self.confirm_dialog = None