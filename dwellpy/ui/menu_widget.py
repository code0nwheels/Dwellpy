"""Floating menu widget for Dwellpy."""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QPoint, QPointF, QTimer, pyqtSignal, QRect, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF, QCursor, QFont, QPixmap
from pynput.mouse import Controller as MouseController
import math
import sys
import time

try:
    from ..config.constants import Colors, BUTTON_IDS, ICON_MAPPING
    from ..utils.helpers import get_asset_path
except ImportError:
    # Fallback if constants not available
    class Colors:
        DARK_BG = "#1e1e1e"
        BLUE_ACCENT = "#0078d7"
        TEXT_COLOR = "#ffffff"
        GREEN_ACCENT = "#2ecc71"
        RED_ACCENT = "#e74c3c"
    
    def get_asset_path(asset_name):
        """Fallback get_asset_path function"""
        import os
        return os.path.join(os.path.dirname(__file__), '..', 'assets', 'icons', asset_name)
    
    BUTTON_IDS = {
        'LEFT': 'LEFT',
        'DOUBLE': 'DOUBLE', 
        'DRAG': 'DRAG',
        'RIGHT': 'RIGHT',
        'SETUP': 'SETUP'
    }
    
    ICON_MAPPING = {
        "LEFT": "left.png",
        "DOUBLE": "double.png", 
        "DRAG": "drag.png",
        "RIGHT": "right.png",
        "SETUP": "setup.png",
        "ON_OFF": "off.png"
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
    Shows a hamburger icon at a safe distance from cursor, expands in a circle when hovered.
    Redesigned for optimal accessibility - circular layout centers around cursor position.
    """
    
    # Signals
    menu_item_triggered = pyqtSignal(str)  # Emits menu item ID when clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Widget configuration - redesigned for circular layout around hamburger icon
        self.hamburger_size = 30  # Size of the hamburger icon
        self.circle_radius = 60  # Radius of the circular menu layout from hamburger center
        self.expanded_size = 200  # Size of the expanded widget (smaller since we're centering on hamburger)
        self.offset_distance = 100  # Distance from cursor for hamburger icon
        self.offset_angle = -45  # Angle in degrees (bottom-right by default)
        self.min_safe_distance = 50  # Minimum distance to keep widget away from cursor
        
        # State tracking
        self.is_active = False
        self.is_expanded = False
        self.current_hover = None  # Menu item being hovered
        self.base_opacity = 0.8
        self.hover_opacity = 0.95
        
        # Position lock state - keeping existing lock logic for accessibility
        self.is_locked = False  # Whether widget is locked in position
        self.lock_threshold = 120  # Distance to lock
        self.unlock_threshold = 180  # Distance to resume following (will be set by settings)
        
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
            {'id': 'LEFT', 'label': 'Left', 'color': Colors.BLUE_ACCENT, 'icon': ICON_MAPPING.get('LEFT', 'left.png')},
            {'id': 'DOUBLE', 'label': 'Double', 'color': Colors.GREEN_ACCENT, 'icon': ICON_MAPPING.get('DOUBLE', 'double.png')},
            {'id': 'RIGHT', 'label': 'Right', 'color': Colors.RED_ACCENT, 'icon': ICON_MAPPING.get('RIGHT', 'right.png')},
            {'id': 'DRAG', 'label': 'Drag', 'color': Colors.BLUE_ACCENT, 'icon': ICON_MAPPING.get('DRAG', 'drag.png')},
            {'id': 'SETUP', 'label': 'Settings', 'color': Colors.TEXT_COLOR, 'icon': ICON_MAPPING.get('SETUP', 'setup.png')},
            {'id': 'OFF', 'label': 'Turn Off', 'color': Colors.RED_ACCENT, 'icon': ICON_MAPPING.get('ON_OFF', 'off.png')}  # Use OFF state icon
        ]
        
        # Layout configuration - circular layout around hamburger icon
        self.item_size = 35  # Size of each circular menu item
        self.cursor_in_widget = QPoint(0, 0)  # Cursor position relative to widget
        
        # Animation state for radial expansion
        self.current_radius = 0  # Current animated radius for menu items
        
        # Reference to UI manager for state checking
        self.ui_manager = None
        
        # Load hamburger icon
        self.hamburger_icon = None
        self._load_hamburger_icon()
        
        # Load menu item icons
        self.menu_item_icons = {}
        self._load_menu_item_icons()
        
        # Setup UI
        self._setup_ui()
        
        # Set up expansion/contraction animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_expansion)
        self.animation_steps = 8  # Reduced from 15 for faster animation
        self.current_animation_step = 0
        self.target_expanded = False
        
    def _setup_ui(self):
        """Setup the widget UI."""        # Platform-specific window flags for better macOS compatibility
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
        
        # Prevent focus stealing on all platforms - this is crucial for macOS
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Set to not accept focus
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # Set initial size (hamburger icon size)
        self.setFixedSize(self.hamburger_size, self.hamburger_size)
        
        # Set initial opacity
        self.setWindowOpacity(self.base_opacity)
        
        # Initially hide the widget
        self.hide()
    
    def _load_hamburger_icon(self):
        """Load the hamburger icon from assets."""
        try:
            icon_path = get_asset_path("hamburger.png")
            self.hamburger_icon = QPixmap(icon_path)
            if self.hamburger_icon.isNull():
                self.hamburger_icon = None
        except Exception:
            self.hamburger_icon = None
    
    def _load_menu_item_icons(self):
        """Load icons for menu items."""
        self.menu_item_icons = {}
        for item in self.menu_items:
            try:
                icon_path = get_asset_path(item['icon'])
                icon = QPixmap(icon_path)
                if not icon.isNull():
                    self.menu_item_icons[item['id']] = icon
            except Exception:
                pass  # Icon will not be available for this item
        
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
        
        # Draw hamburger icon from file if available, otherwise fallback to lines
        if self.hamburger_icon and not self.hamburger_icon.isNull():
            # Calculate icon size with minimal padding for larger icon
            icon_size = min(self.width(), self.height()) - 6  # 3px padding on each side
            center_x = self.width() // 2
            center_y = self.height() // 2
            
            # Create target rectangle for the icon
            icon_rect = QRect(
                center_x - icon_size // 2,
                center_y - icon_size // 2,
                icon_size,
                icon_size
            )
            
            # Draw the scaled hamburger icon
            painter.drawPixmap(icon_rect, self.hamburger_icon)
        else:
            # Fallback to drawing hamburger lines
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
        """Draw the expanded menu with items in circular layout around hamburger icon."""
        # The hamburger icon stays in the center of the expanded widget
        hamburger_center_x = self.width() // 2
        hamburger_center_y = self.height() // 2
        hamburger_center = QPoint(hamburger_center_x, hamburger_center_y)
        
        # Draw hamburger icon at center
        hamburger_size = 30  # Increased size for better visibility
        hamburger_rect = QRect(hamburger_center_x - hamburger_size//2, hamburger_center_y - hamburger_size//2, 
                              hamburger_size, hamburger_size)
        
        # Draw hamburger background
        background_color = QColor(40, 40, 40, 220) if self.is_locked else QColor(30, 30, 30, 200)
        painter.setBrush(QBrush(background_color))
        
        # Draw border to indicate lock state
        if self.is_locked:
            painter.setPen(QPen(QColor(0, 120, 215), 2))
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            
        painter.drawEllipse(hamburger_rect)
        
        # Draw hamburger icon from file if available, otherwise fallback to lines
        if self.hamburger_icon and not self.hamburger_icon.isNull():
            # Use the icon file for the hamburger in expanded menu
            icon_size = hamburger_size - 4  # Small padding within the background circle
            icon_rect = QRect(
                hamburger_center_x - icon_size // 2,
                hamburger_center_y - icon_size // 2,
                icon_size,
                icon_size
            )
            painter.drawPixmap(icon_rect, self.hamburger_icon)
        else:
            # Fallback to drawing hamburger lines
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            line_width = 8
            line_spacing = 3
            
            for i in range(3):
                y = hamburger_center_y - line_spacing + (i * line_spacing)
                painter.drawLine(
                    hamburger_center_x - line_width // 2, y,
                    hamburger_center_x + line_width // 2, y
                )
        
        # Draw menu items in a circle around hamburger icon using animated radius
        for i, item in enumerate(self.menu_items):
            self._draw_circular_menu_item(painter, item, i, hamburger_center)
    
    def _draw_circular_menu_item(self, painter, item, index, center_pos):
        """Draw a single menu item in circular layout around the hamburger center."""
        # Calculate position on circle around hamburger icon using animated radius
        angle = (index * 360 / len(self.menu_items)) - 90  # Start from top (-90 degrees)
        angle_rad = math.radians(angle)
        
        # Use animated radius instead of fixed radius
        item_x = center_pos.x() + int(self.current_radius * math.cos(angle_rad)) - self.item_size // 2
        item_y = center_pos.y() + int(self.current_radius * math.sin(angle_rad)) - self.item_size // 2
        
        item_rect = QRect(item_x, item_y, self.item_size, self.item_size)
        
        # Calculate opacity based on animation progress for fade-in effect
        animation_progress = self.current_radius / self.circle_radius if self.circle_radius > 0 else 0
        base_alpha = int(200 * animation_progress)
        
        # Determine if this item is hovered
        is_hovered = (self.current_hover == item['id'])
        
        # Determine the item's state color based on UI manager state
        item_color = self._get_item_state_color(item)
        
        # Draw item background circle with animated alpha
        if is_hovered:
            hover_color = QColor(70, 70, 70, min(220, base_alpha + 50))
            painter.setBrush(QBrush(hover_color))
            painter.setPen(QPen(QColor(item_color), 2))
        else:
            # Use different background color based on state
            if self._is_item_active_state(item):
                # Active state (blue or red) - show colored background
                bg_color = QColor(item_color)
                bg_color.setAlpha(min(140, base_alpha))  # Animated alpha
                painter.setBrush(QBrush(bg_color))
                painter.setPen(QPen(QColor(item_color), 1))
            else:
                # Inactive state - show dark background
                inactive_color = QColor(50, 50, 50, base_alpha)
                painter.setBrush(QBrush(inactive_color))
                painter.setPen(QPen(QColor(80, 80, 80), 1))
        
        painter.drawEllipse(item_rect)
        
        # Draw item icon if available, otherwise draw text
        if item['id'] in self.menu_item_icons:
            # Draw icon
            icon = self.menu_item_icons[item['id']]
            # Calculate icon size with padding
            icon_size = min(item_rect.width(), item_rect.height()) - 8  # 4px padding on each side
            icon_rect = QRect(
                item_rect.center().x() - icon_size // 2,
                item_rect.center().y() - icon_size // 2,
                icon_size,
                icon_size
            )
            painter.drawPixmap(icon_rect, icon)
        else:
            # Fallback to text if icon not available
            text_color = QColor(item_color) if is_hovered or self._is_item_active_state(item) else QColor(255, 255, 255)
            text_color.setAlpha(min(255, base_alpha + 55))  # Ensure text is visible
            painter.setPen(QPen(text_color))
            painter.setFont(QFont("Helvetica Neue", 8, QFont.Weight.Bold))
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
    
    def update_position(self, cursor_pos, coordinated_mode=False, y_offset=0):
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
            
            # Position widget so hamburger icon is centered under cursor
            widget_size = self.expanded_size if self.is_expanded else self.hamburger_size
            new_x = int(cursor_x - widget_size // 2)
            new_y = int(cursor_y - widget_size // 2) + y_offset
            
            # Check if widget actually needs to move
            if self.last_widget_pos is not None:
                widget_dx = new_x - self.last_widget_pos[0]
                widget_dy = new_y - self.last_widget_pos[1]
                widget_movement = math.sqrt(widget_dx * widget_dx + widget_dy * widget_dy)
                
                if widget_movement < 5:
                    return
            
            # Check for screen bounds and adjust position if necessary
            off_screen_info = self._detect_off_screen_position(QPoint(new_x, new_y), self.size())
            if off_screen_info['off_screen']:
                # Off-screen - adjust position to be within bounds
                adjusted_pos = self._adjust_position_for_screen_bounds(QPoint(new_x, new_y), self.size())
                self.last_move_time = time.time()
                self.last_widget_pos = (adjusted_pos.x(), adjusted_pos.y())
                
                self.move(adjusted_pos.x(), adjusted_pos.y())
            else:
                self.last_move_time = time.time()
                self.last_widget_pos = (new_x, new_y)
                
                self.move(new_x, new_y)
        else:
            # Widget is locked - check if cursor moved far enough to unlock
            if distance_to_widget > self.unlock_threshold:
                self.is_locked = False
                
                # Immediately update to new position centered under cursor
                widget_size = self.expanded_size if self.is_expanded else self.hamburger_size
                new_x = int(cursor_x - widget_size // 2)
                new_y = int(cursor_y - widget_size // 2) + y_offset
                
                # Check for screen bounds and adjust position if necessary
                off_screen_info = self._detect_off_screen_position(QPoint(new_x, new_y), self.size())
                if off_screen_info['off_screen']:
                    # Off-screen - adjust position to be within bounds
                    adjusted_pos = self._adjust_position_for_screen_bounds(QPoint(new_x, new_y), self.size())
                    self.last_move_time = time.time()
                    self.last_widget_pos = (adjusted_pos.x(), adjusted_pos.y())
                    
                    self.move(adjusted_pos.x(), adjusted_pos.y())
                else:
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
            # For expanded menu, use the center of the widget as hamburger position
            hamburger_center_x = self.width() // 2
            hamburger_center_y = self.height() // 2
            hamburger_center = QPoint(hamburger_center_x, hamburger_center_y)
            
            # Check center hamburger area
            center_size = 20
            center_rect = QRect(hamburger_center_x - center_size//2, hamburger_center_y - center_size//2, 
                               center_size, center_size)
            
            if center_rect.contains(widget_pos):
                self._set_hover(None)
                return 'hamburger'
            
            # Check which circular menu item is being hovered using current animated radius
            for i, item in enumerate(self.menu_items):
                # Calculate position on circle around hamburger center using current radius
                angle = (i * 360 / len(self.menu_items)) - 90  # Start from top
                angle_rad = math.radians(angle)
                
                item_x = hamburger_center.x() + int(self.current_radius * math.cos(angle_rad)) - self.item_size // 2
                item_y = hamburger_center.y() + int(self.current_radius * math.sin(angle_rad)) - self.item_size // 2
                
                item_rect = QRect(item_x, item_y, self.item_size, self.item_size)
                
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
            
            # When expanding, immediately resize and reposition centered under cursor
            if expanded and not self.is_expanded:
                # Get current cursor position
                try:
                    cursor_global = self._get_qt_cursor_position()
                    cursor_x, cursor_y = cursor_global.x(), cursor_global.y()
                    
                    # Immediately resize to full size and center under cursor
                    self.setFixedSize(self.expanded_size, self.expanded_size)
                    new_x = int(cursor_x - self.expanded_size // 2)
                    new_y = int(cursor_y - self.expanded_size // 2)
                    self.move(new_x, new_y)
                    
                    # Start with radius 0 for animation
                    self.current_radius = 0
                except:
                    # Fallback to current positioning if cursor position unavailable
                    self.setFixedSize(self.expanded_size, self.expanded_size)
                    self.current_radius = 0
                
            elif not expanded and self.is_expanded:
                # When contracting, start with full radius and animate to 0
                self.current_radius = self.circle_radius
            
            if not self.animation_timer.isActive():
                self.animation_timer.start(12)  # Reduced from 20ms for faster animation
    
    def _animate_expansion(self):
        """Animate the expansion/contraction of the menu with radial item animation."""
        self.current_animation_step += 1
        progress = self.current_animation_step / self.animation_steps
        
        if self.target_expanded:
            # Expanding - widget is already full size, just animate radius
            self.current_radius = self.circle_radius * progress
        else:
            # Contracting - animate radius to 0, then resize widget at end
            self.current_radius = self.circle_radius * (1 - progress)
        
        self.update()
        
        if self.current_animation_step >= self.animation_steps:
            self.animation_timer.stop()
            self.is_expanded = self.target_expanded
            
            if self.is_expanded:
                # Already at full size, just ensure final radius
                self.current_radius = self.circle_radius
            else:
                # Contraction finished - now resize back to hamburger size
                self.current_radius = 0
                
                # Move back to original position and resize
                size_diff = self.expanded_size - self.hamburger_size
                offset = size_diff // 2
                current_pos = self.pos()
                
                self.setFixedSize(self.hamburger_size, self.hamburger_size)
                self.move(current_pos.x() + offset, current_pos.y() + offset)

    def trigger_menu_item(self, item_id):
        """Trigger a menu item action."""
        if item_id and item_id != 'hamburger' and item_id != 'expanded':
            self.menu_item_triggered.emit(item_id)            # Don't contract menu after selection - keep it expanded
            # self._set_expanded(False)
            # self._set_hover(None)
    
    def set_active(self, active):
        """Set the active state of the menu widget."""
        self.is_active = active
        if active:
            self.show()
            # Only raise on non-macOS platforms to prevent focus stealing
            if sys.platform != "darwin":
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
        # Only raise on non-macOS platforms to prevent focus stealing
        if sys.platform != "darwin":
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
    
    def _get_screen_geometry(self):
        """Get the screen geometry that contains the current cursor position."""
        try:
            app = QApplication.instance()
            if not app:
                return None
            
            # Get all screens
            screens = app.screens()
            if not screens:
                return None
            
            # Get current cursor position
            cursor_pos = QCursor.pos()
            
            # Find which screen contains the cursor
            for screen in screens:
                geometry = screen.geometry()
                if geometry.contains(cursor_pos):
                    return geometry
            
            # If no screen contains cursor, return primary screen
            return app.primaryScreen().geometry()
            
        except Exception:
            return None
    
    def _detect_off_screen_position(self, proposed_pos, widget_size):
        """
        Detect if a proposed widget position would place it off-screen.
        
        Args:
            proposed_pos: QPoint representing the proposed widget position
            widget_size: QSize representing the widget dimensions
            
        Returns:
            dict: Information about off-screen positioning
        """
        screen_geometry = self._get_screen_geometry()
        if not screen_geometry:
            return {'off_screen': False}
        
        # Calculate widget bounds at proposed position
        widget_right = proposed_pos.x() + widget_size.width()
        widget_bottom = proposed_pos.y() + widget_size.height()
        widget_left = proposed_pos.x()
        widget_top = proposed_pos.y()
        
        # Check each edge
        off_screen_info = {
            'off_screen': False,
            'off_left': widget_left < screen_geometry.left(),
            'off_right': widget_right > screen_geometry.right(),
            'off_top': widget_top < screen_geometry.top(),
            'off_bottom': widget_bottom > screen_geometry.bottom()
        }
        
        # Set overall off_screen flag
        off_screen_info['off_screen'] = any([
            off_screen_info['off_left'],
            off_screen_info['off_right'], 
            off_screen_info['off_top'],
            off_screen_info['off_bottom']
        ])
        
        return off_screen_info
    
    def _adjust_position_for_screen_bounds(self, proposed_pos, widget_size):
        """
        Adjust a proposed position to keep the widget within screen bounds.
        
        Args:
            proposed_pos: QPoint representing the proposed widget position
            widget_size: QSize representing the widget dimensions
            
        Returns:
            QPoint: Adjusted position that stays within screen bounds
        """
        screen_geometry = self._get_screen_geometry()
        if not screen_geometry:
            return proposed_pos
        
        adjusted_x = proposed_pos.x()
        adjusted_y = proposed_pos.y()
        
        # Adjust horizontal position
        if adjusted_x < screen_geometry.left():
            adjusted_x = screen_geometry.left()
        elif adjusted_x + widget_size.width() > screen_geometry.right():
            adjusted_x = screen_geometry.right() - widget_size.width()
        
        # Adjust vertical position  
        if adjusted_y < screen_geometry.top():
            adjusted_y = screen_geometry.top()
        elif adjusted_y + widget_size.height() > screen_geometry.bottom():
            adjusted_y = screen_geometry.bottom() - widget_size.height()
        
        return QPoint(adjusted_x, adjusted_y)