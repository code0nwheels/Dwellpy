# Linux Setup Guide

This guide will help you install and run Dwellpy on Linux.

## System Requirements

- Linux distribution with X11 (Wayland support coming soon)
- Python 3.8 or newer (usually pre-installed)
- Internet connection for installation

## Step 1: Install pip

Most Linux distributions come with Python but not pip. Install it using your package manager:

### Ubuntu/Debian
```
sudo apt update
sudo apt install python3-pip
```

### Fedora
```
sudo dnf install python3-pip
```

### Arch Linux
```
sudo pacman -S python-pip
```

### Other Distributions
Check your distribution's documentation for installing `python3-pip`.

## Step 2: Install Dwellpy

```
pip3 install dwellpy
```

## Step 3: Run Dwellpy

```
dwellpy
```

The Dwellpy toolbar should appear on your screen!

## Common Issues

### "Command not found: dwellpy"
The installation likely put dwellpy in `~/.local/bin` which isn't in your PATH:

1. Add it to your PATH temporarily:
   ```
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. Make it permanent by adding to your shell config:
   ```
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Permission Errors
If you get permission errors during installation, try:
```
pip3 install --user dwellpy
```

### Wayland Issues
Dwellpy currently requires X11. If you're using Wayland:

1. Log out of your session
2. At the login screen, look for a gear/settings icon
3. Select "Ubuntu on Xorg" or similar X11 option
4. Log back in and try running Dwellpy

## Running Dwellpy Automatically

Create a systemd user service:

1. Create the service file:
   ```
   mkdir -p ~/.config/systemd/user
   cat > ~/.config/systemd/user/dwellpy.service << EOF
   [Unit]
   Description=Dwellpy accessibility tool
   After=graphical-session.target

   [Service]
   Type=simple
   ExecStart=dwellpy
   Restart=on-failure

   [Install]
   WantedBy=default.target
   EOF
   ```

2. Enable and start the service:
   ```
   systemctl --user enable dwellpy.service
   systemctl --user start dwellpy.service
   ```

Dwellpy will now start automatically when you log in.

## Updating Dwellpy

```
pip3 install --upgrade dwellpy
```

## Uninstalling

```
pip3 uninstall dwellpy
```

## Getting Help

If you're still having trouble:

1. Check the [Troubleshooting Guide](https://github.com/code0nwheels/dwellpy/wiki/Troubleshooting)
2. Open an issue on [GitHub](https://github.com/code0nwheels/dwellpy/issues)
3. Include your Linux distribution, desktop environment, and any error messages

## Next Steps

Once Dwellpy is running, check out the [Configuration Guide](https://github.com/code0nwheels/dwellpy/wiki/Configuration) to adjust the settings for your needs.