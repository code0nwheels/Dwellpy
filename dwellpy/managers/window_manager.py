"""Window management for the Dwellpy application."""

from PyQt6.QtCore import QPoint
from PyQt6.QtWidgets import QMainWindow
from utils import center_window

class WindowManager:
    """
    Manages window position, dragging, and positioning.
    Centralizes window-related functionality.
    """
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        
        # Window dragging state
        self.is_dragging = False
        self.drag_start_position = None
        self.window_start_position = None
    
    def load_position(self, window):
        """Load window position from settings and apply it."""
        position = self.settings_manager.get_setting('window_position', (100, 100))
        x, y = position
        window.move(x, y)
    
    def save_position(self, window):
        """Save current window position to settings."""
        position = (window.x(), window.y())
        self.settings_manager.set_setting('window_position', position)
        self.settings_manager.save_settings()
    
    def start_drag(self, event, window):
        """Start window drag operation."""
        # Mark that we're dragging
        self.is_dragging = True
        
        # Store initial positions
        self.drag_start_position = event.globalPosition().toPoint()
        self.window_start_position = window.pos()
        
        # Set mouse tracking on the window
        window.setMouseTracking(True)
        
        # Remember original event handlers
        if not hasattr(window, 'original_mouseMoveEvent'):
            window.original_mouseMoveEvent = window.mouseMoveEvent
        if not hasattr(window, 'original_mouseReleaseEvent'):
            window.original_mouseReleaseEvent = window.mouseReleaseEvent
        
        # Capture mouse events - using lambda to pass window reference
        window.mouseMoveEvent = lambda e: self.update_drag_position(e, window)
        window.mouseReleaseEvent = lambda e: self.stop_drag(e, window)
    
    def update_drag_position(self, event, window):
        """Update window position during drag."""
        if not self.is_dragging:
            return
            
        # Calculate movement delta
        # In PyQt6, need to use globalPosition().toPoint() to get QPoint
        current_pos = event.globalPosition().toPoint()
        delta = current_pos - self.drag_start_position
        
        # Calculate new position (QPoint + QPoint = QPoint)
        new_position = self.window_start_position + delta
        
        # Apply boundary checking to keep window within screen bounds
        bounded_position = self._ensure_position_in_bounds(new_position, window)
        
        # Move the window
        window.move(bounded_position)
    
    def _ensure_position_in_bounds(self, position, window):
        """Ensure the window position stays within screen bounds, considering all monitors."""
        try:
            from PyQt6.QtGui import QGuiApplication
            
            # Get all available screens
            app = QGuiApplication.instance()
            screens = app.screens()
            
            # Calculate the combined desktop geometry (all monitors)
            desktop_rect = None
            for screen in screens:
                screen_geometry = screen.geometry()
                if desktop_rect is None:
                    desktop_rect = screen_geometry
                else:
                    desktop_rect = desktop_rect.united(screen_geometry)
            
            # If we couldn't get screen info, return original position
            if desktop_rect is None:
                return position
            
            window_size = window.size()
            
            # Calculate the bounds across all monitors
            min_x = desktop_rect.left()
            min_y = desktop_rect.top()
            max_x = desktop_rect.right() - window_size.width()
            max_y = desktop_rect.bottom() - window_size.height()
            
            # Constrain position to the combined desktop bounds
            bounded_x = max(min_x, min(position.x(), max_x))
            bounded_y = max(min_y, min(position.y(), max_y))
            
            return QPoint(bounded_x, bounded_y)
            
        except Exception:
            # If there's any error, return the original position
            return position
    
    def stop_drag(self, event, window):
        """Stop the drag operation when mouse is released."""
        if not self.is_dragging:
            return
            
        # Reset drag flag
        self.is_dragging = False
        
        # Reset mouse tracking
        window.setMouseTracking(False)
        
        # Reset event handlers to original ones
        if hasattr(window, 'original_mouseMoveEvent'):
            window.mouseMoveEvent = window.original_mouseMoveEvent
        if hasattr(window, 'original_mouseReleaseEvent'):
            window.mouseReleaseEvent = window.original_mouseReleaseEvent
        
        # Save the new position
        self.save_position(window)
    
    def center_window(self, window):
        """Center a window on the screen."""
        center_window(window)