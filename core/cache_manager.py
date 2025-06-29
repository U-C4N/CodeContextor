"""
Cache management system for CodeContextor.
Handles directory listings and file content caching.
"""

from pathlib import Path
from typing import Dict, List
from .constants import MAX_FILE_CACHE_SIZE


class CacheManager:
    """Manages caching for directory listings and file contents."""
    
    def __init__(self, max_file_cache_size: int = MAX_FILE_CACHE_SIZE):
        """Initialize the cache manager."""
        self.dir_cache: Dict[Path, List[Path]] = {}
        self.file_content_cache: Dict[Path, str] = {}
        self.max_cache_size = max_file_cache_size
    
    def get_directory_listing(self, path: Path) -> List[Path]:
        """Get directory listing from cache or filesystem."""
        if path in self.dir_cache:
            return self.dir_cache[path]
        
        try:
            items = list(path.iterdir())
            self.dir_cache[path] = items
            return items
        except Exception:
            return []
    
    def cache_directory_listing(self, path: Path, items: List[Path]) -> None:
        """Cache a directory listing."""
        self.dir_cache[path] = items
    
    def get_file_content(self, path: Path) -> str:
        """Get file content from cache or filesystem."""
        if path in self.file_content_cache:
            return self.file_content_cache[path]
        
        try:
            content = path.read_text(encoding="utf-8")
            
            # Cache the content (with size management)
            if len(self.file_content_cache) >= self.max_cache_size:
                # Remove the first item (least recently added)
                self.file_content_cache.pop(next(iter(self.file_content_cache)))
            self.file_content_cache[path] = content
            
            return content
        except Exception as e:
            return f"Cannot read file: {e}"
    
    def cache_file_content(self, path: Path, content: str) -> None:
        """Cache file content."""
        # Manage cache size
        if len(self.file_content_cache) >= self.max_cache_size:
            # Remove the first item (least recently added)
            self.file_content_cache.pop(next(iter(self.file_content_cache)))
        self.file_content_cache[path] = content
    
    def clear_caches(self) -> None:
        """Clear all caches."""
        self.dir_cache.clear()
        self.file_content_cache.clear()
    
    def clear_directory_cache(self) -> None:
        """Clear only directory cache."""
        self.dir_cache.clear()
    
    def clear_file_cache(self) -> None:
        """Clear only file content cache."""
        self.file_content_cache.clear() 