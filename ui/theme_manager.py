import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ThemeManager:
    """Manages application themes and persistence."""
    
    THEMES = {
        "light": {
            "background_primary": "#ffffff",
            "background_secondary": "#f8f9fa",
            "background_card": "#ffffff",
            "border": "#e9ecef",
            "border_hover": "#ced4da",
            "text_primary": "#212529",
            "text_secondary": "#6c757d",
            "text_muted": "#868e96",
            "accent": "#007bff",
            "accent_hover": "#0056b3",
            "success": "#28a745",
            "warning": "#ffc107",
            "danger": "#dc3545",
            "button_bg": "#ffffff",
            "button_hover": "#f8f9fa",
            "entry_bg": "#ffffff",
            "entry_focus": "#fff3cd",
            "treeview_bg": "#ffffff",
            "treeview_select": "#007bff",
            "scrollbar_bg": "#f8f9fa",
            "scrollbar_thumb": "#ced4da"
        },
        "dark": {
            "background_primary": "#0a0a0a",
            "background_secondary": "#1a1a1a",
            "background_card": "#111111",
            "border": "#333333",
            "border_hover": "#444444",
            "text_primary": "#ffffff",
            "text_secondary": "#adb5bd",
            "text_muted": "#6c757d",
            "accent": "#3a86ff",
            "accent_hover": "#2563eb",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "button_bg": "#1a1a1a",
            "button_hover": "#2a2a2a",
            "entry_bg": "#1a1a1a",
            "entry_focus": "#2a2a2a",
            "treeview_bg": "#1a1a1a",
            "treeview_select": "#3a86ff",
            "scrollbar_bg": "#1a1a1a",
            "scrollbar_thumb": "#333333"
        }
    }
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the theme manager.
        
        Args:
            config_dir: Directory to store theme configuration. Defaults to user's home/.codecontextor
        """
        self.current_theme: str = "light"
        self.config_dir: Path = config_dir or Path.home() / ".codecontextor"
        self.config_file: Path = self.config_dir / "theme_settings.json"
        self._theme_change_callbacks = []
        self._load_theme_preference()
    
    def _load_theme_preference(self) -> None:
        """Load saved theme preference from disk."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    theme = settings.get("theme", "light")
                    if theme in self.THEMES:
                        self.current_theme = theme
                    else:
                        self.current_theme = "light"
            except (json.JSONDecodeError, IOError, KeyError) as e:
                print(f"Error loading theme settings: {e}")
                self.current_theme = "light"
    
    def _save_theme_preference(self) -> None:
        """Save current theme preference to disk."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            settings = {"theme": self.current_theme}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except (IOError, OSError) as e:
            print(f"Error saving theme settings: {e}")
    
    def get_current_theme(self) -> str:
        """
        Return the current theme name.
        
        Returns:
            Current theme name ('light' or 'dark')
        """
        return self.current_theme
    
    def get_theme_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """
        Return the color palette for the specified theme.
        
        Args:
            theme_name: Name of the theme. If None, uses current theme.
            
        Returns:
            Dictionary containing color values for the theme
        """
        theme = theme_name or self.current_theme
        return self.THEMES.get(theme, self.THEMES["light"]).copy()
    
    def get_color(self, color_name: str, theme_name: Optional[str] = None) -> str:
        """
        Get a specific color from the theme.
        
        Args:
            color_name: Name of the color to retrieve
            theme_name: Theme to get color from. If None, uses current theme.
            
        Returns:
            Color value as hex string
        """
        colors = self.get_theme_colors(theme_name)
        return colors.get(color_name, "#000000")
    
    def toggle_theme(self) -> str:
        """
        Switch between light and dark themes.
        
        Returns:
            New theme name after toggle
        """
        old_theme = self.current_theme
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self._save_theme_preference()
        
        # Notify all registered callbacks
        self._notify_theme_change(old_theme, self.current_theme)
        
        return self.current_theme
    
    def set_theme(self, theme_name: str) -> bool:
        """
        Set the theme to a specific value.
        
        Args:
            theme_name: Name of the theme to set ('light' or 'dark')
            
        Returns:
            True if theme was set successfully, False otherwise
        """
        if theme_name not in self.THEMES:
            return False
        
        old_theme = self.current_theme
        if old_theme != theme_name:
            self.current_theme = theme_name
            self._save_theme_preference()
            self._notify_theme_change(old_theme, theme_name)
        
        return True
    
    def is_dark_theme(self) -> bool:
        """
        Check if the current theme is dark.
        
        Returns:
            True if current theme is dark, False otherwise
        """
        return self.current_theme == "dark"
    
    def add_theme_change_callback(self, callback) -> None:
        """
        Add a callback function to be called when theme changes.
        
        Args:
            callback: Function to call when theme changes. 
                     Should accept (old_theme, new_theme) parameters.
        """
        if callback not in self._theme_change_callbacks:
            self._theme_change_callbacks.append(callback)
    
    def remove_theme_change_callback(self, callback) -> None:
        """
        Remove a theme change callback.
        
        Args:
            callback: Callback function to remove
        """
        if callback in self._theme_change_callbacks:
            self._theme_change_callbacks.remove(callback)
    
    def _notify_theme_change(self, old_theme: str, new_theme: str) -> None:
        """
        Notify all registered callbacks about theme change.
        
        Args:
            old_theme: Previous theme name
            new_theme: New theme name
        """
        for callback in self._theme_change_callbacks:
            try:
                callback(old_theme, new_theme)
            except Exception as e:
                print(f"Error in theme change callback: {e}")
    
    def get_available_themes(self) -> list:
        """
        Get list of available theme names.
        
        Returns:
            List of available theme names
        """
        return list(self.THEMES.keys())
    
    def reset_to_default(self) -> None:
        """Reset theme to default (light) and save preference."""
        old_theme = self.current_theme
        self.current_theme = "light"
        self._save_theme_preference()
        if old_theme != "light":
            self._notify_theme_change(old_theme, "light") 