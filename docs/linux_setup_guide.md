# Linux Setup Guide

This guide will help you install and run Dwellpy on Linux.

## System Requirements

- Linux distribution with X11 (Wayland support coming soon)
- Python 3.8 or newer (usually pre-installed)
- Internet connection for installation

## Quick Install (Recommended)

The easiest way to install Dwellpy is using our automated install script:

```bash
curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/linux-install.sh | bash
```

This script will:
- ✅ Detect your Linux distribution automatically
- ✅ Install Python 3 and git if needed
- ✅ Download and install Dwellpy from source
- ✅ Create a launcher script in `~/.local/bin/dwellpy`
- ✅ Add the launcher to your PATH
- ✅ Set up a systemd service for auto-start
- ✅ Check for X11/Wayland compatibility

### Supported Distributions
- Ubuntu/Debian/Pop!_OS/Linux Mint
- Fedora
- CentOS/RHEL/Rocky Linux/AlmaLinux
- Arch Linux/Manjaro
- openSUSE

After installation completes, you can start Dwellpy with:
```bash
dwellpy
```

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

## Managing the Dwellpy Service

If you used the automated installer, Dwellpy is set up as a systemd user service:

### Check service status:
```bash
systemctl --user status dwellpy.service
```

### Start the service manually:
```bash
systemctl --user start dwellpy.service
```

### Stop the service:
```bash
systemctl --user stop dwellpy.service
```

### Disable auto-start:
```bash
systemctl --user disable dwellpy.service
```

### Re-enable auto-start:
```bash
systemctl --user enable dwellpy.service
```

## Manual Auto-Start Setup

If you installed manually and want auto-start, create a systemd user service:

1. Create the service file:
   ```bash
   mkdir -p ~/.config/systemd/user
   cat > ~/.config/systemd/user/dwellpy.service << EOF
   [Unit]
   Description=Dwellpy accessibility tool
   After=graphical-session.target

   [Service]
   Type=simple
   ExecStart=dwellpy
   Restart=on-failure
   Environment=DISPLAY=:0

   [Install]
   WantedBy=default.target
   EOF
   ```

2. Enable and start the service:
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable dwellpy.service
   systemctl --user start dwellpy.service
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
```bash
# Stop and disable the service
systemctl --user stop dwellpy.service
systemctl --user disable dwellpy.service

# Remove installation directory
rm -rf ~/.local/dwellpy

# Remove launcher script
rm -f ~/.local/bin/dwellpy

# Remove service file
rm -f ~/.config/systemd/user/dwellpy.service

# Reload systemd
systemctl --user daemon-reload
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