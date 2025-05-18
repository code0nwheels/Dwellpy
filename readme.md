# Dwellpy

Dwellpy is an accessibility application designed for people with motor disabilities that allows users to perform mouse clicks by simply hovering (or "dwelling") their cursor over a target area for a short period of time. No physical button presses required! This tool is particularly helpful for individuals who use head trackers or alternative mouse controls where physical clicking isn't possible, as well as for those with cerebral palsy, hand tremors, repetitive strain injuries, limited dexterity, or conditions like Parkinson's, arthritis, or muscular dystrophy.

## Features

- **Multiple Click Types**: Left click, right click, double click, and drag operations without physical clicking
- **Adaptive Sensitivity**: Customize dwell detection radius and timing to accommodate different types of motor challenges
- **Temporary/Default Modes**: Easily switch between click types with temporary or permanent mode selection
- **Accessible Interface**: Small, always-on-top UI with high-contrast buttons that can be positioned anywhere on screen
- **Cross-platform Support**: Works on Windows, macOS, and Linux with consistent behavior
- **Persistent Settings**: Your preferences are saved between sessions, so you only need to configure once

## Installation

### Requirements

- Python 3.6 or higher
- Required Python packages:
  - pynput
  - tkinter (usually included with Python installation)

### Installing Dependencies

