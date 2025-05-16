"""Exit functionality for the Dwell Clicker application."""

import tkinter as tk
from utils import center_window

class ExitManager:
    """Manages exit confirmation dialog and exit functionality."""
    
    def __init__(self, root, settings_manager, button_manager):
        self.root = root
        self.settings_manager = settings_manager
        self.button_manager = button_manager
        self.confirm_dialog = None  # Track confirmation dialog
        self.move_tracking_thread = None  # Reference to move tracking thread if needed
        self.move_thread_running_flag = False  # Flag for thread state
        
        # Register button commands
        self.button_manager.register_command("EXIT", self.show_exit_dialog)
        self.button_manager.register_command("EXIT_YES", self.confirm_exit)
        self.button_manager.register_command("EXIT_NO", self.cancel_exit)
    
    def set_move_thread(self, thread_ref, thread_running_flag):
        """Set reference to move thread for cleanup on exit."""
        self.move_tracking_thread = thread_ref
        self.move_thread_running_flag = thread_running_flag
    
    def show_exit_dialog(self):
        """Show exit confirmation dialog."""
        # Check if dialog is already open
        if self.confirm_dialog is not None and self.confirm_dialog.winfo_exists():
            self.confirm_dialog.lift()
            return
        
        # Pre-define window size
        width = 300
        height = 150
        
        # Create confirmation dialog
        self.confirm_dialog = tk.Toplevel(self.root)
        self.confirm_dialog.geometry(f"{width}x{height}")
        
        # Configure window
        self.confirm_dialog.title("Exit Confirmation")
        self.confirm_dialog.resizable(False, False)
        self.confirm_dialog.transient(self.root)
        self.confirm_dialog.attributes('-topmost', True)
        self.confirm_dialog.configure(background='#f0f0f0')  # Light gray background
        
        # Dialog content
        frame = tk.Frame(self.confirm_dialog, padx=30, pady=20, bg='#f0f0f0')
        frame.pack(fill=tk.BOTH, expand=True)
        
        message = tk.Label(frame, 
                          text="Are you sure you want to exit?", 
                          font=("Segoe UI", 12),
                          bg='#f0f0f0',
                          fg='#333333')
        message.pack(pady=15)
        
        buttons_frame = tk.Frame(frame, bg='#f0f0f0')
        buttons_frame.pack(pady=10)
        
        # Mark EXIT_YES and EXIT_NO as physical-click-only buttons
        self.button_manager.mark_as_physical_click_only(["EXIT_YES", "EXIT_NO"])
        
        # Yes button - red styling like "EXIT"
        yes_button = tk.Button(
            buttons_frame, 
            text="Yes", 
            width=8,
            command=self.confirm_exit,
            font=("Segoe UI", 10),
            bg='#e74c3c',  # Red
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        yes_button.pack(side=tk.LEFT, padx=10)
        
        # No button - blue styling like default mode
        no_button = tk.Button(
            buttons_frame, 
            text="No", 
            width=8,
            command=self.cancel_exit,
            font=("Segoe UI", 10),
            bg='#3498db',  # Blue
            fg='white',
            activebackground='#2980b9',
            activeforeground='white',
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor="hand2"
        )
        no_button.pack(side=tk.LEFT, padx=10)
        
        # Make buttons dwell-clickable
        yes_button.button_id = "EXIT_YES"
        no_button.button_id = "EXIT_NO"
        
        def on_yes_hover(event):
            self.button_manager.set_hover("EXIT_YES")
            yes_button.config(bg='#c0392b')  # Darker red
            
        def on_yes_leave(event):
            self.button_manager.clear_hover("EXIT_YES")
            yes_button.config(bg='#e74c3c')  # Back to normal red
            
        def on_no_hover(event):
            self.button_manager.set_hover("EXIT_NO")
            no_button.config(bg='#2980b9')  # Darker blue
            
        def on_no_leave(event):
            self.button_manager.clear_hover("EXIT_NO")
            no_button.config(bg='#3498db')  # Back to normal blue
        
        yes_button.bind('<Enter>', on_yes_hover)
        yes_button.bind('<Leave>', on_yes_leave)
        no_button.bind('<Enter>', on_no_hover)
        no_button.bind('<Leave>', on_no_leave)
        
        # Center the window on screen
        self.confirm_dialog.update_idletasks()
        center_window(self.confirm_dialog)
        
        # Now make the window visible
        self.confirm_dialog.deiconify()
    
    def confirm_exit(self):
        """Exit the application after confirmation."""
        # Stop move thread if running
        if hasattr(self, 'move_thread_running_flag') and self.move_thread_running_flag:
            self.move_thread_running_flag = False
            if self.move_tracking_thread:
                self.move_tracking_thread.join(timeout=1.0)
        
        # Close confirmation dialog
        if self.confirm_dialog:
            self.confirm_dialog.destroy()
        
        # Save settings before exiting
        self.settings_manager.save_settings()
        print("Exiting application")
        self.root.quit()
    
    def cancel_exit(self):
        """Cancel exit and close confirmation dialog."""
        if self.confirm_dialog:
            self.confirm_dialog.destroy()
            self.confirm_dialog = None
        print("Exit cancelled")
