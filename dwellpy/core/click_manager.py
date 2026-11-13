import time
from pynput.mouse import Button, Controller
import sys

class ClickManager:
    """Click manager that handles mouse clicks using pynput for cross-platform support."""
    
    def __init__(self, min_click_interval=0.5):
        self.min_click_interval = min_click_interval
        self.last_click_time = 0
        
        # Create pynput mouse controller
        self.mouse = Controller()
        
        # Click feedback manager - will be set by main application
        self.feedback_manager = None

        # True while we are holding the left button down for a dwell drag
        self.left_button_held = False
    
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
        
        return can_click
    
    def perform_left_click(self, position=None):
        """Perform a left mouse click at the CURRENT mouse position safely."""
        if not self.can_click():
            return False
            
        try:
            # Get current mouse position for feedback
            current_pos = self.mouse.position
            
            # Use pynput to perform a left click
            self.mouse.click(Button.left)
            
            # Show visual feedback
            if self.feedback_manager:
                self.feedback_manager.show_feedback(current_pos, 'left')
            
            self.last_click_time = time.time()
                
            return True
            
        except Exception as e:
            return False

    def perform_right_click(self, position=None):
        """Perform a right mouse click without moving cursor."""
        if not self.can_click():
            return False
            
        try:
            # Get current mouse position for feedback
            current_pos = self.mouse.position
            
            # Use pynput to perform a right click
            self.mouse.click(Button.right)
            
            # Show visual feedback
            if self.feedback_manager:
                self.feedback_manager.show_feedback(current_pos, 'right')
            
            self.last_click_time = time.time()
            return True
        except Exception as e:
            return False

    def perform_double_click(self, position=None):
        """Perform a double click without moving cursor."""
        if not self.can_click():
            return False
            
        try:
            # Get current mouse position for feedback
            current_pos = self.mouse.position
            
            # Use pynput to perform a double click
            self.mouse.click(Button.left, 2)
            
            # Show visual feedback
            if self.feedback_manager:
                self.feedback_manager.show_feedback(current_pos, 'double')
            
            self.last_click_time = time.time()
            return True
        except Exception as e:
            return False

    def perform_middle_click(self, position=None):
        """Perform a middle mouse click without moving cursor."""
        if not self.can_click():
            return False
            
        try:
            # Get current mouse position for feedback
            current_pos = self.mouse.position
            
            # Use pynput to perform a middle click
            self.mouse.click(Button.middle)
            
            # Show visual feedback
            if self.feedback_manager:
                self.feedback_manager.show_feedback(current_pos, 'middle')
            
            self.last_click_time = time.time()
            return True
        except Exception as e:
            return False

    def mouse_down(self):
        """Press and hold the left mouse button."""
        try:
            # Get current mouse position for feedback
            current_pos = self.mouse.position
            
            # Use pynput to press the mouse button
            self.mouse.press(Button.left)
            self.left_button_held = True

            # Show visual feedback for drag start
            if self.feedback_manager:
                self.feedback_manager.show_feedback(current_pos, 'drag_down')
            
            self.last_click_time = time.time()
            return True
        except Exception as e:
            return False

    def mouse_up(self):
        """Release the left mouse button."""
        try:
            # Get current mouse position for feedback
            current_pos = self.mouse.position
            
            # Use pynput to release the mouse button
            self.mouse.release(Button.left)
            self.left_button_held = False

            # Show visual feedback for drag end
            if self.feedback_manager:
                self.feedback_manager.show_feedback(current_pos, 'drag_up')

            return True
        except Exception as e:
            return False

    def release_if_held(self):
        """Release the left button if a dwell drag left it pressed.

        Safety net for paths that abandon a drag (mode change, turning the
        clicker off, exiting) so the system is never left with the button stuck down.
        """
        if not self.left_button_held:
            return False
        return self.mouse_up()