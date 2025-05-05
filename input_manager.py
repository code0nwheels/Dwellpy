import pyautogui
import threading
import time

class InputManager:
    """Tracks mouse positions continuously in a separate thread."""
    
    def __init__(self, sample_rate=0.01):
        self.sample_rate = sample_rate
        self.running = False
        self.thread = None
        self.current_position = (0, 0)
        self.on_position_update = None  # Callback function
        
    def start(self):
        """Start tracking mouse positions."""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._track_mouse)
        self.thread.daemon = True
        self.thread.start()
        
    def stop(self):
        """Stop tracking mouse positions."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            
    def _track_mouse(self):
        """Track mouse positions in background thread."""
        while self.running:
            try:
                # Get current mouse position
                pos = pyautogui.position()
                self.current_position = (pos.x, pos.y)
                
                # Call the update callback if registered
                if self.on_position_update:
                    self.on_position_update(self.current_position)
                    
                # Wait for next sample
                time.sleep(self.sample_rate)
                
            except Exception as e:
                print(f"Error tracking mouse: {e}")
                time.sleep(0.1)  # Avoid tight loop on error