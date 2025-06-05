#!/usr/bin/env python3
"""
macOS DMG Creator for Dwellpy
Creates a professional DMG installer with drag-and-drop functionality.
"""

import os
import sys
import shutil
import subprocess
import tempfile
import plistlib
from pathlib import Path

def check_macos():
    """Ensure we're running on macOS."""
    import platform
    if platform.system() != 'Darwin':
        print("ERROR: This script must be run on macOS")
        return False
    return True

def check_dependencies():
    """Check for required macOS tools."""
    print("Checking macOS dependencies...")
    
    required_tools = ['hdiutil', 'iconutil']
    missing = []
    
    for tool in required_tools:
        try:
            subprocess.run([tool], capture_output=True, timeout=5)
            print(f"   ✓ {tool} available")
        except FileNotFoundError:
            missing.append(tool)
            print(f"   ✗ {tool} missing")
        except subprocess.TimeoutExpired:
            print(f"   ✓ {tool} available")
    
    if missing:
        print(f"\nERROR: Missing tools: {', '.join(missing)}")
        print("Install Xcode Command Line Tools: xcode-select --install")
        return False
    
    return True

def create_app_bundle():
    """Create a proper macOS .app bundle from the PyInstaller executable."""
    print("Creating macOS app bundle...")
    
    # Check if we have a PyInstaller-built executable
    if Path('dist/Dwellpy.app').exists():
        print("   ✓ PyInstaller app bundle already exists")
        return Path('dist/Dwellpy.app')
    
    exe_path = Path('dist/Dwellpy')
    if not exe_path.exists():
        print("   ERROR: No executable found in dist/")
        print("   Run the build script first: python utils/build_executable.py")
        return None
    
    # Create app bundle structure
    app_path = Path('dist/Dwellpy.app')
    contents_path = app_path / 'Contents'
    macos_path = contents_path / 'MacOS'
    resources_path = contents_path / 'Resources'
    
    # Create directories
    macos_path.mkdir(parents=True, exist_ok=True)
    resources_path.mkdir(parents=True, exist_ok=True)
    
    # Move executable
    shutil.move(str(exe_path), str(macos_path / 'Dwellpy'))
    os.chmod(macos_path / 'Dwellpy', 0o755)
    
    # Copy icon
    icon_source = Path('dwellpy/assets/icons/Dwellpy.icns')
    if icon_source.exists():
        shutil.copy2(icon_source, resources_path / 'Dwellpy.icns')
        print("   ✓ Icon copied")
    else:
        print("   ! No ICNS icon found, creating from PNG...")
        create_icns_from_png()
    
    # Create Info.plist
    create_info_plist(contents_path)
    
    print(f"   ✓ App bundle created: {app_path}")
    return app_path

def create_icns_from_png():
    """Create ICNS icon from PNG using macOS iconutil."""
    png_path = Path('dwellpy/assets/icons/Dwellpy.png')
    if not png_path.exists():
        print("   ! No PNG icon found either")
        return False
    
    # Create iconset structure
    iconset_path = Path('dist/Dwellpy.iconset')
    iconset_path.mkdir(exist_ok=True)
    
    # Icon sizes for macOS
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    try:
        for size in sizes:
            # Create regular resolution
            subprocess.run([
                'sips', '-z', str(size), str(size), 
                str(png_path), '--out', 
                str(iconset_path / f'icon_{size}x{size}.png')
            ], check=True, capture_output=True)
            
            # Create @2x resolution for retina
            if size <= 512:  # Don't create @2x for 1024px
                subprocess.run([
                    'sips', '-z', str(size * 2), str(size * 2),
                    str(png_path), '--out',
                    str(iconset_path / f'icon_{size}x{size}@2x.png')
                ], check=True, capture_output=True)
        
        # Convert iconset to icns
        subprocess.run([
            'iconutil', '-c', 'icns', str(iconset_path),
            '-o', 'dist/Dwellpy.app/Contents/Resources/Dwellpy.icns'
        ], check=True)
        
        # Cleanup
        shutil.rmtree(iconset_path)
        print("   ✓ ICNS icon created from PNG")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ! Failed to create ICNS: {e}")
        return False

def create_info_plist(contents_path):
    """Create a proper Info.plist for the app bundle."""
    info_plist = {
        'CFBundleName': 'Dwellpy',
        'CFBundleDisplayName': 'Dwellpy',
        'CFBundleIdentifier': 'com.dwellpy.dwellpy',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleExecutable': 'Dwellpy',
        'CFBundleIconFile': 'Dwellpy.icns',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'DWEL',
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.14.0',
        'LSBackgroundOnly': False,  # Changed to False so it appears in dock
        'LSUIElement': True,  # But hide dock icon since it's a utility
        
        # Accessibility permissions description
        'NSAppleEventsUsageDescription': 'Dwellpy needs accessibility permissions to monitor mouse movements and provide dwell clicking functionality.',
        'NSAccessibilityUsageDescription': 'Dwellpy requires accessibility permissions to detect mouse hover events and perform clicks for users with motor disabilities.',
        
        # App category
        'LSApplicationCategoryType': 'public.app-category.utilities',
        
        # Document types (for settings files)
        'CFBundleDocumentTypes': [{
            'CFBundleTypeName': 'Dwellpy Settings',
            'CFBundleTypeIconFile': 'Dwellpy.icns',
            'LSItemContentTypes': ['public.json'],
            'LSHandlerRank': 'Owner',
            'CFBundleTypeRole': 'Editor'
        }],
        
        # URL schemes (for future deep linking)
        'CFBundleURLTypes': [{
            'CFBundleURLName': 'com.dwellpy.settings',
            'CFBundleURLSchemes': ['dwellpy']
        }]
    }
    
    plist_path = contents_path / 'Info.plist'
    with open(plist_path, 'wb') as f:
        plistlib.dump(info_plist, f)
    
    print("   ✓ Info.plist created")

