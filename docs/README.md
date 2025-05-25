# Dwellpy

[![GitHub release](https://img.shields.io/github/v/release/code0nwheels/dwellpy)](https://github.com/code0nwheels/dwellpy/releases)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

Dwellpy is a professional accessibility application designed for people with motor disabilities that allows users to perform mouse clicks by simply hovering (or "dwelling") their cursor over a target area for a short period of time. No physical button presses required!

This tool is particularly helpful for individuals who use head trackers or alternative mouse controls where physical clicking isn't possible, as well as for those with cerebral palsy, hand tremors, repetitive strain injuries, limited dexterity, or conditions like Parkinson's, arthritis, or muscular dystrophy.

## ✨ Features

- **Multiple Click Types**: Left click, right click, double click, and drag operations without physical clicking
- **Intelligent Scroll Widget**: Floating scroll interface that follows your cursor for hands-free scrolling
- **Adaptive Sensitivity**: Customize dwell detection radius and timing to accommodate different types of motor challenges
- **Temporary/Default Modes**: Easily switch between click types with temporary or permanent mode selection
- **Accessible Interface**: Small, always-on-top UI with high-contrast buttons that can be positioned anywhere on screen
- **Window Transparency**: Optional transparency when not in use to reduce visual clutter
- **Cross-platform Support**: Works on Windows, macOS, and Linux with consistent behavior
- **Persistent Settings**: Your preferences are saved between sessions, so you only need to configure once

## 🚀 Quick Start

### Installation

1. **Install Python 3.8+**: Download from [python.org](https://www.python.org/downloads/)

2. **Install Dwellpy**:
   ```bash
   pip install dwellpy
   ```

3. **Run the application**:
   ```bash
   dwellpy
   ```

### Alternative Installation (Development)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/code0nwheels/dwellpy.git
   cd dwellpy
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run from source**:
   ```bash
   python -m dwellpy.main
   ```

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux with X11
- **Memory**: 50MB RAM minimum
- **Dependencies**: PyQt6, pynput

### Platform-Specific Notes

- **Windows**: Generally works out of the box with pip installation
- **macOS**: May require Homebrew for Qt dependencies: `brew install qt@6`
- **Linux**: Currently supports X11 only (Wayland support under investigation)

## 🎯 Usage

### Main Interface

The Dwellpy interface consists of a compact toolbar with these buttons:

| Button | Function |
|--------|----------|
| **ON/OFF** | Activates/deactivates dwell clicking |
| **LEFT** | Left mouse click mode (default) |
| **DOUBLE** | Double-click mode |
| **DRAG** | Drag operation mode |
| **RIGHT** | Right-click mode |
| **SCROLL** | Quick toggle scroll widget on/off (useful to avoid conflicts with onscreen keyboards) |
| **SETUP** | Opens settings dialog |
| **MOVE** | Repositions the Dwellpy window |
| **EXIT** | Closes the application |

### Click Modes

- **Temporary Mode**: Select a different mode than your default - it becomes temporary (highlighted in red). After one action, returns to default mode.
- **Default Mode**: Double-select a mode to make it permanent (highlighted in blue). This mode persists until changed.

### Scroll Widget

The scroll widget is a floating interface that appears near your cursor when enabled:

- **Automatic Positioning**: Follows your cursor at a safe distance to avoid interference
- **Smart Locking**: Locks in place when your cursor approaches, preventing accidental movement
- **Hover-to-Scroll**: Hover over the up/down arrows to scroll in that direction
- **Visual Feedback**: Changes opacity and color to indicate hover state and active scrolling
- **Configurable**: Adjust speed, opacity, and positioning through settings

**How to Use**:
1. Enable with the **SCROLL** button (turns green when active)
2. Move your cursor near content you want to scroll
3. The scroll widget appears automatically
4. Hover over the up ↑ or down ↓ arrows to scroll
5. Widget follows your cursor as you navigate

**Quick Toggle**: The SCROLL button allows instant on/off control, which is particularly useful when:
- Using an onscreen keyboard (prevents widget interference)
- Switching between scrolling and precision tasks
- Temporarily disabling for specific applications

### Settings

Access via the **SETUP** button:

- **Move Limit (3-20px)**: How much the cursor can move while still "dwelling"
  - *Head tracker users*: 8-15px accommodates natural head movement
  - *Hand tremors/cerebral palsy*: 10-20px accommodates more movement
  - *Good cursor stability*: 3-8px provides precision

- **Dwell Time (0.1-2.0s)**: How long to hold position before clicking
  - *Fatigue issues*: 0.1-0.5s requires less sustained focus
  - *Avoid accidental clicks*: 0.8-2.0s prevents unintended actions
  - *Head tracker users*: 0.5-0.8s balances responsiveness and accuracy

- **Window Transparency**: Optional transparency when cursor is away
  - Enable/disable window transparency
  - Adjust transparency level (10-90%)

- **Scroll Widget Settings**:
  - **Enable Scroll Widget**: Toggle scroll functionality on/off
  - **Scroll Speed (1-10)**: Adjust how fast scrolling occurs
    - 1 = Slowest (200ms intervals)
    - 10 = Fastest (20ms intervals)

- **Start Active**: Automatically enable dwell clicking on launch

#### Hover-to-Adjust Settings

Settings sliders support accessibility-friendly adjustment:
- **Hover over +/- buttons** for 0.5 seconds to adjust values
- **Continue hovering** for repeated adjustments
- **Move cursor away** to stop adjustment

## 🔧 Advanced Configuration

### For Different Motor Challenges

| Condition | Recommended Settings |
|-----------|---------------------|
| **Head Tracker** | Move Limit: 8-15px, Dwell Time: 0.5-0.8s, Scroll Speed: 3-5 |
| **Cerebral Palsy** | Move Limit: 10-20px, adjust based on movement patterns |
| **Hand Tremors** | Move Limit: 12-20px, Dwell Time: 0.3-0.6s, Scroll Speed: 2-4 |
| **Fatigue/Weakness** | Dwell Time: 0.1-0.5s, Scroll Speed: 6-8 (faster response) |
| **Occasional Spasms** | Dwell Time: 1.0-2.0s, Scroll Speed: 1-3 (slower, more controlled) |
| **Limited Range** | Position window in accessible area using MOVE, enable scroll widget |

### Scroll Widget Use Cases

The scroll widget is particularly useful for:
- **Document Reading**: Scroll through long documents without precise cursor placement
- **Web Browsing**: Navigate web pages with natural cursor movement
- **Code Editing**: Scroll through source code while maintaining cursor context
- **Spreadsheets**: Navigate large datasets without losing your place
- **PDF Viewing**: Read documents with continuous scrolling

**Onscreen Keyboard Compatibility**: The quick SCROLL toggle allows you to instantly disable the scroll widget when using onscreen keyboards or other assistive input tools to prevent interface conflicts.

### Temporary Mode Use Cases

Perfect for precision tasks requiring different settings:
- **Small buttons**: Temporarily use lower Move Limit for precision
- **Spreadsheet cells**: Switch to precise mode for individual cell selection
- **Photo editing**: Use higher tolerance for navigation, precise for tools
- **Text cursor placement**: Precise mode for character-level positioning

## 🏗️ Technical Details

- **Cross-platform Mouse Control**: Uses pynput for consistent behavior
- **Counter-based Dwell Detection**: Efficient algorithm with low CPU usage
- **Adaptive Movement Threshold**: Separate X/Y direction detection
- **Smart Scroll Widget**: Auto-positioning with collision avoidance
- **Qt-based UI**: Modern, accessible interface with transparency support
- **JSON Settings**: Human-readable configuration persistence

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Clicks not triggering** | Increase Move Limit or decrease Dwell Time |
| **Too many accidental clicks** | Decrease Move Limit or increase Dwell Time |
| **Scroll widget interfering** | Disable with SCROLL button (especially useful with onscreen keyboards) |
| **Scroll widget not appearing** | Check that SCROLL button is enabled (green) |
| **Scrolling too fast/slow** | Adjust Scroll Speed in settings (1=slow, 10=fast) |
| **Difficulty with precision** | Use temporary mode for specific tasks |
| **High-DPI display issues** | Adjust settings based on screen resolution |
| **Linux Wayland issues** | Switch to X11 session (Wayland support coming) |

## 📦 Development

### Project Structure

```
dwellpy/
├── dwellpy/                # Main package
│   ├── core/              # Core algorithms
│   ├── ui/                # User interface
│   │   └── scroll_widget.py  # Floating scroll widget
│   ├── managers/          # Application managers
│   ├── config/            # Configuration
│   └── utils/             # Utilities
├── docs/                  # Documentation
└── requirements.txt       # Dependencies
```

### Building from Source

```bash
# Clone repository
git clone https://github.com/code0nwheels/dwellpy.git
cd dwellpy

# Install in development mode
pip install -e .

# Run from source
python -m dwellpy.main
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 💡 Support

- **Issues**: Report bugs on [GitHub Issues](https://github.com/code0nwheels/dwellpy/issues)
- **Discussions**: Join conversations on [GitHub Discussions](https://github.com/code0nwheels/dwellpy/discussions)
- **Documentation**: Visit the [Wiki](https://github.com/code0nwheels/dwellpy/wiki)

---

**Dwellpy was developed as an accessibility tool to enable independent computer use for people with motor disabilities. Our mission is to make technology more accessible to everyone, regardless of physical ability.**

*Made by a disabled person, for the disabled community.*
