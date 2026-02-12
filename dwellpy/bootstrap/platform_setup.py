#!/usr/bin/env python3
"""Platform-specific setup and initialization for Dwellpy."""

import sys
import os
import signal
from pathlib import Path
from typing import Optional

from ..utils.helpers import get_asset_path


def setup_dpi_awareness() -> None:
    """Set DPI awareness as early as possible for Windows multi-monitor support."""
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes
            
            # Set DPI awareness before any Qt initialization
            try:
                # Try the newer SetProcessDpiAwarenessContext first (Windows 10 1703+)
                ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
            except:
                try:
                    # Fallback to SetProcessDpiAwareness (Windows 8.1+)
                    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
                except:
                    try:
                        # Final fallback to SetProcessDPIAware (Windows Vista+)
                        ctypes.windll.user32.SetProcessDPIAware()
                    except:
                        pass  # DPI awareness not available
        except ImportError:
            pass  # ctypes not available


def create_linux_desktop_file() -> None:
    """Create a .desktop file for Linux desktop integration."""
    # Only create on Linux
    if sys.platform != "linux":
        return
    
    try:
        import shutil
        
        # Get paths
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_file = desktop_dir / "dwellpy.desktop"
        
        # Icon directory and file
        icon_dir = Path.home() / ".local" / "share" / "icons"
        permanent_icon_path = icon_dir / "dwellpy.png"
        
        # Create directories if they don't exist
        desktop_dir.mkdir(parents=True, exist_ok=True)
        icon_dir.mkdir(parents=True, exist_ok=True)
        
        # Get executable path and copy icon to permanent location
        if getattr(sys, 'frozen', False):
            # PyInstaller executable - icon is bundled, extract it
            exec_path = os.path.abspath(sys.executable)
            
            # Get icon from bundled assets
            bundled_icon_path = get_asset_path("Dwellpy.png")
            if os.path.exists(bundled_icon_path):
                # Copy icon to permanent location
                shutil.copy2(bundled_icon_path, permanent_icon_path)
            
            icon_path = str(permanent_icon_path)
        else:
            # Development mode
            exec_path = f"python {os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main.py'))}"
            icon_path = os.path.abspath(get_asset_path("Dwellpy.png"))
        
        # Desktop file content
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Dwellpy
Comment=Mouse dwell clicking application for accessibility
Exec={exec_path}
Icon={icon_path}
Terminal=false
Categories=Utility;Accessibility;
Keywords=mouse;dwell;accessibility;click;assistive;
StartupNotify=true
"""
        
        # Write the desktop file
        with open(desktop_file, 'w') as f:
            f.write(desktop_content)
        
        # Make it executable
        os.chmod(desktop_file, 0o755)
        
        print(f"Created desktop file: {desktop_file}")
        if getattr(sys, 'frozen', False):
            print(f"Extracted icon to: {permanent_icon_path}")
        
    except Exception as e:
        # Don't let desktop file creation errors prevent app startup
        print(f"Warning: Could not create desktop file: {e}")


def setup_signal_handlers(cleanup_callback) -> None:
    """Setup signal handlers for clean shutdown."""
    def signal_handler(signum, frame):
        try:
            cleanup_callback()
        except:
            os._exit(1)
    
    # Handle common termination signals
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination request
    
    # Windows-specific signal handling
    if sys.platform == "win32":
        try:
            signal.signal(signal.SIGBREAK, signal_handler)  # Ctrl+Break on Windows
        except AttributeError:
            pass  # SIGBREAK not available on all Windows versions 