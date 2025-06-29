"""
UI styling and theme management for CodeContextor.
Contains all styling configurations and color schemes.
"""

import tkinter as tk
from tkinter import ttk


class StyleManager:
    """Manages UI styling and themes."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the style manager."""
        self.root = root
        self.style = ttk.Style(root)
        
        # shadcn/ui inspired color scheme - completely white background
        self.colors = {
            'bg_primary': "#ffffff",      # White background
            'bg_secondary': "#ffffff",    # Completely white background
            'bg_card': "#ffffff",         # Card background
            'border_color': "#e5e7eb",    # Soft gray border
            'text_primary': "#111827",    # Almost black text
            'text_secondary': "#6b7280",  # Gray text
            'text_muted': "#9ca3af",      # Muted text
            'accent_color': "#3b82f6",    # Blue accent
            'accent_hover': "#2563eb",    # Darker blue on hover
            'success_color': "#10b981",   # Green
            'danger_color': "#ef4444"     # Red
        }
        
        self._configure_theme()
        self._configure_styles()
    
    def _configure_theme(self) -> None:
        """Configure the base theme."""
        # Try to use a modern theme if available
        available_themes = self.style.theme_names()
        if "vista" in available_themes:
            self.style.theme_use("vista")  # Windows modern theme
        elif "aqua" in available_themes:
            self.style.theme_use("aqua")   # macOS theme
        elif "clam" in available_themes:
            self.style.theme_use("clam")   # Cross-platform modern theme
        else:
            self.style.theme_use("default")
        
        # Configure main window background
        self.root.configure(bg=self.colors['bg_primary'])
    
    def _configure_styles(self) -> None:
        """Configure all UI component styles."""
        # Enhanced global style configurations
        self.style.configure(".", 
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_primary'],
                           font=("Inter", 9))
        
        # Frame styles
        self.style.configure("Card.TFrame", 
                           background=self.colors['bg_card'], 
                           relief="flat",
                           borderwidth=1)
        
        self.style.configure("Background.TFrame", 
                           background=self.colors['bg_primary'],
                           relief="flat")
        
        # Button styles
        self.style.configure("ShadcnUI.TButton", 
                           padding=(12, 8), 
                           font=("Inter", 9),
                           borderwidth=1,
                           relief="flat",
                           focuscolor="none")
        self.style.map("ShadcnUI.TButton",
                     background=[("active", "#f8fafc"), ("!active", self.colors['bg_card'])],
                     foreground=[("active", self.colors['text_primary']), ("!active", self.colors['text_primary'])],
                     bordercolor=[("focus", self.colors['accent_color']), ("!focus", self.colors['border_color'])])
                     
        self.style.configure("Primary.TButton", 
                           padding=(12, 8), 
                           font=("Inter", 9, "bold"),
                           borderwidth=0,
                           relief="flat",
                           focuscolor="none")
        self.style.map("Primary.TButton",
                     background=[("active", self.colors['accent_hover']), ("!active", self.colors['accent_color'])],
                     foreground=[("active", "white"), ("!active", "white")])
        
        self.style.configure("Success.TButton", 
                           padding=(12, 8), 
                           font=("Inter", 9, "bold"),
                           borderwidth=0,
                           relief="flat",
                           focuscolor="none")
        self.style.map("Success.TButton",
                     background=[("active", "#059669"), ("!active", self.colors['success_color'])],
                     foreground=[("active", "white"), ("!active", "white")])
        
        self.style.configure("Ghost.TButton", 
                           padding=(12, 8), 
                           font=("Inter", 9),
                           borderwidth=0,
                           relief="flat",
                           focuscolor="none")
        self.style.map("Ghost.TButton",
                     background=[("active", "#f8fafc"), ("!active", "transparent")],
                     foreground=[("active", self.colors['text_primary']), ("!active", self.colors['text_primary'])])
        
        # Label styles
        self.style.configure("ShadcnUI.TLabel", 
                           background=self.colors['bg_card'], 
                           foreground=self.colors['text_primary'],
                           font=("Inter", 10))
        self.style.configure("Heading.TLabel", 
                           font=("Inter", 16, "bold"),
                           foreground=self.colors['text_primary'],
                           background=self.colors['bg_card'])
        self.style.configure("Muted.TLabel", 
                           font=("Inter", 9),
                           foreground=self.colors['text_muted'],
                           background=self.colors['bg_card'])
        
        # Treeview styles
        self.style.configure("ShadcnUI.Treeview",
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_primary'],
                           fieldbackground=self.colors['bg_card'],
                           borderwidth=1,
                           relief="solid",
                           font=("Inter", 9))
        self.style.configure("ShadcnUI.Treeview.Heading",
                           background="#f8fafc",
                           foreground=self.colors['text_secondary'],
                           font=("Inter", 9),
                           borderwidth=0,
                           relief="flat")
        self.style.map("ShadcnUI.Treeview",
                     background=[("selected", "#eff6ff")],
                     foreground=[("selected", self.colors['text_primary'])])
        
        # Entry styles
        self.style.configure("ShadcnUI.TEntry",
                           fieldbackground=self.colors['bg_card'],
                           borderwidth=1,
                           relief="solid",
                           insertcolor=self.colors['text_primary'],
                           font=("Inter", 10))
        self.style.map("ShadcnUI.TEntry",
                     bordercolor=[("focus", self.colors['accent_color']), ("!focus", self.colors['border_color'])])
        
        # Checkbutton styles
        self.style.configure("ShadcnUI.TCheckbutton",
                           background=self.colors['bg_card'],
                           foreground=self.colors['text_primary'],
                           focuscolor="none",
                           font=("Inter", 9))
        
        # Scrollbar styles
        self.style.configure("Vertical.TScrollbar",
                           background="#f8fafc",
                           troughcolor=self.colors['bg_primary'],
                           borderwidth=0,
                           arrowcolor=self.colors['text_secondary'],
                           darkcolor="#f8fafc",
                           lightcolor="#f8fafc")
        
        self.style.configure("Horizontal.TScrollbar",
                           background="#f8fafc",
                           troughcolor=self.colors['bg_primary'],
                           borderwidth=0,
                           arrowcolor=self.colors['text_secondary'],
                           darkcolor="#f8fafc",
                           lightcolor="#f8fafc")
        
        # Combobox styles
        self.style.configure("TCombobox",
                           fieldbackground=self.colors['bg_primary'],
                           background="#f8fafc",
                           borderwidth=1,
                           focuscolor="none",
                           font=("Inter", 9))
        self.style.map("TCombobox",
                     focuscolor=[("focus", self.colors['accent_color'])])
        
        # Checkbutton styles
        self.style.configure("TCheckbutton",
                           background=self.colors['bg_primary'],
                           foreground=self.colors['text_primary'],
                           focuscolor="none",
                           font=("Inter", 9))
        self.style.map("TCheckbutton",
                     background=[("active", "#f8fafc")],
                     foreground=[("active", self.colors['text_primary'])])
    
    def get_text_widget_config(self) -> dict:
        """Get configuration for Text widgets."""
        return {
            'bg': self.colors['bg_card'],
            'fg': self.colors['text_primary'],
            'insertbackground': self.colors['accent_color'],
            'selectbackground': "#dbeafe",
            'selectforeground': self.colors['text_primary'],
            'borderwidth': 0,
            'highlightthickness': 0,
            'font': ("JetBrains Mono", 10),
            'padx': 16,
            'pady': 16
        }
    
    def get_text_tags_config(self) -> dict:
        """Get configuration for Text widget tags."""
        return {
            'header': {
                'foreground': self.colors['accent_color'],
                'font': ("JetBrains Mono", 12, "bold")
            },
            'code_block': {
                'foreground': self.colors['text_primary'],
                'background': "#f9fafb"
            },
            'code_marker': {
                'foreground': self.colors['text_muted'],
                'font': ("JetBrains Mono", 9)
            },
            'filename': {
                'foreground': self.colors['accent_color'],
                'font': ("JetBrains Mono", 11)
            }
        }
    
    def get_status_bar_config(self) -> dict:
        """Get configuration for status bar."""
        return {
            'bg': self.colors['bg_primary'],
            'border_color': self.colors['border_color'],
            'text_primary': self.colors['text_primary'],
            'text_secondary': self.colors['text_secondary']
        } 