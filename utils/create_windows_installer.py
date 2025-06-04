#!/usr/bin/env python3
"""
Windows NSIS Installer Creator for Dwellpy
Creates a professional Windows installer with shortcuts and uninstaller.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import re

def check_windows():
    """Ensure we're running on Windows."""
    import platform
    if platform.system() != 'Windows':
        print("ERROR: This script must be run on Windows")
        return False
    return True

def check_nsis():
    """Check if NSIS (makensis) is available."""
    print("Checking NSIS installation...")
    
    # Common NSIS installation paths
    nsis_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        "makensis.exe"  # If in PATH
    ]
    
    for nsis_path in nsis_paths:
        try:
            result = subprocess.run([nsis_path, "/VERSION"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"   ✓ NSIS {version} found at: {nsis_path}")
                return nsis_path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    print("   ✗ NSIS not found")
    print("\nTo install NSIS:")
    print("1. Download from: https://nsis.sourceforge.io/Download")
    print("2. Run the installer as administrator")
    print("3. Or install via chocolatey: choco install nsis")
    print("4. Or install via winget: winget install NSIS.NSIS")
    return None

def check_executable():
    """Check if Dwellpy executable exists."""
    print("Checking for Dwellpy executable...")
    
    exe_path = Path('dist/Dwellpy.exe')
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"   ✓ Found: {exe_path} ({size_mb:.1f} MB)")
        return exe_path
    else:
        print("   ✗ Dwellpy.exe not found in dist/")
        print("   Run the build script first: python utils/build_executable.py")
        return None

def get_version():
    """Extract version from various sources."""
    print("Detecting version...")
    
    # Try to get version from pyproject.toml
    pyproject_path = Path('pyproject.toml')
    if pyproject_path.exists():
        try:
            with open(pyproject_path, 'r') as f:
                content = f.read()
                # Look for version = "x.x.x"
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    version = match.group(1)
                    print(f"   ✓ Version from pyproject.toml: {version}")
                    return version
        except Exception as e:
            print(f"   ! Could not read pyproject.toml: {e}")
    
    # Try to get version from setup.py or __init__.py
    init_files = [
        Path('dwellpy/__init__.py'),
        Path('dwellpy/__version__.py'),
        Path('setup.py')
    ]
    
    for file_path in init_files:
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Look for __version__ = "x.x.x" or version = "x.x.x"
                    match = re.search(r'(?:__)?version(?:__)?\s*=\s*["\']([^"\']+)["\']', content)
                    if match:
                        version = match.group(1)
                        print(f"   ✓ Version from {file_path}: {version}")
                        return version
            except Exception as e:
                print(f"   ! Could not read {file_path}: {e}")
    
    # Fallback to asking user or using default
    print("   ! Version not detected automatically")
    version = input("   Enter version (default 1.0.0): ").strip()
    if not version:
        version = "1.0.0"
    
    print(f"   Using version: {version}")
    return version

