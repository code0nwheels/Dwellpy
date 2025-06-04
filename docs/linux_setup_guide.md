# Linux Setup Guide

This guide will help you install and run Dwellpy on Linux.

## System Requirements

- Linux distribution with X11 (Wayland support coming soon)
- Python 3.9 or newer (for pip installation)
- Internet connection for downloads

## Method 1: Standalone Executables (Easiest)

Download and run the executable for your architecture - no installation required:

### For x64 Systems (Most Common)
1. Go to the [latest releases page](https://github.com/code0nwheels/dwellpy/releases/latest)
2. Download the x64 executable (look for `dwellpy-*-linux-debian-x64`)
3. Open a terminal and navigate to Downloads: `cd ~/Downloads`
4. **Rename and organize** (recommended):
   ```bash
   # Rename the file
   mv dwellpy-*-linux-debian-x64 Dwellpy
   
   # Move to a proper location
   sudo mkdir -p /opt/dwellpy
   sudo mv Dwellpy /opt/dwellpy/
   sudo chmod +x /opt/dwellpy/Dwellpy
   
   # Create a symlink for easy access
   sudo ln -sf /opt/dwellpy/Dwellpy /usr/local/bin/dwellpy
      ```
5. Run: `dwellpy` (or `/opt/dwellpy/Dwellpy`)

### For ARM64 Systems (Raspberry Pi, Apple Silicon, etc.)
1. Go to the [latest releases page](https://github.com/code0nwheels/dwellpy/releases/latest)
2. Download the ARM64 executable (look for `dwellpy-*-linux-debian-arm64`)
3. Open a terminal and navigate to Downloads: `cd ~/Downloads`
4. **Rename and organize** (recommended):
   ```bash
   # Rename the file
   mv dwellpy-*-linux-debian-arm64 Dwellpy
   
   # Move to a proper location
   sudo mkdir -p /opt/dwellpy
   sudo mv Dwellpy /opt/dwellpy/
   sudo chmod +x /opt/dwellpy/Dwellpy
   
   # Create a symlink for easy access
   sudo ln -sf /opt/dwellpy/Dwellpy /usr/local/bin/dwellpy
   ```
5. Run: `./dwellpy-*-linux-debian-arm64`

### Quick Installation Script
For easier access, you can install the executable system-wide:

```bash
# For x64 systems - replace * with actual version number
curl -L https://github.com/code0nwheels/dwellpy/releases/latest/download/dwellpy-*-linux-debian-x64 -o dwellpy
chmod +x dwellpy
sudo mv dwellpy /usr/local/bin/

# For ARM64 systems - replace * with actual version number  
curl -L https://github.com/code0nwheels/dwellpy/releases/latest/download/dwellpy-*-linux-debian-arm64 -o dwellpy
chmod +x dwellpy
sudo mv dwellpy /usr/local/bin/
```

Then run with just: `dwellpy`

## Method 2: Automated Install Script (Recommended for pip users)

The easiest way to install Dwellpy via pip is using our automated install script:

```bash
curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/utils/linux-install.sh | bash
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

## Method 3: Manual Installation (Advanced Users)

## Comparison of Installation Methods

| Method | Pros | Cons |
|--------|------|------|
| **Standalone Executable** | No dependencies, instant startup, works on any Linux | Larger file size (~68 MB), architecture-specific |
| **Automated Script** | Full desktop integration, auto-start option, automatic updates | Requires Python, distribution-specific |
| **Manual pip install** | Lightweight, latest features, easy updates | No desktop integration, requires Python knowledge |

**Recommendation**: Use standalone executables for simplicity, or the automated script for full desktop integration.

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

### Method 1: Via Dwellpy Settings (Recommended)
The easiest way to enable auto-start is through Dwellpy's built-in settings:

1. Open Dwellpy
2. Click the **Settings** button (gear icon) 
3. Go to the **General** tab
4. Check **"Auto-start on system login"**
5. Click **OK**

Dwellpy will now automatically start when you log in to your desktop environment. This method creates an XDG autostart entry that integrates properly with your system.

### Method 2: Manual File Management
If you prefer to manage auto-start manually:

#### Check if auto-start is enabled:
```bash
ls -la ~/.config/autostart/dwellpy.desktop
```

#### Disable auto-start:
```bash
rm ~/.config/autostart/dwellpy.desktop
```

#### Enable auto-start (if not set up during installation):
```bash
# Copy the desktop entry to autostart
cp ~/.local/share/applications/dwellpy.desktop ~/.config/autostart/dwellpy.desktop
```

### Method 3: Desktop Environment Settings
You can also manage auto-start through your desktop environment:
- **GNOME**: Settings → Applications → Startup Applications
- **KDE**: System Settings → Startup and Shutdown → Autostart  
- **XFCE**: Settings → Session and Startup → Application Autostart
- **Ubuntu**: Search for "Startup Applications" in Activities

### Disabling Auto-Start
To disable auto-start:
- **Via Settings**: Uncheck "Auto-start on system login" in Dwellpy Settings → General
- **Manually**: Remove the file `~/.config/autostart/dwellpy.desktop`
- **Desktop Environment**: Use your desktop's startup application settings

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
curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/utils/linux-install.sh | bash
```

### If installed with pip:
```bash
pip3 install --upgrade dwellpy
```

## Uninstalling

### If installed with automated script:
Use the automated uninstall script:
```bash
curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/utils/linux-uninstall.sh | bash
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