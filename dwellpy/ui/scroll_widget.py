"""Floating scroll widget for Dwellpy."""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QPoint, QPointF, QTimer, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF
from pynput.mouse import Controller as MouseController
import math

try:
    from ..config.constants import Colors
except ImportError:
    # Fallback if constants not available
    class Colors:
        DARK_BG = "#1e1e1e"
        BLUE_ACCENT = "#0078d7"
        TEXT_COLOR = "#ffffff"

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
        self.offset_distance = 50  # Distance from cursor
        self.offset_angle = 45  # Angle in degrees (top-right by default)
        
        # State tracking
        self.is_active = False
        self.current_hover = None  # 'up', 'down', or None
        self.base_opacity = 0.7  # 30% opacity when not hovered
        self.hover_opacity = 0.9  # 90% opacity when hovered
        self.is_scrolling = False
        self.scroll_direction = None
        
        # Position lock state
        self.is_locked = False  # Whether widget is locked in position
        self.lock_threshold = 60  # Distance to lock/unlock
        self.unlock_threshold = 120  # Distance to resume following
        
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
        # Window flags for floating behavior
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
        
        # Ensure wheel events pass through
        self.installEventFilter(self)
        
        # Set fixed size
        self.setFixedSize(self.widget_size, self.widget_size * 2)
        
        # Set initial opacity
        self.setWindowOpacity(self.base_opacity)
    
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
        
    def update_position(self, cursor_pos):
        """Update widget position relative to cursor."""
        if not self.is_active:
            return
            
        # Get widget center in global coordinates
        widget_center = self.rect().center()
        widget_global_center = self.mapToGlobal(widget_center)
        
        # Calculate distance from cursor to widget center
        dx = cursor_pos[0] - widget_global_center.x()
        dy = cursor_pos[1] - widget_global_center.y()
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
            
            # Set new position
            new_x = cursor_pos[0] + offset_x
            new_y = cursor_pos[1] - offset_y - self.height()//2
            
            self.move(new_x, new_y)
        else:
            # Widget is locked - check if cursor moved far enough to unlock
            if distance_to_widget > self.unlock_threshold:
                self.is_locked = False
                
                # Immediately update to new position
                angle_rad = math.radians(self.offset_angle)
                offset_x = int(self.offset_distance * math.cos(angle_rad))
                offset_y = int(self.offset_distance * math.sin(angle_rad))
                
                new_x = cursor_pos[0] + offset_x
                new_y = cursor_pos[1] - offset_y - self.height()//2
                
                self.move(new_x, new_y)
        
    def check_hover(self, cursor_pos):
        """Check if cursor is hovering over scroll buttons."""
        if not self.is_active:
            return None
            
        # Convert cursor position to widget coordinates
        widget_pos = self.mapFromGlobal(QPoint(cursor_pos[0], cursor_pos[1]))
        
        # Check if cursor is within widget bounds
        if not self.rect().contains(widget_pos):
            if self.current_hover is not None:
                self._set_hover(None)
            return None

        # DO NOT change WindowTransparentForInput here!
        # Only visual feedback:
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
        
        # Use winuser.dll for Windows scrolling
        # ... existing code ...