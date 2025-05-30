"""Constants and theme configuration for Dwellpy."""

# Application Constants
APP_NAME = "Dwellpy"
WINDOW_HEIGHT = 60
WINDOW_FIXED_HEIGHT = True

# Timing Constants (in milliseconds)
POSITION_UPDATE_INTERVAL = 100  # Mouse position polling interval
HOVER_DELAY = 500              # Delay before hover actions activate
HOVER_REPEAT_INTERVAL = 500    # Repeat interval for hover actions
TRANSPARENCY_DELAY = 100       # Delay before applying transparency

# Dwell Detection Constants
MIN_MOVE_LIMIT = 3             # Minimum movement threshold (pixels)
MAX_MOVE_LIMIT = 20            # Maximum movement threshold (pixels)
MIN_DWELL_TIME = 0.1           # Minimum dwell time (seconds)
MAX_DWELL_TIME = 2.0           # Maximum dwell time (seconds)
DEFAULT_MOVE_LIMIT = 5         # Default movement threshold
DEFAULT_DWELL_TIME = 1.0       # Default dwell time

# Click Manager Constants
MIN_CLICK_INTERVAL = 0.5       # Minimum time between clicks (seconds)
MIN_MOVE_DISTANCE = 10         # Minimum distance before allowing another click

# Transparency Constants
MIN_TRANSPARENCY = 10          # Minimum transparency percentage
MAX_TRANSPARENCY = 90          # Maximum transparency percentage
DEFAULT_TRANSPARENCY = 70      # Default transparency level
TRANSPARENCY_STEP = 5          # Step size for transparency adjustment

# UI Constants
BUTTON_SIZE = (55, 55)         # Button dimensions (width, height)
LAYOUT_MARGIN = 2              # Layout margins
LAYOUT_SPACING = 2             # Spacing between elements
BORDER_RADIUS = 5              # Button border radius
SLIDER_HEIGHT = 4              # Slider track height
SLIDER_HANDLE_SIZE = 16        # Slider handle dimensions

# Scroll Widget Constants
SCROLL_WIDGET_SIZE = 40
SCROLL_WIDGET_OFFSET = 120  # Increased for safer cursor distance
SCROLL_WIDGET_ANGLE = 45  # Top-right position
SCROLL_INTERVAL = 100  # ms between scrolls
SCROLL_AMOUNT = 3  # lines per scroll
SCROLL_OPACITY_BASE = 70  # Base opacity percentage
SCROLL_OPACITY_HOVER = 90

# UI Contraction Constants
CONTRACT_DELAY = 1000          # Delay before contracting UI (milliseconds)
EXPAND_DELAY = 100             # Delay before expanding UI (milliseconds)
CONTRACT_BUTTON_SIZE = (40, 40) # Size of the contracted button
CONTRACT_BUTTON_TEXT = "≡"     # Text for the contracted button
EXPANSION_DIRECTIONS = ['auto', 'horizontal', 'vertical']  # Available expansion directions
DEFAULT_EXPANSION_DIRECTION = 'auto'  # Default expansion direction
SCREEN_EDGE_MARGIN = 50        # Margin from screen edge for expansion decisions

# Color Scheme - Dark Theme
class Colors:
    # Primary colors
    DARK_BG = "#1e1e1e"          # Main dark background
    DARK_BUTTON_BG = "#2d2d2d"   # Button background
    TEXT_COLOR = "#ffffff"       # Primary text color
    
    # Accent colors
    BLUE_ACCENT = "#0078d7"      # Primary blue accent
    GREEN_ACCENT = "#2ecc71"     # Success/active green
    RED_ACCENT = "#e74c3c"       # Warning/error red
    
    # UI element colors
    BORDER_COLOR = "#3c3c3c"     # Subtle borders
    SLIDER_TRACK = "#444444"     # Slider track color
    DISABLED_TEXT = "#999999"    # Disabled text color
    
    # Hover states
    BLUE_HOVER = "#0069c0"       # Blue hover state
    GREEN_HOVER = "#27ae60"      # Green hover state
    RED_HOVER = "#d63031"        # Red hover state
    GRAY_HOVER = "#3d3d3d"       # Gray hover state
    LIGHT_HOVER = "#5d5d5d"      # Light gray hover

