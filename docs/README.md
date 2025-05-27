# Dwellpy

[![GitHub release](https://img.shields.io/github/v/release/code0nwheels/dwellpy)](https://github.com/code0nwheels/dwellpy/releases)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

**An accessibility tool that lets you click by hovering** - designed for people with motor disabilities who use head trackers, eye trackers, or have limited hand mobility.

*Made by a disabled person, for the disabled community.*

---

## 🎯 What is Dwellpy?

Instead of physically clicking, **just hover your cursor over any area for a short time** and Dwellpy will click for you automatically. This "dwell clicking" technique is essential for people who:

- Use head tracking or eye tracking devices
- Have cerebral palsy, hand tremors, or limited dexterity  
- Experience fatigue, weakness, or repetitive strain injuries
- Have conditions like Parkinson's, arthritis, or muscular dystrophy
- Use alternative mouse controls where physical clicking isn't possible

## ✨ Key Features

### 🖱️ **Smart Clicking**
- **Multiple Click Types**: Left, right, double-click, and drag operations
- **Intelligent Modes**: Temporary mode switching with visual feedback  
- **Adaptive Sensitivity**: Customizable hover time and movement tolerance

### 📜 **Hands-Free Scrolling**
- **Floating Scroll Widget**: Follows your cursor automatically
- **Hover to Scroll**: No clicking required - just hover over arrows
- **Smart Positioning**: Stays out of your way, locks when you need precision

### ♿ **Accessibility First**
- **Motor Disability Support**: Designed specifically for movement challenges
- **Customizable Settings**: Adapt to your specific needs and abilities
- **Persistent Configuration**: Set it once, works every time
- **Cross-Platform**: Works consistently on Windows, macOS, and Linux

## 🚀 Quick Start

Get up and running in 2 minutes:

### 1. Install Dwellpy
```bash
pip install dwellpy
```

### 2. Launch the App
```bash
dwellpy
```

### 3. Start Using
- Click the green **ON/OFF** button to activate
- **Windows users**: For best results, run as Administrator (recommended)
- **macOS users**: Grant Accessibility permissions when prompted (required for mouse control)
- Hover your cursor anywhere for 1 second - it will click automatically!
- Use the **SETUP** button to adjust sensitivity to your needs

That's it! 🎉

## 📖 How to Use

### Main Interface

Dwellpy shows a small toolbar with these buttons:

| Button | Function | Visual Cue |
|--------|----------|------------|
| **ON/OFF** | Activate/deactivate dwell clicking | 🟢 Green = On, 🔴 Red = Off |
| **LEFT** | Left click mode (default) | 🔵 Blue = Default mode |
| **DOUBLE** | Double-click mode | 🔴 Red = Temporary mode |
| **DRAG** | Drag operation mode | Requires two hovers: down + up |
| **RIGHT** | Right-click mode | For context menus |
| **SCROLL** | Toggle scroll widget | 🟢 Green = Active |
| **SETUP** | Open settings | Customize to your needs |
| **MOVE** | Reposition toolbar | Drag to move |
| **EXIT** | Close application | |

### Click Mode System

**🔵 Default Mode (Blue)**: Your primary click type - returns here after each action  
**🔴 Temporary Mode (Red)**: One-time use, then returns to default  

- **Single selection**: Makes a mode temporary (red)
- **Double selection**: Makes a mode permanent default (blue)

### Scroll Widget

The scroll widget automatically appears near your cursor when active:

- **Follows your cursor** at a safe distance
- **Locks in place** when you get close for precision
- **Hover over arrows** to scroll up ⬆️ or down ⬇️  
- **Quick toggle** with SCROLL button (great for avoiding conflicts with on-screen keyboards)

## ⚙️ Settings & Configuration

Access via **SETUP** button - all settings apply immediately:

### Core Settings

**Move Limit (3-20px)**: How much your cursor can move while "dwelling"
- Head tracker users: 8-15px (natural head movement)
- Hand tremors/cerebral palsy: 10-20px (accommodates movement)
- Good stability: 3-8px (precise control)

**Dwell Time (0.1-2.0s)**: How long to hover before clicking
- Fatigue/concentration issues: 0.1-0.5s (less sustained focus)
- Prevent accidents: 0.8-2.0s (deliberate clicking)
- Head tracker users: 0.5-0.8s (balanced)

### Advanced Settings

**Window Transparency**: Make toolbar see-through when not in use  
**Scroll Widget**: Adjust speed, positioning, and opacity  
**Auto-Start**: Launch active by default

### Accessibility-Friendly Controls

Settings can be adjusted by **hovering over +/- buttons** - no clicking required!

## 💻 Installation Options

### Option 1: Simple Install (Recommended)
```bash
pip install dwellpy
dwellpy
```

### Option 2: From Source (Developers)
```bash
git clone https://github.com/code0nwheels/dwellpy.git
cd dwellpy
pip install -r requirements.txt
python -m dwellpy.main
```

### 🚀 Coming Soon: Pre-built Binaries
We're working on downloadable executables for even easier installation - no Python required! These will be available for Windows, macOS, and Linux.

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux with X11
- **Memory**: 50MB RAM minimum
- **Dependencies**: PyQt6, pynput (installed automatically)

### Platform Notes

- **Windows**: 
  - Works out of the box
  - **Recommended**: Run as Administrator for best mouse control reliability
  - Right-click Dwellpy → "Run as Administrator" or run Command Prompt as Administrator
- **macOS**: 
  - May require `brew install qt@6` for Qt dependencies
  - **Important**: macOS will prompt you to grant Accessibility permissions to Dwellpy - this is required for mouse control to work
  - Go to System Preferences → Security & Privacy → Privacy → Accessibility and enable Dwellpy
- **Linux**: X11 only (Wayland support coming soon)

## 🔧 Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| **Clicks not working** | Increase Move Limit or decrease Dwell Time in settings |
| **Too many accidental clicks** | Decrease Move Limit or increase Dwell Time |
| **Windows: Inconsistent clicking** | Run as Administrator - right-click Dwellpy → "Run as Administrator" |
| **macOS: App not clicking** | Grant Accessibility permissions: System Preferences → Security & Privacy → Privacy → Accessibility → Enable Dwellpy |
| **Scroll widget interfering** | Use SCROLL button to toggle off (especially with on-screen keyboards) |
| **Scroll widget not appearing** | Check SCROLL button is green (active) |
| **Precision issues** | Use temporary mode for specific tasks |

### For Different Conditions

| Condition | Recommended Settings |
|-----------|---------------------|
| **Head Tracker** | Move: 8-15px, Time: 0.5-0.8s, Scroll Speed: 3-5 |
| **Cerebral Palsy** | Move: 10-20px, adjust based on movement patterns |
| **Hand Tremors** | Move: 12-20px, Time: 0.3-0.6s, Scroll Speed: 2-4 |
| **Fatigue/Weakness** | Time: 0.1-0.5s, Scroll Speed: 6-8 (faster response) |
| **Spasms** | Time: 1.0-2.0s, Scroll Speed: 1-3 (controlled) |

## 🏗️ Technical Details

- **Cross-platform mouse control** via pynput
- **Efficient dwell detection** with low CPU usage
- **Qt-based interface** with accessibility support
- **Smart scroll positioning** with collision avoidance
- **JSON settings** for easy configuration backup

## 🤝 Contributing & Support

### Get Help
- **Issues**: Report bugs on [GitHub Issues](https://github.com/code0nwheels/dwellpy/issues)
- **Discussions**: Join conversations on [GitHub Discussions](https://github.com/code0nwheels/dwellpy/discussions)
- **Documentation**: Visit the [Wiki](https://github.com/code0nwheels/dwellpy/wiki)

### Contributing
Contributions are welcome! Please feel free to submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

### Development
```bash
git clone https://github.com/code0nwheels/dwellpy.git
cd dwellpy
pip install -e .
python -m dwellpy.main
```

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 💡 Our Mission

**Dwellpy was created to break down barriers and enable independent computer use for people with motor disabilities.** 

Technology should be accessible to everyone, regardless of physical ability. By providing a free, open-source solution for dwell clicking, we aim to:

- **Reduce the cost barrier** to assistive technology
- **Provide cross-platform accessibility** that works everywhere
- **Enable independence** in digital spaces
- **Support the disability community** with tools made by someone who understands

---

**Made with ❤️ by a disabled person, for the disabled community.**

*Have feedback or need help? We'd love to hear from you on [GitHub Discussions](https://github.com/code0nwheels/dwellpy/discussions).*