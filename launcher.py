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

def main():
    """Main entry point that sets up path and runs Dwellpy."""
    try:
        # Setup the Python path
        setup_path()
        
        # Now import and run the main application
        from dwellpy.main import main as dwellpy_main
        
        # Run the application
        dwellpy_main()
        
    except ImportError as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
