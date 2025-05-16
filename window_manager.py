"""Window management for the Dwellpy application."""

import tkinter as tk
from utils import center_window

class WindowManager:
    """
    Manages window position, dragging, and positioning.
    Centralizes window-related functionality.
    """
    
    def __init__(self, root, settings_manager):
        self.root = root
        self.settings_manager = settings_manager
        
        # Window dragging state
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.window_start_x = 0
        self.window_start_y = 0
    
    def load_position(self):
        """Load window position from settings and apply it."""
        position = self.settings_manager.get_setting('window_position', (100, 100))
        x, y = position
        self.root.geometry(f"+{x}+{y}")
    
    def save_position(self):
        """Save current window position to settings."""
        position = (self.root.winfo_x(), self.root.winfo_y())
        self.settings_manager.set_setting('window_position', position)
        self.settings_manager.save_settings()
    
    def start_drag(self, event):
        """Start window drag operation."""
        # Mark that we're dragging
        self.is_dragging = True
        
        # Store initial positions
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        self.window_start_x = self.root.winfo_x()
        self.window_start_y = self.root.winfo_y()
        
        # Bind motion and release events to the entire root window
        self.root.bind("<B1-Motion>", self.update_drag_position)
        self.root.bind("<ButtonRelease-1>", self.stop_drag)
        
        print("Window drag started")
    
    def update_drag_position(self, event):
        """Update window position during drag."""
        if not self.is_dragging:
            return
            
        # Calculate movement delta
        dx = event.x_root - self.drag_start_x
        dy = event.y_root - self.drag_start_y
        
        # Calculate new position
        new_x = self.window_start_x + dx
        new_y = self.window_start_y + dy
        
        # Move the window
        self.root.geometry(f"+{new_x}+{new_y}")
    
    def stop_drag(self, event):
        """Stop the drag operation when mouse is released."""
        if not self.is_dragging:
            return
            
        # Reset drag flag
        self.is_dragging = False
        
        # Unbind events from root window
        self.root.unbind("<B1-Motion>")
        self.root.unbind("<ButtonRelease-1>")
        
        # Save the new position
        self.save_position()
            
        print("Window drag completed")
    
    def center_window(self, window=None):
        """Center a window on the screen."""
        if window is None:
            window = self.root
            
        center_window(window)
