"""Floating menu widget for Dwellpy."""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QPoint, QPointF, QTimer, pyqtSignal, QRect, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF, QCursor, QFont, QPixmap
from pynput.mouse import Controller as MouseController
from .components.menu_drawing import MenuDrawingManager
from ..utils.coordinate_manager import get_cursor_position, get_screen_at_cursor, get_dpi_scale_at_cursor
import math
import sys
import time

try:
    from ..config.constants import Colors, BUTTON_IDS, WIDGET_UNLOCK_THRESHOLD_DEFAULT, ICON_MAPPING
    from ..utils.helpers import get_asset_path
    from ..utils.platform import ensure_windows_dpi_awareness
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

    def ensure_windows_dpi_awareness():
        pass

ensure_windows_dpi_awareness()


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
        self.unlock_threshold = WIDGET_UNLOCK_THRESHOLD_DEFAULT  # Distance to resume following (will be set by settings)
        
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
        
        # Safety mechanism to prevent getting permanently stuck
        self.last_lock_time = 0
        self.max_lock_duration = 5.0  # Maximum time to stay locked (5 seconds)
        
        # Mouse controller
        self.mouse = MouseController()
        
        # Menu items configuration
        self.menu_items = [
            {'id': 'LEFT', 'label': 'Left', 'color': Colors.BLUE_ACCENT, 'icon': ICON_MAPPING.get('LEFT', 'left.png')},
            {'id': 'DOUBLE', 'label': 'Double', 'color': Colors.GREEN_ACCENT, 'icon': ICON_MAPPING.get('DOUBLE', 'double.png')},
            {'id': 'RIGHT', 'label': 'Right', 'color': Colors.RED_ACCENT, 'icon': ICON_MAPPING.get('RIGHT', 'right.png')},
            {'id': 'DRAG', 'label': 'Drag', 'color': Colors.BLUE_ACCENT, 'icon': ICON_MAPPING.get('DRAG', 'drag.png')},
            {'id': 'SETUP', 'label': 'Settings', 'color': Colors.TEXT_COLOR, 'icon': ICON_MAPPING.get('SETUP', 'setup.png')},
            {'id': 'OFF', 'label': 'Turn Off', 'color': Colors.RED_ACCENT, 'icon': 'off.png'}  # Explicitly use off.png icon
        ]
        
        # Layout configuration - circular layout around hamburger icon
        self.item_size = 35
        self.set_item_size(self.item_size)  # Initialize dynamic sizes
        
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
        
        # Setup drawing manager
        self.drawing_manager = MenuDrawingManager(self)
        
        # Setup UI
        self._setup_ui()
        
        # Set up expansion/contraction animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_expansion)
        self.animation_steps = 8  # Reduced from 15 for faster animation
        self.current_animation_step = 0
        self.target_expanded = False
        
    def _setup_ui(self):
        """Setup the widget UI."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            #Qt.WindowType.Tool |  # Prevents taskbar icon
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
            self.drawing_manager.draw_hamburger_icon(painter)
        else:
            self.drawing_manager.draw_expanded_menu(painter)

    def _get_qt_cursor_position(self):
        """Get cursor position using the coordinate manager for DPI-aware positioning."""
        try:
            return get_cursor_position()
        except:
            # Fallback to pynput if coordinate manager fails
            pos = self.mouse.position
            return QPoint(int(pos[0]), int(pos[1]))
    
    def _get_screen_geometry(self):
        """Get the screen geometry that contains the current cursor position."""
        try:
            screen = get_screen_at_cursor()
            if screen:
                return screen.geometry()
            
            # Fallback to QApplication if coordinate manager fails
            app = QApplication.instance()
            if app:
                return app.primaryScreen().geometry()
            return None
            
        except Exception:
            return None
    
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
        
        # If in coordinated mode, skip normal positioning logic but track cursor
        if coordinated_mode:
            # Get DPI-aware cursor position from coordinate manager
            qt_cursor_pos = self._get_qt_cursor_position()
            cursor_x, cursor_y = qt_cursor_pos.x(), qt_cursor_pos.y()
            
            # Update cursor tracking for hover detection
            self.last_cursor_pos = (cursor_x, cursor_y)
            return
        
        # Get DPI-aware cursor position from coordinate manager
        qt_cursor_pos = self._get_qt_cursor_position()
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
        
        # Lock/unlock logic - simplified to prevent getting stuck
        if not self.is_locked:
            if distance_to_widget < self.lock_threshold:
                self.is_locked = True
                self.last_lock_time = time.time()
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
            # Also check if we've been locked too long (safety mechanism)
            current_time = time.time()
            should_unlock = (distance_to_widget > self.unlock_threshold or 
                           (current_time - self.last_lock_time) > self.max_lock_duration)
            
            if should_unlock:
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
        
        # Get DPI-aware cursor position from coordinate manager
        qt_cursor_pos = self._get_qt_cursor_position()
        
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
                    
                    # Update last widget position to prevent conflicts
                    self.last_widget_pos = (new_x, new_y)
                    self.last_move_time = time.time()
                    
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
                new_x = current_pos.x() + offset
                new_y = current_pos.y() + offset
                self.move(new_x, new_y)
                
                # Update last widget position to prevent conflicts
                self.last_widget_pos = (new_x, new_y)
                self.last_move_time = time.time()

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
                pos = self._get_qt_cursor_position()
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

    def set_item_size(self, size):
        """Set the size of menu items and dynamically adjust layout."""
        self.item_size = size
        
        # Dynamically calculate radius and expanded size based on item size
        # These multipliers are derived from design choices for good aesthetics
        self.circle_radius = int(self.item_size * 1.7)
        self.expanded_size = int(2 * self.circle_radius + self.item_size * 1.2)
        
        # If the menu is already expanded, we need to resize it
        if self.is_expanded:
            self.setFixedSize(self.expanded_size, self.expanded_size)
            self.update()

    def set_unlock_threshold(self, threshold: int):
        """Update the unlock threshold for the widget."""
        self.unlock_threshold = threshold
    
    def force_unlock(self):
        """Force unlock the widget if it gets stuck."""
        if self.is_locked:
            self.is_locked = False
            self.last_lock_time = 0
            # Force a position update
            if self.last_cursor_pos is not None:
                self.update_position(self.last_cursor_pos)