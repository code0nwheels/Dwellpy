"""Floating menu widget for Dwellpy."""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QPoint, QPointF, QTimer, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF, QCursor, QFont
from pynput.mouse import Controller as MouseController
import math
import sys
import time

try:
    from ..config.constants import Colors, BUTTON_IDS
except ImportError:
    # Fallback if constants not available
    class Colors:
        DARK_BG = "#1e1e1e"
        BLUE_ACCENT = "#0078d7"
        TEXT_COLOR = "#ffffff"
        GREEN_ACCENT = "#2ecc71"
        RED_ACCENT = "#e74c3c"
    
    BUTTON_IDS = {
        'LEFT': 'LEFT',
        'DOUBLE': 'DOUBLE', 
        'DRAG': 'DRAG',
        'RIGHT': 'RIGHT',
        'SETUP': 'SETUP'
    }

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

class MenuWidget(QWidget):
    """
    A floating widget that follows the cursor and provides menu functionality.
    Shows a hamburger icon at a safe distance from cursor, expands when hovered.
    """
    
    # Signals
    menu_item_triggered = pyqtSignal(str)  # Emits menu item ID when clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Widget configuration
        self.hamburger_size = 30  # Size of the hamburger icon
        self.expanded_width = 150  # Width when expanded
        self.expanded_height = 220  # Height when expanded - increased to fit all 6 items
        self.offset_distance = 100  # Distance from cursor
        self.offset_angle = -45  # Angle in degrees (bottom-right by default)
        self.min_safe_distance = 50  # Minimum distance to keep widget away from cursor
        
        # State tracking
        self.is_active = False
        self.is_expanded = False
        self.current_hover = None  # Menu item being hovered
        self.base_opacity = 0.8
        self.hover_opacity = 0.95
        
        # Position lock state
        self.is_locked = False  # Whether widget is locked in position
        self.lock_threshold = 120  # Distance to lock
        self.unlock_threshold = 180  # Distance to resume following
        
        # Movement tracking to prevent false hover detection
        self.last_move_time = 0
        self.movement_cooldown = 0.2
        
        # Smooth movement tracking
        self.last_cursor_pos = None
        self.movement_threshold = 15  # Only move widget if cursor moved this many pixels
        self.last_widget_pos = None
        
        # Cursor velocity tracking
        self.cursor_velocity_history = []
        self.max_velocity_for_hover = 100
        self.velocity_check_window = 3
        
        # Mouse controller
        self.mouse = MouseController()
        
        # Menu items configuration
        self.menu_items = [
            {'id': 'LEFT', 'label': 'Left Click', 'color': Colors.BLUE_ACCENT},
            {'id': 'DOUBLE', 'label': 'Double Click', 'color': Colors.GREEN_ACCENT},
            {'id': 'RIGHT', 'label': 'Right Click', 'color': Colors.RED_ACCENT},
            {'id': 'DRAG', 'label': 'Drag', 'color': Colors.BLUE_ACCENT},
            {'id': 'SETUP', 'label': 'Settings', 'color': Colors.TEXT_COLOR},
            {'id': 'OFF', 'label': 'Turn Off', 'color': Colors.RED_ACCENT}
        ]
        
        # Layout configuration
        self.item_height = 30
        self.item_padding = 5
        
        # Reference to UI manager for state checking
        self.ui_manager = None
        
        # Setup UI
        self._setup_ui()
        
        # Set up expansion/contraction animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_expansion)
        self.animation_steps = 10  # Number of animation steps
        self.current_animation_step = 0
        self.target_expanded = False
        
    def _setup_ui(self):
        """Setup the widget UI."""
        # Platform-specific window flags for better macOS compatibility
        if sys.platform == "darwin":  # macOS
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint
            )
        else:
            # Windows/Linux flags
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
        
        # Set initial size (hamburger icon size)
        self.setFixedSize(self.hamburger_size, self.hamburger_size)
        
        # Set initial opacity
        self.setWindowOpacity(self.base_opacity)
        
        # Initially hide the widget
        self.hide()
        
    def paintEvent(self, event):
        """Custom paint event to draw the menu."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not self.is_expanded:
            self._draw_hamburger_icon(painter)
        else:
            self._draw_expanded_menu(painter)
            
    def _draw_hamburger_icon(self, painter):
        """Draw the hamburger icon."""
        # Draw background circle
        background_color = QColor(40, 40, 40, 220) if self.is_locked else QColor(30, 30, 30, 200)
        painter.setBrush(QBrush(background_color))
        
        # Draw border to indicate lock state
        if self.is_locked:
            painter.setPen(QPen(QColor(0, 120, 215), 2))
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            
        # Draw circular background
        painter.drawEllipse(self.rect())
        
        # Draw hamburger lines
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        line_width = 12
        line_spacing = 4
        
        # Three horizontal lines
        for i in range(3):
            y = center_y - line_spacing + (i * line_spacing)
            painter.drawLine(
                center_x - line_width // 2, y,
                center_x + line_width // 2, y
            )
    
    def _draw_expanded_menu(self, painter):
        """Draw the expanded menu with items."""
        # Draw background with rounded corners
        background_color = QColor(30, 30, 30, 240)
        painter.setBrush(QBrush(background_color))
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawRoundedRect(self.rect(), 10, 10)
        
        # Draw menu items
        for i, item in enumerate(self.menu_items):
            self._draw_menu_item(painter, item, i)
    
    def _draw_menu_item(self, painter, item, index):
        """Draw a single menu item."""
        y = index * (self.item_height + self.item_padding) + self.item_padding
        item_rect = QRect(self.item_padding, y, 
                         self.width() - 2 * self.item_padding, self.item_height)
        
        # Determine if this item is hovered
        is_hovered = (self.current_hover == item['id'])
        
        # Determine the item's state color based on UI manager state
        item_color = self._get_item_state_color(item)
        
        # Draw item background
        if is_hovered:
            hover_color = QColor(50, 50, 50, 200)
            painter.setBrush(QBrush(hover_color))
            painter.setPen(QPen(QColor(item_color), 2))
        else:
            # Use different background color based on state
            if self._is_item_active_state(item):
                # Active state (blue or red) - show colored background
                bg_color = QColor(item_color)
                bg_color.setAlpha(100)  # Semi-transparent
                painter.setBrush(QBrush(bg_color))
            else:
                # Inactive state - show dark background
                painter.setBrush(QBrush(QColor(40, 40, 40, 150)))
            painter.setPen(Qt.PenStyle.NoPen)
        
        painter.drawRoundedRect(item_rect, 5, 5)
        
        # Draw item text
        text_color = QColor(item_color) if is_hovered or self._is_item_active_state(item) else QColor(255, 255, 255)
        painter.setPen(QPen(text_color))
        painter.setFont(QFont("Helvetica Neue", 10, QFont.Weight.Bold))
        painter.drawText(item_rect, Qt.AlignmentFlag.AlignCenter, item['label'])
    
    def _get_item_state_color(self, item):
        """Get the color for a menu item based on current UI state."""
        if not self.ui_manager:
            return item['color']
        
        item_id = item['id']
        
        # Handle special buttons
        if item_id == 'OFF':
            return Colors.RED_ACCENT
        elif item_id == 'SETUP':
            return Colors.TEXT_COLOR
        
        # Handle click mode buttons
        if item_id in ['LEFT', 'DOUBLE', 'RIGHT', 'DRAG']:
            if not self.ui_manager.is_active:
                return "#999999"  # Disabled color when app is off
            
            # Check if this is the current mode
            if item_id == self.ui_manager.current_mode:
                # Current mode - red if temporary, blue if permanent
                if self.ui_manager.is_temporary_mode:
                    return Colors.RED_ACCENT  # Temporary mode
                else:
                    return Colors.BLUE_ACCENT  # Current permanent mode
            elif item_id == self.ui_manager.default_mode:
                # Default mode (but not current) - blue
                return Colors.BLUE_ACCENT
            else:
                # Other modes - default color
                return Colors.TEXT_COLOR
        
        return item['color']
    
    def _is_item_active_state(self, item):
        """Check if a menu item should show an active state background."""
        if not self.ui_manager:
            return False
        
        item_id = item['id']
        
        # Handle click mode buttons
        if item_id in ['LEFT', 'DOUBLE', 'RIGHT', 'DRAG']:
            if not self.ui_manager.is_active:
                return False
            
            # Show active background for current mode or default mode
            return (item_id == self.ui_manager.current_mode or 
                   item_id == self.ui_manager.default_mode)
        
        return False
    
    def _get_qt_cursor_position(self):
        """Get cursor position using Qt's coordinate system for consistency."""
        try:
            return QCursor.pos()
        except:
            pos = self.mouse.position
            return QPoint(int(pos[0]), int(pos[1]))
    
    def _convert_pynput_to_qt_coords(self, pynput_pos):
        """Convert pynput coordinates to Qt coordinates for multi-monitor consistency."""
        try:
            app = QApplication.instance()
            if not app:
                return QPoint(int(pynput_pos[0]), int(pynput_pos[1]))
            
            # Try using Qt's cursor position as it should be more accurate
            try:
                qt_direct = QCursor.pos()
                dx = abs(qt_direct.x() - pynput_pos[0])
                dy = abs(qt_direct.y() - pynput_pos[1])
                if dx < 10 and dy < 10:  # Within 10 pixels, use Qt directly
                    return qt_direct
            except:
                pass
            
            return QPoint(int(pynput_pos[0]), int(pynput_pos[1]))
            
        except Exception as e:
            print(f"MenuWidget coordinate conversion error: {e}")
            return QPoint(int(pynput_pos[0]), int(pynput_pos[1]))

    def set_coordinated_position(self, position):
        """Set widget position using coordinated positioning (for multi-widget layouts)."""
        if not self.is_active:
            return
        
        # Move widget to the specified coordinated position
        self.move(position[0], position[1])
        self.last_widget_pos = position
    
    def update_position(self, cursor_pos, coordinated_mode=False):
        """Update widget position relative to cursor, with optional coordinated mode."""
        if not self.is_active:
            return
        
        # If in coordinated mode, skip normal positioning logic
        if coordinated_mode:
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
            
            time_delta = current_time - getattr(self, 'last_update_time', current_time)
            if time_delta > 0:
                velocity = distance / time_delta
                self.cursor_velocity_history.append(velocity)
                if len(self.cursor_velocity_history) > self.velocity_check_window:
                    self.cursor_velocity_history.pop(0)
        
        self.last_update_time = current_time
        
        # Check if cursor has moved significantly since last update
        if self.last_cursor_pos is not None:
            dx = cursor_x - self.last_cursor_pos[0]
            dy = cursor_y - self.last_cursor_pos[1]
            movement_distance = math.sqrt(dx * dx + dy * dy)
            
            if movement_distance < self.movement_threshold and not self.is_locked:
                return
        
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
            if distance_to_widget < self.lock_threshold:
                self.is_locked = True
                return
            
            # Calculate new position
            angle_rad = math.radians(self.offset_angle)
            offset_x = int(self.offset_distance * math.cos(angle_rad))
            offset_y = int(self.offset_distance * math.sin(angle_rad))
            
            new_x = int(cursor_x + offset_x)
            new_y = int(cursor_y + offset_y)
            
            # Safety check for minimum distance
            widget_center_x = new_x + self.width() // 2
            widget_center_y = new_y + self.height() // 2
            distance_to_cursor = math.sqrt((widget_center_x - cursor_x) ** 2 + (widget_center_y - cursor_y) ** 2)
            
            if distance_to_cursor < self.min_safe_distance:
                angle_to_cursor = math.atan2(widget_center_y - cursor_y, widget_center_x - cursor_x)
                new_x = int(cursor_x + int(self.min_safe_distance * math.cos(angle_to_cursor)) - self.width() // 2)
                new_y = int(cursor_y + int(self.min_safe_distance * math.sin(angle_to_cursor)) - self.height() // 2)
            
            # Check if widget actually needs to move
            if self.last_widget_pos is not None:
                widget_dx = new_x - self.last_widget_pos[0]
                widget_dy = new_y - self.last_widget_pos[1]
                widget_movement = math.sqrt(widget_dx * widget_dx + widget_dy * widget_dy)
                
                if widget_movement < 5:
                    return
            
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
                new_y = int(cursor_y + offset_y)
                
                # Safety check
                widget_center_x = new_x + self.width() // 2
                widget_center_y = new_y + self.height() // 2
                distance_to_cursor = math.sqrt((widget_center_x - cursor_x) ** 2 + (widget_center_y - cursor_y) ** 2)
                
                if distance_to_cursor < self.min_safe_distance:
                    angle_to_cursor = math.atan2(widget_center_y - cursor_y, widget_center_x - cursor_x)
                    new_x = int(cursor_x + int(self.min_safe_distance * math.cos(angle_to_cursor)) - self.width() // 2)
                    new_y = int(cursor_y + int(self.min_safe_distance * math.sin(angle_to_cursor)) - self.height() // 2)
                
                self.last_move_time = time.time()
                self.last_widget_pos = (new_x, new_y)
                
                self.move(new_x, new_y)

    def check_hover(self, cursor_pos):
        """Check if cursor is hovering over the widget or menu items."""
        if not self.is_active:
            return None
        
        # Don't check hover immediately after moving
        current_time = time.time()
        if current_time - self.last_move_time < self.movement_cooldown:
            return None
        
        # Simple velocity check - only block if moving very fast
        if len(self.cursor_velocity_history) > 0:
            avg_velocity = sum(self.cursor_velocity_history) / len(self.cursor_velocity_history)
            if avg_velocity > 200:
                if self.current_hover is not None or self.is_expanded:
                    self._set_hover(None)
                    self._set_expanded(False)
                return None
        
        # Convert pynput coordinates to Qt coordinates
        qt_cursor_pos = self._convert_pynput_to_qt_coords(cursor_pos)
        
        # Convert cursor position to widget coordinates
        widget_pos = self.mapFromGlobal(qt_cursor_pos)
        
        # Check if cursor is within widget bounds
        if not self.rect().contains(widget_pos):
            if self.current_hover is not None or self.is_expanded:
                self._set_hover(None)
                self._set_expanded(False)
            return None

        # If we're here, cursor is over the widget
        if not self.is_expanded:
            # Hovering over hamburger icon - expand the menu
            self._set_expanded(True)
            return 'hamburger'
        else:
            # Check which menu item is being hovered
            for i, item in enumerate(self.menu_items):
                item_y = i * (self.item_height + self.item_padding) + self.item_padding
                item_rect = QRect(self.item_padding, item_y, 
                                 self.width() - 2 * self.item_padding, self.item_height)
                
                if item_rect.contains(widget_pos):
                    self._set_hover(item['id'])
                    return item['id']
            
            # Hovering over expanded menu but not on specific item
            self._set_hover(None)
            return 'expanded'

    def _set_hover(self, item_id):
        """Set hover state for menu items."""
        if self.current_hover != item_id:
            self.current_hover = item_id
            
            if item_id is not None:
                self.setWindowOpacity(self.hover_opacity)
                if not self.is_locked:
                    self.is_locked = True
            else:
                self.setWindowOpacity(self.base_opacity)
                
            self.update()  # Trigger repaint
    
    def _set_expanded(self, expanded):
        """Set the expanded state of the menu."""
        if self.target_expanded != expanded:
            self.target_expanded = expanded
            self.current_animation_step = 0
            
            if not self.animation_timer.isActive():
                self.animation_timer.start(20)  # 20ms intervals for smooth animation
    
    def _animate_expansion(self):
        """Animate the expansion/contraction of the menu."""
        self.current_animation_step += 1
        progress = self.current_animation_step / self.animation_steps
        
        if self.target_expanded:
            # Expanding
            current_width = int(self.hamburger_size + (self.expanded_width - self.hamburger_size) * progress)
            current_height = int(self.hamburger_size + (self.expanded_height - self.hamburger_size) * progress)
        else:
            # Contracting
            current_width = int(self.expanded_width - (self.expanded_width - self.hamburger_size) * progress)
            current_height = int(self.expanded_height - (self.expanded_height - self.hamburger_size) * progress)
        
        self.setFixedSize(current_width, current_height)
        self.update()
        
        if self.current_animation_step >= self.animation_steps:
            self.animation_timer.stop()
            self.is_expanded = self.target_expanded
            
            if self.is_expanded:
                self.setFixedSize(self.expanded_width, self.expanded_height)
            else:
                self.setFixedSize(self.hamburger_size, self.hamburger_size)
    
    def trigger_menu_item(self, item_id):
        """Trigger a menu item action."""
        if item_id and item_id != 'hamburger' and item_id != 'expanded':
            self.menu_item_triggered.emit(item_id)
            # Don't contract menu after selection - keep it expanded
            # self._set_expanded(False)
            # self._set_hover(None)
    
    def set_active(self, active):
        """Set the active state of the menu widget."""
        self.is_active = active
        if active:
            self.show()
            self.raise_()
            try:
                pos = self.mouse.position
                self.update_position(pos)
            except:
                pass
        else:
            self._set_hover(None)
            self._set_expanded(False)
            self.hide()
        self.update()
    
    def showEvent(self, event):
        """Override show event to ensure widget appears on top."""
        super().showEvent(event)
        self.raise_()
    
    def set_offset(self, distance=None, angle=None):
        """Set the offset distance and angle for positioning relative to cursor."""
        if distance is not None:
            self.offset_distance = distance
        if angle is not None:
            self.offset_angle = angle
    
    def set_opacity(self, base=None, hover=None):
        """Set the opacity levels for the menu widget."""
        if base is not None:
            self.base_opacity = base if base <= 1.0 else base / 100.0
        if hover is not None:
            self.hover_opacity = hover if hover <= 1.0 else hover / 100.0
        
        # Update current opacity if not hovering
        if self.current_hover is None:
            self.setWindowOpacity(self.base_opacity) 