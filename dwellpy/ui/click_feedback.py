"""Click feedback widget for visual click indication."""

import sys
import time
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QCursor

try:
    from ..config.constants import Colors
except ImportError:
    # Fallback if constants not available
    class Colors:
        BLUE_ACCENT = "#0078d7"
        GREEN_ACCENT = "#00d7aa"
        RED_ACCENT = "#d70000"
        TEXT_COLOR = "#ffffff"

# Windows DPI awareness for better multi-monitor support
if sys.platform == "win32":
    try:
        import ctypes
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

class ClickFeedbackWidget(QWidget):
    """
    A floating widget that provides visual feedback when clicks are performed.
    Shows a brief expanding circle animation at the click location.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Widget configuration
        self.widget_size = 60  # Size of the widget
        self.animation_duration = 400  # Animation duration in milliseconds
        self.fade_start_delay = 200  # When to start fading out (ms)
        
        # Widget setup
        self.setFixedSize(self.widget_size, self.widget_size)
        
        # Platform-specific window flags for better macOS compatibility
        if sys.platform == "darwin":  # macOS
            # macOS: Use minimal flags that actually work (based on testing)
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint
            )
            # macOS: Don't use WA_ShowWithoutActivating as it might cause issues
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        else:
            # Windows/Linux flags (original behavior)
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | 
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool |
                Qt.WindowType.WindowTransparentForInput
            )
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Animation properties
        self._radius = 0
        self._opacity = 1.0
        
        # Animation objects
        self.radius_animation = QPropertyAnimation(self, b"radius")
        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        
        # Setup animations
        self.setup_animations()
        
        # Hide initially
        self.hide()
        
        # Settings manager - will be set by the feedback manager
        self.settings_manager = None
        
        # Default click type colors (fallback if settings not available)
        self.default_click_colors = {
            'left': QColor("#00e676"),       # Bright green - clearly intentional
            'right': QColor("#ff9800"),      # Orange - distinct from other actions  
            'double': QColor("#e91e63"),     # Pink/magenta - clearly special action
            'drag_down': QColor("#9c27b0"),  # Purple - start of drag operation
            'drag_up': QColor("#673ab7"),    # Darker purple - end of drag operation
            'middle': QColor("#00bcd4")      # Cyan - distinct middle click
        }
        self.current_color = QColor(Colors.BLUE_ACCENT)
        
    def set_settings_manager(self, settings_manager):
        """Set the settings manager for accessing color settings."""
        self.settings_manager = settings_manager
        
    def get_click_color(self, click_type):
        """Get the color for a specific click type from settings or defaults."""
        if self.settings_manager:
            # Get color from settings
            color_hex = self.settings_manager.get_setting(f'click_color_{click_type}', None)
            if color_hex:
                return QColor(color_hex)
        
        # Fallback to default colors
        if click_type in self.default_click_colors:
            return self.default_click_colors[click_type]
        else:
            return self.default_click_colors['left']
        
    def setup_animations(self):
        """Setup the radius and opacity animations."""
        # Radius animation (expanding circle)
        self.radius_animation.setDuration(self.animation_duration)
        self.radius_animation.setStartValue(5)
        self.radius_animation.setEndValue(self.widget_size // 2 - 5)
        self.radius_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Opacity animation (fade out)
        self.opacity_animation.setDuration(self.animation_duration - self.fade_start_delay)
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Connect animation finished to hide widget
        self.radius_animation.finished.connect(self.hide)
        
    @pyqtProperty(float)
    def radius(self):
        """Get the current animation radius."""
        return self._radius
    
    @radius.setter
    def radius(self, value):
        """Set the current animation radius and trigger repaint."""
        self._radius = value
        self.update()
        
    @pyqtProperty(float)
    def opacity(self):
        """Get the current animation opacity."""
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        """Set the current animation opacity and trigger repaint."""
        self._opacity = value
        self.update()
        
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
            print(f"ClickFeedback coordinate conversion error: {e}")
            # Fallback to direct conversion
            return QPoint(int(pynput_pos[0]), int(pynput_pos[1]))

    def show_click_feedback(self, position, click_type='left'):
        """
        Show click feedback at the specified position.
        
        Args:
            position: Tuple (x, y) representing the click position in screen coordinates
            click_type: String indicating the type of click ('left', 'right', 'double', 'drag_down', 'drag_up', 'middle')
        """
        # Set color based on click type using settings or defaults
        self.current_color = self.get_click_color(click_type)
        
        # Convert pynput coordinates to Qt coordinates for multi-monitor consistency
        qt_position = self._convert_pynput_to_qt_coords(position)
        
        # Position the widget centered on the click point
        widget_x = qt_position.x() - self.widget_size // 2
        widget_y = qt_position.y() - self.widget_size // 2
        
        # Position widget using the corrected coordinates
        self.move(widget_x, widget_y)
        
        # Reset animation properties
        self._radius = 5
        self._opacity = 1.0
        
        # Show the widget
        self.show()
        self.raise_()
        
        # Start animations
        self.radius_animation.stop()
        self.opacity_animation.stop()
        
        self.radius_animation.start()
        
        # Start opacity animation after delay
        QTimer.singleShot(self.fade_start_delay, lambda: self.opacity_animation.start())
        
    def paintEvent(self, event):
        """Paint the click feedback circle."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate center point
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # Set up color with current opacity
        color = QColor(self.current_color)
        color.setAlphaF(self._opacity * 0.8)  # Slightly transparent even at full opacity
        
        # Draw filled circle
        brush = QBrush(color)
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Draw main circle
        painter.drawEllipse(
            int(center_x - self._radius),
            int(center_y - self._radius),
            int(self._radius * 2),
            int(self._radius * 2)
        )
        
        # Draw border circle with more opaque color
        border_color = QColor(self.current_color)
        border_color.setAlphaF(self._opacity)
        pen = QPen(border_color, 2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        painter.drawEllipse(
            int(center_x - self._radius),
            int(center_y - self._radius),
            int(self._radius * 2),
            int(self._radius * 2)
        )

    def test_feedback_display(self):
        """Test method to show feedback at screen center for debugging."""
        if sys.platform == "darwin":
            print("macOS: Testing feedback display at screen center")
            
            # Get primary screen center
            screen = QApplication.primaryScreen()
            if screen:
                rect = screen.geometry()
                center_x = rect.width() // 2
                center_y = rect.height() // 2
                print(f"macOS: Screen center: {center_x}, {center_y}")
                self.show_click_feedback((center_x, center_y), 'left')
            else:
                print("macOS: Could not get primary screen")
                
    def cleanup(self):
        """Clean up resources."""
        try:
            self.hide()
            self.deleteLater()
        except:
            pass

class ClickFeedbackManager:
    """
    Manager class for handling click feedback across the application.
    Provides a simple interface for showing click feedback.
    """
    
    def __init__(self):
        self.feedback_widget = None
        self.settings_manager = None  # Will be set by main application
        self.initialize_widget()
        
    def set_settings_manager(self, settings_manager):
        """Set the settings manager for checking if visible clicks are enabled."""
        self.settings_manager = settings_manager
        
        # Also set it on the feedback widget for color access
        if self.feedback_widget:
            self.feedback_widget.set_settings_manager(settings_manager)
        
    def initialize_widget(self):
        """Initialize the feedback widget."""
        try:
            self.feedback_widget = ClickFeedbackWidget()
            
            # Set settings manager if we have one
            if self.settings_manager:
                self.feedback_widget.set_settings_manager(self.settings_manager)
                
        except Exception as e:
            # If widget creation fails, feedback will be disabled
            self.feedback_widget = None
            
    def show_feedback(self, position, click_type='left'):
        """
        Show click feedback at the specified position.
        
        Args:
            position: Tuple (x, y) representing the click position in screen coordinates
            click_type: String indicating the type of click
        """
        # Check if visible clicks are enabled
        if self.settings_manager:
            if not self.settings_manager.get_setting('visible_clicks_enabled', True):
                return  # Don't show feedback if disabled
        
        if self.feedback_widget is not None:
            try:
                self.feedback_widget.show_click_feedback(position, click_type)
            except Exception as e:
                # If showing feedback fails, silently ignore to avoid disrupting the app
                pass
                
    def test_feedback(self):
        """Test feedback display for debugging."""
        if self.feedback_widget is not None:
            try:
                self.feedback_widget.test_feedback_display()
            except Exception as e:
                if sys.platform == "darwin":
                    print(f"macOS: Test feedback failed: {e}")
                
    def cleanup(self):
        """Clean up resources."""
        if self.feedback_widget:
            try:
                self.feedback_widget.cleanup()
            except:
                pass
            self.feedback_widget = None 