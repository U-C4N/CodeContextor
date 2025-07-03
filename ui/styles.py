import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
from .theme_manager import ThemeManager

class UIStyles:
    """Manages UI styling and theming for the application with dynamic theme support."""
    
    # Typography
    FONTS = {
        'default': ('Inter', 10),
        'heading': ('Inter', 12, 'bold'),
        'code': ('JetBrains Mono', 9),
        'small': ('Inter', 8),
        'button': ('Inter', 9),
    }
    
    # Spacing and layout
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
    }
    
    def __init__(self, theme_manager: Optional[ThemeManager] = None):
        """
        Initialize styling system with theme support.
        
        Args:
            theme_manager: ThemeManager instance for dynamic theming
        """
        self.theme_manager = theme_manager or ThemeManager()
        self.style = None
        self._setup_ttk_styles()
    
    def get_colors(self) -> Dict[str, str]:
        """Get current theme colors."""
        return self.theme_manager.get_theme_colors()
    
    def get_color(self, color_name: str) -> str:
        """Get a specific color from current theme."""
        return self.theme_manager.get_color(color_name)
    
    def _setup_ttk_styles(self) -> None:
        """Setup TTK styles that will be updated when theme changes."""
        self.style = ttk.Style()
        self.apply_current_theme()
    
    def apply_current_theme(self) -> None:
        """Apply the current theme to all TTK styles."""
        if not self.style:
            return
            
        colors = self.get_colors()
        
        # Configure Treeview (file browser)
        self.style.configure("Modern.Treeview",
                            background=colors['treeview_bg'],
                            foreground=colors['text_primary'],
                            borderwidth=0,
                            relief='flat',
                            fieldbackground=colors['treeview_bg'])
        
        self.style.configure("Modern.Treeview.Heading",
                            background=colors['button_bg'],
                            foreground=colors['text_primary'],
                            relief='flat',
                            borderwidth=0)
        
        self.style.map("Modern.Treeview",
                      background=[('selected', colors['treeview_select']),
                                ('focus', colors['treeview_bg']),
                                ('!focus', colors['treeview_bg'])],
                      foreground=[('selected', 'white'),
                                ('focus', colors['text_primary']),
                                ('!focus', colors['text_primary'])])
        
        # Configure Buttons
        self.style.configure("Modern.TButton",
                            background=colors['button_bg'],
                            foreground=colors['text_primary'],
                            borderwidth=0,
                            relief='flat',
                            padding=(self.SPACING['sm'], self.SPACING['xs']),
                            font=self.FONTS['button'])
        
        self.style.map("Modern.TButton",
                      background=[('active', colors['button_hover']),
                                ('pressed', colors['accent']),
                                ('focus', colors['button_hover']),
                                ('!focus', colors['button_bg'])],
                      foreground=[('pressed', 'white'),
                                ('active', colors['text_primary']),
                                ('focus', colors['text_primary']),
                                ('!focus', colors['text_primary'])])
        
        # Configure Entry widgets
        self.style.configure("Modern.TEntry",
                            fieldbackground=colors['entry_bg'],
                            borderwidth=0,
                            relief='flat',
                            padding=self.SPACING['xs'],
                            foreground=colors['text_primary'])
        
        self.style.map("Modern.TEntry",
                      fieldbackground=[('focus', colors['entry_focus']),
                                     ('!focus', colors['entry_bg'])],
                      foreground=[('focus', colors['text_primary']),
                                ('!focus', colors['text_primary'])])
        
        # Configure Combobox
        self.style.configure("Modern.TCombobox",
                            fieldbackground=colors['entry_bg'],
                            borderwidth=0,
                            relief='flat',
                            arrowcolor=colors['text_secondary'],
                            foreground=colors['text_primary'])
        
        self.style.map("Modern.TCombobox",
                      fieldbackground=[('readonly', colors['entry_bg']),
                                     ('disabled', colors['background_secondary'])],
                      foreground=[('readonly', colors['text_primary']),
                                ('disabled', colors['text_muted'])])
        
        # Configure Checkbutton
        self.style.configure("Modern.TCheckbutton",
                            background=colors['background_card'],
                            foreground=colors['text_primary'],
                            focuscolor=colors['accent'],
                            font=self.FONTS['default'])
        
        self.style.map("Modern.TCheckbutton",
                      background=[('active', colors['background_card']),
                                ('!active', colors['background_card'])],
                      foreground=[('active', colors['text_primary']),
                                ('!active', colors['text_primary'])])
        
        # Configure Progressbar
        self.style.configure("Modern.Horizontal.TProgressbar",
                            background=colors['accent'],
                            borderwidth=0,
                            lightcolor=colors['accent'],
                            darkcolor=colors['accent'],
                            troughcolor=colors['background_secondary'])
        
        # Configure Labels
        self.style.configure("Modern.TLabel",
                            background=colors['background_primary'],
                            foreground=colors['text_primary'],
                            font=self.FONTS['default'])
        
        self.style.configure("Heading.TLabel",
                            background=colors['background_primary'],
                            foreground=colors['text_primary'],
                            font=self.FONTS['heading'])
        
        self.style.configure("Muted.TLabel",
                            background=colors['background_primary'],
                            foreground=colors['text_muted'],
                            font=self.FONTS['small'])
        
        # Configure PanedWindow
        self.style.configure("TPanedwindow",
                            background=colors['background_primary'])
        
        # Configure Notebook (if used)
        self.style.configure("TNotebook",
                            background=colors['background_primary'],
                            borderwidth=0)
        
        self.style.configure("TNotebook.Tab",
                            background=colors['button_bg'],
                            foreground=colors['text_primary'],
                            padding=(12, 8))
        
        self.style.map("TNotebook.Tab",
                      background=[('selected', colors['accent']),
                                ('active', colors['button_hover']),
                                ('!active', colors['button_bg'])],
                      foreground=[('selected', 'white'),
                                ('active', colors['text_primary']),
                                ('!active', colors['text_primary'])])
        

    
    def configure_root_window(self, root: tk.Tk) -> None:
        """Configure the root window with current theme."""
        colors = self.get_colors()
        root.configure(bg=colors['background_primary'])
        self.apply_current_theme()
    
    def create_card_frame(self, parent: tk.Widget, **kwargs) -> tk.Frame:
        """Create a card-style frame with current theme styling."""
        colors = self.get_colors()
        default_kwargs = {
            'bg': colors['background_card'],
            'relief': 'flat',
            'bd': 0,
            'padx': self.SPACING['md'],
            'pady': self.SPACING['md'],
        }
        default_kwargs.update(kwargs)
        
        return tk.Frame(parent, **default_kwargs)
    
    def create_text_widget(self, parent: tk.Widget, **kwargs) -> tk.Text:
        """Create a text widget with current theme styling."""
        colors = self.get_colors()
        default_kwargs = {
            'bg': colors['background_card'],
            'fg': colors['text_primary'],
            'insertbackground': colors['accent'],
            'selectbackground': colors['accent'],
            'selectforeground': 'white',
            'relief': 'solid',
            'bd': 1,
            'highlightcolor': colors['border'],
            'highlightbackground': colors['border'],
            'highlightthickness': 1,
            'font': self.FONTS['code'],
            'wrap': tk.WORD,
            'undo': True,
            'maxundo': 20,
        }
        default_kwargs.update(kwargs)
        
        return tk.Text(parent, **default_kwargs)
    
    def create_scrollbar(self, parent: tk.Widget, **kwargs) -> tk.Scrollbar:
        """Create a scrollbar with current theme styling."""
        colors = self.get_colors()
        default_kwargs = {
            'bg': colors['scrollbar_thumb'],
            'troughcolor': colors['scrollbar_bg'],
            'borderwidth': 0,
            'highlightthickness': 0,
        }
        default_kwargs.update(kwargs)
        
        return tk.Scrollbar(parent, **default_kwargs)
    
    def get_syntax_highlighting_colors(self) -> Dict[str, str]:
        """Get colors for syntax highlighting based on current theme."""
        is_dark = self.theme_manager.is_dark_theme()
        
        if is_dark:
            return {
                'keyword': '#c792ea',      # Purple
                'string': '#c3e88d',       # Green  
                'comment': '#546e7a',      # Gray
                'number': '#f78c6c',       # Orange
                'operator': '#89ddff',     # Cyan
                'function': '#82b1ff',     # Blue
                'class': '#ffcb6b',        # Yellow
                'variable': '#eeffff',     # White
            }
        else:
            return {
                'keyword': '#8b5cf6',      # Purple
                'string': '#10b981',       # Green  
                'comment': '#6b7280',      # Gray
                'number': '#f59e0b',       # Orange
                'operator': '#ef4444',     # Red
                'function': '#3b82f6',     # Blue
                'class': '#8b5cf6',        # Purple
                'variable': '#111827',     # Default text
            }
    
    def apply_hover_effect(self, widget: tk.Widget, hover_color: str = None) -> None:
        """Apply hover effect to a widget with current theme colors."""
        if hover_color is None:
            hover_color = self.get_color('button_hover')
        
        original_color = widget.cget('bg')
        
        def on_enter(event):
            widget.configure(bg=hover_color)
        
        def on_leave(event):
            widget.configure(bg=original_color)
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def update_widget_theme(self, widget: tk.Widget, widget_type: str = 'default') -> None:
        """
        Update a widget's colors to match current theme.
        
        Args:
            widget: Widget to update
            widget_type: Type of widget ('frame', 'button', 'text', etc.)
        """
        colors = self.get_colors()
        
        try:
            if widget_type == 'frame':
                widget.configure(bg=colors['background_card'])
            elif widget_type == 'button':
                widget.configure(
                    bg=colors['button_bg'],
                    fg=colors['text_primary'],
                    activebackground=colors['button_hover']
                )
            elif widget_type == 'text':
                widget.configure(
                    bg=colors['background_card'],
                    fg=colors['text_primary'],
                    insertbackground=colors['accent']
                )
            elif widget_type == 'label':
                widget.configure(
                    bg=colors['background_primary'],
                    fg=colors['text_primary']
                )
            else:  # default
                if hasattr(widget, 'configure'):
                    widget.configure(bg=colors['background_primary'])
        except tk.TclError:
            # Some widgets may not support certain color options
            pass
    
    def on_theme_change(self, old_theme: str, new_theme: str) -> None:
        """
        Callback for when theme changes.
        
        Args:
            old_theme: Previous theme name
            new_theme: New theme name
        """
        self.apply_current_theme()
    
    # Static methods for backward compatibility
    @staticmethod
    def create_card_frame_static(parent: tk.Widget, theme_manager: ThemeManager, **kwargs) -> tk.Frame:
        """Static method to create card frame with theme support."""
        styles = UIStyles(theme_manager)
        return styles.create_card_frame(parent, **kwargs)
    
    @staticmethod  
    def create_text_widget_static(parent: tk.Widget, theme_manager: ThemeManager, **kwargs) -> tk.Text:
        """Static method to create text widget with theme support."""
        styles = UIStyles(theme_manager)
        return styles.create_text_widget(parent, **kwargs)
    
    @staticmethod
    def create_scrollbar_static(parent: tk.Widget, theme_manager: ThemeManager, **kwargs) -> tk.Scrollbar:
        """Static method to create scrollbar with theme support."""
        styles = UIStyles(theme_manager)
        return styles.create_scrollbar(parent, **kwargs) 