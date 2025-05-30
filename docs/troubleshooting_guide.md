# Troubleshooting Guide

This guide helps you diagnose and fix common issues with Dwellpy.

## Installation Issues

### "Command not found: dwellpy"

**Cause**: Dwellpy installed but isn't in your system's PATH.

**Solutions**:

**Windows**:
1. Try running: `python -m dwellpy`
2. If that works, pip likely installed to the wrong location
3. Reinstall Python and check "Add Python to PATH" during installation

**macOS**:
1. Try: `python3 -m dwellpy`
2. If that works, add to PATH:
   ```
   echo 'export PATH="$HOME/Library/Python/3.11/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```
   (Replace 3.11 with your Python version)

**Linux**:
1. Try: `python3 -m dwellpy`
2. If that works, add to PATH:
   ```
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```
3. **Alternative**: Try the automated installer:
   ```
   curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/linux-install.sh | bash
   ```

*If you need to completely remove and reinstall:*
```
curl -sSL https://raw.githubusercontent.com/code0nwheels/dwellpy/main/linux-uninstall.sh | bash
```

### "pip is not recognized" (Windows)
**Cause**: Python wasn't installed correctly or PATH wasn't set.

**Solution**:
1. Uninstall Python from Windows Settings > Apps
2. Reinstall Python from python.org
3. Check "Add Python to PATH" during installation

### "Permission denied" during installation
**Cause**: Insufficient privileges to install packages.

**Solutions**:
- **Windows**: Run Command Prompt as administrator
- **macOS/Linux**: Try `pip3 install --user dwellpy`

## Permission and Access Issues

### "Access denied" when running Dwellpy

**Windows**:
1. Run Command Prompt as administrator
2. Type: `dwellpy`
3. If still failing, check Windows Defender isn't blocking it

**macOS**:
1. Dwellpy should automatically prompt for accessibility permissions
2. If not prompted, go to System Preferences > Security & Privacy > Privacy > Accessibility
3. Add Terminal to the list and check it

**Linux**:
1. Ensure you're running X11 (not Wayland)
2. Check your desktop environment's accessibility settings

### Dwellpy can't click on system dialogs

**Windows**:
- This is normal - Dwellpy cannot click on UAC prompts
- Consider disabling UAC if you need to interact with system dialogs
- See the Windows Setup Guide for UAC disable instructions

**macOS**:
- Some system dialogs may be protected
- Ensure Terminal has accessibility permissions

## Clicking Problems

### Clicks not registering
**Symptoms**: Hovering but no clicks happen

**Diagnosis**:
1. Check if the ON/OFF button is green (active)
2. Observe your cursor behavior - does it seem like the dwell detection keeps restarting when you try to hover?
3. Try hovering over a large target (like desktop)

**Solutions**:
1. Increase Move Limit in settings (try +3 pixels)
2. Decrease Dwell Time (try -0.2 seconds)
3. Ensure your cursor input method is working correctly

### Too many accidental clicks
**Symptoms**: Clicking when you don't intend to

**Solutions**:
1. Increase Dwell Time in settings (try +0.2 seconds)
2. Decrease Move Limit (try -2 pixels)
3. Practice moving your cursor more deliberately between targets

### Clicks happening in wrong location
**Symptoms**: Clicks appear offset from where you're hovering

**Cause**: Usually a multi-monitor setup issue or display scaling problem.

**Solutions**:
1. Try on a single monitor to test
2. Check Windows display scaling settings
3. If this persists, please open an issue on GitHub with details about your monitor setup

### Can't click on specific programs
**Cause**: The program is running with higher privileges than Dwellpy.

**Solutions**:
- **Windows**: Run Command Prompt as administrator before starting Dwellpy
- **macOS**: Ensure Terminal has accessibility permissions
- **Linux**: The program might be running as root

## Platform-Specific Issues

### Windows: Antivirus blocking Dwellpy
**Symptoms**: Installation fails, or Dwellpy won't start

**Solutions**:
1. Add Python to your antivirus whitelist
2. Add the pip installation directory to whitelist
3. Temporarily disable real-time protection during installation

### Windows: Microsoft Store opens instead of Python
**Cause**: Windows app execution aliases interfering.

**Solution**:
1. Go to Settings > Apps > App execution aliases
2. Turn off Python aliases

### macOS: "Python quit unexpectedly"
**Cause**: Usually permissions or Python installation issues.

**Solutions**:
1. Try running from Terminal: `python3 -m dwellpy`
2. Check Console app for detailed error messages
3. Reinstall Python if needed

### Linux: Works in X11 but not Wayland
**Cause**: Dwellpy requires X11 currently.

**Solution**:
1. Log out
2. At login screen, select "Ubuntu on Xorg" or similar
3. Log back in

## Diagnostic Steps

### Basic Troubleshooting Process
1. **Verify installation**: Can you run `python3 -m dwellpy`?
2. **Check permissions**: Are you getting permission errors?
3. **Test basic clicking**: Does it work on the desktop or a simple app?
4. **Check settings**: Are Move Limit and Dwell Time reasonable?
5. **Isolate the issue**: Does it happen with all programs or just specific ones?

### Gathering Information for Support
If you need to report a bug, collect this information:

**System Info**:
- Operating system and version
- Python version (`python3 --version`)
- Dwellpy version
- Input device type (mouse, head tracker, etc.)

**Error Details**:
- Exact error messages
- When the problem occurs
- Steps to reproduce
- What you expected vs. what happened

**Settings**:
- Your current Move Limit and Dwell Time settings
- Whether transparency is enabled
- Any other accessibility software running

### Log Files
Dwellpy creates log files that can help diagnose issues. Include relevant log entries when reporting bugs.

**Log file locations**:

**Windows**:
```
%APPDATA%\Dwellpy\logs\
```
Or navigate to: `C:\Users\[YourUsername]\AppData\Roaming\Dwellpy\logs\`

**macOS**:
```
~/Library/Application Support/Dwellpy/logs/
```

**Linux**:
```
~/.local/share/Dwellpy/logs/
```

**What to look for**:
- Error messages around the time the problem occurred
- Warning messages that might indicate configuration issues
- The most recent log file (usually named with current date)

**How to access**:
1. Navigate to the log directory for your operating system
2. Open the most recent log file in a text editor
3. Look for entries around the time you experienced the issue
4. Copy relevant error messages

## Getting Help

### Before Asking for Help
1. Try the solutions in this guide
2. Search existing GitHub issues
3. Test with default settings
4. Try restarting Dwellpy and/or your computer

### Where to Get Help
1. **GitHub Issues**: https://github.com/code0nwheels/dwellpy/issues
2. **GitHub Discussions**: For questions and general help
3. **Setup Guides**: Platform-specific installation help

### Reporting Bugs
When reporting issues:
1. Use the GitHub issue template
2. Include system information
3. Describe steps to reproduce
4. Mention what you expected vs. what happened
5. Include any error messages

## Common Solutions Summary

| Problem | Quick Fix |
|---------|-----------|
| No clicks | Increase Move Limit, decrease Dwell Time |
| Accidental clicks | Decrease Move Limit, increase Dwell Time |
| Can't find dwellpy | Try `python3 -m dwellpy` |
| Permission errors | Run with admin/sudo, check accessibility settings |
| High CPU usage | Close other accessibility tools |
| System dialogs | Use manual clicking, or disable UAC (Windows) |