def create_dmg_background():
    """Create a custom DMG background image."""
    # For now, we'll use a simple approach without custom background
    # This could be enhanced later with a custom background image
    pass

def create_dmg(app_path):
    """Create the DMG installer."""
    print("Creating DMG installer...")
    app_name = app_path.name
    dmg_name = "dwellpy-installer"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create staging directory
        staging_path = Path(temp_dir) / 'dmg_staging'
        staging_path.mkdir()
        
        # Copy app bundle to staging
        staged_app = staging_path / app_name
        shutil.copytree(app_path, staged_app)
        
        # Create Applications symlink
        applications_link = staging_path / 'Applications'
        applications_link.symlink_to('/Applications')
        
        # Create .DS_Store for layout (optional)
        create_ds_store(staging_path)
        
        # Create temporary DMG
        temp_dmg = Path(temp_dir) / f'{dmg_name}-temp.dmg'
        
        print("   Creating temporary DMG...")
        subprocess.run([
            'hdiutil', 'create',
            '-volname', 'Dwellpy Installer',
            '-srcfolder', str(staging_path),
            '-ov', '-format', 'UDRW',
            str(temp_dmg)
        ], check=True)
        
        # Mount the DMG to customize it
        print("   Mounting DMG for customization...")
        mount_result = subprocess.run([
            'hdiutil', 'attach', str(temp_dmg)
        ], capture_output=True, text=True, check=True)
        
        # Extract mount point
        mount_point = None
        for line in mount_result.stdout.split('\n'):
            if '/Volumes/' in line:
                mount_point = line.split('\t')[-1].strip()
                break
        
        if not mount_point:
            raise Exception("Could not determine mount point")
        
        try:
            # Set DMG window properties using AppleScript
            applescript = f'''
            tell application "Finder"
                tell disk "Dwellpy Installer"
                    open
                    set current view of container window to icon view
                    set toolbar visible of container window to false
                    set statusbar visible of container window to false
                    set the bounds of container window to {{100, 100, 600, 400}}
                    set viewOptions to the icon view options of container window
                    set arrangement of viewOptions to not arranged
                    set icon size of viewOptions to 128
                    set position of item "Dwellpy.app" of container window to {{150, 200}}
                    set position of item "Applications" of container window to {{350, 200}}
                    close
                    open
                    update without registering applications
                    delay 2
                end tell
            end tell
            '''
            
            subprocess.run(['osascript', '-e', applescript], check=True)
            print("   ✓ DMG layout configured")
            
        except subprocess.CalledProcessError:
            print("   ! Could not set DMG layout (continuing anyway)")
        
        finally:
            # Unmount
            subprocess.run(['hdiutil', 'detach', mount_point], check=True)
        
        # Create final compressed DMG
        final_dmg = Path('dist') / f'{dmg_name}.dmg'
        print(f"   Creating final DMG: {final_dmg}")
        
        subprocess.run([
            'hdiutil', 'convert', str(temp_dmg),
            '-format', 'UDZO',
            '-imagekey', 'zlib-level=9',
            '-o', str(final_dmg)
        ], check=True)
        
        print(f"   ✓ DMG created: {final_dmg}")
        return final_dmg

def create_ds_store(staging_path):
    """Create .DS_Store for custom folder layout."""
    # This is complex to do programmatically
    # For now, we'll rely on the AppleScript approach
    pass

def main():
    """Main DMG creation process."""
    print("Dwellpy macOS DMG Creator")
    print("=" * 40)
    
    # Check environment
    if not check_macos():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Ensure we're in project root
    if not Path('dwellpy').exists():
        print("ERROR: Run this script from the project root directory")
        sys.exit(1)
    
    # Create app bundle
    app_path = create_app_bundle()
    if not app_path:
        sys.exit(1)
    
    # Create DMG
    try:
        dmg_path = create_dmg(app_path)
        
        print("\n" + "=" * 40)
        print("SUCCESS: DMG created successfully!")
        print(f"\nInstaller: {dmg_path}")
        print(f"App Bundle: {app_path}")
        
        # Get file sizes
        dmg_size = dmg_path.stat().st_size / (1024 * 1024)
        print(f"\nDMG Size: {dmg_size:.1f} MB")
        
        print("\nNext steps:")
        print("1. Test the DMG on a clean macOS system")
        print("2. Consider code signing for distribution")
        print("3. Update your macOS setup guide")
        
    except Exception as e:
        print(f"\nERROR: DMG creation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
