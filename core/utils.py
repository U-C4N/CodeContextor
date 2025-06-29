"""
Utility functions for CodeContextor.
Contains helper functions and decorators.
"""

import threading
import functools
from pathlib import Path
from .constants import IGNORE_PATTERNS, IGNORE_EXTENSIONS


def should_ignore_path(path: Path) -> bool:
    """Check if a path should be ignored based on ignore patterns."""
    # Check if it's a directory with ignored name
    if path.is_dir() and path.name.lower() in IGNORE_PATTERNS:
        return True
    
    # Check if it's a file with ignored extension
    if path.is_file() and path.suffix.lower() in IGNORE_EXTENSIONS:
        return True
    
    # Check if it's a hidden file (starts with .) except for some common ones
    if path.name.startswith('.') and path.name not in {'.gitignore', '.env.example', '.env.template', '.editorconfig', '.dockerignore', '.htaccess'}:
        return True
        
    return False


def threaded(fn):
    """Decorator to run a function in a separate thread"""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper


def get_file_size_str(size_bytes: int) -> str:
    """Convert file size in bytes to a human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0 or unit == 'GB':
            return f"{size_bytes:.1f} {unit}" if unit != 'B' else f"{size_bytes} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} GB" 