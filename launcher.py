#!/usr/bin/env python3
"""
Launcher script for Dwellpy - PyInstaller entry point.
Place this file in the project root directory (same level as dwellpy/ folder).
"""

import sys
import os

def setup_path():
    """Setup Python path for both development and PyInstaller environments."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable
        application_path = os.path.dirname(sys.executable)
        # Add the application directory to Python path
        sys.path.insert(0, application_path)
    else:
        # Running in development - add project root to path
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)

def report_startup_error():
    """Show the current exception to the user, then exit.

    The windowed (console=False) build has no stdin/stdout, so input() raises
    "lost sys.stdin" and hides the real error. In that case show a native
    message box instead (not Qt - the failure may be importing Qt itself).
    """
    import traceback
    details = traceback.format_exc()

    if sys.stdin is not None and sys.stderr is not None:
        sys.stderr.write(details)
        try:
            input("Press Enter to exit...")
        except (EOFError, RuntimeError):
            pass
    elif sys.platform == "win32":
        import ctypes
        MB_ICONERROR = 0x10
        ctypes.windll.user32.MessageBoxW(
            None, f"Dwellpy failed to start:\n\n{details}", "Dwellpy", MB_ICONERROR
        )

    sys.exit(1)

def main():
    """Main entry point that sets up path and runs Dwellpy."""
    try:
        # Setup the Python path
        setup_path()

        # Now import and run the main application
        from dwellpy.main import main as dwellpy_main

        # Run the application
        dwellpy_main()

    except Exception:
        report_startup_error()

if __name__ == "__main__":
    main()
