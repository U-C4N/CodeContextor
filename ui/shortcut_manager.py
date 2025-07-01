"""
Keyboard shortcut manager for CodeContextor.

This module provides centralized keyboard shortcut handling for the application,
including Ctrl+A (select all), Ctrl+C (copy), and Ctrl+S (save).
"""

import tkinter as tk
from typing import Optional, Callable


class ShortcutManager:
    """Manages keyboard shortcuts for the CodeContextor application."""
    
    def __init__(self, main_window) -> None:
        """
        Initialize the shortcut manager.
        
        Args:
            main_window: The main FileExplorer window instance
        """
        self.main_window = main_window
        self.master = main_window.master
        self.setup_shortcuts()
    
    def setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts for the application."""
        # Select All (Ctrl+A)
        self.master.bind_all('<Control-a>', self.select_all)
        self.master.bind_all('<Control-A>', self.select_all)  # Caps lock variant
        
        # Copy (Ctrl+C)
        self.master.bind_all('<Control-c>', self.copy_selection)
        self.master.bind_all('<Control-C>', self.copy_selection)  # Caps lock variant
        
        # Save (Ctrl+S)
        self.master.bind_all('<Control-s>', self.save_file)
        self.master.bind_all('<Control-S>', self.save_file)  # Caps lock variant
        
        # Refresh (F5)
        self.master.bind_all('<F5>', self.refresh)
        
        # Toggle theme (Ctrl+T)
        self.master.bind_all('<Control-t>', self.toggle_theme)
        self.master.bind_all('<Control-T>', self.toggle_theme)
    
    def select_all(self, event: Optional[tk.Event] = None) -> str:
        """
        Select all content in the currently focused widget.
        
        Args:
            event: The keyboard event (optional)
            
        Returns:
            'break' to prevent default behavior
        """
        try:
            widget = self.master.focus_get()
            
            if widget is None:
                # If no widget has focus, select all in the file tree
                self.main_window.select_all()
                return 'break'
            
            # Handle custom select_all method
            if hasattr(widget, 'select_all') and callable(getattr(widget, 'select_all')):
                widget.select_all()
            # Handle Text widget
            elif isinstance(widget, tk.Text):
                widget.tag_add(tk.SEL, "1.0", tk.END)
                widget.mark_set(tk.INSERT, "1.0")
                widget.see(tk.INSERT)
            # Handle Entry widget
            elif isinstance(widget, tk.Entry):
                widget.select_range(0, tk.END)
                widget.icursor(tk.END)
            # Handle Treeview (our file tree)
            elif hasattr(widget, 'get_children'):  # Treeview-like widget
                self.main_window.select_all()
            else:
                # Fallback: try to select all in the main text area
                if hasattr(self.main_window, 'text'):
                    self.main_window.text.tag_add(tk.SEL, "1.0", tk.END)
                    self.main_window.text.mark_set(tk.INSERT, "1.0")
                    self.main_window.text.see(tk.INSERT)
                    
        except Exception as e:
            print(f"Error in select_all shortcut: {e}")
        
        return 'break'  # Prevent default behavior
    
    def copy_selection(self, event: Optional[tk.Event] = None) -> str:
        """
        Copy selected text to clipboard.
        
        Args:
            event: The keyboard event (optional)
            
        Returns:
            'break' to prevent default behavior
        """
        try:
            widget = self.master.focus_get()
            
            if widget is None:
                # If no widget has focus, try to copy from main text area
                if hasattr(self.main_window, 'copy_to_clipboard'):
                    self.main_window.copy_to_clipboard()
                return 'break'
            
            # Handle Text and Entry widgets
            if isinstance(widget, (tk.Text, tk.Entry)):
                try:
                    selected_text = widget.selection_get()
                    self.master.clipboard_clear()
                    self.master.clipboard_append(selected_text)
                    
                    # Show brief status message
                    if hasattr(self.main_window, 'status_label'):
                        original_text = self.main_window.status_label.cget('text')
                        self.main_window.status_label.config(text="✓ Copied to clipboard")
                        self.master.after(2000, lambda: self.main_window.status_label.config(text=original_text))
                        
                except tk.TclError:
                    # No selection, try to copy all content
                    if isinstance(widget, tk.Text):
                        all_text = widget.get("1.0", tk.END).rstrip('\n')
                    else:
                        all_text = widget.get()
                    
                    if all_text:
                        self.master.clipboard_clear()
                        self.master.clipboard_append(all_text)
                        
                        if hasattr(self.main_window, 'status_label'):
                            original_text = self.main_window.status_label.cget('text')
                            self.main_window.status_label.config(text="✓ Copied all content to clipboard")
                            self.master.after(2000, lambda: self.main_window.status_label.config(text=original_text))
            else:
                # Fallback: use main window's copy method
                if hasattr(self.main_window, 'copy_to_clipboard'):
                    self.main_window.copy_to_clipboard()
                    
        except Exception as e:
            print(f"Error in copy_selection shortcut: {e}")
        
        return 'break'  # Prevent default behavior
    
    def save_file(self, event: Optional[tk.Event] = None) -> str:
        """
        Save the current file or content.
        
        Args:
            event: The keyboard event (optional)
            
        Returns:
            'break' to prevent default behavior
        """
        try:
            if hasattr(self.main_window, 'save_to_file'):
                self.main_window.save_to_file()
                
                # Show brief status message
                if hasattr(self.main_window, 'status_label'):
                    original_text = self.main_window.status_label.cget('text')
                    self.main_window.status_label.config(text="✓ File saved successfully")
                    self.master.after(2000, lambda: self.main_window.status_label.config(text=original_text))
                    
        except Exception as e:
            print(f"Error in save_file shortcut: {e}")
            if hasattr(self.main_window, 'status_label'):
                original_text = self.main_window.status_label.cget('text')
                self.main_window.status_label.config(text="✗ Error saving file")
                self.master.after(3000, lambda: self.main_window.status_label.config(text=original_text))
        
        return 'break'  # Prevent default behavior
    
    def refresh(self, event: Optional[tk.Event] = None) -> str:
        """
        Refresh the file listing.
        
        Args:
            event: The keyboard event (optional)
            
        Returns:
            'break' to prevent default behavior
        """
        try:
            if hasattr(self.main_window, 'populate_listbox'):
                self.main_window.populate_listbox()
                
                # Show brief status message
                if hasattr(self.main_window, 'status_label'):
                    original_text = self.main_window.status_label.cget('text')
                    self.main_window.status_label.config(text="✓ File list refreshed")
                    self.master.after(1500, lambda: self.main_window.status_label.config(text=original_text))
                    
        except Exception as e:
            print(f"Error in refresh shortcut: {e}")
        
        return 'break'  # Prevent default behavior
    
    def toggle_theme(self, event: Optional[tk.Event] = None) -> str:
        """
        Toggle between light and dark themes.
        
        Args:
            event: The keyboard event (optional)
            
        Returns:
            'break' to prevent default behavior
        """
        try:
            if hasattr(self.main_window, 'toggle_theme'):
                self.main_window.toggle_theme()
                
        except Exception as e:
            print(f"Error in toggle_theme shortcut: {e}")
        
        return 'break'  # Prevent default behavior
    
    def get_shortcuts_help(self) -> str:
        """
        Get a formatted string describing available keyboard shortcuts.
        
        Returns:
            Formatted help text for shortcuts
        """
        shortcuts = [
            "Keyboard Shortcuts:",
            "Ctrl+A - Select All",
            "Ctrl+C - Copy",
            "Ctrl+S - Save File",
            "Ctrl+T - Toggle Theme",
            "F5 - Refresh File List"
        ]
        return "\n".join(shortcuts) 