import threading
import time
from pynput.mouse import Controller

class InputManager:
    """
    Manages mouse position tracking and dispatches position updates
    at regular intervals to the dwell detection system.
    
    This class runs a background thread that continuously tracks
    the cursor position, but only sends updates at fixed intervals
    (100ms) to match the timing precision needed for dwell detection.
    """
    
    def __init__(self):
        self.running = False             # Thread control flag
        self.thread = None               # Reference to background thread
        self.current_position = (0, 0)   # Current cursor position
        self.on_position_update = None   # Callback function for position updates
        self.mouse = Controller()        # pynput mouse controller
        
    def start(self):
        """
        Start the mouse position tracking thread.
        Does nothing if already running.
        """
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._track_mouse)
        self.thread.daemon = True  # Thread will terminate when main program exits
        self.thread.start()
        
    def stop(self):
        """
        Stop the mouse position tracking thread.
        Attempts to gracefully terminate the thread.
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)  # Wait up to 1 second for thread to exit
            
    def _track_mouse(self):
        """
        Background thread function that continuously monitors
        mouse position and triggers updates at fixed intervals.
        
        Updates are triggered every 100ms to provide consistent
        timing for dwell detection while keeping CPU usage low.
        """
        last_update_time = 0
        update_interval = 0.1  # 100ms interval for position updates
        
        while self.running:
            try:
                # Get current mouse position using pynput
                pos = self.mouse.position
                self.current_position = pos
                
                # Only send updates at fixed intervals
                # This ensures consistent timing for dwell detection
                current_time = time.time()
                if current_time - last_update_time >= update_interval:
                    if self.on_position_update:
                        self.on_position_update(self.current_position)
                    last_update_time = current_time
                    
                # Small sleep to prevent high CPU usage
                # This doesn't affect timing precision since we track actual time
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Error tracking mouse: {e}")
                time.sleep(0.1)  # Avoid tight loop on error