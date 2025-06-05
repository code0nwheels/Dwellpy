#!/usr/bin/env python3
"""
Build script for creating Dwellpy executable with PyInstaller.
Usage: python build.py
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def clean_build():
    """Clean previous build artifacts."""
    print("Cleaning previous build artifacts...")
    
    # Directories to clean
    clean_dirs = ['build', 'dist', '__pycache__']
    
    for dir_name in clean_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed: {dir_name}")
    
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(root, '__pycache__'))

def check_pyinstaller():
    """Check if PyInstaller is installed and accessible."""
    print("Checking PyInstaller...")
    
    # Method 1: Try to run pyinstaller --version directly
    try:
        result = subprocess.run(['pyinstaller', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"    PyInstaller {version}")
            return True
        else:
            print("   ERROR: PyInstaller command failed")
            print(f"   Error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("   ERROR: PyInstaller command not found")
        print("   Install with: pip install pyinstaller")
        return False
    except subprocess.TimeoutExpired:
        print("   ERROR: PyInstaller command timed out")
        return False
    except Exception as e:
        print(f"   ERROR: Error checking PyInstaller: {e}")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking Python dependencies...")
    
    required = ['PyQt6', 'pynput']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"   OK: {package}")
        except ImportError:
            missing.append(package)
            print(f"   MISSING: {package}")
    
    if missing:
        print(f"\nERROR: Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    return True

def is_windows():
    """Check if running on Windows."""
    return platform.system().lower() == 'windows'

def create_spec_file():
    """Create the PyInstaller spec file if it doesn't exist."""
    spec_file = Path('dwellpy.spec')
    
    if not spec_file.exists():
        print("Creating dwellpy.spec file...")
        
        # Platform-specific settings
        if is_windows():
            # Windows UAC flags for mouse control
            platform_settings = '' #"""    uac_admin=True,   # Request admin privileges (for mouse control)
    #uac_uiaccess=True,"""
            icon_line = "    icon='dwellpy/assets/icons/Dwellpy.ico',"
            macos_app_bundle = ""
            #print("   Adding Windows UAC flags for mouse control")
            print("   Using Windows .ico icon")
        elif platform.system().lower() == 'darwin':  # macOS
            # macOS - no UAC, different icon handling, create app bundle
            platform_settings = ""
            
            # Try ICNS first, fall back to PNG if ICNS has issues
            icns_path = Path('dwellpy/assets/icons/Dwellpy.icns')
            png_path = Path('dwellpy/assets/icons/Dwellpy.png')
            
            if icns_path.exists():
                icon_line = "    icon='dwellpy/assets/icons/Dwellpy.icns',"
                bundle_icon = 'dwellpy/assets/icons/Dwellpy.icns'
                icon_file = 'Dwellpy.icns'
                print("   Using .icns icon for macOS")
            elif png_path.exists():
                icon_line = "    icon='dwellpy/assets/icons/Dwellpy.png',"
                bundle_icon = 'dwellpy/assets/icons/Dwellpy.png'
                icon_file = 'Dwellpy.png'
                print("    ICNS not found, using PNG (Pillow will convert)")
            else:
                icon_line = ""
                bundle_icon = None
                icon_file = None
                print("    No icon found, building without icon")
            
            if bundle_icon:
                macos_app_bundle = f"""

# Create macOS app bundle for proper GUI application behavior
app = BUNDLE(
    exe,
    name='Dwellpy.app',
    icon='{bundle_icon}',
    bundle_identifier='com.dwellpy.dwellpy',
    info_plist={{
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.14.0',
        'LSUIElement': True,
        'NSAppleEventsUsageDescription': 'Dwellpy needs accessibility permissions to monitor mouse movements and provide dwell clicking functionality.',
        'NSAccessibilityUsageDescription': 'Dwellpy requires accessibility permissions to detect mouse hover events and perform clicks for users with motor disabilities.',
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'CFBundleDocumentTypes': [
            {{
                'CFBundleTypeName': 'Dwellpy Settings',
                'CFBundleTypeIconFile': '{icon_file}',
                'LSItemContentTypes': ['public.json'],
                'LSHandlerRank': 'Owner',
                'CFBundleTypeRole': 'Editor'
            }}
        ],
        'CFBundleURLTypes': [
            {{
                'CFBundleURLName': 'com.dwellpy.settings',
                'CFBundleURLSchemes': ['dwellpy']
            }}
        ]
    }},
)"""
            else:
                macos_app_bundle = """

# Create macOS app bundle for proper GUI application behavior
app = BUNDLE(
    exe,
    name='Dwellpy.app',
    bundle_identifier='com.dwellpy.dwellpy',
    info_plist={{
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.14.0',
        'LSUIElement': True,
        'NSAppleEventsUsageDescription': 'Dwellpy needs accessibility permissions to monitor mouse movements and provide dwell clicking functionality.',
        'NSAccessibilityUsageDescription': 'Dwellpy requires accessibility permissions to detect mouse hover events and perform clicks for users with motor disabilities.',
        'LSApplicationCategoryType': 'public.app-category.utilities',
    }},
)"""
            
            print("   Configured for macOS (no UAC flags)")
            print("   Creating macOS app bundle")
        else:  # Linux
            # Linux - no UAC, PNG icon
            platform_settings = ""
            icon_line = "    icon='dwellpy/assets/icons/Dwellpy.png',"
            macos_app_bundle = ""
            print("   Configured for Linux (no UAC flags)")
            print("   Using PNG icon for Linux")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Dwellpy - Generated by build.py
