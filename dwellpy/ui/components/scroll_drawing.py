"""Scroll widget drawing and painting functionality."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen


class ScrollDrawingManager:
    """Manages drawing and painting for the scroll widget."""
    
    def __init__(self, scroll_widget):
        self.scroll_widget = scroll_widget
    
    def draw_scroll_widget(self, painter):
        """Draw the scroll widget with arrows."""
        # Draw background with rounded corners
        if self.scroll_widget.is_locked:
            # Slightly different color when locked
            background_color = QColor(40, 40, 40, 220)  # Darker when locked
        else:
            background_color = QColor(30, 30, 30, 200)  # Normal
            
        painter.setBrush(QBrush(background_color))
        
        # Draw border to indicate lock state
        if self.scroll_widget.is_locked:
            painter.setPen(QPen(QColor(0, 120, 215), 2))  # Blue border when locked
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            
        painter.drawRoundedRect(self.scroll_widget.rect(), 10, 10)
        
        # Draw up arrow
        self.draw_arrow(painter, 'up', self.scroll_widget.current_hover == 'up')
        
        # Draw down arrow
        self.draw_arrow(painter, 'down', self.scroll_widget.current_hover == 'down')
    
    def draw_arrow(self, painter, direction, is_hovered):
        """Draw an arrow button."""
        # Calculate button area
        button_height = self.scroll_widget.height() // 2
        if direction == 'up':
            button_rect = QRect(5, 5, self.scroll_widget.width() - 10, button_height - 10)
        else:
            button_rect = QRect(5, button_height + 5, self.scroll_widget.width() - 10, button_height - 10)
        
        # Draw button background
        if self.scroll_widget.is_scrolling and self.scroll_widget.scroll_direction == direction:
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
        
        # Draw arrow
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        
        # Calculate arrow points
        center_x = button_rect.center().x()
        center_y = button_rect.center().y()
        
        if direction == 'up':
            # Up arrow - point upward
            arrow_points = [
                QPoint(center_x, center_y - 8),  # Top point
                QPoint(center_x - 6, center_y + 2),  # Bottom left
                QPoint(center_x + 6, center_y + 2)   # Bottom right
            ]
        else:
            # Down arrow - point downward
            arrow_points = [
                QPoint(center_x, center_y + 8),  # Bottom point
                QPoint(center_x - 6, center_y - 2),  # Top left
                QPoint(center_x + 6, center_y - 2)   # Top right
            ]
        
        # Draw the arrow
        painter.drawPolygon(arrow_points) 