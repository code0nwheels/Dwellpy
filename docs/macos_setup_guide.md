# macOS Setup Guide

This guide will help you install and run Dwellpy on macOS.

## System Requirements

- macOS 10.14 (Mojave) or newer
- Administrator access
- Internet connection for downloads

## Method 1: DMG Installer (Recommended - Easiest)

This is the simplest way to get Dwellpy running on macOS - just like any other Mac app:

### Download and Install
1. Go to the [latest releases page](https://github.com/code0nwheels/dwellpy/releases/latest)
2. Download the DMG installer (look for `dwellpy-installer.dmg`)
3. Double-click the downloaded DMG file to mount it
4. Drag **Dwellpy** to the **Applications** folder
5. Eject the DMG by clicking the eject button next to "Dwellpy Installer" in Finder sidebar

### First Run
1. Open **Applications** folder and double-click **Dwellpy**
2. macOS may show a security dialog - click **"Open"** to allow it to run
3. Dwellpy will automatically prompt you to grant accessibility permissions
4. Click **"Open System Preferences"** and allow Dwellpy access to control your computer
5. The Dwellpy toolbar should appear on your screen!

### Security Notes
- macOS may show a Gatekeeper warning because the app isn't signed with an Apple Developer certificate
- This is normal for open-source software - just click **"Open"** when prompted
- If the app is blocked, go to **System Preferences > Security & Privacy > General** and click **"Open Anyway"**

## Method 2: Standalone Executable (Advanced Users)

If you prefer the command-line approach or the DMG doesn't work:

### Download and Setup
1. Go to the [latest releases page](https://github.com/code0nwheels/dwellpy/releases/latest)
2. Download the macOS executable (look for `dwellpy-*-macos-x64`)
3. Open Terminal (Applications > Utilities > Terminal)
4. Navigate to your Downloads folder: `cd ~/Downloads`
5. **Rename and organize** (recommended):
   ```bash
   # Rename the file
   mv dwellpy-*-macos-x64 Dwellpy
   
   # Create a dedicated folder and move it there
   mkdir -p ~/Applications/Dwellpy
   mv Dwellpy ~/Applications/Dwellpy/
   
   # Make it executable
   chmod +x ~/Applications/Dwellpy/Dwellpy
   ```
6. Run Dwellpy: `~/Applications/Dwellpy/Dwellpy`
7. macOS will automatically prompt you to grant Terminal accessibility permissions
8. Click "Open System Preferences" and allow Terminal access to control your computer
9. The Dwellpy toolbar should appear on your screen!

### Adding to PATH (Optional)
To run Dwellpy from anywhere in Terminal:
```bash
echo 'export PATH="$HOME/Applications/Dwellpy:$PATH"' >> ~/.zshrc
source ~/.zshrc
```
Then you can simply run: `Dwellpy`

### Security Note
macOS may show a Gatekeeper warning because the executable isn't signed with an Apple Developer certificate. This is normal for open-source software.

If macOS blocks the executable:
1. Go to System Preferences > Security & Privacy > General
2. Click "Allow Anyway" next to the Dwellpy warning
3. Try running the executable again

## Method 3: Install via Python (Advanced Users)

If you prefer to install via Python or need the latest development version:

## Step 1: Install Dwellpy

1. Open Terminal (Applications > Utilities > Terminal)
2. Install Dwellpy by typing: `pip3 install dwellpy`
3. Wait for installation to complete

## Step 2: Run Dwellpy

1. In Terminal, type: `dwellpy`
2. macOS will automatically prompt you to grant Terminal accessibility permissions
3. Click "Open System Preferences" and allow Terminal access to control your computer
4. The Dwellpy toolbar should appear on your screen

### First-Time Security Prompt
macOS may also show a security dialog the first time you run Dwellpy. Click "Open" to allow it to run.

## Comparison of Installation Methods

| Method | Pros | Cons |
|--------|------|------|
| **DMG Installer** | Easy drag-and-drop installation, appears in Applications folder, professional experience | Still requires accessibility permissions, may show Gatekeeper warnings |
| **Standalone Executable** | No Python required, self-contained, consistent performance | Requires terminal usage, larger file size (31.1 MB) |
| **Python pip install** | Smaller download, easier updates, integrates with system Python | Requires Python installation, potential dependency conflicts |

**Recommendation**: Use the DMG installer for the best user experience, especially if you're not familiar with the terminal.

## Common Issues

### Standalone Executable Issues

**"Cannot be opened because it is from an unidentified developer"**
1. Right-click the executable and select "Open"
2. Click "Open" in the dialog that appears
3. Or go to System Preferences > Security & Privacy > General and click "Open Anyway"

**Executable not found after download**
- Make sure you've made it executable with `chmod +x dwellpy-0.9.0-macos-x64`
- Check that you're in the correct directory (usually `~/Downloads`)

### Python Installation Issues

### "Command not found: dwellpy"
This usually means pip installed to a location not in your PATH:

1. Try: `python3 -m pip show dwellpy` to see where it's installed
2. If it shows a path like `/Users/yourname/Library/Python/3.x/bin`, add this to your PATH:
   ```
   echo 'export PATH="$HOME/Library/Python/3.x/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```
   (Replace 3.x with your Python version)

### "Permission denied" Errors
If you get permission errors after granting accessibility access:

1. Make sure you clicked "Allow" when macOS prompted for accessibility permissions
2. If problems persist, manually check System Preferences > Security & Privacy > Privacy > Accessibility
3. Ensure Terminal is listed and checked

### Gatekeeper Warnings
If macOS blocks Dwellpy from running:

1. Go to System Preferences > Security & Privacy > General
2. Click "Allow Anyway" next to the Dwellpy warning
3. Try running Dwellpy again

## Updating Dwellpy

To update to a newer version:
```
pip3 install --upgrade dwellpy
```

## Uninstalling

To remove Dwellpy:
```
pip3 uninstall dwellpy
```

## Running Dwellpy Automatically

### Auto-Start with Login
To start Dwellpy automatically when you log in:

1. Create a simple startup script:
   ```
   echo '#!/bin/bash
   dwellpy' > ~/dwellpy_start.sh
   chmod +x ~/dwellpy_start.sh
   ```

2. Go to System Preferences > Users & Groups
3. Click your user account
4. Click "Login Items"
5. Click the "+" button
6. Navigate to your home folder and select `dwellpy_start.sh`
7. Add it to the list

Dwellpy will now start automatically when you log in.

## Getting Help

If you're still having trouble:

1. Check the [Troubleshooting Guide](https://github.com/code0nwheels/dwellpy/wiki/Troubleshooting)
2. Open an issue on [GitHub](https://github.com/code0nwheels/dwellpy/issues)
3. Include your macOS version and any error messages you see

## Next Steps

Once Dwellpy is running, check out the [Configuration Guide](https://github.com/code0nwheels/dwellpy/wiki/Configuration) to adjust the settings for your needs.