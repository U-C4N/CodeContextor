"""
File handling functionality for CodeContextor.

This module provides file and directory operations including
reading file contents, path management, and directory traversal.
"""

from pathlib import Path
from typing import List, Optional

from .constants import should_ignore_path

class FileHandler:
    """Handles file operations and path management."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize FileHandler with base path.
        
        Args:
            base_path: Base directory path. If None, uses current file's parent directory.
        """
        if base_path is None:
            # Use the directory where this file is located as default
            self.base_path = Path(__file__).resolve().parent.parent
        else:
            self.base_path = Path(base_path).resolve()
        
        self.current_path = self.base_path
    
    def set_current_path(self, path: Path) -> None:
        """Set the current working path."""
        self.current_path = Path(path).resolve()
    
    def get_current_path(self) -> Path:
        """Get the current working path."""
        return self.current_path
    
    def can_go_up(self) -> bool:
        """Check if we can navigate up from current directory."""
        try:
            return self.current_path != self.base_path and self.current_path.parent != self.current_path
        except (OSError, ValueError):
            return False
    
    def go_up_directory(self) -> bool:
        """
        Navigate up one directory level.
        
        Returns:
            True if navigation was successful, False otherwise.
        """
        if not self.can_go_up():
            return False
        
        try:
            self.current_path = self.current_path.parent
            return True
        except (OSError, ValueError):
            return False
    
    def list_directory(self, path: Optional[Path] = None, show_ignored: bool = False) -> List[Path]:
        """
        List contents of a directory.
        
        Args:
            path: Directory path to list. If None, uses current_path.
            show_ignored: Whether to include ignored files/directories.
            
        Returns:
            List of Path objects in the directory.
        """
        if path is None:
            path = self.current_path
        
        try:
            items = []
            for item in path.iterdir():
                # Apply ignore filters unless show_ignored is True
                if not show_ignored and should_ignore_path(item):
                    continue
                items.append(item)
            
            # Sort: directories first, then files, both alphabetically
            return sorted(items, key=lambda x: (x.is_file(), x.name.lower()))
            
        except (PermissionError, OSError, ValueError) as e:
            print(f"Error listing directory {path}: {e}")
            return []
    
    def read_file_content(self, path: Path) -> str:
        """
        Read content of a file with encoding detection.
        
        Args:
            path: Path to the file to read.
            
        Returns:
            File content as string, or empty string if reading fails.
        """
        if not path.is_file():
            return ""
        
        # Try different encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(path, 'r', encoding=encoding) as file:
                    return file.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
            except (PermissionError, OSError, FileNotFoundError) as e:
                print(f"Error reading file {path}: {e}")
                return ""
        
        # If all encodings fail, try binary mode and decode with errors='replace'
        try:
            with open(path, 'rb') as file:
                content = file.read()
                return content.decode('utf-8', errors='replace')
        except Exception as e:
            print(f"Error reading file {path} in binary mode: {e}")
            return ""
    
    def get_file_size_str(self, path: Path) -> str:
        """
        Get human-readable file size string.
        
        Args:
            path: Path to the file.
            
        Returns:
            Human-readable size string (e.g., "1.2 KB", "3.4 MB").
        """
        try:
            if not path.exists():
                return "0 B"
            
            if path.is_dir():
                return "folder"
            
            size_bytes = path.stat().st_size
            
            if size_bytes == 0:
                return "0 B"
            
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    if unit == 'B':
                        return f"{int(size_bytes)} {unit}"
                    else:
                        return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024.0
            
            return f"{size_bytes:.1f} TB"
            
        except (OSError, ValueError):
            return "0 B"
    
    def is_text_file(self, path: Path) -> bool:
        """
        Check if a file is likely a text file based on extension.
        
        Args:
            path: Path to check.
            
        Returns:
            True if likely a text file, False otherwise.
        """
        if not path.is_file():
            return False
        
        text_extensions = {
            '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json',
            '.xml', '.yaml', '.yml', '.ini', '.cfg', '.conf', '.log',
            '.sh', '.bat', '.ps1', '.sql', '.r', '.rb', '.php', '.go',
            '.rs', '.cpp', '.c', '.h', '.hpp', '.java', '.kt', '.swift',
            '.dart', '.vue', '.jsx', '.tsx', '.scss', '.less', '.styl'
        }
        
        return path.suffix.lower() in text_extensions 