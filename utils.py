"""Utility functions for the Dwell Clicker application."""

import tkinter as tk

def center_window(window):
    """
    Center a window on the screen.
    
    Args:
        window: Tkinter window to center
    """
    window.update_idletasks()
    
    # Get window size
    width = window.winfo_width()
    height = window.winfo_height()
    
    # Get screen size
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Calculate position
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Set window position
    window.geometry(f"+{x}+{y}")
