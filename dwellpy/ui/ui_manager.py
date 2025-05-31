"""UI management for the Dwell Clicker application."""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QPushButton, 
                           QHBoxLayout, QVBoxLayout, QFrame)
from PyQt6.QtCore import Qt, QSize, QTimer, QCoreApplication
from PyQt6.QtGui import QCursor
from .scroll_widget import ScrollWidget
from .menu_widget import MenuWidget
import time

# Updated imports for new structure
try:
    from ..config.constants import (
        Colors, BUTTON_SIZE, LAYOUT_MARGIN, LAYOUT_SPACING, BORDER_RADIUS, Fonts,
        CONTRACT_DELAY, EXPAND_DELAY, CONTRACT_BUTTON_SIZE, CONTRACT_BUTTON_TEXT,
        EXPANSION_DIRECTIONS, DEFAULT_EXPANSION_DIRECTION, SCREEN_EDGE_MARGIN
    )
except ImportError:
    # Fallback constants for testing
    class Colors:
        DARK_BG = "#1e1e1e"
        DARK_BUTTON_BG = "#2d2d2d"
        TEXT_COLOR = "#ffffff"
        BLUE_ACCENT = "#0078d7"
        GREEN_ACCENT = "#2ecc71"
        RED_ACCENT = "#e74c3c"
        BORDER_COLOR = "#3c3c3c"
        DISABLED_TEXT = "#999999"
        BLUE_HOVER = "#0069c0"
        GREEN_HOVER = "#27ae60"
        RED_HOVER = "#d63031"
    
    BUTTON_SIZE = (55, 55)
    LAYOUT_MARGIN = 2
    LAYOUT_SPACING = 2
    BORDER_RADIUS = 5
    
    # UI Contraction fallback constants
    CONTRACT_DELAY = 1000
    EXPAND_DELAY = 100
    CONTRACT_BUTTON_SIZE = (40, 40)
    CONTRACT_BUTTON_TEXT = "≡"
    EXPANSION_DIRECTIONS = ['auto', 'horizontal', 'vertical']
    DEFAULT_EXPANSION_DIRECTION = 'auto'
    SCREEN_EDGE_MARGIN = 50


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


