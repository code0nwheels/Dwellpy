"""Cursor movement detection for UI widget visibility control."""

import time


class CursorMovementDetector:
    """Detects cursor movement vs dwelling to control widget visibility."""
    
    def __init__(self, dwell_delay=0.2):
        self.last_position = None
        self.last_movement_time = 0
        self.movement_threshold = 5  # pixels - reduced for more sensitivity
        self.dwell_delay = dwell_delay  # seconds - configurable time to wait before showing widgets
        self.hide_delay = 0.05  # seconds - very quick hiding
        self.movement_velocity_history = []
        self.velocity_window = 2  # reduced window for faster response
        self.movement_velocity_threshold = 30  # pixels per second - reduced threshold
        self.last_update_time = 0
        
    def set_dwell_delay(self, delay):
        """Update the dwell delay setting."""
        self.dwell_delay = delay
    
    def set_movement_threshold(self, threshold):
        """Update the movement threshold to match dwell detection."""
        self.movement_threshold = threshold
    
    def update_position(self, position):
        """Update cursor position and return movement state."""
        current_time = time.time()
        
        if self.last_position is None:
            self.last_position = position
            self.last_update_time = current_time
            return 'dwelling'  # Start in dwelling state
        
        # Calculate movement distance
        dx = abs(position[0] - self.last_position[0])
        dy = abs(position[1] - self.last_position[1])
        distance = max(dx, dy)  # Use max distance for consistency with dwell detection
        
        # Calculate velocity
        time_delta = current_time - self.last_update_time
        if time_delta > 0:
            velocity = distance / time_delta
            self.movement_velocity_history.append(velocity)
            if len(self.movement_velocity_history) > self.velocity_window:
                self.movement_velocity_history.pop(0)
        
        # Determine if cursor is moving based on distance and velocity
        is_moving = False
        
        # Check immediate movement
        if distance >= self.movement_threshold:
            is_moving = True
            self.last_movement_time = current_time
        
        # Also check average velocity over recent history
        if len(self.movement_velocity_history) > 0:
            avg_velocity = sum(self.movement_velocity_history) / len(self.movement_velocity_history)
            if avg_velocity > self.movement_velocity_threshold:
                is_moving = True
                self.last_movement_time = current_time
        
        # Update position tracking
        self.last_position = position
        self.last_update_time = current_time
        
        # Determine state based on movement and timing
        time_since_movement = current_time - self.last_movement_time
        
        if is_moving:
            return 'moving'
        elif time_since_movement < self.dwell_delay:
            return 'settling'  # Just stopped moving, waiting to show widgets
        else:
            return 'dwelling'  # Settled and dwelling
            
    def should_show_widgets(self, movement_state):
        """Determine if widgets should be shown based on movement state."""
        return movement_state == 'dwelling'
        
    def should_hide_widgets(self, movement_state):
        """Determine if widgets should be hidden based on movement state."""
        return movement_state in ['moving', 'settling'] 