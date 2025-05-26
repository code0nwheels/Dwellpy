"""Floating scroll widget for Dwellpy."""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QPoint, QPointF, QTimer, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF, QCursor
from pynput.mouse import Controller as MouseController
import math
import sys
import time

try:
    from ..config.constants import Colors
except ImportError:
    # Fallback if constants not available
    class Colors:
        DARK_BG = "#1e1e1e"
        BLUE_ACCENT = "#0078d7"
        TEXT_COLOR = "#ffffff"

# Windows DPI awareness for better multi-monitor support
if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes
        
        # Set DPI awareness to handle multiple monitors properly
        try:
            # Try the newer SetProcessDpiAwarenessContext first (Windows 10 1703+)
            ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
        except:
            try:
                # Fallback to SetProcessDpiAwareness (Windows 8.1+)
                ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
            except:
                try:
                    # Final fallback to SetProcessDPIAware (Windows Vista+)
                    ctypes.windll.user32.SetProcessDPIAware()
                except:
                    pass  # DPI awareness not available
    except ImportError:
        pass  # ctypes not available

class ScrollWidget(QWidget):
    """
    A floating widget that follows the cursor and provides scroll functionality.
    Appears at a fixed offset from the cursor and allows dwelling to scroll.
    """
    
    # Signals
    scroll_triggered = pyqtSignal(str)  # Emits 'up' or 'down'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Widget configuration
        self.widget_size = 40  # Size of the widget
        self.button_size = 35  # Size of scroll buttons
        self.offset_distance = 120  # Distance from cursor (increased to prevent cursor overlap)
        self.offset_angle = 45  # Angle in degrees (top-right by default)
        self.min_safe_distance = 60  # Minimum distance to keep widget away from cursor
        
        # State tracking
        self.is_active = False
        self.current_hover = None  # 'up', 'down', or None
        self.base_opacity = 0.7  # 30% opacity when not hovered
        self.hover_opacity = 0.9  # 90% opacity when hovered
        self.is_scrolling = False
        self.scroll_direction = None
        
        # Position lock state
        self.is_locked = False  # Whether widget is locked in position
        self.lock_threshold = 140  # Distance to lock (must be greater than offset_distance)
        self.unlock_threshold = 200  # Distance to resume following
        
        # Movement tracking to prevent false hover detection
        self.last_move_time = 0
        self.movement_cooldown = 0.2  # Back to a reasonable cooldown period
        
        # Smooth movement tracking
        self.last_cursor_pos = None
        self.movement_threshold = 15  # Only move widget if cursor moved this many pixels
        self.last_widget_pos = None
        
        # Cursor velocity tracking to prevent hover during fast movement
        self.cursor_velocity_history = []
        self.max_velocity_for_hover = 100  # Increased from 50 - allow some movement
        self.velocity_check_window = 3  # check velocity over last 3 updates
        
        # Mouse controller for scroll operations
        self.mouse = MouseController()
        
        # Scroll timing
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self._perform_scroll)
        self.scroll_interval = 100  # Scroll every 100ms when dwelling
        self.scroll_amount = 3  # Lines to scroll per interval

        self._scroll_count = 0
        
        # Setup UI
        self._setup_ui()
        
        # Make widget always pass scroll events through
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
    def _setup_ui(self):
        """Setup the widget UI."""
        # Platform-specific window flags for better macOS compatibility
        if sys.platform == "darwin":  # macOS
            # macOS: Use minimal flags that actually work (based on testing)
            # The blue widget test showed only these flags work reliably
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint
            )
        else:
            # Windows/Linux flags (original behavior)
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool |  # Prevents taskbar icon
                Qt.WindowType.WindowTransparentForInput  # Click-through by default
            )
        
        # Make widget transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set to not accept focus
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # macOS-specific attributes for better window management
        if sys.platform == "darwin":
            # Note: Removed complex macOS attributes as they cause invisibility
            # Keep it simple for macOS compatibility
            pass
        
        # Ensure wheel events pass through
        self.installEventFilter(self)
        
        # Set fixed size
        self.setFixedSize(self.widget_size, self.widget_size * 2)
        
        # Set initial opacity
        self.setWindowOpacity(self.base_opacity)
        
        # Initially hide the widget - it will be shown when activated
        self.hide()
        
    def eventFilter(self, obj, event):
        """Filter out wheel events to ensure they don't get stuck in our widget."""
        if event.type() == event.Type.Wheel and obj == self:
            # Always ignore wheel events on our widget
            return True
        return False
        
    def paintEvent(self, event):
        """Custom paint event to draw the scroll arrows."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background with rounded corners
        if self.is_locked:
            # Slightly different color when locked
            background_color = QColor(40, 40, 40, 220)  # Darker when locked
        else:
            background_color = QColor(30, 30, 30, 200)  # Normal
            
        painter.setBrush(QBrush(background_color))
        
        # Draw border to indicate lock state
        if self.is_locked:
            painter.setPen(QPen(QColor(0, 120, 215), 2))  # Blue border when locked
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            
        painter.drawRoundedRect(self.rect(), 10, 10)
        
        # Draw up arrow
        self._draw_arrow(painter, 'up', self.current_hover == 'up')
        
        # Draw down arrow
        self._draw_arrow(painter, 'down', self.current_hover == 'down')
        
    def _draw_arrow(self, painter, direction, is_hovered):
        """Draw an arrow button."""
        # Calculate button area
        button_height = self.height() // 2
        if direction == 'up':
            button_rect = QRect(5, 5, self.width() - 10, button_height - 10)
        else:
            button_rect = QRect(5, button_height + 5, self.width() - 10, button_height - 10)
        
        # Draw button background
        if self.is_scrolling and self.scroll_direction == direction:
            # Actively scrolling - use bright blue
            color = QColor(0, 150, 255)
        elif is_hovered:
            # Just hovering - use medium blue
            color = QColor(0, 120, 215)
        else:
            # Not hovered - dark gray
            color = QColor(60, 60, 60)
            
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(button_rect, 5, 5)
        
        # Draw arrow with white color
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        
        # Calculate arrow points
        center_x = button_rect.center().x()
        center_y = button_rect.center().y()
        arrow_size = 8
        
        if direction == 'up':
            points = QPolygonF([
                QPointF(center_x, center_y - arrow_size),
                QPointF(center_x - arrow_size, center_y + arrow_size//2),
                QPointF(center_x + arrow_size, center_y + arrow_size//2)
            ])
        else:
            points = QPolygonF([
                QPointF(center_x, center_y + arrow_size),
                QPointF(center_x - arrow_size, center_y - arrow_size//2),
                QPointF(center_x + arrow_size, center_y - arrow_size//2)
            ])
            
        painter.drawPolygon(points)
        
    def _get_qt_cursor_position(self):
        """Get cursor position using Qt's coordinate system for consistency."""
        try:
            # Use Qt's QCursor.pos() which is DPI-aware and consistent across monitors
            return QCursor.pos()
        except:
            # Fallback to pynput if Qt method fails
            pos = self.mouse.position
            return QPoint(int(pos[0]), int(pos[1]))
    
    def _convert_pynput_to_qt_coords(self, pynput_pos):
        """Convert pynput coordinates to Qt coordinates for multi-monitor consistency."""
        try:
            # Get the screen that contains this position
            app = QApplication.instance()
            if not app:
                return QPoint(int(pynput_pos[0]), int(pynput_pos[1]))
            
            # First, try using Qt's cursor position as it should be more accurate
            try:
                qt_direct = QCursor.pos()
                # If Qt and pynput positions are very close, prefer Qt
                dx = abs(qt_direct.x() - pynput_pos[0])
                dy = abs(qt_direct.y() - pynput_pos[1])
                if dx < 10 and dy < 10:  # Within 10 pixels, use Qt directly
                    return qt_direct
            except:
                pass
            
            # Find which screen contains the pynput position
            target_screen = None
            for screen in app.screens():
                geometry = screen.geometry()
                # Expand the geometry slightly to handle edge cases
                expanded_geom = geometry.adjusted(-10, -10, 10, 10)
                if (expanded_geom.x() <= pynput_pos[0] < expanded_geom.x() + expanded_geom.width() and
                    expanded_geom.y() <= pynput_pos[1] < expanded_geom.y() + expanded_geom.height()):
                    target_screen = screen
                    break
            
            if target_screen:
                # Account for DPI scaling
                device_pixel_ratio = target_screen.devicePixelRatio()
                if device_pixel_ratio != 1.0:
                    # Get the logical geometry (what Qt thinks the screen size is)
                    logical_geom = target_screen.geometry()
                    
                    # Convert pynput position to relative position on this screen
                    relative_x = pynput_pos[0] - logical_geom.x()
                    relative_y = pynput_pos[1] - logical_geom.y()
                    
                    # Apply DPI scaling
                    scaled_x = relative_x / device_pixel_ratio
                    scaled_y = relative_y / device_pixel_ratio
                    
                    # Convert back to global coordinates
                    qt_x = logical_geom.x() + scaled_x
                    qt_y = logical_geom.y() + scaled_y
                    
                    return QPoint(int(qt_x), int(qt_y))
            
            # If no scaling needed or screen not found, use direct conversion
            return QPoint(int(pynput_pos[0]), int(pynput_pos[1]))
            
        except Exception as e:
            print(f"ScrollWidget coordinate conversion error: {e}")
            # Fallback to direct conversion
            return QPoint(int(pynput_pos[0]), int(pynput_pos[1]))

    def update_position(self, cursor_pos):
        """Update widget position relative to cursor."""
        if not self.is_active:
            return
        
        # Convert pynput coordinates to Qt coordinates for consistency
        qt_cursor_pos = self._convert_pynput_to_qt_coords(cursor_pos)
        cursor_x, cursor_y = qt_cursor_pos.x(), qt_cursor_pos.y()
        
        # Track cursor velocity for hover detection
        current_time = time.time()
        if self.last_cursor_pos is not None:
            dx = cursor_x - self.last_cursor_pos[0]
            dy = cursor_y - self.last_cursor_pos[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Calculate velocity (pixels per second)
            # Note: update_position is called every 100ms, so time_delta should be ~0.1
            time_delta = current_time - getattr(self, 'last_update_time', current_time)
            if time_delta > 0:
                velocity = distance / time_delta
                
                # Keep a rolling window of recent velocities
                self.cursor_velocity_history.append(velocity)
                if len(self.cursor_velocity_history) > self.velocity_check_window:
                    self.cursor_velocity_history.pop(0)
        
        self.last_update_time = current_time
        
        # Check if cursor has moved significantly since last update
        if self.last_cursor_pos is not None:
            dx = cursor_x - self.last_cursor_pos[0]
            dy = cursor_y - self.last_cursor_pos[1]
            movement_distance = math.sqrt(dx * dx + dy * dy)
            
            # Only update position if cursor moved enough (reduces jittery movement)
            if movement_distance < self.movement_threshold and not self.is_locked:
                return
        
        # Update last cursor position
        self.last_cursor_pos = (cursor_x, cursor_y)
            
        # Get widget center in global coordinates
        widget_center = self.rect().center()
        widget_global_center = self.mapToGlobal(widget_center)
        
        # Calculate distance from cursor to widget center
        dx = cursor_x - widget_global_center.x()
        dy = cursor_y - widget_global_center.y()
        distance_to_widget = math.sqrt(dx * dx + dy * dy)
        
        # Lock/unlock logic
        if not self.is_locked:
            # If cursor gets close, lock the widget position
            if distance_to_widget < self.lock_threshold:
                self.is_locked = True
                return
            
            # Otherwise, update position normally
            angle_rad = math.radians(self.offset_angle)
            offset_x = int(self.offset_distance * math.cos(angle_rad))
            offset_y = int(self.offset_distance * math.sin(angle_rad))
            
            # Set new position using Qt coordinates - ensure integers
            new_x = int(cursor_x + offset_x)
            new_y = int(cursor_y - offset_y - self.height()//2)
            
            # Safety check: ensure widget doesn't end up too close to cursor
            widget_center_x = new_x + self.width() // 2
            widget_center_y = new_y + self.height() // 2
            distance_to_cursor = math.sqrt((widget_center_x - cursor_x) ** 2 + (widget_center_y - cursor_y) ** 2)
            
            if distance_to_cursor < self.min_safe_distance:
                # Adjust position to maintain safe distance
                angle_to_cursor = math.atan2(widget_center_y - cursor_y, widget_center_x - cursor_x)
                new_x = int(cursor_x + int(self.min_safe_distance * math.cos(angle_to_cursor)) - self.width() // 2)
                new_y = int(cursor_y + int(self.min_safe_distance * math.sin(angle_to_cursor)) - self.height() // 2)
            
            # Check if widget actually needs to move (prevent unnecessary updates)
            if self.last_widget_pos is not None:
                widget_dx = new_x - self.last_widget_pos[0]
                widget_dy = new_y - self.last_widget_pos[1]
                widget_movement = math.sqrt(widget_dx * widget_dx + widget_dy * widget_dy)
                
                # Only move if the widget position would change significantly
                if widget_movement < 5:  # Less than 5 pixels, don't bother moving
                    return
            
            # Track when we move to prevent false hover detection
            self.last_move_time = time.time()
            self.last_widget_pos = (new_x, new_y)
            
            self.move(new_x, new_y)
        else:
            # Widget is locked - check if cursor moved far enough to unlock
            if distance_to_widget > self.unlock_threshold:
                self.is_locked = False
                
                # Immediately update to new position
                angle_rad = math.radians(self.offset_angle)
                offset_x = int(self.offset_distance * math.cos(angle_rad))
                offset_y = int(self.offset_distance * math.sin(angle_rad))
                
                new_x = int(cursor_x + offset_x)
                new_y = int(cursor_y - offset_y - self.height()//2)
                
                # Safety check: ensure widget doesn't end up too close to cursor
                widget_center_x = new_x + self.width() // 2
                widget_center_y = new_y + self.height() // 2
                distance_to_cursor = math.sqrt((widget_center_x - cursor_x) ** 2 + (widget_center_y - cursor_y) ** 2)
                
                if distance_to_cursor < self.min_safe_distance:
                    # Adjust position to maintain safe distance
                    angle_to_cursor = math.atan2(widget_center_y - cursor_y, widget_center_x - cursor_x)
                    new_x = int(cursor_x + int(self.min_safe_distance * math.cos(angle_to_cursor)) - self.width() // 2)
                    new_y = int(cursor_y + int(self.min_safe_distance * math.sin(angle_to_cursor)) - self.height() // 2)
                
                # Track when we move to prevent false hover detection
                self.last_move_time = time.time()
                self.last_widget_pos = (new_x, new_y)
                
                self.move(new_x, new_y)

    def check_hover(self, cursor_pos):
        """Check if cursor is hovering over scroll buttons."""
        if not self.is_active:
            return None
        
        # Don't check hover immediately after moving to prevent false detection
        current_time = time.time()
        if current_time - self.last_move_time < self.movement_cooldown:
            return None
        
        # Simple velocity check - only block if moving very fast
        if len(self.cursor_velocity_history) > 0:
            avg_velocity = sum(self.cursor_velocity_history) / len(self.cursor_velocity_history)
            if avg_velocity > 200:  # Much higher threshold - only block very fast movement
                if self.current_hover is not None:
                    self._set_hover(None)
                return None
        
        # Convert pynput coordinates to Qt coordinates for consistency
        qt_cursor_pos = self._convert_pynput_to_qt_coords(cursor_pos)
            
        # Convert cursor position to widget coordinates
        widget_pos = self.mapFromGlobal(qt_cursor_pos)
        
        # Simple bounds checking - just check if cursor is within widget
        if not self.rect().contains(widget_pos):
            if self.current_hover is not None:
                self._set_hover(None)
            return None

        # Determine which button is hovered - simple and straightforward
        button_height = self.height() // 2
        
        if widget_pos.y() < button_height:
            self._set_hover('up')
            return 'up'
        else:
            self._set_hover('down')
            return 'down'

    def _set_hover(self, button):
        """Set hover state and update appearance."""
        if self.current_hover != button:
            # If we're currently scrolling and the new hover is a different direction, stop scrolling
            if (self.is_scrolling and 
                button is not None and 
                self.scroll_direction is not None and 
                button != self.scroll_direction):
                self.stop_scrolling()
            
            self.current_hover = button
            
            if button is not None:
                # Make more opaque when hovered
                self.setWindowOpacity(self.hover_opacity)
                # Lock position when hovering
                if not self.is_locked:
                    self.is_locked = True
            else:
                # Return to base opacity
                self.setWindowOpacity(self.base_opacity)
                
            self.update()  # Trigger repaint
            
    def start_scrolling(self, direction):
        """Start continuous scrolling in given direction."""
        if not self.is_scrolling:
            self.is_scrolling = True
            self.scroll_direction = direction
            self._perform_scroll()  # Immediate first scroll
            self.scroll_timer.start(self.scroll_interval)
            self.scroll_triggered.emit(direction)
            self.update()  # Update appearance
            
    def stop_scrolling(self):
        """Stop continuous scrolling."""
        if self.is_scrolling:
            self.is_scrolling = False
            self.scroll_direction = None
            self.scroll_timer.stop()
            self.update()  # Update appearance
        
    def _perform_scroll(self):
        """Perform a single scroll action."""
        self._scroll_count += 1
        
        # Platform-specific scrolling
        if sys.platform == "darwin":
            # macOS: Use pynput scrolling (more reliable than trying to use macOS APIs)
            try:
                if self.scroll_direction == 'up':
                    self.mouse.scroll(0, self.scroll_amount)
                else:  # 'down'
                    self.mouse.scroll(0, -self.scroll_amount)
            except Exception as e:
                # If scrolling fails, just pass silently
                pass
        else:
            # Windows: Use Windows API for scrolling
            try:
                import ctypes
                from ctypes import wintypes
                
                # Get the current cursor position using Qt for consistency
                try:
                    qt_pos = self._get_qt_cursor_position()
                    cursor_pos = (qt_pos.x(), qt_pos.y())
                except:
                    # Fallback to pynput
                    cursor_pos = self.mouse.position
                
                # Windows API constants for mouse wheel
                WM_MOUSEWHEEL = 0x020A
                WHEEL_DELTA = 120  # Standard wheel delta
                
                # Calculate scroll delta based on direction and amount
                if self.scroll_direction == 'up':
                    wheel_delta = WHEEL_DELTA * self.scroll_amount
                else:  # 'down'
                    wheel_delta = -WHEEL_DELTA * self.scroll_amount
                
                # Get window under cursor
                user32 = ctypes.windll.user32
                
                # Get the window handle at the cursor position
                hwnd = user32.WindowFromPoint(wintypes.POINT(int(cursor_pos[0]), int(cursor_pos[1])))
                
                if hwnd:
                    # Send mouse wheel message to the window
                    wparam = (wheel_delta << 16)
                    lparam = (int(cursor_pos[1]) << 16) | (int(cursor_pos[0]) & 0xFFFF)
                    
                    user32.PostMessageW(hwnd, WM_MOUSEWHEEL, wparam, lparam)
                    
            except Exception as e:
                # Fallback to pynput scrolling if Windows API fails
                try:
                    if self.scroll_direction == 'up':
                        self.mouse.scroll(0, self.scroll_amount)
                    else:  # 'down'
                        self.mouse.scroll(0, -self.scroll_amount)
                except Exception as fallback_error:
                    # If both methods fail, just pass silently
                    pass
        
    def set_active(self, active):
        """Set the active state of the scroll widget."""
        self.is_active = active
        if active:
            # Show the widget when activated
            self.show()
            # Force widget to show on top
            self.raise_()
            # Set initial position if we can get mouse position
            try:
                pos = self.mouse.position
                self.update_position(pos)
            except:
                pass
        else:
            # Stop any active scrolling when deactivated
            self.stop_scrolling()
            self._set_hover(None)
            # Hide the widget when deactivated
            self.hide()
        self.update()  # Trigger repaint
    
    def showEvent(self, event):
        """Override show event to ensure widget appears on top."""
        super().showEvent(event)
        self.raise_()
    
    def changeEvent(self, event):
        """Handle window state changes."""
        super().changeEvent(event)
        # Keep it simple - no special macOS handling
    
    def set_offset(self, distance=None, angle=None):
        """Set the offset distance and angle for positioning relative to cursor."""
        if distance is not None:
            self.offset_distance = distance
        if angle is not None:
            self.offset_angle = angle
    
    def set_scroll_speed(self, interval=None, amount=None):
        """Set the scroll speed settings."""
        if interval is not None:
            self.scroll_interval = interval
        if amount is not None:
            self.scroll_amount = amount
    
    def set_opacity(self, base=None, hover=None):
        """Set the opacity levels for the scroll widget."""
        if base is not None:
            self.base_opacity = base if base <= 1.0 else base / 100.0  # Handle both decimal and percentage
        if hover is not None:
            self.hover_opacity = hover if hover <= 1.0 else hover / 100.0  # Handle both decimal and percentage
        
        # Update current opacity if not hovering
        if self.current_hover is None:
            self.setWindowOpacity(self.base_opacity)