class DwellClickerUI:
    """UI Manager for the Dwell Clicker application with temporary/default modes."""
    
    def __init__(self, click_manager, dwell_detector, button_manager, window_manager):
        self.click_manager = click_manager
        self.dwell_detector = dwell_detector
        self.button_manager = button_manager
        self.window_manager = window_manager
        
        # These will be set later
        self.settings_manager = None
        self.exit_manager = None
        
        # State variables
        self.is_active = False
        
        # Mode tracking
        self.current_mode = "LEFT"       # Currently active mode
        self.default_mode = "LEFT"       # Mode to return to after temporary use
        self.is_temporary_mode = False   # Flag for temporary mode
        self.last_mode_selection = None  # For tracking double selection
        self.last_selection_time = 0     # For timing double selection
        
        self.drag_state = None  # Can be None, "down", or "up"
        
        # Store button references
        self.buttons = {}
        
        # Transparency state
        self.is_cursor_over_window = False
        self.opacity_timer = QTimer()
        self.opacity_timer.setSingleShot(True)
        self.opacity_timer.timeout.connect(self.set_transparent)

        # UI Contraction state
        self.is_contracted = False
        self.contract_timer = QTimer()
        self.contract_timer.setSingleShot(True)
        self.contract_timer.timeout.connect(self.contract_ui)
        self.expand_timer = QTimer()
        self.expand_timer.setSingleShot(True)
        self.expand_timer.timeout.connect(self.expand_ui)
        
        # Store original layout and widgets for contraction
        self.original_layout = None
        self.contracted_button = None
        self.current_expansion_direction = None  # Track current expansion direction
        self.original_window_size = None  # Store original window size

        self.scroll_widget = ScrollWidget()
        self.scroll_widget.set_active(False)  # Start inactive

        # Track scroll widget hover state
        self.scroll_hover = None
        self.scroll_dwell_start_time = None
        self.scroll_dwell_triggered = False
        
        # Initialize menu widget
        self.menu_widget = MenuWidget()
        self.menu_widget.set_active(False)  # Start inactive
        self.menu_widget.menu_item_triggered.connect(self.handle_menu_item_selection)
        self.menu_widget.ui_manager = self  # Set reference for state checking
        
        # Track menu widget hover state
        self.menu_hover = None
        self.menu_dwell_start_time = None
        self.menu_dwell_triggered = False
        
        # Track widget initial orientation for consistent positioning
        self.widgets_initial_orientation = None
        
        # Movement state tracking for widget visibility
        initial_delay = 0.2  # Default delay, will be updated when settings manager connects
        self.cursor_movement_detector = CursorMovementDetector(dwell_delay=initial_delay)
        self.widgets_hidden_for_movement = False
        
        # UI setup
        self.setup_ui()
        
        # Register button commands
        self.register_button_commands()
    
    def connect_managers(self, settings_manager, exit_manager):
        """Connect to the settings and exit managers after initialization."""
        self.settings_manager = settings_manager
        self.exit_manager = exit_manager
        
        # Give settings manager a reference to this UI manager for transparency updates
        self.settings_manager.ui_manager = self
        
        # Give exit manager a reference to this UI manager for cleanup
        self.exit_manager.ui_manager = self
        
        # Apply transparency settings once settings manager is connected
        self.apply_transparency_settings()
        
        # Apply contraction settings
        self.apply_contraction_settings()
        
        # Apply expansion settings to ensure proper initial layout
        self.apply_expansion_settings()
        
        # Apply default active state if configured BEFORE applying scroll settings
        if self.settings_manager.get_setting('default_active', False):
            self.is_active = True
            self.update_button_states()
        
        # Apply scroll widget settings AFTER setting the active state
        self.apply_scroll_settings()
        
        # Apply menu widget settings AFTER setting the active state
        self.apply_menu_settings()
        
        # Apply widget appearance settings
        self.apply_widget_appearance_settings()
    
    def register_button_commands(self):
        """Register button commands with the button manager."""
        # Register basic button commands
        self.button_manager.register_command("ON_OFF", self.toggle_active)
        self.button_manager.register_command("LEFT", lambda: self.set_mode("LEFT"))
        self.button_manager.register_command("DOUBLE", lambda: self.set_mode("DOUBLE"))
        self.button_manager.register_command("DRAG", lambda: self.set_mode("DRAG"))
        self.button_manager.register_command("RIGHT", lambda: self.set_mode("RIGHT"))
        self.button_manager.register_command("SCROLL", self.toggle_scroll_widget)
        self.button_manager.register_command("MENU", self.toggle_menu_widget)
        self.button_manager.register_command("CONTRACTED", self.expand_ui)
        # SETUP and EXIT will be set by the respective managers
    
    def setup_ui(self):
        """Set up the main UI components."""
        # Create main window without frame
        self.window = QMainWindow()
        self.window.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.window.setFixedHeight(60)  # Set fixed height for the toolbar
        self.window.setStyleSheet(f"background-color: {Colors.DARK_BG};")
        
        # Set up window transparency events
        self.setup_transparency_events()
        
        # Add close event handler for both widgets cleanup
        original_close_event = self.window.closeEvent
        def close_event_handler(event):
            self.cleanup_scroll_widget()
            self.cleanup_menu_widget()
            if original_close_event:
                original_close_event(event)
            else:
                event.accept()
        self.window.closeEvent = close_event_handler
        
        # Create central widget
        central_widget = QWidget()
        central_widget.setStyleSheet(f"background-color: {Colors.DARK_BG};")
        self.window.setCentralWidget(central_widget)
        
        # Create button layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN)
        button_layout.setSpacing(LAYOUT_SPACING)
        
        # Set the layout to the central widget
        central_widget.setLayout(button_layout)
        
        # Store original layout for contraction
        self.original_layout = button_layout
        
        # Create buttons
        # ON/OFF button
        self.buttons["ON_OFF"] = self.create_button("ON/OFF", "green", "ON_OFF")
        button_layout.addWidget(self.buttons["ON_OFF"])
        
        # Click type buttons
        self.buttons["LEFT"] = self.create_button("LEFT", "blue", "LEFT")
        button_layout.addWidget(self.buttons["LEFT"])
        
        self.buttons["DOUBLE"] = self.create_button("DOUBLE", "blue", "DOUBLE")
        button_layout.addWidget(self.buttons["DOUBLE"])
        
        self.buttons["DRAG"] = self.create_button("DRAG", "blue", "DRAG")
        button_layout.addWidget(self.buttons["DRAG"])
        
        self.buttons["RIGHT"] = self.create_button("RIGHT", "blue", "RIGHT")
        button_layout.addWidget(self.buttons["RIGHT"])
        
        # Scroll toggle button
        self.buttons["SCROLL"] = self.create_button("SCROLL", "gray", "SCROLL")
        button_layout.addWidget(self.buttons["SCROLL"])
        
        # Menu toggle button
        self.buttons["MENU"] = self.create_button("MENU", "gray", "MENU")
        button_layout.addWidget(self.buttons["MENU"])
        
        # Utility buttons
        self.buttons["SETUP"] = self.create_button("SETUP", "gray", "SETUP")
        button_layout.addWidget(self.buttons["SETUP"])
        
        self.buttons["MOVE"] = self.create_button("MOVE", "gray", "MOVE")
        button_layout.addWidget(self.buttons["MOVE"])
        
        self.buttons["EXIT"] = self.create_button("EXIT", "red", "EXIT")
        button_layout.addWidget(self.buttons["EXIT"])
        
        # Highlight initial mode
        self.update_button_states()
    
    def setup_transparency_events(self):
        """Set up window transparency based on cursor presence."""
        # Store original event handlers
        self.window.original_enterEvent = self.window.enterEvent
        self.window.original_leaveEvent = self.window.leaveEvent
        
        # Set custom event handlers
        self.window.enterEvent = self.on_window_enter
        self.window.leaveEvent = self.on_window_leave
        
        # Start with transparent state if enabled
        self.apply_transparency_settings()
    
    def apply_transparency_settings(self):
        """Apply transparency settings from the settings manager."""
        if not self.settings_manager:
            # Default to opaque if settings not available yet
            self.window.setWindowOpacity(1.0)
            return
            
        transparency_enabled = self.settings_manager.get_setting('transparency_enabled', False)
        
        if transparency_enabled and not self.is_cursor_over_window:
            transparency_level = self.settings_manager.get_setting('transparency_level', 70)
            # Convert percentage to opacity (70% transparent = 0.3 opaque)
            opacity = (100 - transparency_level) / 100.0
            self.window.setWindowOpacity(opacity)
        else:
            self.window.setWindowOpacity(1.0)
    
    def apply_contraction_settings(self):
        """Apply UI contraction settings from the settings manager."""
        if not self.settings_manager:
            return
        
        contract_enabled = self.settings_manager.get_setting('contract_ui_enabled', False)
        
        # If contraction is disabled and UI is currently contracted, expand it
        if not contract_enabled and self.is_contracted:
            self.expand_ui()
        
        # If contraction is enabled and cursor is not over window, start contraction timer
        elif contract_enabled and not self.is_cursor_over_window and not self.is_contracted:
            self.contract_timer.start(CONTRACT_DELAY)
    
    def apply_expansion_settings(self):
        """Apply UI expansion direction settings immediately."""
        if not self.settings_manager:
            return
        
        # If UI is currently expanded (not contracted), re-layout with new direction
        if not self.is_contracted:
            # Determine new expansion direction
            new_direction = self.determine_expansion_direction()
            
            # Only re-layout if direction actually changed
            if new_direction != self.current_expansion_direction:
                self.current_expansion_direction = new_direction
                
                # Create a new central widget with the correct layout
                self._rebuild_layout(new_direction)
    
    def _rebuild_layout(self, direction):
        """Rebuild the UI layout with the specified direction."""
        # Store current window position before resizing
        current_pos = self.window.pos()
        
        # Create a new central widget to avoid layout conflicts
        new_central_widget = QWidget()
        new_central_widget.setStyleSheet(f"background-color: {Colors.DARK_BG};")
        
        # Create new layout based on direction
        if direction == 'vertical':
            # Create vertical layout
            new_layout = QVBoxLayout()
            new_layout.setContentsMargins(LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN)
            new_layout.setSpacing(LAYOUT_SPACING)
            
            # Calculate window size for vertical layout
            total_buttons = len(self.buttons)
            window_height = (total_buttons * BUTTON_SIZE[1] + 
                           (total_buttons - 1) * LAYOUT_SPACING + 
                           LAYOUT_MARGIN * 2)
            window_width = BUTTON_SIZE[0] + (LAYOUT_MARGIN * 2)
            
            self.window.setFixedSize(window_width, window_height)
            
        else:  # horizontal
            # Create horizontal layout
            new_layout = QHBoxLayout()
            new_layout.setContentsMargins(LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN)
            new_layout.setSpacing(LAYOUT_SPACING)
            
            # Calculate window size for horizontal layout
            total_buttons = len(self.buttons)
            window_width = (total_buttons * BUTTON_SIZE[0] + 
                           (total_buttons - 1) * LAYOUT_SPACING + 
                           LAYOUT_MARGIN * 2)
            window_height = BUTTON_SIZE[1] + (LAYOUT_MARGIN * 2)
            
            self.window.setFixedSize(window_width, window_height)
        
        # Ensure window stays within screen bounds after resizing
        self._ensure_window_in_bounds(current_pos)
        
        # Set the layout to the new central widget
        new_central_widget.setLayout(new_layout)
        
        # Add all buttons to the new layout
        button_order = ["ON_OFF", "LEFT", "DOUBLE", "DRAG", "RIGHT", "SCROLL", "MENU", "SETUP", "MOVE", "EXIT"]
        for button_id in button_order:
            if button_id in self.buttons:
                button = self.buttons[button_id]
                button.show()
                new_layout.addWidget(button)
        
        # Add the contracted button back to layout (hidden)
        if self.contracted_button:
            new_layout.addWidget(self.contracted_button)
        
        # Replace the central widget
        self.window.setCentralWidget(new_central_widget)
        
        # Store the new layout
        self.original_layout = new_layout
    
    def _calculate_optimal_expansion_position(self, contracted_pos, expanded_size):
        """Calculate the optimal position for the expanded window to avoid going off-screen."""
        try:
            from PyQt6.QtGui import QGuiApplication
            
            # Get all available screens
            app = QGuiApplication.instance()
            screens = app.screens()
            
            # Calculate the combined desktop geometry (all monitors)
            desktop_rect = None
            for screen in screens:
                screen_geometry = screen.geometry()
                if desktop_rect is None:
                    desktop_rect = screen_geometry
                else:
                    desktop_rect = desktop_rect.united(screen_geometry)
            
            # If we couldn't get screen info, return original position
            if desktop_rect is None:
                return contracted_pos.x(), contracted_pos.y()
            
            # Calculate available space in each direction from the contracted position
            space_right = desktop_rect.right() - (contracted_pos.x() + CONTRACT_BUTTON_SIZE[0])
            space_left = contracted_pos.x() - desktop_rect.left()
            space_bottom = desktop_rect.bottom() - (contracted_pos.y() + CONTRACT_BUTTON_SIZE[1])
            space_top = contracted_pos.y() - desktop_rect.top()
            
            # Determine optimal position based on expansion direction and available space
            direction = self.current_expansion_direction or 'horizontal'
            
            if direction == 'horizontal':
                # For horizontal expansion, try to keep the same Y position
                new_y = contracted_pos.y()
                
                # Check if we can expand to the right from current position
                if space_right >= expanded_size.width() - CONTRACT_BUTTON_SIZE[0]:
                    # Enough space to the right - keep current X position
                    new_x = contracted_pos.x()
                else:
                    # Not enough space to the right - position so the right edge aligns with desktop edge
                    new_x = desktop_rect.right() - expanded_size.width()
                    
                    # Make sure we don't go off the left edge
                    if new_x < desktop_rect.left():
                        new_x = desktop_rect.left()
                        
            else:  # vertical expansion
                # For vertical expansion, try to keep the same X position
                new_x = contracted_pos.x()
                
                # Check if we can expand downward from current position
                if space_bottom >= expanded_size.height() - CONTRACT_BUTTON_SIZE[1]:
                    # Enough space below - keep current Y position
                    new_y = contracted_pos.y()
                else:
                    # Not enough space below - position so the bottom edge aligns with desktop edge
                    new_y = desktop_rect.bottom() - expanded_size.height()
                    
                    # Make sure we don't go off the top edge
                    if new_y < desktop_rect.top():
                        new_y = desktop_rect.top()
            
            # Final bounds check across all monitors
            new_x = max(desktop_rect.left(), min(new_x, desktop_rect.right() - expanded_size.width()))
            new_y = max(desktop_rect.top(), min(new_y, desktop_rect.bottom() - expanded_size.height()))
            
            return new_x, new_y
            
        except Exception:
            # Fallback to original position
            return contracted_pos.x(), contracted_pos.y()

    def _ensure_window_in_bounds(self, preferred_pos):
        """Ensure the window stays within screen bounds, adjusting position if necessary."""
        try:
            from PyQt6.QtGui import QGuiApplication
            
            # Get all available screens
            app = QGuiApplication.instance()
            screens = app.screens()
            
            # Calculate the combined desktop geometry (all monitors)
            desktop_rect = None
            for screen in screens:
                screen_geometry = screen.geometry()
                if desktop_rect is None:
                    desktop_rect = screen_geometry
                else:
                    desktop_rect = desktop_rect.united(screen_geometry)
            
            # If we couldn't get screen info, keep current position
            if desktop_rect is None:
                return
            
            window_size = self.window.size()
            
            # If we're expanding from a contracted state, use optimal positioning
            if hasattr(self, '_expanding_from_contracted') and self._expanding_from_contracted:
                new_x, new_y = self._calculate_optimal_expansion_position(preferred_pos, window_size)
                self._expanding_from_contracted = False  # Reset flag
            else:
                # Calculate the bounds across all monitors
                min_x = desktop_rect.left()
                min_y = desktop_rect.top()
                max_x = desktop_rect.right() - window_size.width()
                max_y = desktop_rect.bottom() - window_size.height()
                
                # For horizontal expansion near screen edges, we need special handling
                if not self.is_contracted:  # Only during expansion
                    # If we're expanding and the preferred position would put us off-screen
                    if preferred_pos.x() < min_x:
                        # Too far left - position at left edge
                        new_x = min_x
                    elif preferred_pos.x() > max_x:
                        # Too far right - position at right edge
                        new_x = max_x
                    else:
                        # Position is fine horizontally
                        new_x = preferred_pos.x()
                    
                    if preferred_pos.y() < min_y:
                        # Too far up - position at top edge
                        new_y = min_y
                    elif preferred_pos.y() > max_y:
                        # Too far down - position at bottom edge
                        new_y = max_y
                    else:
                        # Position is fine vertically
                        new_y = preferred_pos.y()
                else:
                    # For contraction, just ensure within bounds
                    new_x = max(min_x, min(preferred_pos.x(), max_x))
                    new_y = max(min_y, min(preferred_pos.y(), max_y))
            
            # Move window to the adjusted position
            self.window.move(new_x, new_y)
            
        except Exception:
            # If there's any error, keep the window at its current position
            pass
    
    def apply_scroll_settings(self):
        """Apply scroll widget settings from the settings manager."""
        if not self.settings_manager:
            return
        
        # Get scroll settings
        scroll_enabled = self.settings_manager.get_setting('scroll_enabled', True)
        scroll_offset = self.settings_manager.get_setting('scroll_offset', 50)
        scroll_angle = self.settings_manager.get_setting('scroll_angle', 45)
        scroll_speed = self.settings_manager.get_setting('scroll_speed', 100)
        scroll_amount = self.settings_manager.get_setting('scroll_amount', 3)
        scroll_opacity_base = self.settings_manager.get_setting('scroll_opacity_base', 70)
        scroll_opacity_hover = self.settings_manager.get_setting('scroll_opacity_hover', 90)
        
        # Apply settings to scroll widget
        self.scroll_widget.set_offset(distance=scroll_offset, angle=scroll_angle)
        self.scroll_widget.set_scroll_speed(interval=scroll_speed, amount=scroll_amount)
        self.scroll_widget.set_opacity(
            base=scroll_opacity_base,  # Pass raw percentage values
            hover=scroll_opacity_hover
        )
        
        # Enable/disable scroll widget based on setting and active state
        should_be_active = self.is_active and scroll_enabled
        self.scroll_widget.set_active(should_be_active)
        
        # Update button states to reflect scroll setting changes
        self.update_button_states()
    
    def on_window_enter(self, event):
        """Handle cursor entering the window area."""
        self.is_cursor_over_window = True
        self.opacity_timer.stop()  # Cancel any pending transparency change
        self.contract_timer.stop()  # Cancel any pending contraction
        
        # Always make opaque when cursor is over window
        self.set_opaque()
        
        # Expand UI if contracted and contraction is enabled
        if self.is_contracted and self.settings_manager and self.settings_manager.get_setting('contract_ui_enabled', False):
            self.expand_timer.start(EXPAND_DELAY)
        
        # Call original event handler if it exists
        if hasattr(self.window, 'original_enterEvent'):
            self.window.original_enterEvent(event)
    
    def on_window_leave(self, event):
        """Handle cursor leaving the window area."""
        self.is_cursor_over_window = False
        self.expand_timer.stop()  # Cancel any pending expansion
        
        # Only set transparency if enabled in settings
        if self.settings_manager and self.settings_manager.get_setting('transparency_enabled', False):
            # Add a small delay before making transparent to avoid flickering
            # when cursor moves between buttons
            self.opacity_timer.start(100)  # 100ms delay
        
        # Start contraction timer if contraction is enabled and UI is not already contracted
        if (self.settings_manager and 
            self.settings_manager.get_setting('contract_ui_enabled', False) and 
            not self.is_contracted):
            self.contract_timer.start(CONTRACT_DELAY)
        
        # Call original event handler if it exists
        if hasattr(self.window, 'original_leaveEvent'):
            self.window.original_leaveEvent(event)
    
    def set_opaque(self):
        """Make the window fully opaque."""
        self.window.setWindowOpacity(1.0)
    
    def set_transparent(self):
        """Make the window transparent if cursor is not over it and transparency is enabled."""
        if not self.is_cursor_over_window and self.settings_manager:
            transparency_enabled = self.settings_manager.get_setting('transparency_enabled', False)
            if transparency_enabled:
                transparency_level = self.settings_manager.get_setting('transparency_level', 70)
                # Convert percentage to opacity (70% transparent = 0.3 opaque)
                opacity = (100 - transparency_level) / 100.0
                self.window.setWindowOpacity(opacity)
    
    def update_contracted_button_state(self):
        """Update the text and style of the contracted button to match current status."""
        if not self.contracted_button or not self.is_contracted:
            return
            
        status_text = self.get_current_status_text()
        self.contracted_button.setText(status_text)
        
        # Update button style to match current state
        if not self.is_active:
            # OFF state - red like the ON/OFF button when off
            self.contracted_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.RED_ACCENT};
                    color: {Colors.TEXT_COLOR};
                    border: 1px solid {Colors.RED_ACCENT};
                    border-radius: {BORDER_RADIUS}px;
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 8pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Colors.RED_HOVER};
                    border: 1px solid {Colors.RED_HOVER};
                }}
            """)
        elif self.is_temporary_mode:
            # Temporary mode - red like temporary mode buttons
            self.contracted_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.RED_ACCENT};
                    color: {Colors.TEXT_COLOR};
                    border: 1px solid {Colors.RED_ACCENT};
                    border-radius: {BORDER_RADIUS}px;
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 8pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Colors.RED_HOVER};
                    border: 1px solid {Colors.RED_HOVER};
                }}
            """)
        else:
            # Default/permanent mode - blue like default mode buttons
            self.contracted_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.BLUE_ACCENT};
                    color: {Colors.TEXT_COLOR};
                    border: 1px solid {Colors.BLUE_ACCENT};
                    border-radius: {BORDER_RADIUS}px;
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 8pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Colors.BLUE_HOVER};
                    border: 1px solid {Colors.BLUE_HOVER};
                }}
            """)
    
    def contract_ui(self):
        """Contract the UI to a single button."""
        if self.is_contracted or not self.settings_manager:
            return
        
        # Don't contract if cursor is over window
        if self.is_cursor_over_window:
            return
        
        # Don't contract if settings dialog is open
        if (self.settings_manager.settings_dialog and 
            self.settings_manager.settings_dialog.isVisible()):
            return
        
        self.is_contracted = True
        
        # Store current window position before resizing
        current_pos = self.window.pos()
        
        # Determine and store expansion direction
        self.current_expansion_direction = self.determine_expansion_direction()
        
        # Store original window size
        self.original_window_size = self.window.size()
        
        # Hide all existing buttons
        for button in self.buttons.values():
            button.hide()
        
        # Create contracted button if it doesn't exist
        if not self.contracted_button:
            self.contracted_button = self.create_contracted_button()
            self.original_layout.addWidget(self.contracted_button)
        else:
            # Update the text to show current status
            self.update_contracted_button_state()
        
        # Show contracted button
        self.contracted_button.show()
        
        # Resize window to fit contracted button
        self.window.setFixedSize(
            CONTRACT_BUTTON_SIZE[0] + (LAYOUT_MARGIN * 2),
            CONTRACT_BUTTON_SIZE[1] + (LAYOUT_MARGIN * 2)
        )
        
        # Ensure window stays within screen bounds after resizing to contracted form
        self._ensure_window_in_bounds(current_pos)
    
    def expand_ui(self):
        """Expand the UI to show all buttons in the determined direction."""
        if not self.is_contracted:
            return
        
        # Set flag to indicate we're expanding from contracted state
        self._expanding_from_contracted = True
        
        self.is_contracted = False
        
        # Hide contracted button
        if self.contracted_button:
            self.contracted_button.hide()
        
        # Get the expansion direction
        direction = self.current_expansion_direction or 'horizontal'
        
        # Use the shared rebuild layout method
        self._rebuild_layout(direction)
        
        # Update scroll widget position if active
        if self.is_active and self.settings_manager and self.settings_manager.get_setting('scroll_enabled', True):
            try:
                from pynput.mouse import Controller
                mouse = Controller()
                pos = mouse.position
                self.update_scroll_widget_position(pos)
            except Exception:
                pass
    
    def clear_layout(self, layout):
        """Clear all widgets from a layout."""
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    # Remove widget from layout but don't delete it
                    widget = child.widget()
                    widget.setParent(None)
                elif child.layout():
                    # Recursively clear nested layouts
                    self.clear_layout(child.layout())
    
    def get_current_status_text(self):
        """Get the current status text for the contracted button."""
        if not self.is_active:
            return "OFF"
        
        # Show current mode, with indicator for temporary mode
        if self.is_temporary_mode:
            return f"{self.current_mode}*"  # Asterisk indicates temporary
        else:
            return self.current_mode
    
    def create_contracted_button(self):
        """Create the contracted button showing current status."""
        # Get current status text
        status_text = self.get_current_status_text()
        
        button = QPushButton(status_text)
        button.setFixedSize(CONTRACT_BUTTON_SIZE[0], CONTRACT_BUTTON_SIZE[1])
        button.setObjectName("CONTRACTED")  # Give it an ID for button manager
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Connect click to expand
        button.clicked.connect(self.expand_ui)
        
        # Add hover events for dwell detection
        original_enter_event = button.enterEvent
        original_leave_event = button.leaveEvent
        
        def custom_enter_event(event):
            self.button_manager.set_hover("CONTRACTED")
            if original_enter_event:
                original_enter_event(event)
        
        def custom_leave_event(event):
            self.button_manager.clear_hover("CONTRACTED")
            if original_leave_event:
                original_leave_event(event)
        
        button.enterEvent = custom_enter_event
        button.leaveEvent = custom_leave_event
        
        # Hide initially
        button.hide()
        
        # Store the button reference before applying state-based styling
        self.contracted_button = button
        
        # Apply initial state-based styling
        self.update_contracted_button_state()
        
        return button
    
    def create_button(self, text, color, button_id):
        """Create a styled button with hover behavior."""
        # Create button with fixed size
        button = QPushButton(text)
        button.setFixedSize(QSize(BUTTON_SIZE[0], BUTTON_SIZE[1]))
        button.setObjectName(button_id)  # Store ID as object name
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Style the button using Qt stylesheets
        if color == "blue":
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.DARK_BUTTON_BG};
                    color: {Colors.TEXT_COLOR};
                    border: 1px solid {Colors.BORDER_COLOR};
                    border-radius: {BORDER_RADIUS}px;
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 9pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Colors.DARK_BUTTON_BG};
                    border: 1px solid {Colors.BLUE_ACCENT};
                }}
            """)
        elif color == "green":
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.DARK_BUTTON_BG};
                    color: {Colors.TEXT_COLOR};
                    border: 1px solid {Colors.BORDER_COLOR};
                    border-radius: {BORDER_RADIUS}px;
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 9pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Colors.DARK_BUTTON_BG};
                    border: 1px solid {Colors.GREEN_ACCENT};
                }}
            """)
        elif color == "gray":
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.DARK_BUTTON_BG};
                    color: {Colors.TEXT_COLOR};
                    border: 1px solid {Colors.BORDER_COLOR};
                    border-radius: {BORDER_RADIUS}px;
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 9pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #3d3d3d;
                    border: 1px solid #5d5d5d;
                }}
            """)
        elif color == "red":
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.DARK_BUTTON_BG};
                    color: {Colors.TEXT_COLOR};
                    border: 1px solid {Colors.BORDER_COLOR};
                    border-radius: {BORDER_RADIUS}px;
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 9pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Colors.DARK_BUTTON_BG};
                    border: 1px solid {Colors.RED_ACCENT};
                }}
            """)
        
        # Connect signals
        button.clicked.connect(lambda: self.on_button_click(button_id))
        
        # Store original event handlers for the button
        original_enter_event = button.enterEvent
        original_leave_event = button.leaveEvent
        
        # Create custom event handlers
        def custom_enter_event(event):
            self.on_button_hover(button_id, event)
            # Call original handler if it exists
            if original_enter_event:
                original_enter_event(event)
        
        def custom_leave_event(event):
            self.on_button_leave(button_id, event)
            # Call original handler if it exists
            if original_leave_event:
                original_leave_event(event)
        
        # Replace event handlers
        button.enterEvent = custom_enter_event
        button.leaveEvent = custom_leave_event
        
        # Special handling for MOVE button
        if button_id == "MOVE":
            original_mouse_press_event = button.mousePressEvent
            button.mousePressEvent = lambda event: self.window_manager.start_drag(event, self.window)
        
        return button
    
    def on_button_click(self, button_id):
        """Handle physical clicks on buttons."""
        # For ON/OFF button, always allow regardless of active state
        if button_id == "ON_OFF":
            self.toggle_active()
            return
            
        # Don't allow other buttons if clicker is off
        if not self.is_active and button_id not in ["ON_OFF"]:
            return
            
        # Execute the appropriate command via button manager
        self.button_manager.execute_command(button_id)

    def on_button_hover(self, button_id, event):
        """Handle when mouse hovers over a button - visual feedback only."""
        # Store the current hover button in button manager
        self.button_manager.set_hover(button_id)
    
    def on_button_leave(self, button_id, event):
        """Handle when mouse leaves a button - visual feedback only."""
        # Clear the hover button in the button manager
        self.button_manager.clear_hover(button_id)
        
        # Don't clear MOVE button hover status while dragging
        if button_id == "MOVE" and self.window_manager.is_dragging:
            return
    
    def update_button_states(self):
        """Update button appearances to show temporary vs default modes."""
        # Reset all click type buttons
        for button_name in ["LEFT", "DOUBLE", "DRAG", "RIGHT"]:
            # Get the button
            button = self.buttons[button_name]
            
            # Check if clicker is inactive - if so, gray out all click buttons
            if not self.is_active:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.DARK_BUTTON_BG};
                        color: {Colors.DISABLED_TEXT};
                        border: 1px solid {Colors.BORDER_COLOR};
                        border-radius: {BORDER_RADIUS}px;
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        font-size: 9pt;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: #3d3d3d;
                        border: 1px solid #5d5d5d;
                    }}
                """)
            else:
                # Set default styling when active
                if button_name == self.default_mode:
                    # Default mode button - blue
                    button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {Colors.BLUE_ACCENT};
                            color: {Colors.TEXT_COLOR};
                            border: 1px solid {Colors.BLUE_ACCENT};
                            border-radius: {BORDER_RADIUS}px;
                            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                            font-size: 9pt;
                            font-weight: bold;
                        }}
                        QPushButton:hover {{
                            background-color: {Colors.BLUE_HOVER};
                            border: 1px solid {Colors.BLUE_HOVER};
                        }}
                    """)
                else:
                    # Non-default modes - dark gray
                    button.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {Colors.DARK_BUTTON_BG};
                            color: {Colors.TEXT_COLOR};
                            border: 1px solid {Colors.BORDER_COLOR};
                            border-radius: {BORDER_RADIUS}px;
                            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                            font-size: 9pt;
                            font-weight: bold;
                        }}
                        QPushButton:hover {{
                            background-color: #3d3d3d;
                            border: 1px solid {Colors.BLUE_ACCENT};
                        }}
                    """)
        
        # Highlight current mode (only when active)
        if self.is_active and self.is_temporary_mode:
            # Temporary mode - red
            self.buttons[self.current_mode].setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.RED_ACCENT};
                    color: {Colors.TEXT_COLOR};
                    border: 1px solid {Colors.RED_ACCENT};
                    border-radius: {BORDER_RADIUS}px;
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 9pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Colors.RED_HOVER};
                    border: 1px solid {Colors.RED_HOVER};
                }}
            """)
        
        # Update ON/OFF button
        if self.is_active:
            self.buttons["ON_OFF"].setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.GREEN_ACCENT};
                    color: {Colors.TEXT_COLOR};
                    border: 1px solid {Colors.GREEN_ACCENT};
                    border-radius: {BORDER_RADIUS}px;
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 9pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Colors.GREEN_HOVER};
                    border: 1px solid {Colors.GREEN_HOVER};
                }}
            """)
        else:
            self.buttons["ON_OFF"].setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.RED_ACCENT};
                    color: {Colors.TEXT_COLOR};
                    border: 1px solid {Colors.RED_ACCENT};
                    border-radius: {BORDER_RADIUS}px;
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 9pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {Colors.RED_HOVER};
                    border: 1px solid {Colors.RED_HOVER};
                }}
            """)
        
        # Style utility buttons - gray out when inactive
        for button_name in ["SETUP", "MOVE", "EXIT"]:
            if self.is_active:
                if button_name == "EXIT":
                    # EXIT button gets red hover
                    self.buttons[button_name].setStyleSheet(f"""
                        QPushButton {{
                            background-color: {Colors.DARK_BUTTON_BG};
                            color: {Colors.TEXT_COLOR};
                            border: 1px solid {Colors.BORDER_COLOR};
                            border-radius: {BORDER_RADIUS}px;
                            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                            font-size: 9pt;
                            font-weight: bold;
                        }}
                        QPushButton:hover {{
                            background-color: #3d3d3d;
                            border: 1px solid {Colors.RED_ACCENT};
                        }}
                    """)
                else:
                    # SETUP and MOVE buttons
                    self.buttons[button_name].setStyleSheet(f"""
                        QPushButton {{
                            background-color: {Colors.DARK_BUTTON_BG};
                            color: {Colors.TEXT_COLOR};
                            border: 1px solid {Colors.BORDER_COLOR};
                            border-radius: {BORDER_RADIUS}px;
                            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                            font-size: 9pt;
                            font-weight: bold;
                        }}
                        QPushButton:hover {{
                            background-color: #3d3d3d;
                            border: 1px solid #5d5d5d;
                        }}
                    """)
            else:
                # Grayed out when inactive
                hover_border = Colors.RED_ACCENT if button_name == "EXIT" else "#5d5d5d"
                self.buttons[button_name].setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.DARK_BUTTON_BG};
                        color: {Colors.DISABLED_TEXT};
                        border: 1px solid {Colors.BORDER_COLOR};
                        border-radius: {BORDER_RADIUS}px;
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        font-size: 9pt;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: #3d3d3d;
                        border: 1px solid {hover_border};
                    }}
                """)
        
        # Handle SCROLL button state separately
        if "SCROLL" in self.buttons:
            scroll_enabled = self.settings_manager.get_setting('scroll_enabled', True) if self.settings_manager else True
            
            # Consider both app active state and scroll enabled setting
            if self.is_active and scroll_enabled:
                # App is active and scroll is enabled - show as active (green)
                self.buttons["SCROLL"].setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.GREEN_ACCENT};
                        color: {Colors.TEXT_COLOR};
                        border: 1px solid {Colors.GREEN_ACCENT};
                        border-radius: {BORDER_RADIUS}px;
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        font-size: 9pt;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {Colors.GREEN_HOVER};
                        border: 1px solid {Colors.GREEN_HOVER};
                    }}
                """)
            elif self.is_active and not scroll_enabled:
                # App is active but scroll is disabled - show as normal inactive button
                self.buttons["SCROLL"].setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.DARK_BUTTON_BG};
                        color: {Colors.TEXT_COLOR};
                        border: 1px solid {Colors.BORDER_COLOR};
                        border-radius: {BORDER_RADIUS}px;
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        font-size: 9pt;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: #3d3d3d;
                        border: 1px solid #5d5d5d;
                    }}
                """)
            else:
                # App is inactive - show as grayed out (same as other buttons when inactive)
                self.buttons["SCROLL"].setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.DARK_BUTTON_BG};
                        color: {Colors.DISABLED_TEXT};
                        border: 1px solid {Colors.BORDER_COLOR};
                        border-radius: {BORDER_RADIUS}px;
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        font-size: 9pt;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: #3d3d3d;
                        border: 1px solid #5d5d5d;
                    }}
                """)
        
        # Handle MENU button state separately
        if "MENU" in self.buttons:
            menu_enabled = self.settings_manager.get_setting('menu_enabled', True) if self.settings_manager else True
            
            # Consider both app active state and menu enabled setting
            if self.is_active and menu_enabled:
                # App is active and menu is enabled - show as active (green)
                self.buttons["MENU"].setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.GREEN_ACCENT};
                        color: {Colors.TEXT_COLOR};
                        border: 1px solid {Colors.GREEN_ACCENT};
                        border-radius: {BORDER_RADIUS}px;
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        font-size: 9pt;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {Colors.GREEN_HOVER};
                        border: 1px solid {Colors.GREEN_HOVER};
                    }}
                """)
            elif self.is_active and not menu_enabled:
                # App is active but menu is disabled - show as normal inactive button
                self.buttons["MENU"].setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.DARK_BUTTON_BG};
                        color: {Colors.TEXT_COLOR};
                        border: 1px solid {Colors.BORDER_COLOR};
                        border-radius: {BORDER_RADIUS}px;
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        font-size: 9pt;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: #3d3d3d;
                        border: 1px solid #5d5d5d;
                    }}
                """)
            else:
                # App is inactive - show as grayed out (same as other buttons when inactive)
                self.buttons["MENU"].setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.DARK_BUTTON_BG};
                        color: {Colors.DISABLED_TEXT};
                        border: 1px solid {Colors.BORDER_COLOR};
                        border-radius: {BORDER_RADIUS}px;
                        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                        font-size: 9pt;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: #3d3d3d;
                        border: 1px solid #5d5d5d;
                    }}
                """)
    
    def toggle_active(self):
        """Modified toggle_active to also control scroll and menu widgets."""
        self.is_active = not self.is_active
        
        # Clear button hover state when turning off to prevent stuck hover states
        if not self.is_active:
            self.button_manager.clear_hover()
        
        self.update_button_states()
        
        # Reset movement state when toggling
        self.widgets_hidden_for_movement = False
        
        # Update contracted button text if UI is contracted
        self.update_contracted_button_state()
        
        # Apply scroll settings which will show/hide widget based on active state
        self.apply_scroll_settings()
        
        # Apply menu settings which will show/hide widget based on active state
        self.apply_menu_settings()
        
        if self.is_active:
            # Force immediate position update when becoming active
            if (self.settings_manager.get_setting('scroll_enabled', True) or 
                self.settings_manager.get_setting('menu_enabled', True)):
                try:
                    from pynput.mouse import Controller
                    mouse = Controller()
                    pos = mouse.position
                    self.update_scroll_widget_position(pos)
                    self.update_menu_widget_position(pos)
                except Exception as e:
                    pass
    
    def set_mode(self, mode):
        """Set click mode with improved temporary/default behavior."""
        current_time = time.time()
        
        # Determine if this button should currently be blue (permanent)
        # A button is visually blue if it matches what update_button_states() makes blue:
        # 1. It's the default mode button AND we're active AND
        # 2. Either we're not in temporary mode, OR this button is not the current temporary mode
        is_default_mode_button = (mode == self.default_mode)
        will_be_overridden_red = (self.is_active and self.is_temporary_mode and mode == self.current_mode)
        is_button_currently_blue = (is_default_mode_button and self.is_active and not will_be_overridden_red)
        
        # If clicking on a blue button (permanent mode), always ignore the click
        if is_button_currently_blue:
            return
        
        # If selecting the current mode...
        if mode == self.current_mode:
            # If it's temporary (red button), make it permanent (turn blue)
            if self.is_temporary_mode:
                self.default_mode = mode
                self.is_temporary_mode = False
            # If it's already permanent, ignore (this case should be caught above)
            else:
                return
        else:
            # Selecting a different mode - make it temporary (turn red)
            self.current_mode = mode
            self.is_temporary_mode = True
        
        # Update tracking variables
        self.last_mode_selection = mode
        self.last_selection_time = current_time
        
        # Reset any active drag state
        self.drag_state = None
        
        # Update UI to reflect new state
        self.update_button_states()
        
        # Update contracted button text if UI is contracted
        self.update_contracted_button_state()
    
    def process_dwell_event(self, center):
        """Process a dwell event with scroll and menu widget support."""
        # Don't process regular dwell events if we're over scroll widget
        if self.scroll_hover:
            # The scrolling is handled by update_scroll_widget_position
            return
        else:
            # Stop scrolling if we've moved away
            if self.scroll_widget.is_scrolling:
                self.scroll_widget.stop_scrolling()

        # Don't process regular dwell events if we're over menu widget
        if self.menu_hover and self.menu_hover not in ['hamburger', 'expanded']:
            # The menu selection is handled by update_menu_widget_position
            return

        # Get current hover button from button manager
        current_hover = self.button_manager.get_current_hover()
        
        # Check if we're hovering over a button
        if current_hover is not None:
            button_id = current_hover
            
            # Always allow ON/OFF button to be toggled regardless of active state
            if button_id == "ON_OFF":
                self.toggle_active()
                return
            
            # Handle contracted button - always allow expansion
            if button_id == "CONTRACTED":
                self.expand_ui()
                return
                
            # For all other buttons (except MOVE), only act if clicker is active
            if self.is_active and button_id != "MOVE":
                # Execute the command via button manager
                self.button_manager.execute_command(button_id)
                # Don't reset mode for UI button clicks
                return
            
            # If clicker is inactive, don't process other buttons
            if not self.is_active:
                return
        
        # No button detected or button handling complete, process normal dwell clicks
        # Only process if clicker is active
        if not self.is_active:
            return
        
        # Handle DRAG mode
        if self.current_mode == "DRAG":
            self.handle_drag(center)
            return  # Don't reset temporary mode for drag operations
        
        # Perform the appropriate click action for other modes
        if self.current_mode == "LEFT":
            self.click_manager.perform_left_click(center)
        elif self.current_mode == "RIGHT":
            self.click_manager.perform_right_click(center)
        elif self.current_mode == "DOUBLE":
            self.click_manager.perform_double_click(center)
        
        # If this was a temporary mode, switch back to default
        if self.is_temporary_mode:
            self.current_mode = self.default_mode
            self.is_temporary_mode = False
            self.update_button_states()
            # Update contracted button text if UI is contracted
            self.update_contracted_button_state()

    def handle_drag(self, center):
        """Handle drag operations that require two dwells."""
        
        # Regular drag operation for mouse
        if self.drag_state is None:
            # First dwell - mouse down
            success = self.click_manager.mouse_down()
            
            if success:
                self.drag_state = "down"
        
        elif self.drag_state == "down":
            # Second dwell - mouse up
            success = self.click_manager.mouse_up()
            
            if success:
                self.drag_state = None
                
                # After completing drag, switch back to default if temporary
                if self.is_temporary_mode:
                    self.current_mode = self.default_mode
                    self.is_temporary_mode = False
        
        self.update_button_states()
        # Update contracted button text if UI is contracted
        self.update_contracted_button_state()

    def update_scroll_widget_position(self, cursor_pos):
        """Update scroll widget position to follow cursor with coordinated positioning."""
        # Only update if scroll widget is enabled
        if not self.settings_manager.get_setting('scroll_enabled', True):
            return
        
        # Continue with position updates only if widgets should be visible
        if self.is_active and not self.widgets_hidden_for_movement:
            # Check if both widgets are enabled for coordinated positioning
            menu_enabled = self.settings_manager.get_setting('menu_enabled', True)
            
            if menu_enabled:
                # Coordinated positioning mode
                self._update_coordinated_widget_positions(cursor_pos)
            else:
                # Normal positioning if menu is disabled
                self.scroll_widget.update_position(cursor_pos)
            
            # Check for hover on scroll widget
            hover = self.scroll_widget.check_hover(cursor_pos)
            
            # Track hover state changes
            if hover != self.scroll_hover:
                # Stop any existing scrolling when changing hover state
                if self.scroll_widget.is_scrolling:
                    self.scroll_widget.stop_scrolling()
                
                self.scroll_hover = hover
                
                if hover:
                    # Started hovering (either from None or from a different direction)
                    self.scroll_dwell_start_time = time.time()
                    self.scroll_dwell_triggered = False
                else:
                    # Stopped hovering completely
                    self.scroll_dwell_start_time = None
                    self.scroll_dwell_triggered = False
            
            # Check if dwell complete
            if hover and self.scroll_dwell_start_time and not self.scroll_dwell_triggered:
                hover_duration = time.time() - self.scroll_dwell_start_time
                
                # Check if dwell complete
                if hover_duration >= self.dwell_detector.dwell_time:
                    self.scroll_widget.start_scrolling(hover)
                    self.scroll_dwell_triggered = True

    def update_menu_widget_position(self, cursor_pos):
        """Update menu widget position to follow cursor with coordinated positioning."""
        # Only update if menu widget is enabled
        if not self.settings_manager.get_setting('menu_enabled', True):
            return
        
        # Only continue if widgets are not hidden for movement
        if self.is_active and not self.widgets_hidden_for_movement:
            # Check if both widgets are enabled for coordinated positioning
            scroll_enabled = self.settings_manager.get_setting('scroll_enabled', True)
            
            if scroll_enabled:
                # Coordinated positioning is handled by update_scroll_widget_position
                # Just handle hover detection here
                pass
            else:
                # Normal positioning if scroll is disabled
                self.menu_widget.update_position(cursor_pos)
            
            # Check for hover on menu widget
            hover = self.menu_widget.check_hover(cursor_pos)
            
            # Track hover state changes
            if hover != self.menu_hover:
                self.menu_hover = hover
                
                if hover and hover not in ['hamburger', 'expanded']:
                    # Started hovering over a specific menu item
                    self.menu_dwell_start_time = time.time()
                    self.menu_dwell_triggered = False
                else:
                    # Stopped hovering over specific menu item or just over hamburger/expanded area
                    self.menu_dwell_start_time = None
                    self.menu_dwell_triggered = False
            
            # Check if dwell complete for menu item selection
            if (hover and hover not in ['hamburger', 'expanded'] and 
                self.menu_dwell_start_time and not self.menu_dwell_triggered):
                hover_duration = time.time() - self.menu_dwell_start_time
                
                # Check if dwell complete
                if hover_duration >= self.dwell_detector.dwell_time:
                    self.menu_widget.trigger_menu_item(hover)
                    self.menu_dwell_triggered = True

    def _update_coordinated_widget_positions(self, cursor_pos):
        """Update both widgets with coordinated positioning to avoid chaotic movement."""
        import math
        
        # Convert pynput coordinates to Qt coordinates
        if hasattr(cursor_pos, '__iter__'):
            cursor_x, cursor_y = cursor_pos
        else:
            cursor_x, cursor_y = cursor_pos.x(), cursor_pos.y()
        
        # Initialize coordinated lock state if not exists
        if not hasattr(self, '_coordinated_locked'):
            self._coordinated_locked = False
        
        # Check if widgets should be locked based on cursor proximity
        # Only check if widgets are visible and have been positioned
        if self.scroll_widget.isVisible() and self.menu_widget.isVisible():
            # Get current positions of both widgets
            scroll_center = self.scroll_widget.rect().center()
            scroll_global_center = self.scroll_widget.mapToGlobal(scroll_center)
            menu_center = self.menu_widget.rect().center()
            menu_global_center = self.menu_widget.mapToGlobal(menu_center)
            
            # Calculate distances to cursor
            scroll_distance = math.sqrt((cursor_x - scroll_global_center.x()) ** 2 + (cursor_y - scroll_global_center.y()) ** 2)
            menu_distance = math.sqrt((cursor_x - menu_global_center.x()) ** 2 + (cursor_y - menu_global_center.y()) ** 2)
            
            # Use lock thresholds similar to individual widgets
            lock_threshold = 120
            unlock_threshold = 180
            
            # Check if either widget is close enough to lock both
            should_lock = (scroll_distance < lock_threshold or menu_distance < lock_threshold)
            should_unlock = (scroll_distance > unlock_threshold and menu_distance > unlock_threshold)
            
            # Update lock state
            if not self._coordinated_locked and should_lock:
                self._coordinated_locked = True
                # Update widget visual states to show they're locked
                self.scroll_widget.is_locked = True
                self.menu_widget.is_locked = True
                self.scroll_widget.update()
                self.menu_widget.update()
                return  # Don't move when locking
            elif self._coordinated_locked and should_unlock:
                self._coordinated_locked = False
                # Update widget visual states
                self.scroll_widget.is_locked = False
                self.menu_widget.is_locked = False
                self.scroll_widget.update()
                self.menu_widget.update()
                # Continue to update positions after unlocking
            elif self._coordinated_locked:
                return  # Stay locked in place
        
        # Get scroll widget settings for base positioning
        scroll_offset = self.settings_manager.get_setting('scroll_offset', 50)
        scroll_angle = self.settings_manager.get_setting('scroll_angle', 45)
        
        # Calculate side-by-side positioning instead of stacked
        # Place scroll widget to the right, menu widget to the left
        widget_distance = 80  # Distance from cursor to each widget
        
        # Scroll widget position (right side of cursor)
        scroll_widget_x = int(cursor_x + widget_distance - self.scroll_widget.width() // 2)
        scroll_widget_y = int(cursor_y - self.scroll_widget.height() // 2)
        
        # Menu widget position (left side of cursor)
        menu_widget_x = int(cursor_x - widget_distance - self.menu_widget.width() // 2)
        menu_widget_y = int(cursor_y - self.menu_widget.height() // 2)
        
        # Update scroll widget position with coordinated mode
        self.scroll_widget.update_position(cursor_pos, coordinated_mode=True)
        self.scroll_widget.move(scroll_widget_x, scroll_widget_y)
        
        # Update menu widget with coordinated position
        self.menu_widget.update_position(cursor_pos, coordinated_mode=True)
        self.menu_widget.set_coordinated_position((menu_widget_x, menu_widget_y))

    def update_movement_detection(self, cursor_pos):
        """Update movement detection and control widget visibility."""
        # Update movement detector and get current movement state
        movement_state = self.cursor_movement_detector.update_position(cursor_pos)
        
        # Check if cursor is near any widget (override hiding if close to widgets)
        cursor_near_widget = self._is_cursor_near_widgets(cursor_pos)
        
        # Handle widget visibility based on movement state and proximity
        should_hide = self.cursor_movement_detector.should_hide_widgets(movement_state) and not cursor_near_widget
        should_show = self.cursor_movement_detector.should_show_widgets(movement_state) or cursor_near_widget
        
        # Only hide/show if active
        if self.is_active:
            if should_hide and not self.widgets_hidden_for_movement:
                # Hide both widgets when movement detected and not near widgets
                self._hide_widgets_for_movement()
            elif should_show and self.widgets_hidden_for_movement:
                # Show both widgets when dwelling detected or near widgets
                self._show_widgets_for_movement()

    def _hide_widgets_for_movement(self):
        """Hide widgets when cursor movement is detected."""
        if not self.widgets_hidden_for_movement:
            self.widgets_hidden_for_movement = True
            
            # Completely hide widgets when moving for cleaner experience
            if self.scroll_widget.isVisible():
                self.scroll_widget.hide()
            if self.menu_widget.isVisible():
                self.menu_widget.hide()
                
            # Reset any active hover states
            self.scroll_hover = None
            self.scroll_dwell_start_time = None
            self.scroll_dwell_triggered = False
            self.menu_hover = None
            self.menu_dwell_start_time = None
            self.menu_dwell_triggered = False
            
            # Stop any active scrolling
            if self.scroll_widget.is_scrolling:
                self.scroll_widget.stop_scrolling()
                
            # Clear hover states in widgets
            if hasattr(self.scroll_widget, '_set_hover'):
                self.scroll_widget._set_hover(None)
            if hasattr(self.menu_widget, '_set_hover'):
                self.menu_widget._set_hover(None)
            if hasattr(self.menu_widget, '_set_expanded'):
                self.menu_widget._set_expanded(False)
    
    def _show_widgets_for_movement(self):
        """Show widgets when cursor dwelling is detected."""
        if self.widgets_hidden_for_movement:
            self.widgets_hidden_for_movement = False
            
            # Show widgets and restore their normal state
            scroll_enabled = self.settings_manager.get_setting('scroll_enabled', True)
            menu_enabled = self.settings_manager.get_setting('menu_enabled', True)
            
            if scroll_enabled and self.is_active:
                self.scroll_widget.show()
                self.scroll_widget.setWindowOpacity(self.scroll_widget.base_opacity)
                self.scroll_widget.raise_()
                
            if menu_enabled and self.is_active:
                self.menu_widget.show()
                self.menu_widget.setWindowOpacity(self.menu_widget.base_opacity)
                self.menu_widget.raise_()

    def _refresh_button_hover_states(self):
        """Force a refresh of button hover states by simulating mouse movement."""
        try:
            from PyQt6.QtCore import QCoreApplication
            from PyQt6.QtGui import QCursor
            
            # Get current cursor position
            cursor_pos = QCursor.pos()
            
            # Clear all button hover states first
            self.button_manager.clear_hover()
            
            # Check which button (if any) should be hovered based on current cursor position
            for button_id, button in self.buttons.items():
                if button.isVisible():
                    # Convert global cursor position to button coordinates
                    button_pos = button.mapFromGlobal(cursor_pos)
                    
                    # Check if cursor is within button bounds
                    if button.rect().contains(button_pos):
                        # Manually trigger the hover state
                        self.button_manager.set_hover(button_id)
                        break
            
            # Process any pending Qt events to ensure proper state updates
            QCoreApplication.processEvents()
            
        except Exception as e:
            # If there's any error, just clear the hover state
            self.button_manager.clear_hover()
    
    def handle_menu_item_selection(self, item_id):
        """Handle selection of a menu item."""
        if item_id == 'LEFT':
            self.set_mode('LEFT')
        elif item_id == 'DOUBLE':
            self.set_mode('DOUBLE')
        elif item_id == 'RIGHT':
            self.set_mode('RIGHT')
        elif item_id == 'DRAG':
            self.set_mode('DRAG')
        elif item_id == 'OFF':
            # Turn off the application with special handling for menu widget interaction
            if self.is_active:
                # First hide the menu widget to prevent event conflicts
                self.menu_widget.set_active(False)
                # Clear any menu widget hover states
                self.menu_hover = None
                self.menu_dwell_start_time = None
                self.menu_dwell_triggered = False
                # Now toggle the application off
                self.toggle_active()
                # Force a refresh of mouse hover state for main UI
                self._refresh_button_hover_states()
        elif item_id == 'SETUP':
            # Execute the setup command if available
            if self.settings_manager:
                self.button_manager.execute_command('SETUP')

    def toggle_menu_widget(self):
        """Toggle the menu widget on/off."""
        if not self.settings_manager:
            return
            
        # Get current menu enabled state and toggle it
        current_menu_enabled = self.settings_manager.get_setting('menu_enabled', True)
        new_menu_enabled = not current_menu_enabled
        
        # Update setting
        self.settings_manager.set_setting('menu_enabled', new_menu_enabled)
        
        # Apply the new menu settings (this handles show/hide)
        self.apply_menu_settings()
        
        # Update button states to reflect new state
        self.update_button_states()

    def toggle_scroll_widget(self):
        """Toggle the scroll widget on/off."""
        if not self.settings_manager:
            return
            
        # Get current scroll enabled state and toggle it
        current_scroll_enabled = self.settings_manager.get_setting('scroll_enabled', True)
        new_scroll_enabled = not current_scroll_enabled
        
        # Update setting
        self.settings_manager.set_setting('scroll_enabled', new_scroll_enabled)
        
        # Apply the new scroll settings (this handles show/hide)
        self.apply_scroll_settings()
        
        # Update button states to reflect new state
        self.update_button_states()

    def cleanup_scroll_widget(self):
        """Clean up the scroll widget and UI contraction before application exit."""
        if hasattr(self, 'scroll_widget') and self.scroll_widget:
            # Stop any active scrolling
            self.scroll_widget.stop_scrolling()
            # Deactivate the widget (this will hide it)
            self.scroll_widget.set_active(False)
            # Close the widget completely
            self.scroll_widget.close()
            # Clear hover state
            self.scroll_hover = None
            self.scroll_dwell_start_time = None
            self.scroll_dwell_triggered = False
        
        # Clean up UI contraction
        if hasattr(self, 'contract_timer'):
            self.contract_timer.stop()
        if hasattr(self, 'expand_timer'):
            self.expand_timer.stop()
        if hasattr(self, 'opacity_timer'):
            self.opacity_timer.stop()
        
        # Expand UI if contracted
        if hasattr(self, 'is_contracted') and self.is_contracted:
            self.expand_ui()

    def cleanup_menu_widget(self):
        """Clean up the menu widget before application exit."""
        if hasattr(self, 'menu_widget') and self.menu_widget:
            # Deactivate the widget (this will hide it)
            self.menu_widget.set_active(False)
            # Close the widget completely
            self.menu_widget.close()
            # Clear hover state
            self.menu_hover = None
            self.menu_dwell_start_time = None
            self.menu_dwell_triggered = False

    def determine_expansion_direction(self):
        """Determine the best expansion direction based on window position and user preference."""
        if not self.settings_manager:
            return 'horizontal'
        
        user_preference = self.settings_manager.get_setting('expansion_direction', DEFAULT_EXPANSION_DIRECTION)
        
        # If user has a specific preference (not auto), use it
        if user_preference != 'auto':
            return user_preference
        
        # Auto mode - determine best direction based on screen position
        try:
            from PyQt6.QtGui import QGuiApplication
            
            # Get current window position and screen geometry
            window_pos = self.window.pos()
            window_size = self.window.size()
            screen = QGuiApplication.primaryScreen().geometry()
            
            # Calculate available space in each direction
            space_right = screen.width() - (window_pos.x() + window_size.width())
            space_bottom = screen.height() - (window_pos.y() + window_size.height())
            space_left = window_pos.x()
            space_top = window_pos.y()
            
            # Calculate required space for full UI
            total_buttons = len(self.buttons)
            horizontal_space_needed = (total_buttons * BUTTON_SIZE[0] + 
                                     (total_buttons - 1) * LAYOUT_SPACING + 
                                     LAYOUT_MARGIN * 2) - CONTRACT_BUTTON_SIZE[0]
            vertical_space_needed = (total_buttons * BUTTON_SIZE[1] + 
                                   (total_buttons - 1) * LAYOUT_SPACING + 
                                   LAYOUT_MARGIN * 2) - CONTRACT_BUTTON_SIZE[1]
            
            # Check if horizontal expansion is possible
            horizontal_possible = (space_right >= horizontal_space_needed + SCREEN_EDGE_MARGIN or 
                                 space_left >= horizontal_space_needed + SCREEN_EDGE_MARGIN)
            
            # Check if vertical expansion is possible
            vertical_possible = (space_bottom >= vertical_space_needed + SCREEN_EDGE_MARGIN or 
                               space_top >= vertical_space_needed + SCREEN_EDGE_MARGIN)
            
            # Prefer horizontal if both are possible (traditional UI layout)
            if horizontal_possible:
                return 'horizontal'
            elif vertical_possible:
                return 'vertical'
            else:
                # If neither fits perfectly, choose the one with more space
                max_horizontal = max(space_right, space_left)
                max_vertical = max(space_bottom, space_top)
                return 'horizontal' if max_horizontal >= max_vertical else 'vertical'
                
        except Exception:
            # Fallback to horizontal if there's any error
            return 'horizontal'

    def apply_menu_settings(self):
        """Apply menu widget settings from the settings manager."""
        if not self.settings_manager:
            return
        
        # Get menu settings
        menu_enabled = self.settings_manager.get_setting('menu_enabled', True)
        menu_offset = self.settings_manager.get_setting('menu_offset', 100)
        menu_angle = self.settings_manager.get_setting('menu_angle', -45)
        menu_opacity_base = self.settings_manager.get_setting('menu_opacity_base', 80)
        menu_opacity_hover = self.settings_manager.get_setting('menu_opacity_hover', 95)
        
        # Apply settings to menu widget
        self.menu_widget.set_offset(distance=menu_offset, angle=menu_angle)
        self.menu_widget.set_opacity(
            base=menu_opacity_base,
            hover=menu_opacity_hover
        )
        
        # Enable/disable menu widget based on setting and active state
        should_be_active = self.is_active and menu_enabled
        self.menu_widget.set_active(should_be_active)
        
        # Update button states to reflect menu setting changes
        self.update_button_states()

    def apply_widget_appearance_settings(self):
        """Apply widget appearance settings from the settings manager."""
        if not self.settings_manager:
            return
        
        # Get widget appearance delay setting
        appearance_delay = self.settings_manager.get_setting('widget_appearance_delay', 0.2)
        
        # Update the movement detector with the new delay
        self.cursor_movement_detector.set_dwell_delay(appearance_delay)
        
        # Sync movement threshold with dwell detection move_limit
        if hasattr(self, 'dwell_detector') and self.dwell_detector:
            self.cursor_movement_detector.set_movement_threshold(self.dwell_detector.move_limit)

    def _is_cursor_near_widgets(self, cursor_pos):
        """Check if cursor is close enough to any widget to keep them visible."""
        if not self.is_active:
            return False
            
        # Convert cursor position
        if hasattr(cursor_pos, '__iter__'):
            cursor_x, cursor_y = cursor_pos
        else:
            cursor_x, cursor_y = cursor_pos.x(), cursor_pos.y()
        
        # Only check proximity to widgets that are currently visible
        # Don't use predicted positions - that creates the always-near problem
        
        # Check scroll widget if enabled and currently visible
        scroll_enabled = self.settings_manager.get_setting('scroll_enabled', True)
        if scroll_enabled and self.scroll_widget.isVisible() and not self.widgets_hidden_for_movement:
            # First check if cursor is actually hovering over the scroll widget UI
            scroll_hover = self.scroll_widget.check_hover(cursor_pos)
            if scroll_hover is not None:
                return True  # Definitely keep visible if hovering over UI
            
            # Otherwise check proximity and movement direction
            scroll_rect = self.scroll_widget.geometry()
            scroll_center_x = scroll_rect.x() + scroll_rect.width() // 2
            scroll_center_y = scroll_rect.y() + scroll_rect.height() // 2
            
            # Use a larger proximity threshold for staying visible (more forgiving)
            stay_visible_threshold = 140  # pixels - increased for easier interaction
            scroll_distance = ((cursor_x - scroll_center_x) ** 2 + 
                             (cursor_y - scroll_center_y) ** 2) ** 0.5
            
            # Be more forgiving with movement detection - only hide if clearly moving away
            if scroll_distance <= stay_visible_threshold:
                if not self._is_cursor_clearly_moving_away_from_point(cursor_pos, (scroll_center_x, scroll_center_y)):
                    return True
        
        # Check menu widget if enabled and currently visible
        menu_enabled = self.settings_manager.get_setting('menu_enabled', True)
        if menu_enabled and self.menu_widget.isVisible() and not self.widgets_hidden_for_movement:
            # First check if cursor is actually hovering over the menu widget UI
            menu_hover = self.menu_widget.check_hover(cursor_pos)
            if menu_hover is not None:
                return True  # Definitely keep visible if hovering over UI
            
            # Otherwise check proximity and movement direction
            menu_rect = self.menu_widget.geometry()
            menu_center_x = menu_rect.x() + menu_rect.width() // 2
            menu_center_y = menu_rect.y() + menu_rect.height() // 2
            
            stay_visible_threshold = 140  # pixels - increased for easier interaction
            menu_distance = ((cursor_x - menu_center_x) ** 2 + 
                           (cursor_y - menu_center_y) ** 2) ** 0.5
            
            # Be more forgiving with movement detection - only hide if clearly moving away
            if menu_distance <= stay_visible_threshold:
                if not self._is_cursor_clearly_moving_away_from_point(cursor_pos, (menu_center_x, menu_center_y)):
                    return True
        
        return False
    
    def _is_cursor_clearly_moving_away_from_point(self, current_pos, target_point):
        """Check if cursor is clearly moving away from a specific point (more forgiving than before)."""
        if not hasattr(self.cursor_movement_detector, 'last_position') or self.cursor_movement_detector.last_position is None:
            return False
            
        # Convert positions
        if hasattr(current_pos, '__iter__'):
            curr_x, curr_y = current_pos
        else:
            curr_x, curr_y = current_pos.x(), current_pos.y()
            
        last_x, last_y = self.cursor_movement_detector.last_position
        target_x, target_y = target_point
        
        # Calculate distances
        last_distance = ((last_x - target_x) ** 2 + (last_y - target_y) ** 2) ** 0.5
        current_distance = ((curr_x - target_x) ** 2 + (curr_y - target_y) ** 2) ** 0.5
        
        # Only consider it "clearly moving away" if distance increased significantly
        # This is more forgiving for small movements during interaction
        movement_threshold = 8  # pixels - increased threshold for more forgiveness
        return current_distance > last_distance + movement_threshold