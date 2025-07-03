from pathlib import Path
from typing import Dict, List, Optional
import time

class CacheManager:
    """Manages caching for directory listings and file contents."""
    
    def __init__(self, max_cache_size: int = 50, cache_ttl: int = 300):
        """
        Initialize cache manager.
        
        Args:
            max_cache_size: Maximum number of items to cache.
            cache_ttl: Time-to-live for cache entries in seconds.
        """
        self.max_cache_size = max_cache_size
        self.cache_ttl = cache_ttl
        
        # Directory listing cache
        self.dir_cache: Dict[str, List[Path]] = {}
        self.dir_cache_timestamps: Dict[str, float] = {}
        
        # File content cache
        self.file_content_cache: Dict[str, str] = {}
        self.file_content_timestamps: Dict[str, float] = {}
    
    def _get_cache_key(self, path: Path, show_ignored: bool = False) -> str:
        """Generate cache key for a path."""
        return f"{path.as_posix()}:{show_ignored}"
    
    def _cleanup_cache(self, cache: Dict, timestamps: Dict) -> None:
        """Remove old entries from cache to maintain size limit."""
        if len(cache) >= self.max_cache_size:
            # Remove oldest entries (LRU)
            entries_to_remove = max(1, len(cache) // 4)  # Remove 25% of entries
            oldest_keys = sorted(timestamps.keys(), 
                               key=lambda k: timestamps[k])[:entries_to_remove]
            
            for key in oldest_keys:
                cache.pop(key, None)
                timestamps.pop(key, None)
    
    def _is_cache_valid(self, key: str, timestamps: Dict) -> bool:
        """Check if cache entry is still valid."""
        if key not in timestamps:
            return False
        
        return time.time() - timestamps[key] < self.cache_ttl
    
    def get_directory_listing(self, path: Path, show_ignored: bool = False) -> Optional[List[Path]]:
        """
        Get cached directory listing.
        
        Args:
            path: Directory path.
            show_ignored: Whether ignored items are included.
            
        Returns:
            Cached directory listing or None if not cached/expired.
        """
        cache_key = self._get_cache_key(path, show_ignored)
        
        if cache_key in self.dir_cache and self._is_cache_valid(cache_key, self.dir_cache_timestamps):
            return self.dir_cache[cache_key].copy()
        
        # Remove expired entry
        if cache_key in self.dir_cache:
            del self.dir_cache[cache_key]
            del self.dir_cache_timestamps[cache_key]
        
        return None
    
    def cache_directory_listing(self, path: Path, items: List[Path], show_ignored: bool = False) -> None:
        """
        Cache directory listing.
        
        Args:
            path: Directory path.
            items: List of items in directory.
            show_ignored: Whether ignored items are included.
        """
        cache_key = self._get_cache_key(path, show_ignored)
        
        # Cleanup cache if needed
        self._cleanup_cache(self.dir_cache, self.dir_cache_timestamps)
        
        # Cache the listing
        self.dir_cache[cache_key] = items.copy()
        self.dir_cache_timestamps[cache_key] = time.time()
    
    def get_file_content(self, path: Path) -> Optional[str]:
        """
        Get cached file content.
        
        Args:
            path: File path.
            
        Returns:
            Cached file content or None if not cached/expired.
        """
        cache_key = path.as_posix()
        
        if cache_key in self.file_content_cache and self._is_cache_valid(cache_key, self.file_content_timestamps):
            return self.file_content_cache[cache_key]
        
        # Remove expired entry
        if cache_key in self.file_content_cache:
            del self.file_content_cache[cache_key]
            del self.file_content_timestamps[cache_key]
        
        return None
    
    def cache_file_content(self, path: Path, content: str) -> None:
        """
        Cache file content.
        
        Args:
            path: File path.
            content: File content.
        """
        cache_key = path.as_posix()
        
        # Cleanup cache if needed
        self._cleanup_cache(self.file_content_cache, self.file_content_timestamps)
        
        # Cache the content
        self.file_content_cache[cache_key] = content
        self.file_content_timestamps[cache_key] = time.time()
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.dir_cache.clear()
        self.dir_cache_timestamps.clear()
        self.file_content_cache.clear()
        self.file_content_timestamps.clear()
    
    def clear_directory_cache(self) -> None:
        """Clear only directory listing cache."""
        self.dir_cache.clear()
        self.dir_cache_timestamps.clear()
    
    def clear_file_content_cache(self) -> None:
        """Clear only file content cache."""
        self.file_content_cache.clear()
        self.file_content_timestamps.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            'dir_cache_size': len(self.dir_cache),
            'file_cache_size': len(self.file_content_cache),
            'max_cache_size': self.max_cache_size,
            'cache_ttl': self.cache_ttl
        } 