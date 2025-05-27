"""Exit functionality for the Dwellpy application."""

import os
import sys
import signal
import psutil
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QApplication)
from PyQt6.QtCore import Qt
from ..utils import center_window

# Dark theme color constants
DARK_BG = "#222222"         # Dark background
DARK_BUTTON_BG = "#2d2d2d"  # Dark button background
TEXT_COLOR = "#ffffff"      # White text
BLUE_ACCENT = "#0078d7"     # Blue accent color
RED_ACCENT = "#d83638"      # Red accent/title color
BORDER_COLOR = "#3c3c3c"    # Slight border color for depth

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
        
        # Create confirmation dialog
        self.confirm_dialog = QDialog(self.parent_window)
        self.confirm_dialog.setFixedSize(350, 180)
        
        # Set window flags to frameless
        self.confirm_dialog.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint  # No title bar
        )
        
        # Make dialog non-modal to allow dwell clicking to continue
        self.confirm_dialog.setModal(False)
        
        # Apply dark theme with red border
        self.confirm_dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {DARK_BG};
                color: {TEXT_COLOR};
                border: 1px solid {RED_ACCENT};
                border-radius: 3px;
            }}
            QLabel {{
                color: {TEXT_COLOR};
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(self.confirm_dialog)
        main_layout.setContentsMargins(20, 25, 20, 20)
        main_layout.setSpacing(20)
        
        # Message
        message = QLabel("Are you sure you want to exit?", self.confirm_dialog)
        message.setStyleSheet(f"""
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 14pt;
            color: {TEXT_COLOR};
        """)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(message)
        
        # Buttons
        buttons_frame = QFrame(self.confirm_dialog)
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(20)
        buttons_frame.setStyleSheet(f"background-color: {DARK_BG};")
        
        # Yes button - red styling
        yes_button = QPushButton("Yes", buttons_frame)
        yes_button.setFixedSize(100, 40)
        yes_button.setCursor(Qt.CursorShape.PointingHandCursor)
        yes_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED_ACCENT};
                color: {TEXT_COLOR};
                border: none;
                border-radius: 3px;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 12pt;
                font-weight: bold;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
        """)
        buttons_layout.addWidget(yes_button)
        
        # No button - blue styling
        no_button = QPushButton("No", buttons_frame)
        no_button.setFixedSize(100, 40)
        no_button.setCursor(Qt.CursorShape.PointingHandCursor)
        no_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {BLUE_ACCENT};
                color: {TEXT_COLOR};
                border: none;
                border-radius: 3px;
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 12pt;
                font-weight: bold;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: #0069c0;
            }}
        """)
        buttons_layout.addWidget(no_button)
        
        main_layout.addWidget(buttons_frame, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Connect signals
        yes_button.clicked.connect(self.confirm_exit)
        no_button.clicked.connect(self.cancel_exit)
        
        # Center the dialog on screen
        center_window(self.confirm_dialog)
        
        # Show the dialog (non-modal)
        self.confirm_dialog.show()  # Use show() instead of exec() to make it non-modal
    
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