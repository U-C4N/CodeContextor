import threading
import time
from queue import Queue, Empty
from typing import Any, Callable, Optional, Dict, List
from pathlib import Path

class ThreadManager:
    """Manages background threads and task processing."""
    
    def __init__(self):
        """Initialize thread manager."""
        self.task_queue: Queue = Queue()
        self.is_processing: bool = False
        self.cancel_processing: bool = False
        self.worker_thread: Optional[threading.Thread] = None
        self.progress_callback: Optional[Callable[[str], None]] = None
        self.completion_callback: Optional[Callable[[Any], None]] = None
    
    def start_processing(self) -> None:
        """Start the background processing thread."""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.cancel_processing = False
        
        if self.worker_thread and self.worker_thread.is_alive():
            return
        
        self.worker_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self.worker_thread.start()
    
    def stop_processing(self) -> None:
        """Stop background processing."""
        self.cancel_processing = True
        self.is_processing = False
    
    def add_task(self, task_func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Add a task to the processing queue."""
        task = {
            'func': task_func,
            'args': args,
            'kwargs': kwargs
        }
        self.task_queue.put(task)
    
    def set_progress_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for progress updates."""
        self.progress_callback = callback
    
    def set_completion_callback(self, callback: Callable[[Any], None]) -> None:
        """Set callback for task completion."""
        self.completion_callback = callback
    
    def update_progress(self, message: str) -> None:
        """Update progress message."""
        if self.progress_callback and not self.cancel_processing:
            self.progress_callback(message)
    
    def is_busy(self) -> bool:
        """Check if processing tasks."""
        return self.is_processing and not self.task_queue.empty()
    
    def clear_queue(self) -> None:
        """Clear all pending tasks."""
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
                self.task_queue.task_done()
            except Empty:
                break
    
    def _process_tasks(self) -> None:
        """Process tasks from the queue in background thread."""
        while self.is_processing and not self.cancel_processing:
            try:
                task = self.task_queue.get(timeout=0.5)
                
                if self.cancel_processing:
                    break
                
                try:
                    result = task['func'](*task['args'], **task['kwargs'])
                    
                    if self.completion_callback and not self.cancel_processing:
                        self.completion_callback(result)
                        
                except Exception as e:
                    print(f"Task execution error: {e}")
                
                self.task_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                print(f"Task processing error: {e}")
        
        self.is_processing = False 