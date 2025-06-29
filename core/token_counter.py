"""
Token counting functionality for CodeContextor.
Handles LLM token counting with caching and fallback mechanisms.
"""

import time
from .constants import MAX_CACHE_SIZE, CACHE_TTL

# Token counting function: Uses tiktoken if available; otherwise falls back to a regex-based method.
try:
    import tiktoken
    
    # Enhanced cache for token counts with TTL and size management
    token_cache = {}
    cache_timestamps = {}
    
    def count_tokens(text: str) -> int:
        """
        Returns the token count of the given text using the "cl100k_base" encoding,
        which is appropriate for LLM contexts. Uses enhanced caching for performance.
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
            encoding = tiktoken.get_encoding("cl100k_base")
            tokens = encoding.encode(text.strip())
            count = len(tokens)
            
            # Manage cache size
            if len(token_cache) >= MAX_CACHE_SIZE:
                # Remove oldest entries (simple LRU)
                oldest_keys = sorted(cache_timestamps.keys(), 
                                   key=lambda k: cache_timestamps[k])[:10]
                for key in oldest_keys:
                    token_cache.pop(key, None)
                    cache_timestamps.pop(key, None)
            
            # Cache the result
            token_cache[text_hash] = count
            cache_timestamps[text_hash] = current_time
            return count
            
        except Exception as e:
            print(f"Tiktoken error: {e}")
            # Fallback to regex-based counting
            return _fallback_count_tokens(text)
            
except ImportError:
    # Enhanced fallback cache for when tiktoken is not available
    token_cache = {}
    cache_timestamps = {}
    MAX_FALLBACK_CACHE_SIZE = 100
    
    def count_tokens(text: str) -> int:
        """
        Fallback method for token counting using regex when tiktoken is not available.
        Uses enhanced caching for performance and stability.
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
            count = _fallback_count_tokens(text)
            
            # Manage cache size
            if len(token_cache) >= MAX_FALLBACK_CACHE_SIZE:
                # Remove oldest entries
                oldest_keys = sorted(cache_timestamps.keys(), 
                                   key=lambda k: cache_timestamps[k])[:5]
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


def _fallback_count_tokens(text: str) -> int:
    """Enhanced fallback token counting method using improved regex patterns."""
    import re
    try:
        # More sophisticated tokenization that better matches real tokenizers
        # Split on word boundaries, punctuation, and whitespace
        tokens = re.findall(r'\w+|[^\w\s]', text.strip(), re.UNICODE)
        return len(tokens)
    except Exception:
        # Ultimate fallback
        return len(text.strip().split()) 