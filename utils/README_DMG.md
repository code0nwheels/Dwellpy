# macOS DMG Creation for Dwellpy

This directory contains tools for creating professional macOS DMG installers for Dwellpy.

## Quick Start

### For Automated DMG Creation
When building on macOS, the build script will automatically ask if you want to create a DMG:

```bash
python utils/build_executable.py
# After build completes, it will ask:
# "Create DMG installer? (y/N):"
```

### For Manual DMG Creation
If you already have a built app bundle:

```bash
# Using Python script
python utils/create_macos_dmg.py

# Using shell script (macOS only)
chmod +x utils/create_dmg.sh
./utils/create_dmg.sh
```

## What Gets Created

The DMG creation process produces:

1. **Dwellpy.app** - A proper macOS application bundle with:
   - Correct Info.plist with accessibility permissions descriptions
   - App icon (ICNS format)
   - Proper bundle structure
   - macOS-appropriate metadata

2. **dwellpy-installer.dmg** - A professional installer that:
   - Opens to a drag-and-drop interface
   - Shows Dwellpy icon and Applications folder
   - Has proper window layout and styling
   - Is compressed for efficient distribution

## Requirements

### System Requirements
- macOS 10.14 (Mojave) or newer
- Xcode Command Line Tools (`xcode-select --install`)

### Build Requirements
- PyInstaller-built Dwellpy executable
- Icon files in `dwellpy/assets/icons/`

## Technical Details

### App Bundle Structure
```
Dwellpy.app/
├── Contents/
│   ├── Info.plist          # App metadata and permissions
│   ├── MacOS/
│   │   └── Dwellpy         # Main executable
│   └── Resources/
│       └── Dwellpy.icns    # App icon
```

### Info.plist Features
- Accessibility permission descriptions
- Proper app categorization
- File type associations for settings
- URL scheme support for future features
- Retina display support

### DMG Features
- Professional drag-and-drop layout
- Automatic window sizing and positioning
- Applications folder symlink
- Compressed format for distribution
- Custom volume name

## Icon Handling

The script automatically handles icon conversion:

1. **Preferred**: Uses existing `Dwellpy.icns` if available
2. **Fallback**: Converts `Dwellpy.png` to ICNS using macOS tools
3. **Multiple sizes**: Creates all required icon sizes for Retina displays

## Distribution

The final DMG can be distributed like any macOS app:

1. Upload to GitHub releases
2. Users download and double-click
3. Drag to Applications folder
4. Launch normally - no terminal required

## User Experience

After installation via DMG:
- App appears in Applications folder
- Launchable via Spotlight search
- Appears in Dock when running
- Standard macOS app behavior
- Proper accessibility permission prompts

## Troubleshooting

### "Command not found" errors
Install Xcode Command Line Tools:
```bash
xcode-select --install
```

### Permission denied
Make shell script executable:
```bash
chmod +x utils/create_dmg.sh
```

### Icon conversion fails
Ensure you have either:
- `dwellpy/assets/icons/Dwellpy.icns` (preferred)
- `dwellpy/assets/icons/Dwellpy.png` (will be converted)

### DMG layout issues
The script uses AppleScript to set window layout. If this fails:
1. The DMG will still work
2. Users can manually arrange the layout
3. Consider updating macOS or trying on a different system

## Development Notes

### Code Signing (Future)
For distribution outside developer channels, consider:
```bash
# Sign the app bundle
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" Dwellpy.app

# Notarize for Gatekeeper
xcrun notarytool submit dwellpy-installer.dmg --keychain-profile "YourProfile" --wait
```

### Custom Background (Future Enhancement)
The DMG creator can be enhanced with:
- Custom background images
- Styled window layouts
- Brand-specific styling
- License agreements

## Files in This Directory

- `create_macos_dmg.py` - Main DMG creation script
- `create_dmg.sh` - Shell wrapper for convenience
- `README_DMG.md` - This documentation

## Integration with Build Process

The DMG creation is integrated into the main build script:
- Automatically detects macOS
- Prompts user after successful build
- Handles both standalone and app bundle builds
- Provides clear success/failure feedback
