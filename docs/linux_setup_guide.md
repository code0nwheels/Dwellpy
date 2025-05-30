# Linux Setup Guide

This guide will help you install and run Dwellpy on Linux.

## System Requirements

- Linux distribution with X11 (Wayland support coming soon)
- Python 3.9 or newer (usually pre-installed)
- Internet connection for installation

## Quick Install (Recommended)

The easiest way to install Dwellpy is using our automated install script:

```bash
curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/linux-install.sh | bash
```

This script will:
- Detect your Linux distribution automatically
- Install Python 3 and git if needed
- Download and install Dwellpy from source
- Create a launcher script in `~/.local/bin/dwellpy`
- Add the launcher to your PATH
- Create a desktop menu entry (appears in Applications menu)
- Optionally set up autostart (asks for your preference)
- Check for X11/Wayland compatibility
- Detect desktop environment and optimize setup

### Supported Distributions (X11 ONLY)
- Ubuntu/Debian/Pop!_OS/Linux Mint
- Fedora
- CentOS/RHEL/Rocky Linux/AlmaLinux
- Arch Linux/Manjaro
- openSUSE

### Installation Features
The automated installer provides:
- **Desktop Integration**: Dwellpy appears in your Applications menu
- **Optional Auto-start**: Choose whether Dwellpy starts automatically when you log in
- **Enhanced Launcher**: Improved startup script with GUI environment detection
- **Comprehensive Logging**: Installation and runtime logs for troubleshooting

After installation completes, you can:
- Start from command line: `dwellpy`
- Start from Applications menu: Look for "Dwellpy" in Accessibility or System Tools
- Start automatically: If you chose auto-start during installation

## Manual Installation (Alternative)

If you prefer to install manually or the automated script doesn't work for your system:

### Step 1: Install pip

Most Linux distributions come with Python but not pip. Install it using your package manager:

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3-pip
```

#### Fedora
```bash
sudo dnf install python3-pip
```

#### Arch Linux
```bash
sudo pacman -S python-pip
```

#### Other Distributions
Check your distribution's documentation for installing `python3-pip`.

### Step 2: Install Dwellpy

```bash
pip3 install dwellpy
```

### Step 3: Run Dwellpy

```bash
dwellpy
```

The Dwellpy toolbar should appear on your screen!

## Common Issues

### "Command not found: dwellpy"
The installation likely put dwellpy in `~/.local/bin` which isn't in your PATH:

1. Add it to your PATH temporarily:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. Make it permanent by adding to your shell config:
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Permission Errors
If you get permission errors during installation, try:
```bash
pip3 install --user dwellpy
```

### Wayland Issues
Dwellpy currently requires X11. If you're using Wayland:

1. Log out of your session
2. At the login screen, look for a gear/settings icon
3. Select "Ubuntu on Xorg" or similar X11 option
4. Log back in and try running Dwellpy

The automated install script will detect Wayland and warn you about this requirement.

## Managing Auto-Start

### Check if auto-start is enabled:
```bash
ls -la ~/.config/autostart/dwellpy.desktop
```

### Disable auto-start:
```bash
rm ~/.config/autostart/dwellpy.desktop
```

### Enable auto-start (if not set up during installation):
```bash
# Copy the desktop entry to autostart
cp ~/.local/share/applications/dwellpy.desktop ~/.config/autostart/dwellpy.desktop
```

### Desktop Environment Settings:
You can also manage auto-start through your desktop environment:
- **GNOME**: Settings → Applications → Startup Applications
- **KDE**: System Settings → Startup and Shutdown → Autostart  
- **XFCE**: Settings → Session and Startup → Application Autostart
- **Ubuntu**: Search for "Startup Applications" in Activities

## Manual Auto-Start Setup (For Manual Installation)

If you installed manually and want auto-start, create an XDG autostart entry:

```bash
# Create autostart directory
mkdir -p ~/.config/autostart

# Create desktop entry
cat > ~/.config/autostart/dwellpy.desktop << EOF
[Desktop Entry]
Type=Application
Name=Dwellpy
Comment=Click by hovering - accessibility tool
Exec=dwellpy
Icon=applications-accessibility
Categories=Accessibility;Utility;
StartupNotify=false
NoDisplay=false
Hidden=false
X-GNOME-Autostart-enabled=true
EOF
```

## Updating Dwellpy

### If installed with automated script:
Re-run the install script to get the latest version:
```bash
curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/linux-install.sh | bash
```

### If installed with pip:
```bash
pip3 install --upgrade dwellpy
```

## Uninstalling

### If installed with automated script:
Use the automated uninstall script:
```bash
curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/linux-uninstall.sh | bash
```

This will safely remove:
- All Dwellpy source code and files
- Desktop menu entry
- Auto-start configuration
- Launcher script
- Running Dwellpy processes
- Empty directories (if no other apps use them)

**Optional removal**: The uninstaller will ask if you want to remove the PATH modification from `~/.bashrc` (it backs up the file first).

### Manual uninstall (if needed):
```bash
# Stop running processes
pkill -f "python3 -m dwellpy.main"

# Remove auto-start
rm -f ~/.config/autostart/dwellpy.desktop

# Remove desktop menu entry  
rm -f ~/.local/share/applications/dwellpy.desktop

# Remove launcher script
rm -f ~/.local/bin/dwellpy

# Remove source code
rm -rf ~/.local/dwellpy

# Update desktop database
update-desktop-database ~/.local/share/applications 2>/dev/null || true
```

### If installed with pip:
```bash
pip3 uninstall dwellpy
```

## Getting Help

If you're still having trouble:

1. Check the [Troubleshooting Guide](troubleshooting_guide.md)
2. Open an issue on [GitHub](https://github.com/code0nwheels/dwellpy/issues)
3. Include your Linux distribution, desktop environment, and any error messages

## Next Steps

Once Dwellpy is running, check out the [Configuration Guide](configuration_guide.md) to adjust the settings for your needs.