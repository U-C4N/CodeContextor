"""
Code Contextor Portable - Main Entry Point

A specialized Python desktop application designed to prepare and send source code to LLM chats.
It helps developers scan project directories, calculate token usage, and format entire codebases
for AI analysis and modifications.

This is the modularized version with professional structure:
- core/ - Core functionality and utilities
- ui/ - User interface components
- workers/ - Threading and background processing
- localization/ - Multi-language support
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path

from ui import MainWindow


def main() -> None:
    """Main function to run the Code Contextor Portable application with enhanced modern design."""
    root: tk.Tk = tk.Tk()
    
    # Set window properties for modern appearance
    root.attributes("-alpha", 0.98)  # Slight transparency for modern look
    
    # Set window icon and additional properties
    try:
        # Try to set an icon if available
        root.iconbitmap(default="app.ico")
    except:
        pass  # Icon file not found, continue without it
    
    # Center the window on screen
    root.update_idletasks()
    width = 1200
    height = 800
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Start the application
    app = MainWindow(root)
    
    # Configure window close event
    def on_closing():
        """Handle application shutdown gracefully."""
        if app.thread_manager.is_task_running():
            app.thread_manager.cancel_current_task()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the main event loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        on_closing()


if __name__ == "__main__":
    main() 