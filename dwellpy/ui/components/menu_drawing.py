"""Menu widget drawing and painting functionality."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont
import math

# Import constants
try:
    from ...config.constants import Colors
except ImportError:
    # Fallback constants for testing
    class Colors:
        DARK_BG = "#1e1e1e"
        BLUE_ACCENT = "#0078d7"
        TEXT_COLOR = "#ffffff"
        GREEN_ACCENT = "#2ecc71"
        RED_ACCENT = "#e74c3c"


class MenuDrawingManager:
    """Manages drawing and painting for the menu widget."""
    
    def __init__(self, menu_widget):
        self.menu_widget = menu_widget
    
    def draw_hamburger_icon(self, painter):
        """Draw the hamburger icon."""
        # Draw background circle
        background_color = QColor(40, 40, 40, 220) if self.menu_widget.is_locked else QColor(30, 30, 30, 200)
        painter.setBrush(QBrush(background_color))
        
        # Draw border to indicate lock state
        if self.menu_widget.is_locked:
            painter.setPen(QPen(QColor(0, 120, 215), 2))
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            
        # Draw circular background
        painter.drawEllipse(self.menu_widget.rect())
        
        # Draw hamburger lines
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        
        center_x = self.menu_widget.width() // 2
        center_y = self.menu_widget.height() // 2
        line_width = 12
        line_spacing = 4
        
        # Three horizontal lines
        for i in range(3):
            y = center_y - line_spacing + (i * line_spacing)
            painter.drawLine(
                center_x - line_width // 2, y,
                center_x + line_width // 2, y
            )
    
    def draw_expanded_menu(self, painter):
        """Draw the expanded menu with items in circular layout around hamburger icon."""
        # The hamburger icon stays in the center of the expanded widget
        hamburger_center_x = self.menu_widget.width() // 2
        hamburger_center_y = self.menu_widget.height() // 2
        hamburger_center = QPoint(hamburger_center_x, hamburger_center_y)
        
        # Draw hamburger icon at center
        hamburger_size = 20
        hamburger_rect = QRect(hamburger_center_x - hamburger_size//2, hamburger_center_y - hamburger_size//2, 
                              hamburger_size, hamburger_size)
        
        # Draw hamburger background
        background_color = QColor(40, 40, 40, 220) if self.menu_widget.is_locked else QColor(30, 30, 30, 200)
        painter.setBrush(QBrush(background_color))
        
        # Draw border to indicate lock state
        if self.menu_widget.is_locked:
            painter.setPen(QPen(QColor(0, 120, 215), 2))
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            
        painter.drawEllipse(hamburger_rect)
        
        # Draw hamburger lines
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
        for i, item in enumerate(self.menu_widget.menu_items):
            self.draw_circular_menu_item(painter, item, i, hamburger_center)
    
    def draw_circular_menu_item(self, painter, item, index, center_pos):
        """Draw a single menu item in circular layout around the hamburger center."""
        # Calculate position on circle around hamburger icon using animated radius
        angle = (index * 360 / len(self.menu_widget.menu_items)) - 90  # Start from top (-90 degrees)
        angle_rad = math.radians(angle)
        
        # Use animated radius instead of fixed radius
        item_x = center_pos.x() + int(self.menu_widget.current_radius * math.cos(angle_rad)) - self.menu_widget.item_size // 2
        item_y = center_pos.y() + int(self.menu_widget.current_radius * math.sin(angle_rad)) - self.menu_widget.item_size // 2
        
        item_rect = QRect(item_x, item_y, self.menu_widget.item_size, self.menu_widget.item_size)
        
        # Calculate opacity based on animation progress for fade-in effect
        animation_progress = self.menu_widget.current_radius / self.menu_widget.circle_radius if self.menu_widget.circle_radius > 0 else 0
        base_alpha = int(200 * animation_progress)
        
        # Determine if this item is hovered
        is_hovered = (self.menu_widget.current_hover == item['id'])
        
        # Determine the item's state color based on UI manager state
        item_color = self.get_item_state_color(item)
        
        # Draw item background circle with animated alpha
        if is_hovered:
            hover_color = QColor(70, 70, 70, min(220, base_alpha + 50))
            painter.setBrush(QBrush(hover_color))
            painter.setPen(QPen(QColor(item_color), 2))
        else:
            # Use different background color based on state
            if self.is_item_active_state(item):
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
        
        # Draw item text with animated alpha
        text_color = QColor(item_color) if is_hovered or self.is_item_active_state(item) else QColor(255, 255, 255)
        text_color.setAlpha(min(255, base_alpha + 55))  # Ensure text is visible
        painter.setPen(QPen(text_color))
        painter.setFont(QFont("Helvetica Neue", 9, QFont.Weight.Bold))
        painter.drawText(item_rect, Qt.AlignmentFlag.AlignCenter, item['label'])
    
    def get_item_state_color(self, item):
        """Get the color for a menu item based on current UI state."""
        if not self.menu_widget.ui_manager:
            return item['color']
        
        item_id = item['id']
        
        # Handle special buttons
        if item_id == 'OFF':
            return Colors.RED_ACCENT
        elif item_id == 'SETUP':
            return Colors.TEXT_COLOR
        
        # Handle click mode buttons
        if item_id in ['LEFT', 'DOUBLE', 'RIGHT', 'DRAG']:
            if not self.menu_widget.ui_manager.is_active:
                return "#999999"  # Disabled color when app is off
            
            # Check if this is the current mode
            if item_id == self.menu_widget.ui_manager.current_mode:
                # Current mode - red if temporary, blue if permanent
                if self.menu_widget.ui_manager.is_temporary_mode:
                    return Colors.RED_ACCENT  # Temporary mode
                else:
                    return Colors.BLUE_ACCENT  # Current permanent mode
            elif item_id == self.menu_widget.ui_manager.default_mode:
                # Default mode (but not current) - blue
                return Colors.BLUE_ACCENT
            else:
                # Other modes - default color
                return Colors.TEXT_COLOR
        
        return item['color']
    
    def is_item_active_state(self, item):
        """Check if a menu item should show an active state background."""
        if not self.menu_widget.ui_manager:
            return False
        
        item_id = item['id']
        
        # Handle click mode buttons
        if item_id in ['LEFT', 'DOUBLE', 'RIGHT', 'DRAG']:
            if not self.menu_widget.ui_manager.is_active:
                return False
            
            # Show active background for current mode or default mode
            return (item_id == self.menu_widget.ui_manager.current_mode or 
                   item_id == self.menu_widget.ui_manager.default_mode)
        
        return False 