1. **Install Python**: Download and install from [python.org](https://www.python.org/downloads/)

2. **Install pynput**:
   ```bash
   pip install pynput
   ```

3. **Install tkinter** (if not included with your Python installation):
   - **Windows**: Tkinter usually comes with Python. If missing:
     ```bash
     pip install tk
     ```
   
   - **macOS**: Using Homebrew:
     ```bash
     brew install python-tk
     ```
   
   - **Ubuntu/Debian**:
     ```bash
     sudo apt-get update
     sudo apt-get install python3-tk
     ```
   
   - **Fedora**:
     ```bash
     sudo dnf install python3-tkinter
     ```
   
   - **Arch Linux**:
     ```bash
     sudo pacman -S tk
     ```

### Setup

1. Clone or download this repository
2. Run the application:
   ```bash
   python main.py
   ```

### Platform Notes

- **Linux Compatibility**: Currently only X11 is supported. Wayland does not easily allow injection of mouse and keyboard events system-wide, as these can only be implemented at the desktop environment level (currently under investigation).

## Usage

### Main Interface

The Dwellpy interface consists of a small toolbar with the following buttons:

- **ON/OFF**: Activates or deactivates the dwell clicking functionality
- **LEFT**: Performs a left mouse click when dwelling (default mode)
- **DOUBLE**: Performs a double-click when dwelling
- **DRAG**: Initiates a drag operation (requires two dwells - one to start and one to end)
- **RIGHT**: Performs a right-click when dwelling
- **SETUP**: Opens the settings dialog
- **MOVE**: Allows you to reposition the Dwellpy window without triggering clicks
- **EXIT**: Closes the application

### Click Modes

- **Temporary Mode**: When you select a different mode than your default, it becomes temporary (highlighted in red). After performing one click action, it returns to your default mode.
- **Default Mode**: Double-select a mode to make it your default (highlighted in blue). This mode persists until you change it.

### Dwell Detection

1. Move your cursor to where you want to click
2. Hold the cursor still for the configured dwell time
3. The application automatically performs the selected click action
4. For drag operations, dwell once to start the drag, move to your destination, then dwell again to release

### Settings

Access the settings dialog by clicking or dwelling on the SETUP button. Options include:

- **Move Limit**: The number of pixels the cursor can move while still being considered "dwelling" (3-20px)
  * For head tracker users: Medium-high values (8-15px) accommodate slight head movement
  * For people with hand tremors or cerebral palsy: Higher values (10-20px) accommodate more movement
  * For people with good cursor stability: Lower values (3-8px) provide more precision

- **Dwell Time**: How long the cursor must remain still to trigger a click (0.1-2.0 seconds)
  * For users with fatigue issues: Shorter times (0.1-0.5s) require less sustained focus
  * For users who need to avoid accidental clicks: Longer times (0.8-2.0s) prevent unintended actions
  * For head tracker users: Medium times (0.5-0.8s) provide a good balance between responsiveness and accuracy

- **Start active on launch**: Automatically activates Dwellpy when the application starts, making it ready to use immediately

## Accessibility Tips

### For Different Motor Challenges

- **Head Tracker Users**: Set a moderate Move Limit (8-15px) to accommodate natural head movement while maintaining reasonable precision. Consider using a medium Dwell Time (0.5-0.8s) for a balance of control and ease of use.
- **Cerebral Palsy**: Adjust Move Limit based on your specific movement patterns, and use temporary mode for precision tasks
- **Hand Tremors**: Set a higher Move Limit (12-20px) to accommodate natural hand movement
- **Fatigue or Muscle Weakness**: Use shorter Dwell Times (0.1-0.5s) to minimize the time needed to hold position
- **Occasional Spasms**: Consider a longer Dwell Time (1.0-2.0s) to avoid accidental clicks during movement
- **Limited Range of Motion**: Position the Dwellpy window near your common work area using the MOVE button

### Common Tasks Made Easier

- **Text Selection**: Use DRAG mode to select text without having to hold down a mouse button
- **File Management**: Use DOUBLE click mode for opening files and folders
- **Context Menus**: Use RIGHT click mode for accessing contextual options
- **Form Filling**: Switch between LEFT click and DRAG modes for navigating and completing forms

### Difficulty with Precision Tasks

Temporary mode is perfect for precision tasks that require different settings than your everyday use. Here are examples:

- **Small Buttons or Links**: If your default Move Limit is high (15px) for accommodating tremors, temporarily switch to LEFT mode with a lower setting (5-8px) for clicking small buttons, then it automatically returns to your higher-tolerance default.

- **Spreadsheet Cell Selection**: When working in Excel or Google Sheets, temporarily switch to LEFT mode with lower Move Limit to precisely select individual cells, then switch back to DRAG mode with higher tolerance for selecting ranges.

- **Photo Editing**: Use your higher tolerance setting for general navigation, but temporarily switch to a more precise setting when you need to select small tools or make pixel-level adjustments.

- **Text Cursor Placement**: When typing and you need to place the cursor between specific characters, temporarily use a more precise setting, then return to your comfortable default for general typing and navigation.

- **Dropdown Menus**: Temporarily switch to a more precise mode for selecting items from dropdown menus, especially when items are closely spaced.

- **Checkboxes and Radio Buttons**: When filling out forms with small checkboxes, temporarily use a more precise mode for accurate selection.

## Technical Details

- **Cross-platform Mouse Control**: Uses pynput library for consistent behavior across platforms
- **Counter-based Dwell Detection**: Efficient algorithm that reduces CPU usage
- **Adaptive Movement Threshold**: Detects movement in both X and Y directions for precise control, accommodating different types of hand movements
- **Position Tracking**: Background thread monitors cursor position at fixed intervals
- **Drag Support**: Two-phase drag operations (press and release) that don't require holding buttons
- **Linux Support**: Currently works with X11 window systems. Wayland support is under investigation as it requires desktop environment level implementation.

## Troubleshooting

- **Clicks not triggering**: Try increasing the Move Limit if you have hand tremors or cerebral palsy, or decreasing the Dwell Time if you have difficulty holding position
- **Too many accidental clicks**: Try decreasing the Move Limit or increasing the Dwell Time
- **Difficulty with precision tasks**: Try the temporary mode feature to quickly switch to a more precise setting for specific actions
- **High-DPI displays**: You may need to adjust settings differently depending on your screen resolution

---

Dwellpy was developed as an accessibility tool to enable independent computer use for people with motor disabilities. Our mission is to make technology more accessible to everyone, regardless of physical ability.

Made by a disabled person.