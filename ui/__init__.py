"""
UI module for CodeContextor.

This module contains user interface components including the main window,
styling system, theme management, and UI event handlers for the modern shadcn/ui inspired design.
"""

from .main_window import FileExplorer
from .styles import UIStyles
from .theme_manager import ThemeManager

__all__ = ['FileExplorer', 'UIStyles', 'ThemeManager']

 