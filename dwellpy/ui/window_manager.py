"""Window management for the Dwellpy application."""

from PyQt6.QtCore import QPoint
from PyQt6.QtWidgets import QMainWindow

# Updated imports for new structure
try:
    from ..utils.helpers import center_window
except ImportError:
    # Fallback for testing
    from PyQt6.QtGui import QGuiApplication
    
    def center_window(window):
        """Center a window on the screen."""
        screen = QGuiApplication.primaryScreen().geometry()
        window_size = window.frameGeometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        window.move(x, y)


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
        
        # Move the window
        window.move(new_position)
    
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
