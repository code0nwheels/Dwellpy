# macOS Setup Guide

This guide will help you install and run Dwellpy on macOS.

## System Requirements

- macOS 10.14 (Mojave) or newer
- Administrator access
- Internet connection for installation

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

## Common Issues

### "Command not found: dwellpy"
This usually means pip installed to a location not in your PATH:

1. Try: `python3 -m pip show dwellpy` to see where it's installed
2. If it shows a path like `/Users/yourname/Library/Python/3.x/bin`, add this to your PATH:
   ```
   echo 'export PATH="$HOME/Library/Python/3.11/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```
   (Replace 3.11 with your Python version)

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