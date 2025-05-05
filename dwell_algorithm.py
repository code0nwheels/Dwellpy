import numpy as np
import time

class DwellDetector:
    """Optimized dwell detection algorithm with minimal latency and proper click behavior."""
    
    def __init__(self, radius=8, dwell_time=0.2, history_time=1.0):
        self.radius = radius
        self.dwell_time = dwell_time
        self.history_time = history_time 
        self.positions = []
        self.timestamps = []
        self.hover_start_time = None
        self.last_position = None
        self.last_check_time = 0
        self.debug_mode = False  # Set to True for debugging output
        
        # Add state tracking for click behavior
        self.has_clicked = False        # Track if we've already clicked
        self.click_center = None        # The center where the last click happened
        self.needs_exit_radius = False  # Track if cursor needs to exit radius before new clicks
    
    def add_position(self, position):
        """Track positions and check for radius exit condition."""
        current_time = time.time()
        
        # Store new position
        self.positions.append(position)
        self.timestamps.append(current_time)
        
        # Limit history 
        max_history = min(30, int(self.history_time / 0.01))
        if len(self.positions) > max_history:
            self.positions = self.positions[-max_history:]
            self.timestamps = self.timestamps[-max_history:]
        
        # Check if cursor has exited the click radius if we need that
        if self.needs_exit_radius and self.click_center is not None:
            dx = position[0] - self.click_center[0]
            dy = position[1] - self.click_center[1]
            distance = (dx*dx + dy*dy) ** 0.5
            
            # If moved outside radius, allow new clicks
            if distance > self.radius:
                if self.debug_mode:
                    print(f"Cursor exited click radius ({distance:.1f}px) - allowing new clicks")
                self.needs_exit_radius = False
                self.has_clicked = False
        
        # Regular movement checking to reset hover timer
        if self.last_position and self.hover_start_time is not None:
            dx = position[0] - self.last_position[0]
            dy = position[1] - self.last_position[1]
            dist = (dx*dx + dy*dy) ** 0.5
            
            if dist > self.radius * 0.7:
                if self.debug_mode:
                    print(f"Movement detected ({dist:.1f}px) - resetting hover timer")
                self.hover_start_time = None
        
        self.last_position = position
    
    def apply_moving_average(self, window_size=3):
        """Apply moving average with smaller window to avoid oversmoothing."""
        if len(self.positions) < 2:
            return self.positions.copy()
                
        smoothed = []
        for i in range(len(self.positions)):
            # Define window with bounds checking
            start = max(0, i - window_size + 1)
            window = self.positions[start:i+1]
            
            # Calculate average position
            avg_x = sum(p[0] for p in window) / len(window)
            avg_y = sum(p[1] for p in window) / len(window)
            
            smoothed.append((avg_x, avg_y))
                
        return smoothed
    
    def detect_stable_hover(self, positions):
        """Ultra-fast hover detection with minimal computation."""
        if len(positions) < 2:
            return False, None
        
        # Calculate bounding box of recent positions
        min_x = min(p[0] for p in positions)
        max_x = max(p[0] for p in positions)
        min_y = min(p[1] for p in positions)
        max_y = max(p[1] for p in positions)
        
        # Check if bounding box fits within diameter
        width = max_x - min_x
        height = max_y - min_y
        
        # If either dimension exceeds diameter, not hovering
        if width > self.radius*2 or height > self.radius*2:
            return False, None
        
        # Calculate center
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        return True, (int(center_x), int(center_y))
    
    def check_directional_movement(self, positions):
        """Check if points show consistent directional movement."""
        if len(positions) < 5:
            return False
            
        # Get first and last position in window
        start_pos = np.array(positions[0])
        end_pos = np.array(positions[-1])
        
        # Calculate distance between start and end
        path_length = np.sqrt(np.sum((end_pos - start_pos) ** 2))
        
        # If path length is greater than half the radius, it's likely
        # intentional movement rather than hovering
        if path_length > self.radius * 0.5:
            if self.debug_mode:
                print(f"Directional movement detected: path length {path_length:.1f}px")
            return True
        
        return False
    
    def check_dwell(self):
        """Fast dwell checking algorithm with click-once behavior."""
        if len(self.positions) < 3:
            return False, None
        
        # Don't allow new clicks until cursor exits radius
        if self.has_clicked and self.needs_exit_radius:
            return False, None
        
        current_time = time.time()
        
        # Check less frequently to reduce CPU usage, but still responsive
        if current_time - self.last_check_time < 0.01:
            return False, None
        self.last_check_time = current_time
        
        # Quick check if hovering
        recent_positions = self.positions[-min(8, len(self.positions)):]
        
        # Apply light smoothing to reduce jitter
        smoothed_positions = self.apply_moving_average(window_size=2)[-len(recent_positions):]
        
        # Check for directional movement first
        if self.check_directional_movement(smoothed_positions):
            self.hover_start_time = None
            return False, None
        
        # Check if positions represent stable hovering
        is_hovering, center = self.detect_stable_hover(smoothed_positions)
        
        if not is_hovering:
            self.hover_start_time = None
            return False, None
        
        # Start timing if not already
        if self.hover_start_time is None:
            self.hover_start_time = current_time
            if self.debug_mode:
                print(f"Hover started at {center}")
            return False, None
        
        # Calculate hover duration
        hover_duration = current_time - self.hover_start_time
        
        # Check if hit threshold and ready to click
        if hover_duration >= self.dwell_time:
            if self.debug_mode:
                print(f"Dwell complete: {hover_duration:.3f}s")
            
            # Set flags to prevent continuous clicking
            self.has_clicked = True
            self.needs_exit_radius = True
            self.click_center = center
            
            # Reset hover timer
            self.hover_start_time = None
            
            return True, center
        
        # Still hovering but not long enough yet
        if self.debug_mode and (int(hover_duration * 20) % 4) == 0:  # Occasional updates
            print(f"Hovering: {hover_duration:.2f}s / {self.dwell_time:.2f}s")
        
        return False, None