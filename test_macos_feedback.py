#!/usr/bin/env python3
"""
Test script for macOS click feedback widget debugging.
Run this to test if the feedback widget can appear on macOS.
"""

import sys
import os

# Add the dwellpy directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dwellpy'))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import time

def test_feedback():
    """Test the click feedback widget on macOS."""
    app = QApplication(sys.argv)
    
    try:
        from ui.click_feedback import ClickFeedbackManager
        
        print("Creating feedback manager...")
        manager = ClickFeedbackManager()
        
        print("Testing feedback at screen center...")
        manager.test_feedback()
        
        # Keep the app running for 3 seconds to see the feedback
        QTimer.singleShot(3000, app.quit)
        
        print("Starting event loop...")
        app.exec()
        
        print("Cleaning up...")
        manager.cleanup()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_feedback() 