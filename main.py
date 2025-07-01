#!/usr/bin/env python3
"""
Entry point for CodeContextor application.

This is the new modular entry point that replaces the monolithic prototype.py
while preserving all functionality.

Usage:
    python main.py

Author: CodeContextor Team
License: MIT
"""

import sys
import tkinter as tk
from pathlib import Path
import traceback

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point for the application."""
    print("Starting CodeContextor Portable...")
    print("Modular version - Refactored from prototype.py")
    
    try:
        root = tk.Tk()
        
        from ui import FileExplorer
        app = FileExplorer(root)
        
        print("Application initialized successfully!")
        root.mainloop()
        
    except Exception as e:
        print(f"Initialization error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 