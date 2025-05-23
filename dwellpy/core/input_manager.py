"""Input manager for the Dwellpy application."""

from PyQt6.QtCore import QTimer
from pynput.mouse import Controller

class InputManager:
    """
    Manages mouse position tracking and dispatches position updates
    at regular intervals to the dwell detection system.
    
    Uses Qt's timer mechanism instead of threading for better
    compatibility with the Qt event loop.
    """
    
    def __init__(self):
        self.running = False             # Timer control flag
        self.current_position = (0, 0)   # Current cursor position
        self.on_position_update = None   # Callback function for position updates
        self.mouse = Controller()        # pynput mouse controller
        
        # Create timer for position polling
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_position)
        self.timer.setInterval(100)  # 100ms interval
        
    def start(self):
        """
        Start the mouse position tracking timer.
        Does nothing if already running.
        """
        if self.running:
            return
            
        self.running = True
        self.timer.start()
        print("Input manager started")
        
    def stop(self):
        """
        Stop the mouse position tracking timer.
        """
        self.running = False
        self.timer.stop()
        print("Input manager stopped")
            
    def _update_position(self):
        """Timer callback with scroll widget support."""
        try:
            # Get current mouse position using pynput
            pos = self.mouse.position
            self.current_position = pos
            
            # Call the position update callback
            if self.on_position_update:
                self.on_position_update(self.current_position)
                
            # Also update scroll widget position if we have reference to UI
            # This would be set by the main application
            if hasattr(self, 'ui_manager') and self.ui_manager:
                self.ui_manager.update_scroll_widget_position(pos)
                
        except Exception as e:
            print(f"Error tracking mouse: {e}")