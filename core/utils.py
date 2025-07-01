"""
Utility functions for CodeContextor.

This module contains general-purpose utility functions including
threading decorators and helper functions.
"""

import functools
import threading
from typing import Any, Callable, TypeVar

F = TypeVar('F', bound=Callable[..., Any])

def threaded(fn: F) -> F:
    """
    Decorator to run a function in a separate thread.
    
    Args:
        fn: Function to be decorated
        
    Returns:
        Decorated function that runs in a separate thread
    """
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> threading.Thread:
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper  # type: ignore 