"""UI management for the Dwell Clicker application."""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QPushButton, 
                           QHBoxLayout, QVBoxLayout, QFrame)
from PyQt6.QtCore import Qt, QSize, QTimer
from .scroll_widget import ScrollWidget
import time

# Updated imports for new structure
try:
    from ..config.constants import (
        Colors, BUTTON_SIZE, LAYOUT_MARGIN, LAYOUT_SPACING, BORDER_RADIUS, Fonts
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

        self.scroll_widget = ScrollWidget()
        self.scroll_widget.set_active(False)  # Start inactive

        # Track scroll widget hover state
        self.scroll_hover = None
        self.scroll_dwell_start_time = None
        self.scroll_dwell_triggered = False
        
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
        
        # Apply default active state if configured BEFORE applying scroll settings
        if self.settings_manager.get_setting('default_active', False):
            self.is_active = True
            self.update_button_states()
        
        # Apply scroll widget settings AFTER setting the active state
        self.apply_scroll_settings()
    
    def register_button_commands(self):
        """Register button commands with the button manager."""
        # Register basic button commands
        self.button_manager.register_command("ON_OFF", self.toggle_active)
        self.button_manager.register_command("LEFT", lambda: self.set_mode("LEFT"))
        self.button_manager.register_command("DOUBLE", lambda: self.set_mode("DOUBLE"))
        self.button_manager.register_command("DRAG", lambda: self.set_mode("DRAG"))
        self.button_manager.register_command("RIGHT", lambda: self.set_mode("RIGHT"))
        self.button_manager.register_command("SCROLL", self.toggle_scroll_widget)
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
        
        # Add close event handler for scroll widget cleanup
        original_close_event = self.window.closeEvent
        def close_event_handler(event):
            self.cleanup_scroll_widget()
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
        button_layout = QHBoxLayout(central_widget)
        button_layout.setContentsMargins(LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN, LAYOUT_MARGIN)
        button_layout.setSpacing(LAYOUT_SPACING)
        
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
        
        # Always make opaque when cursor is over window
        self.set_opaque()
        
        # Call original event handler if it exists
        if hasattr(self.window, 'original_enterEvent'):
            self.window.original_enterEvent(event)
    
    def on_window_leave(self, event):
        """Handle cursor leaving the window area."""
        self.is_cursor_over_window = False
        
        # Only set transparency if enabled in settings
        if self.settings_manager and self.settings_manager.get_setting('transparency_enabled', False):
            # Add a small delay before making transparent to avoid flickering
            # when cursor moves between buttons
            self.opacity_timer.start(100)  # 100ms delay
        
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
    
    def toggle_active(self):
        """Modified toggle_active to also control scroll widget."""
        self.is_active = not self.is_active
        self.update_button_states()
        
        # Apply scroll settings which will show/hide widget based on active state
        self.apply_scroll_settings()
        
        if self.is_active:
            # Force immediate position update when becoming active
            if self.settings_manager.get_setting('scroll_enabled', True):
                try:
                    from pynput.mouse import Controller
                    mouse = Controller()
                    pos = mouse.position
                    self.update_scroll_widget_position(pos)
                except Exception as e:
                    pass
    
    def set_mode(self, mode):
        """Set click mode with improved temporary/default behavior."""
        current_time = time.time()
        
        # If clicking on the default mode (blue button), ignore the click
        if mode == self.default_mode and not self.is_temporary_mode:
            return
        
        # If selecting the current mode...
        if mode == self.current_mode:
            # If it's temporary (red button), make it permanent (turn blue)
            if self.is_temporary_mode:
                self.default_mode = mode
                self.is_temporary_mode = False
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
    
    def process_dwell_event(self, center):
        """Process a dwell event with scroll widget support."""
        # Don't process regular dwell events if we're over scroll widget
        if self.scroll_hover:
            # The scrolling is handled by update_scroll_widget_position
            return
        else:
            # Stop scrolling if we've moved away
            if self.scroll_widget.is_scrolling:
                self.scroll_widget.stop_scrolling()

        # Get current hover button from button manager
        current_hover = self.button_manager.get_current_hover()
        
        # Check if we're hovering over a button
        if current_hover is not None:
            button_id = current_hover
            
            # Always allow ON/OFF button to be toggled regardless of active state
            if button_id == "ON_OFF":
                self.toggle_active()
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

    
    def update_scroll_widget_position(self, cursor_pos):
        """Update scroll widget position to follow cursor."""
        # Only update if scroll widget is enabled
        if not self.settings_manager.get_setting('scroll_enabled', True):
            return
        
        if self.is_active:
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
        """Clean up the scroll widget before application exit."""
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