def prepare_nsis_script(version):
    """Prepare the NSIS script with current version."""
    print("Preparing NSIS script...")
    nsi_template = Path('utils/dwellpy-installer.nsi')
    nsi_working = Path('utils/dwellpy-installer-temp.nsi')
    
    if not nsi_template.exists():
        print("   ✗ NSIS template not found: utils/dwellpy-installer.nsi")
        return None
    
    try:
        # Read template
        with open(nsi_template, 'r', encoding='utf-8') as f:
            content = f.read()
        # Replace version placeholder
        content = content.replace('!define PRODUCT_VERSION "1.0.0"', f'!define PRODUCT_VERSION "{version}"')
        content = content.replace('VIProductVersion "${PRODUCT_VERSION}.0"', f'VIProductVersion "{version}.0"')
        
        # Fix icon paths to use absolute paths from project root
        project_root = Path.cwd()
        icon_path = project_root / 'dwellpy' / 'assets' / 'icons' / 'Dwellpy.ico'
        content = content.replace('!define MUI_ICON "dwellpy\\assets\\icons\\Dwellpy.ico"', f'!define MUI_ICON "{icon_path}"')
        content = content.replace('!define MUI_UNICON "dwellpy\\assets\\icons\\Dwellpy.ico"', f'!define MUI_UNICON "{icon_path}"')
          # Fix executable path to use absolute path
        exe_path = project_root / 'dist' / 'Dwellpy.exe'
        content = content.replace('File "dist\\Dwellpy.exe"', f'File "{exe_path}"')
        
        # Fix output file path to create installer in project root
        content = content.replace('OutFile "dwellpy-installer.exe"', 'OutFile "dwellpy-installer.exe"')
        
        # Write working script
        with open(nsi_working, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✓ NSIS script prepared with version {version}")
        return nsi_working
        
    except Exception as e:
        print(f"   ✗ Error preparing NSIS script: {e}")
        return None

def create_installer(nsis_path, nsi_script, version):
    """Create the Windows installer using NSIS."""
    print("Creating Windows installer...")
    
    try:
        # Run NSIS compiler from project root directory
        cmd = [nsis_path, str(nsi_script)]
        print(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("   ✓ NSIS compilation successful!")
            
            # Find the generated installer (NSIS creates it in utils directory)
            installer_path = Path('utils/dwellpy-installer.exe')
            if installer_path.exists():
                # Rename with version and move to dist directory
                versioned_installer = Path(f'dist/dwellpy-installer-{version}-windows-x64.exe')
                versioned_installer.parent.mkdir(exist_ok=True)
                
                if versioned_installer.exists():
                    versioned_installer.unlink()
                
                shutil.move(str(installer_path), str(versioned_installer))
                
                size_mb = versioned_installer.stat().st_size / (1024 * 1024)
                print(f"   ✓ Installer created: {versioned_installer} ({size_mb:.1f} MB)")
                return versioned_installer
            else:
                print("   ✗ Installer file not found after compilation")
                return None
        else:
            print("   ✗ NSIS compilation failed!")
            print(f"   Error: {result.stderr}")
            if result.stdout:
                print(f"   Output: {result.stdout}")
            return None
            
    except Exception as e:
        print(f"   ✗ Error running NSIS: {e}")
        return None

def cleanup_temp_files():
    """Clean up temporary files."""
    temp_files = [
        Path('utils/dwellpy-installer-temp.nsi'),
    ]
    
    for temp_file in temp_files:
        if temp_file.exists():
            try:
                temp_file.unlink()
            except Exception:
                pass

def main():
    """Main installer creation process."""
    print("Dwellpy Windows Installer Creator")
    print("=" * 40)
    
    try:
        # Check environment
        if not check_windows():
            sys.exit(1)
        
        # Ensure we're in project root
        if not Path('dwellpy').exists():
            print("ERROR: Run this script from the project root directory")
            sys.exit(1)
        
        # Check NSIS
        nsis_path = check_nsis()
        if not nsis_path:
            sys.exit(1)
        
        # Check executable
        exe_path = check_executable()
        if not exe_path:
            sys.exit(1)
        
        # Get version
        version = get_version()
        
        # Prepare NSIS script
        nsi_script = prepare_nsis_script(version)
        if not nsi_script:
            sys.exit(1)
        
        # Create installer
        installer_path = create_installer(nsis_path, nsi_script, version)
        if not installer_path:
            sys.exit(1)
        
        print("\n" + "=" * 40)
        print("SUCCESS: Windows installer created!")
        print(f"\nInstaller: {installer_path}")
        print(f"Executable: {exe_path}")
        
        # Get file sizes
        installer_size = installer_path.stat().st_size / (1024 * 1024)
        exe_size = exe_path.stat().st_size / (1024 * 1024)
        
        print(f"\nInstaller Size: {installer_size:.1f} MB")
        print(f"Executable Size: {exe_size:.1f} MB")
        
        print("\nInstaller features:")
        print("- Professional Windows installer")
        print("- Start Menu shortcuts")
        print("- Desktop shortcut (optional)")
        print("- Quick Launch shortcut (optional)")
        print("- Uninstaller with registry cleanup")
        print("- Version information")
        print("- Upgrade/downgrade detection")
        
        print("\nNext steps:")
        print("1. Test the installer on a clean Windows system")
        print("2. Consider code signing for distribution")
        print("3. Update your Windows setup guide")
        
    except KeyboardInterrupt:
        print("\n\nInstaller creation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Installer creation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cleanup_temp_files()

if __name__ == "__main__":
    main()
