"""
Token counting functionality for CodeContextor.

This module provides token counting capabilities using tiktoken when available,
with fallback methods for environments where tiktoken is not installed.
"""

import re
import time
from typing import Dict

# Try to import tiktoken for accurate token counting
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

# Enhanced cache for token counts with TTL and size management
token_cache: Dict[int, int] = {}
cache_timestamps: Dict[int, float] = {}
MAX_CACHE_SIZE = 200 if TIKTOKEN_AVAILABLE else 100
CACHE_TTL = 300  # 5 minutes

def count_tokens(text: str) -> int:
    """
    Returns the token count of the given text using the "cl100k_base" encoding
    when tiktoken is available, otherwise falls back to regex-based counting.
    Uses enhanced caching for performance.
    """
    if not text or not text.strip():
        return 0
        
    # Use hash of text as key to avoid storing large strings in memory
    text_hash = hash(text.strip())
    current_time = time.time()
    
    # Check cache with TTL
    if text_hash in token_cache and text_hash in cache_timestamps:
        if current_time - cache_timestamps[text_hash] < CACHE_TTL:
            return token_cache[text_hash]
        else:
            # Remove expired entry
            del token_cache[text_hash]
            del cache_timestamps[text_hash]
    
    try:
        if TIKTOKEN_AVAILABLE:
            count = _tiktoken_count_tokens(text)
        else:
            count = _fallback_count_tokens(text)
        
        # Manage cache size
        if len(token_cache) >= MAX_CACHE_SIZE:
            # Remove oldest entries (simple LRU)
            entries_to_remove = 10 if TIKTOKEN_AVAILABLE else 5
            oldest_keys = sorted(cache_timestamps.keys(), 
                               key=lambda k: cache_timestamps[k])[:entries_to_remove]
            for key in oldest_keys:
                token_cache.pop(key, None)
                cache_timestamps.pop(key, None)
        
        # Cache the result
        token_cache[text_hash] = count
        cache_timestamps[text_hash] = current_time
        return count
        
    except Exception as e:
        print(f"Token counting error: {e}")
        # Ultimate fallback - simple word count
        return len(text.strip().split())

def _tiktoken_count_tokens(text: str) -> int:
    """Count tokens using tiktoken encoding."""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text.strip())
        return len(tokens)
    except Exception as e:
        print(f"Tiktoken error: {e}")
        # Fallback to regex-based counting
        return _fallback_count_tokens(text)

def _fallback_count_tokens(text: str) -> int:
    """Enhanced fallback token counting method using improved regex patterns."""
    try:
        # More sophisticated tokenization that better matches real tokenizers
        # Split on word boundaries, punctuation, and whitespace
        tokens = re.findall(r'\w+|[^\w\s]', text.strip(), re.UNICODE)
        return len(tokens)
    except Exception:
        # Ultimate fallback
        return len(text.strip().split())

def clear_token_cache() -> None:
    """Clear the token counting cache."""
    global token_cache, cache_timestamps
    token_cache.clear()
    cache_timestamps.clear()

def get_cache_stats() -> Dict[str, int]:
    """Get statistics about the token cache."""
    return {
        'cache_size': len(token_cache),
        'max_cache_size': MAX_CACHE_SIZE,
        'cache_ttl': CACHE_TTL,
        'tiktoken_available': TIKTOKEN_AVAILABLE
    } 