Usage: pyinstaller dwellpy.spec
"""

import sys
from pathlib import Path

# Get the project root directory
project_root = Path.cwd()

# Analysis of the main script
a = Analysis(
    # Entry point - use the LAUNCHER script in project root
    ['launcher.py'],
    
    # Paths to search for modules
    pathex=[str(project_root)],
    
    # Binary files to include
    binaries=[],
    
    # Data files to include
    datas=[
        ('dwellpy/assets', 'assets'),
        ('docs/README.md', 'docs'),
    ],
    
    # Hidden imports that PyInstaller might not detect
    hiddenimports=[
        'pynput',
        'pynput.mouse',
        'pynput.keyboard', 
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        # Include all your package modules explicitly
        'dwellpy',
        'dwellpy.main',
        'dwellpy.core',
        'dwellpy.core.dwell_algorithm',
        'dwellpy.core.click_manager', 
        'dwellpy.core.input_manager',
        'dwellpy.ui',
        'dwellpy.ui.ui_manager',
        'dwellpy.ui.window_manager',
        'dwellpy.ui.dialogs',
        'dwellpy.ui.dialogs.settings_dialog',
        'dwellpy.ui.dialogs.exit_dialog',
        'dwellpy.managers',
        'dwellpy.managers.button_manager',
        'dwellpy.managers.settings_manager',
        'dwellpy.managers.exit_manager',
        'dwellpy.config',
        'dwellpy.config.constants',
        'dwellpy.utils', 
        'dwellpy.utils.helpers',
        'dwellpy.__version__',
    ],
    
    # Packages to exclude (reduces size)
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'cv2',
    ],
    
    # Additional options
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Bundle everything
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create the executable - ONE FILE VERSION
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Dwellpy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
{icon_line}
{platform_settings}
){macos_app_bundle}
'''
        
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        print("   Created dwellpy.spec")
    else:
        print("Using existing dwellpy.spec file...")

def check_launcher():
    """Check if launcher.py exists."""
    print("Checking launcher.py...")
    
    launcher_file = Path('launcher.py')
    if launcher_file.exists():
        print("   OK: launcher.py found")
        return True
    else:
        print("   ERROR: launcher.py not found!")
        print("   Create launcher.py in the project root directory")
        return False

def check_icon():
    """Check if the icon file exists."""
    print("Checking icon file...")
    
    if is_windows():
        icon_file = Path('dwellpy/assets/icons/Dwellpy.ico')
        if icon_file.exists():
            print("   OK: Dwellpy.ico found (Windows)")
            return True
        else:
            print("   ERROR: Dwellpy.ico not found!")
            print("   Expected location: dwellpy/assets/icons/Dwellpy.ico")
            return False
    elif platform.system().lower() == 'darwin':  # macOS
        # On macOS, check for .icns file first, then PNG
        icns_file = Path('dwellpy/assets/icons/Dwellpy.icns')
        png_file = Path('dwellpy/assets/icons/Dwellpy.png')
        
        if icns_file.exists():
            print("   OK: Dwellpy.icns found (macOS)")
            return True
        elif png_file.exists():
            print("   WARNING: Dwellpy.icns not found, but Dwellpy.png found")
            print("   INFO: PNG will be used with Pillow conversion")
            return True
        else:
            print("   ERROR: Neither Dwellpy.icns nor Dwellpy.png found!")
            print("   Expected locations:")
            print("      dwellpy/assets/icons/Dwellpy.icns (preferred)")
            print("      dwellpy/assets/icons/Dwellpy.png (fallback)")
            return False
    else:  # Linux
        # On Linux, check if PNG exists
        png_file = Path('dwellpy/assets/icons/Dwellpy.png')
        if png_file.exists():
            print("   OK: Dwellpy.png found (Linux)")
            print("   INFO: Icon will be used for PyInstaller (may work for window icon)")
            return True
        else:
            print("   ERROR: Dwellpy.png not found!")
            print("   Expected location: dwellpy/assets/icons/Dwellpy.png")
            return False
            return False

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable...")
    
    try:
        # Run PyInstaller
        cmd = ['pyinstaller', '--clean', 'dwellpy.spec']
        
        print(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   Build completed successfully!")
            return True
        else:
            print("   ERROR: Build failed!")
            print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"   ERROR: Build failed: {e}")
        return False
    except FileNotFoundError:
        print("   ERROR: PyInstaller command not found")
        return False

def test_executable():
    """Test if the built executable works."""
    print("Testing executable...")
    
    # Check different possible locations
    exe_paths = [
        Path('dist/Dwellpy.exe'),          # Windows one-file
        Path('dist/Dwellpy'),              # Linux one-file
        Path('dist/Dwellpy.app'),          # macOS app bundle
        Path('dist/Dwellpy/Dwellpy.exe'),  # Windows one-dir
        Path('dist/Dwellpy/Dwellpy'),      # Linux/macOS one-dir
    ]
    
    exe_path = None
    for path in exe_paths:
        if path.exists():
            exe_path = path
            break
    
    if exe_path:
        print(f"   OK: Executable found: {exe_path}")
        
        # For macOS app bundle, show the actual executable inside
        if str(exe_path).endswith('.app') and platform.system().lower() == 'darwin':
            actual_exe = exe_path / 'Contents' / 'MacOS' / 'Dwellpy'
            if actual_exe.exists():
                print(f"   App bundle size: {sum(f.stat().st_size for f in exe_path.rglob('*') if f.is_file()) / 1024 / 1024:.1f} MB")
                print(f"   You can test it by running:")
                print(f"      open {exe_path.absolute()}")
                print(f"   or directly:")
                print(f"      {actual_exe.absolute()}")
            else:
                print(f"   ERROR: App bundle structure incomplete!")
                return False
        else:
            print(f"   Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
            print("   You can test it by running:")
            print(f"      {exe_path.absolute()}")
        
        return True
    else:
        print("   ERROR: Executable not found!")
        print("   Expected locations:")
        for path in exe_paths:
            print(f"      {path}")
        return False

def create_installer_info():
    """Create information about the build."""
    print("Creating build information...")
    
    system_info = f"- System: {platform.system()} {platform.release()}"
    python_info = f"- Python: {platform.python_version()}"
    
    # Platform-specific icon info
    icon_info = ""
    if is_windows():
        icon_info = "- Icon embedded in executable (.ico format)"
    else:
        icon_info = "- Icon bundled in assets (PyQt6 window icon)\n- Desktop file automatically created on first launch"
    
    info_content = f"""# Dwellpy Build Information

