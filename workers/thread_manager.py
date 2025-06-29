"""
Thread management for CodeContextor.
Handles background processing and task queuing.
"""

import threading
import time
from queue import Queue
from typing import Any, Callable, Optional, Tuple


class ThreadManager:
    """Manages background tasks and threading operations."""
    
    def __init__(self):
        """Initialize the thread manager."""
        self.task_queue = Queue()
        self.is_processing = False
        self.cancel_processing = False
        self.process_tasks_thread = None
        self._start_worker_thread()
    
    def _start_worker_thread(self) -> None:
        """Start the background worker thread."""
        self.process_tasks_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self.process_tasks_thread.start()
    
    def _process_tasks(self) -> None:
        """Process tasks from the queue in a background thread."""
        while True:
            try:
                task = self.task_queue.get()
                if task:
                    func, args, callback = task
                    self.is_processing = True
                    self.cancel_processing = False
                    
                    # Execute task
                    result = func(*args)
                    
                    # Check if processing was cancelled
                    if not self.cancel_processing and callback:
                        # Schedule callback to run in the main thread
                        if hasattr(callback, '__call__'):
                            callback(result)
                    
                    self.is_processing = False
                    self.task_queue.task_done()
            except Exception as e:
                print(f"Error in task processing: {e}")
                self.is_processing = False
            
            # Small delay to prevent CPU hogging
            time.sleep(0.01)
    
    def add_task(self, func: Callable, args: Tuple[Any, ...], callback: Optional[Callable] = None) -> None:
        """Add a task to the processing queue."""
        self.task_queue.put((func, args, callback))
    
    def cancel_current_task(self) -> None:
        """Cancel the currently running task."""
        self.cancel_processing = True
    
    def is_task_running(self) -> bool:
        """Check if a task is currently running."""
        return self.is_processing
    
    def has_pending_tasks(self) -> bool:
        """Check if there are pending tasks in the queue."""
        return not self.task_queue.empty()
    
    def wait_for_completion(self) -> None:
        """Wait for all tasks to complete."""
        self.task_queue.join() 