"""
Centralized coordinate management system for DPI-aware cursor positioning.

This module provides a unified way to get cursor positions that work correctly
regardless of DPI scaling, multi-monitor setups, or platform differences.
"""

from PyQt6.QtCore import QPoint, QRect
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QCursor, QScreen
from typing import Optional, Tuple, Union
import sys


class CoordinateManager:
    """
    Centralized manager for DPI-aware cursor positioning and coordinate conversion.
    
    This class provides a single source of truth for cursor positions that
    automatically handles DPI scaling, multi-monitor setups, and platform differences.
    """
    
    def __init__(self):
        self._app = None
        self._last_cursor_pos = None
        self._last_screen = None
        
    def _ensure_app(self) -> Optional[QApplication]:
        """Ensure QApplication instance exists and return it."""
        if self._app is None:
            self._app = QApplication.instance()
        return self._app
    
    def get_cursor_position(self) -> QPoint:
        """
        Get the current cursor position in DPI-aware coordinates.
        
        Returns:
            QPoint: Current cursor position that accounts for DPI scaling
        """
        try:
            # Use Qt's native cursor position which is always DPI-aware
            return QCursor.pos()
        except Exception:
            # Fallback: return last known position or (0, 0)
            if self._last_cursor_pos is not None:
                return self._last_cursor_pos
            return QPoint(0, 0)
    
    def get_cursor_position_tuple(self) -> Tuple[int, int]:
        """
        Get the current cursor position as a tuple of integers.
        
        Returns:
            Tuple[int, int]: Current cursor position as (x, y) tuple
        """
        pos = self.get_cursor_position()
        return (pos.x(), pos.y())
    
    def get_screen_at_cursor(self) -> Optional['QScreen']:
        """
        Get the screen that contains the current cursor position.
        
        Returns:
            QScreen or None: The screen containing the cursor, or None if not found
        """
        app = self._ensure_app()
        if not app:
            return None
            
        cursor_pos = self.get_cursor_position()
        
        # Find which screen contains the cursor
        for screen in app.screens():
            geometry = screen.geometry()
            if geometry.contains(cursor_pos):
                return screen
        
        # If no screen contains cursor, return primary screen
        return app.primaryScreen()
    
    def get_screen_geometry_at_cursor(self) -> Optional[QRect]:
        """
        Get the geometry of the screen containing the current cursor.
        
        Returns:
            QRect or None: Screen geometry, or None if no screen found
        """
        screen = self.get_screen_at_cursor()
        if screen:
            return screen.geometry()
        return None
    
    def get_dpi_scale_at_cursor(self) -> float:
        """
        Get the DPI scaling factor for the screen containing the cursor.
        
        Returns:
            float: DPI scaling factor (1.0 = 100%, 1.5 = 150%, etc.)
        """
        screen = self.get_screen_at_cursor()
        if screen:
            return screen.devicePixelRatio()
        return 1.0
    
    def convert_to_screen_coordinates(self, global_pos: QPoint, target_screen: 'QScreen') -> QPoint:
        """
        Convert global coordinates to coordinates relative to a specific screen.
        
        Args:
            global_pos: Global position to convert
            target_screen: Target screen for conversion
            
        Returns:
            QPoint: Position relative to the target screen
        """
        screen_geometry = target_screen.geometry()
        return QPoint(
            global_pos.x() - screen_geometry.x(),
            global_pos.y() - screen_geometry.y()
        )
    
    def convert_from_screen_coordinates(self, screen_pos: QPoint, source_screen: 'QScreen') -> QPoint:
        """
        Convert screen-relative coordinates to global coordinates.
        
        Args:
            screen_pos: Position relative to the source screen
            source_screen: Source screen for conversion
            
        Returns:
            QPoint: Global position
        """
        screen_geometry = source_screen.geometry()
        return QPoint(
            screen_pos.x() + screen_geometry.x(),
            screen_pos.y() + screen_geometry.y()
        )
    
    def is_position_on_screen(self, pos: QPoint, screen: 'QScreen') -> bool:
        """
        Check if a position is within the bounds of a specific screen.
        
        Args:
            pos: Position to check
            screen: Screen to check against
            
        Returns:
            bool: True if position is on the screen, False otherwise
        """
        return screen.geometry().contains(pos)
    
    def get_available_space_around_cursor(self, widget_size: Tuple[int, int]) -> dict:
        """
        Calculate available space around the current cursor position.
        
        Args:
            widget_size: Size of the widget as (width, height) tuple
            
        Returns:
            dict: Available space information with keys:
                - 'left': pixels available to the left
                - 'right': pixels available to the right  
                - 'top': pixels available above
                - 'bottom': pixels available below
                - 'total_horizontal': total horizontal space
                - 'total_vertical': total vertical space
        """
        screen_geometry = self.get_screen_geometry_at_cursor()
        if not screen_geometry:
            return {
                'left': 0, 'right': 0, 'top': 0, 'bottom': 0,
                'total_horizontal': 0, 'total_vertical': 0
            }
        
        cursor_pos = self.get_cursor_position()
        widget_width, widget_height = widget_size
        
        # Calculate available space in each direction
        left_space = cursor_pos.x() - screen_geometry.left()
        right_space = screen_geometry.right() - cursor_pos.x()
        top_space = cursor_pos.y() - screen_geometry.top()
        bottom_space = screen_geometry.bottom() - cursor_pos.y()
        
        # Account for widget size
        left_space = max(0, left_space - widget_width)
        right_space = max(0, right_space - widget_width)
        top_space = max(0, top_space - widget_height)
        bottom_space = max(0, bottom_space - widget_height)
        
        return {
            'left': left_space,
            'right': right_space,
            'top': top_space,
            'bottom': bottom_space,
            'total_horizontal': left_space + right_space,
            'total_vertical': top_space + bottom_space
        }
    
    def calculate_optimal_widget_position(self, 
                                        cursor_pos: QPoint,
                                        widget_size: Tuple[int, int],
                                        preferred_offset: Tuple[int, int] = (0, 0),
                                        avoid_edges: bool = True) -> QPoint:
        """
        Calculate the optimal position for a widget relative to the cursor.
        
        Args:
            cursor_pos: Current cursor position
            widget_size: Size of the widget as (width, height) tuple
            preferred_offset: Preferred offset from cursor as (x, y) tuple
            avoid_edges: Whether to avoid placing widget at screen edges
            
        Returns:
            QPoint: Optimal widget position
        """
        screen_geometry = self.get_screen_geometry_at_cursor()
        if not screen_geometry:
            # Fallback: center widget on cursor
            return QPoint(
                cursor_pos.x() - widget_size[0] // 2,
                cursor_pos.y() - widget_size[1] // 2
            )
        
        # Calculate initial position with preferred offset
        initial_x = cursor_pos.x() + preferred_offset[0] - widget_size[0] // 2
        initial_y = cursor_pos.y() + preferred_offset[1] - widget_size[1] // 2
        
        # Ensure widget stays within screen bounds
        final_x = max(screen_geometry.left(), 
                     min(initial_x, 
                         screen_geometry.right() - widget_size[0]))
        final_y = max(screen_geometry.top(), 
                     min(initial_y, 
                         screen_geometry.bottom() - widget_size[1]))
        
        return QPoint(final_x, final_y)
    
    def update_last_position(self):
        """Update the last known cursor position for fallback purposes."""
        self._last_cursor_pos = self.get_cursor_position()
    
    def get_position_delta(self, current_pos: QPoint, last_pos: QPoint) -> Tuple[int, int]:
        """
        Calculate the delta between two positions.
        
        Args:
            current_pos: Current position
            last_pos: Previous position
            
        Returns:
            Tuple[int, int]: Delta as (dx, dy) tuple
        """
        return (current_pos.x() - last_pos.x(), current_pos.y() - last_pos.y())
    
    def calculate_distance(self, pos1: QPoint, pos2: QPoint) -> float:
        """
        Calculate Euclidean distance between two points.
        
        Args:
            pos1: First position
            pos2: Second position
            
        Returns:
            float: Distance between the points
        """
        dx = pos1.x() - pos2.x()
        dy = pos1.y() - pos2.y()
        return (dx * dx + dy * dy) ** 0.5


# Global instance for easy access
coordinate_manager = CoordinateManager()


def get_cursor_position() -> QPoint:
    """Convenience function to get cursor position."""
    return coordinate_manager.get_cursor_position()


def get_cursor_position_tuple() -> Tuple[int, int]:
    """Convenience function to get cursor position as tuple."""
    return coordinate_manager.get_cursor_position_tuple()


def get_screen_at_cursor():
    """Convenience function to get screen at cursor."""
    return coordinate_manager.get_screen_at_cursor()


def get_dpi_scale_at_cursor() -> float:
    """Convenience function to get DPI scale at cursor."""
    return coordinate_manager.get_dpi_scale_at_cursor()
