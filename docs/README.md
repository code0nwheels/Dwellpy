# Dwellpy

[![GitHub release](https://img.shields.io/github/v/release/code0nwheels/dwellpy)](https://github.com/code0nwheels/dwellpy/releases)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Click by hovering instead of pressing mouse buttons. Dwellpy automatically performs clicks when you position your cursor over a target and wait briefly.

Built for users with motor disabilities who use head trackers, eye-tracking systems, or have difficulty with traditional mouse clicking due to conditions like cerebral palsy, hand tremors, or muscular dystrophy.

**Made by a disabled person for the disabled community.**

## Quick Start

### For End Users

**Option 1: Installers and Executables (Easiest)**

Download the installer or executable for your platform:

- **Windows**: Download the installer from [latest releases](https://github.com/code0nwheels/dwellpy/releases/latest) - look for `dwellpy-installer-*-windows-x64.exe`
- **macOS**: Download from [latest releases](https://github.com/code0nwheels/dwellpy/releases/latest) - look for `dwellpy-*-macos.dmg` or `dwellpy-*-macos-x64`
- **Linux**: For Debian-based systems (Ubuntu, Mint, etc.), download the `.deb` package from [latest releases](https://github.com/code0nwheels/dwellpy/releases/latest) (e.g., `dwellpy-*-linux-debian-x64.deb`). For other distributions, or for a scripted setup, see the [Linux Setup Guide](https://github.com/code0nwheels/dwellpy/wiki/Linux-Setup).

The Windows installer provides a professional installation experience with Start Menu integration and automatic shortcuts. For macOS, the DMG offers a standard installation. For Linux, the .deb package integrates with your system's package manager. See [setup guides](https://github.com/code0nwheels/dwellpy/wiki) for detailed platform-specific instructions.

**Option 2: Package Managers**

**Linux (Automated Install):**
```bash
curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/utils/linux-install.sh | bash
```

*To uninstall:*
```bash
curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/utils/linux-uninstall.sh | bash
```

**All Platforms (pip):**
```bash
pip install dwellpy
dwellpy
```

**Need help?** Check the [setup guides](https://github.com/code0nwheels/dwellpy/wiki) for your operating system.

### For Developers

```bash
git clone https://github.com/code0nwheels/dwellpy.git
cd dwellpy
pip install -r requirements.txt
python -m dwellpy.main
```

## What it does

- **Multiple click types**: Left, right, double-click, and drag operations
- **Floating widgets**: Menu and scroll widgets that appear when you dwell (pause cursor)
- **Visual feedback**: Customizable click animations with distinctive colors for each action type
- **Organized settings**: Tabbed interface with logical grouping (Dwell, Visual, Scroll, General)
- **Dwell-friendly controls**: Large buttons with hover functionality for easy adjustment
- **Auto-collapse UI**: Minimize screen clutter with intelligent toolbar behavior
- **Configurable**: Adjust sensitivity for different motor abilities and use cases
- **Cross-platform**: Windows, macOS, and Linux support

## Documentation

Detailed guides are available in the [project wiki](https://github.com/code0nwheels/dwellpy/wiki):

- [Windows Setup Guide](https://github.com/code0nwheels/dwellpy/wiki/Windows-Setup)
- [macOS Setup Guide](https://github.com/code0nwheels/dwellpy/wiki/macOS-Setup)  
- [Linux Setup Guide](https://github.com/code0nwheels/dwellpy/wiki/Linux-Setup)
- [Configuration Guide](https://github.com/code0nwheels/dwellpy/wiki/Configuration)
- [Troubleshooting](https://github.com/code0nwheels/dwellpy/wiki/Troubleshooting)

For developers interested in the codebase architecture, see [Architecture Documentation](architecture.md).

For details on the recent modularization work, see [Modularization Summary](modularization_summary.md).

## Contributing

This project was created by and for the disability community. We welcome:

- **Bug reports**: Use [GitHub Issues](https://github.com/code0nwheels/dwellpy/issues)
- **Feature requests**: Especially accessibility improvements
- **Documentation**: Help improve setup guides
- **Code contributions**: See [CONTRIBUTING.md](CONTRIBUTING.md)

### Development Setup

1. Fork the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run tests: `python -m pytest` (when available)
6. Make your changes and submit a pull request

### Project Structure

```
dwellpy/
├── dwellpy/              # Main application package
│   ├── bootstrap/        # Application startup and initialization
│   ├── core/            # Core functionality
│   │   ├── click_manager.py      # Click execution logic
│   │   ├── dwell_algorithm.py    # Dwell detection algorithms
│   │   ├── input_manager.py      # Input handling and position tracking
│   │   └── detection/           # Dwell detection components
│   ├── ui/              # User interface components
│   │   ├── ui_manager.py        # Main UI orchestration
│   │   ├── components/          # Modular UI components
│   │   │   ├── cursor_movement_detector.py  # Cursor movement detection
│   │   │   ├── ui_contraction.py           # UI contraction/expansion
│   │   │   ├── menu_drawing.py             # Menu widget drawing logic
│   │   │   └── scroll_drawing.py           # Scroll widget drawing logic
│   │   ├── menu_widget.py       # Menu widget implementation
│   │   ├── scroll_widget.py     # Scroll widget implementation
│   │   └── dialogs/             # Settings and configuration dialogs
│   ├── managers/        # Application state and lifecycle management
│   │   ├── button_manager.py    # Button state and command management
│   │   ├── settings_manager.py  # Settings persistence and management
│   │   ├── window_manager.py    # Window positioning and management
│   │   ├── exit_manager.py      # Application exit handling
│   │   └── lifecycle/           # Application lifecycle components
│   │       └── component_initializer.py    # Component initialization
│   ├── config/          # Configuration and constants
│   └── utils/           # Utility functions and helpers
├── docs/                # Documentation
└── tests/               # Test suite (coming soon)
```

## License

GNU General Public License v3.0. See [LICENSE](LICENSE) for details.

---

**Questions?** Check the [wiki](https://github.com/code0nwheels/dwellpy/wiki) or open an [issue](https://github.com/code0nwheels/dwellpy/issues).