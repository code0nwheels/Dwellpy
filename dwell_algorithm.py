class DwellDetector:
    """
    Dwell detection algorithm that detects when the mouse cursor stays
    within a small area for a defined period of time.
    
    The algorithm uses a counter-based approach with a movement threshold
    instead of time-based calculations for better performance and accuracy.
    """
    
    def __init__(self, radius=5, dwell_time=1.0):
        # Configuration parameters
        self.move_limit = radius         # Maximum distance cursor can move while still considering it "dwelling"
        self.click_time = int(dwell_time / 0.1)  # Convert time to counter ticks (each tick = 100ms)
        
        # State tracking variables
        self.last_position = None        # Last recorded mouse position
        self.dwell_counter = 0           # Counter that tracks how long cursor has been dwelling
        self.debug_mode = False          # Enable/disable debug output
        self.waiting_for_exit = False    # Track if we're waiting for cursor to leave radius
        self.last_dwell_point = None     # Last position where dwell was detected
    
    def add_position(self, position):
        """
        Process a new mouse position and update the dwell state.
        
        This method handles movement detection and counter management.
        The counter increments when the cursor stays within the move_limit
        and resets when movement exceeds the threshold.
        
        Args:
            position: Tuple (x, y) representing cursor position
        """
        # Initialize last_position if this is the first update
        if self.last_position is None:
            self.last_position = position
            return
        
        # Calculate absolute distance in X and Y directions separately
        # This allows for more precise movement detection than euclidean distance
        dx = abs(position[0] - self.last_position[0])
        dy = abs(position[1] - self.last_position[1])
        
        # Check if cursor moved beyond the threshold in either direction
        if dx >= self.move_limit or dy >= self.move_limit:
            # Movement detected - reset the dwell counter
            if self.debug_mode and self.dwell_counter > 0:
                print(f"Movement detected ({dx}, {dy}) - resetting counter")
            self.dwell_counter = 0
        else:
            # Cursor is dwelling within threshold - increment counter
            self.dwell_counter += 1
            if self.debug_mode and self.dwell_counter % 3 == 0:
                print(f"Dwelling: counter = {self.dwell_counter}/{self.click_time}")
        
        # Store current position for next comparison
        self.last_position = position
    
    def check_dwell(self):
        """
        Check if the cursor has dwelled long enough to trigger an action.
        
        Returns:
            tuple: (is_dwelling, position)
                - is_dwelling: Boolean indicating if dwell threshold was reached
                - position: The position where dwelling occurred or None
        """
        # Skip if we don't have a position yet
        if self.last_position is None:
            return False, None
        
        # Check if counter has exceeded the threshold
        if self.dwell_counter > self.click_time:
            if self.debug_mode:
                print(f"Dwell detected! Counter: {self.dwell_counter}")
                
            # Reset counter to negative value
            # This creates a delay period before the next dwell can trigger,
            # preventing accidental double-clicks and allowing time to move away
            self.dwell_counter = -self.click_time
            
            # Return dwell event with current position
            return True, self.last_position
            
        return False, None

    def calculate_distance(self, position1, position2):
        """
        Calculate the Euclidean distance between two positions.
        
        Args:
            position1: Tuple (x, y) representing the first position.
            position2: Tuple (x, y) representing the second position.
        
        Returns:
            float: The Euclidean distance between the two positions.
        """
        dx = position1[0] - position2[0]
        dy = position1[1] - position2[1]
        return (dx ** 2 + dy ** 2) ** 0.5

    def update(self, current_position):
        """
        Update the dwell detection logic with the current cursor position.
        
        Args:
            current_position: Tuple (x, y) representing the current cursor position.
        
        Returns:
            bool: True if a dwell action is detected, False otherwise.
        """
        # If we're waiting for cursor to exit radius
        if self.waiting_for_exit:
            # Check if cursor has moved outside previous dwell point
            distance = self.calculate_distance(current_position, self.last_dwell_point)
            if distance > self.move_limit:
                # Reset the waiting flag when cursor leaves radius
                self.waiting_for_exit = False
            return False  # Don't trigger clicks while waiting for exit
        
        # Regular dwell detection logic
        self.add_position(current_position)
        dwell_detected, position = self.check_dwell()
        
        # When dwell is detected and click performed:
        if dwell_detected:
            self.last_dwell_point = current_position
            self.waiting_for_exit = True  # Set flag to wait for cursor to exit radius
            return True
        
        return False