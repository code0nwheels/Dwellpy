import pyautogui
import time
import ctypes
import platform

# Mouse event constants
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
INPUT_MOUSE = 0

# Windows structures
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT_union(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        # Keyboard and hardware input fields omitted
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("u", INPUT_union)
    ]

class ClickManager:
    """Click manager that handles mouse clicks using platform-specific methods."""
    
    def __init__(self, min_click_interval=0.5):
        self.min_click_interval = min_click_interval
        self.last_click_time = 0
        self.debug_mode = False
        
        # Store the original failsafe setting so we can restore it later
        self.original_failsafe = pyautogui.FAILSAFE
        
        # Check if we're on Windows
        self.use_sendinput = platform.system() == 'Windows'
        
        if self.use_sendinput:
            # Setup for Windows SendInput
            self.SendInput = ctypes.windll.user32.SendInput
            self.SendInput.argtypes = (ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int)
            self.SendInput.restype = ctypes.c_uint
        
    def can_click(self):
        """Check if enough time has passed since last click."""
        current_time = time.time()
        time_since_last = current_time - self.last_click_time
        can_click = time_since_last >= self.min_click_interval
        
        if not can_click and self.debug_mode:
            print(f"Click blocked: only {time_since_last:.2f}s since last click")
            
        return can_click
    
    def _send_mouse_event_windows(self, flags):
        """Use SendInput for Windows mouse events."""
        extra = ctypes.c_ulong(0)
        i = INPUT()
        i.type = INPUT_MOUSE
        i.u.mi = MOUSEINPUT(0, 0, 0, flags, 0, ctypes.pointer(extra))
        self.SendInput(1, ctypes.pointer(i), ctypes.sizeof(i))
        
    def perform_left_click(self, position=None):
        """Perform a left mouse click at the CURRENT mouse position safely."""
        if not self.can_click():
            return False
            
        try:
            if self.use_sendinput:
                # Use Windows SendInput
                self._send_mouse_event_windows(MOUSEEVENTF_LEFTDOWN + MOUSEEVENTF_LEFTUP)
            else:
                # Use PyAutoGUI for non-Windows platforms
                pyautogui.FAILSAFE = False
                pyautogui.click()
                pyautogui.FAILSAFE = self.original_failsafe
            
            self.last_click_time = time.time()
            
            if self.debug_mode:
                current_pos = pyautogui.position()
                print(f"LEFT CLICK PERFORMED at {current_pos}")
                
            return True
            
        except Exception as e:
            print(f"Error performing click: {e}")
            # Make sure fail-safe is restored even if there's an error
            if not self.use_sendinput:
                pyautogui.FAILSAFE = self.original_failsafe
            return False

    def perform_right_click(self, position=None):
        """Perform a right mouse click without moving cursor."""
        if not self.can_click():
            return False
            
        try:
            if self.use_sendinput:
                # Use Windows SendInput
                self._send_mouse_event_windows(MOUSEEVENTF_RIGHTDOWN + MOUSEEVENTF_RIGHTUP)
            else:
                # Use PyAutoGUI for non-Windows platforms
                pyautogui.FAILSAFE = False
                pyautogui.rightClick()
                pyautogui.FAILSAFE = self.original_failsafe
            
            self.last_click_time = time.time()
            return True
        except Exception as e:
            print(f"Error performing right click: {e}")
            if not self.use_sendinput:
                pyautogui.FAILSAFE = self.original_failsafe
            return False

    def perform_double_click(self, position=None):
        """Perform a double click without moving cursor."""
        if not self.can_click():
            return False
            
        try:
            if self.use_sendinput:
                # Use Windows SendInput for double click with proper timing
                # First click
                self._send_mouse_event_windows(MOUSEEVENTF_LEFTDOWN)
                time.sleep(0.002)  # Faster down-up (20ms)
                self._send_mouse_event_windows(MOUSEEVENTF_LEFTUP)
                
                # Brief pause between clicks (keep this a bit longer)
                time.sleep(0.05)  # Slight pause between clicks
                
                # Second click
                self._send_mouse_event_windows(MOUSEEVENTF_LEFTDOWN)
                time.sleep(0.002)  # Faster down-up (20ms)
                self._send_mouse_event_windows(MOUSEEVENTF_LEFTUP)
            else:
                # Use PyAutoGUI for non-Windows platforms
                pyautogui.FAILSAFE = False
                pyautogui.doubleClick()
                pyautogui.FAILSAFE = self.original_failsafe
            
            self.last_click_time = time.time()
            return True
        except Exception as e:
            print(f"Error performing double click: {e}")
            if not self.use_sendinput:
                pyautogui.FAILSAFE = self.original_failsafe
            return False

    def perform_middle_click(self, position=None):
        """Perform a middle mouse click without moving cursor."""
        if not self.can_click():
            return False
            
        try:
            if self.use_sendinput:
                # Use Windows SendInput
                self._send_mouse_event_windows(MOUSEEVENTF_MIDDLEDOWN + MOUSEEVENTF_MIDDLEUP)
            else:
                # Use PyAutoGUI for non-Windows platforms
                pyautogui.FAILSAFE = False
                pyautogui.middleClick()
                pyautogui.FAILSAFE = self.original_failsafe
            
            self.last_click_time = time.time()
            return True
        except Exception as e:
            print(f"Error performing middle click: {e}")
            if not self.use_sendinput:
                pyautogui.FAILSAFE = self.original_failsafe
            return False

    def mouse_down(self):
        """Press and hold the left mouse button."""
        try:
            if self.use_sendinput:
                # Use Windows SendInput for better responsiveness
                self._send_mouse_event_windows(MOUSEEVENTF_LEFTDOWN)
            else:
                # Use PyAutoGUI for non-Windows platforms
                pyautogui.FAILSAFE = False
                pyautogui.mouseDown()
                pyautogui.FAILSAFE = self.original_failsafe
            
            self.last_click_time = time.time()
            if self.debug_mode:
                print(f"MOUSE DOWN at {pyautogui.position()}")
            return True
        except Exception as e:
            print(f"Error in mouse down: {e}")
            if not self.use_sendinput:
                pyautogui.FAILSAFE = self.original_failsafe
            return False

    def mouse_up(self):
        """Release the left mouse button."""
        try:
            if self.use_sendinput:
                # Use Windows SendInput for better responsiveness
                self._send_mouse_event_windows(MOUSEEVENTF_LEFTUP)
            else:
                # Use PyAutoGUI for non-Windows platforms
                pyautogui.FAILSAFE = False
                pyautogui.mouseUp()
                pyautogui.FAILSAFE = self.original_failsafe
            
            if self.debug_mode:
                print(f"MOUSE UP at {pyautogui.position()}")
            return True
        except Exception as e:
            print(f"Error in mouse up: {e}")
            if not self.use_sendinput:
                pyautogui.FAILSAFE = self.original_failsafe
            return False