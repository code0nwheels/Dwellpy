# Windows Setup Guide

This guide will help you install and run Dwellpy on Windows.

## System Requirements

- Windows 10 or Windows 11
- Administrator access (for some installation methods)
- Internet connection for downloads

## Method 1: Standalone Executable (Recommended - Easiest)

This is the simplest way to get Dwellpy running on Windows:

### Download and Setup
1. Go to the [latest releases page](https://github.com/code0nwheels/dwellpy/releases/latest)
2. Download the Windows executable (look for `dwellpy-*-windows-x64.exe`)
3. **Rename and organize** (recommended):
   - Rename the downloaded file to `Dwellpy.exe`
   - Move it to a permanent location like `C:\Program Files\Dwellpy\` or `C:\Users\[YourName]\AppData\Local\Programs\Dwellpy\`
   - Or simply keep it in a dedicated folder like `C:\Dwellpy\`
4. Double-click `Dwellpy.exe` to run
5. If Windows shows a security warning, click "More info" then "Run anyway"
6. The Dwellpy toolbar should appear on your screen!

### Security Note
Windows may show a SmartScreen warning because the executable isn't digitally signed. This is normal for open-source software. Click "More info" then "Run anyway" to proceed.

### Creating a Desktop Shortcut (Recommended)
1. Right-click on the renamed `Dwellpy.exe` file
2. Select "Create shortcut"
3. Move the shortcut to your desktop or Start menu for easy access

## Method 2: Install via Python (Advanced Users)

If you prefer to install via Python or need the latest development version:

## Step 1: Install Python

Dwellpy requires Python 3.9 or newer. If you already have Python installed, you can skip to Step 2.

### Download Python
1. Go to https://www.python.org/downloads/
2. Click the yellow "Download Python" button (this gets the latest version)
3. Run the downloaded installer

### Install Python
**Important**: During installation, make sure to:
- Check "Add Python to PATH" (this is crucial!)
- Check "Install for all users" if you have admin rights
- Click "Install Now"

### Verify Python Installation
1. Press `Windows Key + R`
2. Type `cmd` and press Enter
3. In the black window that opens, type: `python --version`
4. You should see something like "Python 3.x.x"

If you get an error like "python is not recognized", Python wasn't added to your PATH. You'll need to reinstall Python and check the "Add Python to PATH" option.

## Step 2: Install and Run Dwellpy

**Important**: Run Command Prompt as administrator for both installation and running:

1. Press `Windows Key`
2. Type `cmd`
3. Right-click "Command Prompt" and select "Run as administrator"
4. Click "Yes" when UAC asks for permission
5. Install Dwellpy by typing: `pip install dwellpy`
6. Wait for installation to complete
7. Run Dwellpy by typing: `dwellpy`

The Dwellpy toolbar should appear on your screen!

## Comparison of Installation Methods

| Method | Pros | Cons |
|--------|------|------|
| **Standalone Executable** | No Python required, instant startup, no dependencies | Larger file size (~36 MB) |
| **Python pip install** | Smaller download, easier updates, access to latest features | Requires Python installation, potential dependency conflicts |

**Recommendation**: Use the standalone executable unless you're already comfortable with Python or need development features.

## Common Issues

### Standalone Executable Issues

**Windows Security Warning**
- This is normal for unsigned executables
- Click "More info" then "Run anyway"
- You can also right-click the file, go to Properties, and check "Unblock" at the bottom

**Slow Startup**
- First run may be slower as Windows scans the executable
- Subsequent runs should be faster

### Python Installation Issues

### "Access Denied" or Permission Errors
If you get permission errors, make sure you're running Command Prompt as administrator (see Step 3 above).

### "pip is not recognized"
If you get this error, Python wasn't installed correctly:

1. Uninstall Python from Windows Settings > Apps
2. Reinstall Python, making sure to check "Add Python to PATH"

### Python Opens Microsoft Store
If typing `python` opens the Microsoft Store instead of running Python:

1. Go to Windows Settings > Apps > App execution aliases
2. Turn off the aliases for Python

## Updating Dwellpy

To update to a newer version:
```
pip install --upgrade dwellpy
```

## Uninstalling

To remove Dwellpy:
```
pip uninstall dwellpy
```

## Creating a Desktop Shortcut

For easier manual access:

1. Right-click on your desktop
2. Select "New" > "Shortcut"
3. For location, enter: `dwellpy`
4. Name it "Dwellpy" and click Finish
5. Right-click the new shortcut, select "Properties"
6. Click "Advanced" and check "Run as administrator"

**Note**: This shortcut will ask for UAC permission each time you run it.

## Running Dwellpy Automatically

### Auto-Start with Windows (Advanced)
For automatic startup with administrator privileges, use Task Scheduler:

1. Press `Windows Key + R`, type `taskschd.msc`, press Enter
2. In Task Scheduler, click "Create Task" in the right panel
3. **General tab**:
   - Name: "Dwellpy Startup"
   - Check "Run with highest privileges"
   - Select "Run whether user is logged on or not"
4. **Triggers tab**:
   - Click "New"
   - Set "Begin the task" to "At startup"
   - Click "OK"
5. **Actions tab**:
   - Click "New"
   - Action: "Start a program"
   - Program: `dwellpy`
   - Click "OK"
6. Click "OK" to save the task

**Note**: You may see one UAC prompt when the task first runs, but after that it will start automatically with admin privileges.

**Important**: Do NOT use the regular startup folder (`shell:startup`) for Dwellpy. Windows ignores "Run as administrator" settings for shortcuts in the startup folder, so Dwellpy won't have the permissions it needs.

## UAC Limitation

**Important**: Dwellpy cannot click on UAC (User Account Control) prompts. These are the blue/gray dialog boxes that ask "Do you want to allow this app to make changes to your device?" This is a Windows security feature that blocks all automated clicking.

If you frequently encounter UAC prompts and need to click on them, you may want to consider disabling UAC:

### To Disable UAC:
1. Press `Windows Key + R`
2. Type `msconfig` and press Enter
3. Go to the "Tools" tab
4. Select "Change UAC Settings" and click "Launch"
5. Move the slider to "Never notify"
6. Click "OK" and restart your computer

**Security Warning**: Disabling UAC reduces your system's security. Only disable it if you understand the risks and need Dwellpy to work with system dialogs.

## Getting Help

If you're still having trouble:

1. Check the [Troubleshooting Guide](https://github.com/code0nwheels/dwellpy/wiki/Troubleshooting)
2. Open an issue on [GitHub](https://github.com/code0nwheels/dwellpy/issues)
3. Include your Windows version and any error messages you see

## Next Steps

Once Dwellpy is running, check out the [Configuration Guide](https://github.com/code0nwheels/dwellpy/wiki/Configuration) to adjust the settings for your needs.