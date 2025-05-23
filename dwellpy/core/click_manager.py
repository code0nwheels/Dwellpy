import time
from pynput.mouse import Button, Controller

class ClickManager:
    """Click manager that handles mouse clicks using pynput for cross-platform support."""
    
    def __init__(self, min_click_interval=0.5):
        self.min_click_interval = min_click_interval
        self.last_click_time = 0
        self.debug_mode = False
        
        # Create pynput mouse controller
        self.mouse = Controller()
    
    def can_click(self):
        """
        Check if a click can be performed based on time interval only.
        The dwell algorithm handles position-based click prevention.
        """
        # Check time-based restriction
        current_time = time.time()
        time_since_last = current_time - self.last_click_time
        
        # Allow click if enough time has passed
        can_click = time_since_last >= self.min_click_interval
        
        if not can_click and self.debug_mode:
            print(f"Click blocked: only {time_since_last:.1f}s since last click")
        
        return can_click
    
    def perform_left_click(self, position=None):
        """Perform a left mouse click at the CURRENT mouse position safely."""
        if not self.can_click():
            return False
        
        print(f"Performing left click at {self.mouse.position}")
            
        try:
            # Use pynput to perform a left click
            self.mouse.click(Button.left)
            
            self.last_click_time = time.time()
            
            if self.debug_mode:
                current_pos = self.mouse.position
                print(f"LEFT CLICK PERFORMED at {current_pos}")
                
            return True
            
        except Exception as e:
            print(f"Error performing click: {e}")
            return False

    def perform_right_click(self, position=None):
        """Perform a right mouse click without moving cursor."""
        if not self.can_click():
            return False
            
        try:
            # Use pynput to perform a right click
            self.mouse.click(Button.right)
            
            self.last_click_time = time.time()
            return True
        except Exception as e:
            print(f"Error performing right click: {e}")
            return False

    def perform_double_click(self, position=None):
        """Perform a double click without moving cursor."""
        if not self.can_click():
            return False
            
        try:
            # Use pynput to perform a double click
            self.mouse.click(Button.left, 2)
            
            self.last_click_time = time.time()
            return True
        except Exception as e:
            print(f"Error performing double click: {e}")
            return False

    def perform_middle_click(self, position=None):
        """Perform a middle mouse click without moving cursor."""
        if not self.can_click():
            return False
            
        try:
            # Use pynput to perform a middle click
            self.mouse.click(Button.middle)
            
            self.last_click_time = time.time()
            return True
        except Exception as e:
            print(f"Error performing middle click: {e}")
            return False

    def mouse_down(self):
        """Press and hold the left mouse button."""
        try:
            # Use pynput to press the mouse button
            self.mouse.press(Button.left)
            
            self.last_click_time = time.time()
            if self.debug_mode:
                print(f"MOUSE DOWN at {self.mouse.position}")
            return True
        except Exception as e:
            print(f"Error in mouse down: {e}")
            return False

    def mouse_up(self):
        """Release the left mouse button."""
        try:
            # Use pynput to release the mouse button
            self.mouse.release(Button.left)
            
            if self.debug_mode:
                print(f"MOUSE UP at {self.mouse.position}")
            return True
        except Exception as e:
            print(f"Error in mouse up: {e}")
            return False