# Button Styles
BUTTON_STYLES = {
    'base': {
        'background-color': Colors.DARK_BUTTON_BG,
        'color': Colors.TEXT_COLOR,
        'border': f'1px solid {Colors.BORDER_COLOR}',
        'border-radius': f'{BORDER_RADIUS}px',
        'font-family': "'Helvetica Neue', Helvetica, Arial, sans-serif",
        'font-size': '9pt',
        'font-weight': 'bold'
    },
    'blue': {
        'background-color': Colors.BLUE_ACCENT,
        'border': f'1px solid {Colors.BLUE_ACCENT}',
        'hover-background': Colors.BLUE_HOVER,
        'hover-border': Colors.BLUE_HOVER
    },
    'green': {
        'background-color': Colors.GREEN_ACCENT,
        'border': f'1px solid {Colors.GREEN_ACCENT}',
        'hover-background': Colors.GREEN_HOVER,
        'hover-border': Colors.GREEN_HOVER
    },
    'red': {
        'background-color': Colors.RED_ACCENT,
        'border': f'1px solid {Colors.RED_ACCENT}',
        'hover-background': Colors.RED_HOVER,
        'hover-border': Colors.RED_HOVER
    },
    'gray': {
        'hover-background': Colors.GRAY_HOVER,
        'hover-border': Colors.LIGHT_HOVER
    },
    'disabled': {
        'color': Colors.DISABLED_TEXT
    }
}

# Slider Styles
SLIDER_STYLE = f"""
QSlider::groove:horizontal {{
    background: {Colors.SLIDER_TRACK};
    height: {SLIDER_HEIGHT}px;
    border-radius: {SLIDER_HEIGHT//2}px;
}}
QSlider::handle:horizontal {{
    background: {Colors.BLUE_ACCENT};
    width: {SLIDER_HANDLE_SIZE}px;
    height: {SLIDER_HANDLE_SIZE}px;
    margin: -{(SLIDER_HANDLE_SIZE-SLIDER_HEIGHT)//2}px 0;
    border-radius: {SLIDER_HANDLE_SIZE//2}px;
}}
QSlider::sub-page:horizontal {{
    background: {Colors.BLUE_ACCENT};
    height: {SLIDER_HEIGHT}px;
    border-radius: {SLIDER_HEIGHT//2}px;
}}
"""

# Font Configuration
class Fonts:
    PRIMARY_FAMILY = "'Helvetica Neue', Helvetica, Arial, sans-serif"
    TITLE_SIZE = 16
    REGULAR_SIZE = 11
    BUTTON_SIZE = 9
    VERSION_SIZE = 9
    
# File Configuration
SETTINGS_FILENAME = "dwell_settings.json"

# Default Settings
DEFAULT_SETTINGS = {
    'window_position': (100, 100),
    'move_limit': DEFAULT_MOVE_LIMIT,
    'dwell_time': DEFAULT_DWELL_TIME,
    'default_active': False,
    'transparency_enabled': False,
    'transparency_level': DEFAULT_TRANSPARENCY,
    'visible_clicks_enabled': True,
    'scroll_enabled': True,
    'scroll_offset': SCROLL_WIDGET_OFFSET,
    'scroll_angle': SCROLL_WIDGET_ANGLE,
    'scroll_speed': SCROLL_INTERVAL,
    'scroll_amount': SCROLL_AMOUNT,
    'scroll_opacity_base': SCROLL_OPACITY_BASE,
    'scroll_opacity_hover': SCROLL_OPACITY_HOVER,
    'contract_ui_enabled': False,
    'expansion_direction': DEFAULT_EXPANSION_DIRECTION,
    'click_color_left': '#00e676',
    'click_color_right': '#ff9800',
    'click_color_double': '#e91e63',
    'click_color_drag_down': '#9c27b0',
    'click_color_drag_up': '#673ab7',
    'click_color_middle': '#00bcd4'
}

# Available Click Modes
CLICK_MODES = ['LEFT', 'DOUBLE', 'DRAG', 'RIGHT']

# Button IDs
BUTTON_IDS = {
    'ON_OFF': 'ON_OFF',
    'LEFT': 'LEFT',
    'DOUBLE': 'DOUBLE', 
    'DRAG': 'DRAG',
    'RIGHT': 'RIGHT',
    'SETUP': 'SETUP',
    'MOVE': 'MOVE',
    'EXIT': 'EXIT'
}