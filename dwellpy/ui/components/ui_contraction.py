"""UI contraction and expansion management."""

import os
from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QGuiApplication, QIcon

# Import constants
try:
    from ...config.constants import (
        Colors, BUTTON_SIZE, LAYOUT_MARGIN, LAYOUT_SPACING, BORDER_RADIUS,
        CONTRACT_DELAY, EXPAND_DELAY, CONTRACT_BUTTON_SIZE, CONTRACT_BUTTON_TEXT,
        EXPANSION_DIRECTIONS, DEFAULT_EXPANSION_DIRECTION, SCREEN_EDGE_MARGIN,
        ICON_MAPPING
    )
    from ...utils.helpers import get_asset_path
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
    
    ICON_MAPPING = {
        "ON_OFF": "on.png",
        "LEFT": "left.png",
        "DOUBLE": "double.png",
        "DRAG": "drag.png",
        "RIGHT": "right.png",
        "SETUP": "setup.png"
    }
    
    def get_asset_path(asset_name):
        """Fallback get_asset_path function"""
        return os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'icons', asset_name)


class UIContractionManager:
    """Manages UI contraction and expansion functionality."""
    
    def __init__(self, ui_manager):
        self.ui_manager = ui_manager
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
        self.current_expansion_direction = None
        self.original_window_size = None
        self._expanding_from_contracted = False
    
    def setup_timers(self):
        """Set up contraction and expansion timers."""
        self.contract_timer.timeout.connect(self.contract_ui)
        self.expand_timer.timeout.connect(self.expand_ui)
    
    def apply_contraction_settings(self):
        """Apply UI contraction settings from the settings manager."""
        if not self.ui_manager.settings_manager:
            return
        
        contract_enabled = self.ui_manager.settings_manager.get_setting('contract_ui_enabled', False)
        
        if contract_enabled and not self.is_contracted:
            # If contraction is enabled and UI is not contracted, contract it immediately
            # This handles the startup case where the user wants the UI to start contracted
            # Use force_contract=True to bypass cursor position check during startup
            self.contract_ui(force_contract=True)
        elif not contract_enabled and self.is_contracted:
            # If contraction is disabled and UI is currently contracted, expand it
            self.expand_ui()
    
    def apply_expansion_settings(self):
        """Apply UI expansion direction settings immediately."""
        if not self.ui_manager.settings_manager:
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
        current_pos = self.ui_manager.window.pos()
        
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
            total_buttons = len(self.ui_manager.buttons)
            window_height = (total_buttons * BUTTON_SIZE[1] + 
                           (total_buttons - 1) * LAYOUT_SPACING + 
                           LAYOUT_MARGIN * 2)
            window_width = BUTTON_SIZE[0] + (LAYOUT_MARGIN * 2)
            
            self.ui_manager.window.setFixedSize(window_width, window_height)
            
        else:  # horizontal
            # Create horizontal layout
            new_layout = QHBoxLayout()
            new_layout.setContentsMargins(LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN)
            new_layout.setSpacing(LAYOUT_SPACING)
            
            # Calculate window size for horizontal layout
            total_buttons = len(self.ui_manager.buttons)
            window_width = (total_buttons * BUTTON_SIZE[0] + 
                           (total_buttons - 1) * LAYOUT_SPACING + 
                           LAYOUT_MARGIN * 2)
            window_height = BUTTON_SIZE[1] + (LAYOUT_MARGIN * 2)
            
            self.ui_manager.window.setFixedSize(window_width, window_height)
        
        # Ensure window stays within screen bounds after resizing
        self._ensure_window_in_bounds(current_pos)
        
        # Set the layout to the new central widget
        new_central_widget.setLayout(new_layout)
        
        # Add all buttons to the new layout
        button_order = ["ON_OFF", "LEFT", "DOUBLE", "DRAG", "RIGHT", "SCROLL", "MENU", "SETUP", "MOVE", "EXIT"]
        for button_id in button_order:
            if button_id in self.ui_manager.buttons:
                button = self.ui_manager.buttons[button_id]
                button.show()
                new_layout.addWidget(button)
        
        # Add the contracted button back to layout (hidden)
        if self.contracted_button:
            new_layout.addWidget(self.contracted_button)
        
        # Replace the central widget
        self.ui_manager.window.setCentralWidget(new_central_widget)
        
        # Store the new layout
        self.original_layout = new_layout
    
    def _calculate_optimal_expansion_position(self, contracted_pos, expanded_size):
        """Calculate the optimal position for the expanded window to avoid going off-screen."""
        try:
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
            
            window_size = self.ui_manager.window.size()
            
            # If we're expanding from a contracted state, use optimal positioning
            if self._expanding_from_contracted:
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
            self.ui_manager.window.move(new_x, new_y)
        except Exception:
            # If there's any error, keep the window at its current position
            pass
    
    def update_contracted_button_state(self):
        """Update the icon and style of the contracted button to match current status."""
        if not self.contracted_button or not self.is_contracted:
            return
            
        # Determine which icon to use based on current state
        if not self.ui_manager.is_active:
            icon_id = "ON_OFF"  # Will use off.png
        else:
            icon_id = self.ui_manager.current_mode  # Use current mode icon
        
        # Set the icon and clear any text
        icon_path = self._get_icon_path(icon_id)
        if icon_path and os.path.exists(icon_path):
            icon = QIcon(icon_path)
            # Scale icon to fit button size minus padding
            icon_size = min(CONTRACT_BUTTON_SIZE[0], CONTRACT_BUTTON_SIZE[1]) - 10
            self.contracted_button.setIcon(icon)
            self.contracted_button.setIconSize(QSize(icon_size, icon_size))
            self.contracted_button.setText("")  # Clear text to show only icon
        
        # Update button style to match current state (no font styling for icons)
        if not self.ui_manager.is_active:
            # OFF state - red like the ON/OFF button when off
            self.contracted_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.RED_ACCENT};
                    border: 1px solid {Colors.RED_ACCENT};
                    border-radius: {BORDER_RADIUS}px;
                }}
                QPushButton:hover {{
                    background-color: {Colors.RED_HOVER};
                    border: 1px solid {Colors.RED_HOVER};
                }}
            """)
        elif self.ui_manager.is_temporary_mode:
            # Temporary mode - red like temporary mode buttons
            self.contracted_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.RED_ACCENT};
                    border: 1px solid {Colors.RED_ACCENT};
                    border-radius: {BORDER_RADIUS}px;
                }}
                QPushButton:hover {{
                    background-color: {Colors.RED_HOVER};
                    border: 1px solid {Colors.RED_HOVER};
                }}
            """)
        else:
            # Default mode - blue like the default mode buttons
            self.contracted_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.BLUE_ACCENT};
                    border: 1px solid {Colors.BLUE_ACCENT};
                    border-radius: {BORDER_RADIUS}px;
                }}
                QPushButton:hover {{
                    background-color: {Colors.BLUE_HOVER};
                    border: 1px solid {Colors.BLUE_HOVER};
                }}
            """)
    
    def _get_icon_path(self, button_id):
        """Get the icon path for a button ID."""
        # Special case for ON_OFF button - use different icon based on state
        if button_id == "ON_OFF":
            icon_file = "on.png" if self.ui_manager.is_active else "off.png"
        else:
            icon_file = ICON_MAPPING.get(button_id, "setup.png")  # Default to setup icon
            
        try:
            return get_asset_path(icon_file)
        except Exception:
            return None
    
    def contract_ui(self, force_contract=False):
        """Contract the UI to a single button."""
        if self.is_contracted or not self.ui_manager.settings_manager:
            return
        
        # Don't contract if cursor is over window, unless forced (for startup)
        if self.ui_manager.is_cursor_over_window and not force_contract:
            return
        
        self.is_contracted = True
        
        # Store current window position before resizing
        current_pos = self.ui_manager.window.pos()
        
        # Determine and store expansion direction
        self.current_expansion_direction = self.determine_expansion_direction()
        
        # Store original window size
        self.original_window_size = self.ui_manager.window.size()
        
        # Hide all existing buttons
        for button in self.ui_manager.buttons.values():
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
        self.ui_manager.window.setFixedSize(
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
        if (self.ui_manager.is_active and self.ui_manager.settings_manager and 
            self.ui_manager.settings_manager.get_setting('scroll_enabled', True)):
            try:
                from pynput.mouse import Controller
                mouse = Controller()
                pos = mouse.position
                self.ui_manager.update_scroll_widget_position(pos)
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
        if not self.ui_manager.is_active:
            return "OFF"
        
        # When active, show current click mode with temporary mode priority
        if self.ui_manager.is_temporary_mode:
            return f"{self.ui_manager.current_mode}*"  # Asterisk indicates temporary
        else:
            return self.ui_manager.current_mode
    
    def create_contracted_button(self):
        """Create the contracted button showing current status."""
        button = QPushButton()  # No text - will use icon
        button.setFixedSize(CONTRACT_BUTTON_SIZE[0], CONTRACT_BUTTON_SIZE[1])
        button.setObjectName("CONTRACTED")  # Give it an ID for button manager
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Connect click to expand
        button.clicked.connect(self.expand_ui)
        
        # Add hover events for dwell detection
        original_enter_event = button.enterEvent
        original_leave_event = button.leaveEvent
        
        def custom_enter_event(event):
            self.ui_manager.button_manager.set_hover("CONTRACTED")
            if original_enter_event:
                original_enter_event(event)
        
        def custom_leave_event(event):
            self.ui_manager.button_manager.clear_hover("CONTRACTED")
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
    
    def determine_expansion_direction(self):
        """Determine the optimal expansion direction based on settings and screen position."""
        if not self.ui_manager.settings_manager:
            return DEFAULT_EXPANSION_DIRECTION
        
        # Get the setting for expansion direction
        direction_setting = self.ui_manager.settings_manager.get_setting('expansion_direction', DEFAULT_EXPANSION_DIRECTION)
        
        # If set to 'auto', determine based on screen position
        if direction_setting == 'auto':
            try:
                # Get current window position
                window_pos = self.ui_manager.window.pos()
                
                # Get screen geometry
                app = QGuiApplication.instance()
                screen = app.primaryScreen()
                screen_geometry = screen.geometry()
                
                # Calculate available space in each direction
                space_right = screen_geometry.right() - window_pos.x()
                space_left = window_pos.x() - screen_geometry.left()
                space_bottom = screen_geometry.bottom() - window_pos.y()
                space_top = window_pos.y() - screen_geometry.top()
                
                # Calculate required space for expansion
                total_buttons = len(self.ui_manager.buttons)
                horizontal_space_needed = (total_buttons * BUTTON_SIZE[0] + 
                                         (total_buttons - 1) * LAYOUT_SPACING + 
                                         LAYOUT_MARGIN * 2)
                vertical_space_needed = (total_buttons * BUTTON_SIZE[1] + 
                                       (total_buttons - 1) * LAYOUT_SPACING + 
                                       LAYOUT_MARGIN * 2)
                
                # Determine which direction has more space
                if space_right >= horizontal_space_needed or space_left >= horizontal_space_needed:
                    return 'horizontal'
                elif space_bottom >= vertical_space_needed or space_top >= vertical_space_needed:
                    return 'vertical'
                else:
                    # Default to horizontal if no clear winner
                    return 'horizontal'
                    
            except Exception:
                # Fallback to default direction
                return DEFAULT_EXPANSION_DIRECTION
        else:
            # Use the explicitly set direction
            return direction_setting 