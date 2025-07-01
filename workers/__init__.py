"""
Workers module for CodeContextor.

This module provides background processing capabilities including
thread management and task queuing for non-blocking UI operations.
"""

from .thread_manager import ThreadManager

__all__ = ['ThreadManager'] 