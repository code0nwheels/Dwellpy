import pyautogui
import time

class ClickManager:
    """Click manager that safely handles PyAutoGUI's fail-safe."""
    
    def __init__(self, min_click_interval=0.5):
        self.min_click_interval = min_click_interval
        self.last_click_time = 0
        self.debug_mode = False
        
        # Store the original failsafe setting so we can restore it later
        self.original_failsafe = pyautogui.FAILSAFE
        
    def can_click(self):
        """Check if enough time has passed since last click."""
        current_time = time.time()
        time_since_last = current_time - self.last_click_time
        can_click = time_since_last >= self.min_click_interval
        
        if not can_click and self.debug_mode:
            print(f"Click blocked: only {time_since_last:.2f}s since last click")
            
        return can_click
        
    def perform_left_click(self, position):
        """Perform a left mouse click at the CURRENT mouse position safely."""
        if not self.can_click():
            return False
            
        try:
            # IMPORTANT: We're not moving the mouse at all - just clicking at current position
            # Temporarily disable fail-safe for the click operation
            pyautogui.FAILSAFE = False
            
            # Perform the click without moving the mouse
            pyautogui.click()
            
            # Restore the original fail-safe setting
            pyautogui.FAILSAFE = self.original_failsafe
            
            self.last_click_time = time.time()
            
            if self.debug_mode:
                current_pos = pyautogui.position()
                print(f"LEFT CLICK PERFORMED at {current_pos}")
                
            return True
            
        except Exception as e:
            print(f"Error performing click: {e}")
            # Make sure fail-safe is restored even if there's an error
            pyautogui.FAILSAFE = self.original_failsafe
            return False
    
    def perform_right_click(self, position):
        """Perform a right mouse click without moving cursor."""
        if not self.can_click():
            return False
            
        try:
            # Temporarily disable fail-safe for the click operation
            pyautogui.FAILSAFE = False
            
            pyautogui.rightClick()
            
            # Restore the original fail-safe setting
            pyautogui.FAILSAFE = self.original_failsafe
            
            self.last_click_time = time.time()
            return True
        except Exception as e:
            print(f"Error performing right click: {e}")
            # Make sure fail-safe is restored even if there's an error
            pyautogui.FAILSAFE = self.original_failsafe
            return False
    
    def perform_double_click(self, position):
        """Perform a double click without moving cursor."""
        if not self.can_click():
            return False
            
        try:
            # Temporarily disable fail-safe for the click operation
            pyautogui.FAILSAFE = False
            
            pyautogui.doubleClick()
            
            # Restore the original fail-safe setting
            pyautogui.FAILSAFE = self.original_failsafe
            
            self.last_click_time = time.time()
            return True
        except Exception as e:
            print(f"Error performing double click: {e}")
            # Make sure fail-safe is restored even if there's an error
            pyautogui.FAILSAFE = self.original_failsafe
            return False