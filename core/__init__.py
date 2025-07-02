"""
Core module for CodeContextor.

This module contains the essential functionality for file handling,
token counting, caching, and utility functions.
"""

from .constants import IGNORE_PATTERNS, IGNORE_EXTENSIONS, should_ignore_path, APP_VERSION
from .token_counter import count_tokens
from .file_handler import FileHandler
from .cache_manager import CacheManager
from .utils import threaded

__all__ = [
    'IGNORE_PATTERNS',
    'IGNORE_EXTENSIONS', 
    'should_ignore_path',
    'APP_VERSION',
    'count_tokens',
    'FileHandler',
    'CacheManager',
    'threaded'
] 