## Executable Location
- **One-file build**: `dist/Dwellpy.exe` (Windows) or `dist/Dwellpy` (Linux/Mac)
- Ready to distribute - single file, no dependencies needed

## Distribution
1. Simply distribute the single executable file
2. Users run the .exe file directly (Windows) or ./Dwellpy (Linux/Mac)
3. No Python installation required on target machine

## Icon Support
{icon_info}
- Application window will display the Dwellpy icon automatically

## Features Included
- All Python dependencies bundled
- PyQt6 GUI framework  
- pynput mouse control library
- Application configuration and documentation
- Custom icon included{' (Windows)' if is_windows() else ' (in assets)'}

## Build Environment
{system_info}
{python_info}
- PyInstaller: Latest version
- Target: Single executable file

## Troubleshooting
- **Antivirus detection**: Some antivirus may flag PyInstaller executables as suspicious
- **Slow startup**: First run may take a few seconds to extract bundled files
- **Debugging**: Change `console=True` in dwellpy.spec and rebuild to see console output
- **UAC prompts**: {'Windows UAC enabled for mouse control access' if is_windows() else 'No UAC required (non-Windows)'}

## Usage
{'Double-click the executable to run Dwellpy' if is_windows() else 'Run ./Dwellpy from terminal or double-click in file manager. A desktop file will be automatically created for system integration'}. The application will create its settings file in the same directory as the executable.
"""
    
    with open('BUILD_INFO.md', 'w') as f:
        f.write(info_content)
    
    print("   Created BUILD_INFO.md")

def macos_post_build():
    """Handle macOS-specific post-build actions."""
    if platform.system().lower() != 'darwin':
        return True  # Skip on non-macOS

    print("macOS post-build actions...")
    # Always attempt to run the DMG script if the one-file executable exists
    onefile_exe = Path('dist/Dwellpy')
    if onefile_exe.exists():
        print("    One-file executable found; running DMG script"
        dmg_script = Path('utils/create_macos_dmg.py')
        if dmg_script.exists():
            result = subprocess.run([
                sys.executable, str(dmg_script)
            ], cwd=Path.cwd())
            if result.returncode == 0:
                print("    DMG created successfully")
            else:
                print("   ! DMG creation failed (continuing anyway)")
                return True  # Don't fail the build for DMG issues
        else:
            print("   ! DMG script not found")
    else:
        print("   ! No one-file executable found in dist/")
    return True

def windows_post_build():
    """Handle Windows-specific post-build actions."""
    if not is_windows():
        return True  # Skip on non-Windows
    
    print("Windows post-build actions...")
    
    # Check if we have an executable
    exe_path = Path('dist/Dwellpy.exe')
    if exe_path.exists():
        print("    Executable found")
        
        # Automatically create Windows installer
        print("   Creating NSIS installer...")
        installer_script = Path('utils/create_windows_installer.py')
        if installer_script.exists():
            result = subprocess.run([
                sys.executable, str(installer_script)
            ], cwd=Path.cwd())
            
            if result.returncode == 0:
                print("    Windows installer created successfully")
            else:
                print("   ! Installer creation failed (continuing anyway)")
                return True  # Don't fail the build for installer issues
        else:
            print("   ! Windows installer script not found")
    else:
        print("   ! No executable found")
    
    return True

def main():
    """Main build process."""
    print("Building Dwellpy Executable")
    print("=" * 40)
    
    # Show system info
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print()
    
    # Check we're in the right directory
    if not Path('dwellpy').exists():
        print("ERROR: Run this script from the project root directory")
        print("   (where the 'dwellpy' folder is located)")
        sys.exit(1)
    
    # Build process
    steps = [
        ("Clean build artifacts", clean_build),
        ("Check PyInstaller", check_pyinstaller),
        ("Check Python dependencies", check_dependencies),
        ("Check launcher script", check_launcher),
        ("Check icon file", check_icon),
        ("Create spec file", create_spec_file),
        ("Build executable", build_executable),
        ("Test executable", test_executable),
        ("Create build info", create_installer_info),
        ("macOS post-build actions", macos_post_build),
        ("Windows post-build actions", windows_post_build),
    ]
    
    for step_name, step_func in steps:
        print(f"\nStep: {step_name}")
        try:
            result = step_func()
            if result is False:  # Explicit False check
                print(f"ERROR: Step failed: {step_name}")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR in {step_name}: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    print("\n" + "=" * 40)
    print("SUCCESS: Build completed successfully!")
    print(f"\nYour executable is in: dist/")
    print("See BUILD_INFO.md for distribution instructions")
    
    #if is_windows():
        #print("Windows UAC flags included for mouse control access")

if __name__ == "__main__":
    main()
