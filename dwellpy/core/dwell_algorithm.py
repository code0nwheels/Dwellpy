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
        self.dwell_time = dwell_time     # Store original time value for UI representation
        
        # State tracking variables
        self.last_position = None        # Last recorded mouse position
        self.dwell_counter = 0           # Counter that tracks how long cursor has been dwelling
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
        # Skip processing if we're waiting for cursor to exit previous dwell point
        if self.waiting_for_exit and self.last_dwell_point is not None:
            # Check if cursor has moved outside previous dwell point
            dx = abs(position[0] - self.last_dwell_point[0])
            dy = abs(position[1] - self.last_dwell_point[1])
            
            # If cursor has moved outside radius, clear the waiting flag
            if dx >= self.move_limit or dy >= self.move_limit:
                self.waiting_for_exit = False
                self.last_dwell_point = None
            
            # Don't increment counter while waiting for exit
            # This effectively prevents new dwells until cursor moves
            return
        
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
            self.dwell_counter = 0
        else:
            # Cursor is dwelling within threshold - increment counter
            self.dwell_counter += 1
        
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
        
        # Skip if we're waiting for cursor to exit previous dwell radius
        if self.waiting_for_exit:
            return False, None
        
        # Check if counter has exceeded the threshold
        if self.dwell_counter > self.click_time:
            # Reset counter to negative value
            # This creates a delay period before the next dwell can trigger,
            # preventing accidental double-clicks and allowing time to move away
            self.dwell_counter = -self.click_time
            
            # Set waiting_for_exit flag to prevent repeated dwells in same spot
            self.waiting_for_exit = True
            self.last_dwell_point = self.last_position
            
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