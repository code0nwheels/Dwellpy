# Linux Setup Guide

This guide will help you install and run Dwellpy on Linux.

## System Requirements

- Linux distribution with X11 (Wayland support coming soon)
- Python 3.9 or newer (if using the install script or pip)
- Internet connection for downloads

## Method 1: Debian Package (.deb) Installation (Recommended for Debian/Ubuntu/Mint)

If you are using a Debian-based distribution (like Debian, Ubuntu, Linux Mint, Pop!_OS, etc.), the recommended way to install Dwellpy is using the `.deb` package.

1.  Go to the [latest releases page](https://github.com/code0nwheels/dwellpy/releases/latest).
2.  Download the `.deb` file for your system's architecture.
    *   For **x64 (amd64)** systems (most common), download `dwellpy-*-linux-debian-x64.deb`.
    *   For **ARM64** systems, download `dwellpy-*-linux-debian-arm64.deb`.
3.  Open a terminal and navigate to the directory where you downloaded the file (e.g., `cd ~/Downloads`).
4.  Install the package using `dpkg`. Replace `dwellpy-version-architecture.deb` with the actual filename:
    ```bash
    sudo dpkg -i dwellpy-version-architecture.deb
    ```
    For example:
    ```bash
    sudo dpkg -i dwellpy-0.9.1-linux-debian-x64.deb
    ```
5.  If you encounter any dependency errors, run the following command to fix them. This command will also install Dwellpy if `dpkg` failed due to missing dependencies.
    ```bash
    sudo apt-get update && sudo apt-get install -f
    ```
6.  Once installed, you can run Dwellpy by typing `dwellpy` in your terminal or finding it in your application menu.

**Note on Architectures:** The `.deb` package for `x64` is built with the architecture `amd64` in its control file to ensure compatibility with `dpkg`. Similarly, `arm64` is used for ARM64 systems.

### Updating Dwellpy (Installed via .deb)

To update Dwellpy if you installed it using the `.deb` package:

1.  Go to the [latest releases page](https://github.com/code0nwheels/dwellpy/releases/latest) and download the new `.deb` file for your architecture.
2.  Open a terminal and navigate to the directory where you downloaded the new version.
3.  Install the new package. This will typically upgrade the existing installation.
    ```bash
    sudo dpkg -i dwellpy-new-version-architecture.deb
    ```
    Replace `dwellpy-new-version-architecture.deb` with the actual filename of the new version.
4.  If you encounter dependency issues, or to ensure all dependencies are correct, run:
    ```bash
    sudo apt-get update && sudo apt-get install -f
    ```

Alternatively, if Dwellpy was installed and its dependencies were resolved with `apt` (e.g., after `sudo apt-get install -f`), you might be able to upgrade using `apt` directly if you've added a PPA or if the package is in a configured repository (though this guide currently focuses on direct .deb installation):
    ```bash
    # sudo apt-get update
    # sudo apt-get install --only-upgrade dwellpy
    ```
    For direct .deb file downloads, the `dpkg -i` method is the most straightforward for upgrading.

### Uninstalling Dwellpy (Installed via .deb)

To uninstall Dwellpy if you installed it using the `.deb` package:

1.  Open a terminal.
2.  Use the following command to remove the package:
    ```bash
    sudo apt-get remove dwellpy
    ```
3.  If you also want to remove any system-wide configuration files that were installed with the package (though Dwellpy primarily stores user-specific settings in the user's home directory), you can use:
    ```bash
    sudo apt-get purge dwellpy
    ```
    For most users, `sudo apt-get remove dwellpy` is sufficient.

## Method 2: Automated Install Script (Recommended for Other Distributions or Script-Based Setup)

For other Linux distributions, or if you prefer a script-based setup that handles dependencies and creates a desktop entry, you can use our automated install script. This script installs Dwellpy using pip and sets up the environment.

```bash
curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/utils/linux-install.sh | bash
```

This script will:
- Detect your Linux distribution.
- Install Python 3 and pip if needed.
- Install Dwellpy and its dependencies using pip.
- Create a launcher script (usually in `~/.local/bin/dwellpy`).
- Attempt to add the launcher to your PATH.
- Create a desktop menu entry (Dwellpy should appear in your Applications menu).
- Optionally set up autostart (it will ask for your preference).
- Check for X11/Wayland compatibility.

### Supported Distributions by Script (X11 ONLY)
The script aims to support a wide range of distributions, including:
- Ubuntu/Debian/Pop!_OS/Linux Mint (though the .deb package is preferred here)
- Fedora
- CentOS/RHEL/Rocky Linux/AlmaLinux
- Arch Linux/Manjaro
- openSUSE

If your distribution is not listed, the script might still work, especially if it's based on one of the above.

### Installation Features via Script
- **Desktop Integration**: Dwellpy appears in your Applications menu.
- **Optional Auto-start**: Choose whether Dwellpy starts automatically when you log in.
- **Environment Setup**: Handles Python, pip, and PATH adjustments.

After installation completes, you can typically:
- Start from command line: `dwellpy`
- Start from Applications menu: Look for "Dwellpy".

## Method 3: Manual Installation (Advanced Users)

## Comparison of Installation Methods

| Method | Pros | Cons |
|--------|------|------|
| **Debian Package (.deb)** | System-wide installation, dependency handling via `apt`, integrates with package manager, desktop entry. | Primarily for Debian-based systems (Ubuntu, Mint, etc.). |
| **Automated Install Script** | Handles dependencies, full desktop integration, auto-start option, works on many distributions. | Requires Python & pip, relies on script compatibility with your system. |
| **Manual pip install** | Lightweight, latest features directly from PyPI, fine-grained control. | No automatic desktop integration or auto-start setup, requires Python & pip knowledge, PATH management might be needed. |

**Recommendation**:
- For **Debian-based systems (Ubuntu, Mint, etc.)**: Use the **Debian Package (.deb)** for the best integration.
- For **other Linux distributions**: Use the **Automated Install Script**.
- For **advanced users** who prefer manual control or are on an unsupported distribution: Use **Manual pip install**.

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