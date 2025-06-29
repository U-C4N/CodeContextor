"""
File handling operations for CodeContextor.
Handles file reading and markdown generation.
"""

from pathlib import Path
from typing import List
from .utils import should_ignore_path, get_file_size_str
from .cache_manager import CacheManager


class FileHandler:
    """Handles file operations and markdown generation."""
    
    def __init__(self, base_path: Path, cache_manager: CacheManager):
        """Initialize the file handler."""
        self.base_path = base_path
        self.cache_manager = cache_manager
        self.cancel_processing = False
        self.show_ignored = False
    
    def set_show_ignored(self, show_ignored: bool) -> None:
        """Set whether to show ignored items."""
        self.show_ignored = show_ignored
    
    def set_cancel_flag(self, cancel: bool) -> None:
        """Set the cancellation flag."""
        self.cancel_processing = cancel
    
    def get_markdown_for_path(self, path: Path, max_depth: int = 3, current_depth: int = 0) -> str:
        """
        Generate Markdown content for the given file or folder path.
        - File: Uses the relative path as a header and includes its content inside a code block.
        - Folder: Uses the folder name as a header and recursively includes all files/folders inside.
        
        Implements depth limiting and ignore patterns to prevent excessive recursion and 
        exclude cache/build directories from LLM context.
        """
        # Check for cancellation request
        if self.cancel_processing:
            return "Operation cancelled"
            
        # Skip ignored items completely unless specifically showing them
        if not self.show_ignored and should_ignore_path(path):
            return ""
            
        try:
            rel_path = path.relative_to(self.base_path)
        except ValueError:
            rel_path = path
        display_path: str = f"{self.base_path.name}/{rel_path.as_posix()}"
        
        if path.is_file():
            content = self.cache_manager.get_file_content(path)
            # Get file extension for syntax highlighting
            ext = path.suffix.lower()[1:] if path.suffix else "text"
            
            # Markdown with file size info
            try:
                size = path.stat().st_size
                size_str = get_file_size_str(size)
                markdown_str: str = f"## {display_path}\n\n"
                markdown_str += f"*{size_str}*\n\n"
                markdown_str += f"```{ext}\n{content}\n```\n\n"
            except:
                markdown_str: str = f"## {display_path}\n\n```{ext}\n{content}\n```\n\n"
            return markdown_str
            
        elif path.is_dir():
            # Folder header
            markdown_str: str = f"## {display_path}/\n\n"
            
            # Stop recursion if we've reached the maximum depth
            if current_depth >= max_depth:
                markdown_str += f"*Directory content not shown due to depth limit ({max_depth})*\n\n"
                return markdown_str
                
            try:
                # Get directory items from cache
                items = self.cache_manager.get_directory_listing(path)
                
                # Filter out ignored items unless specifically showing them
                if not self.show_ignored:
                    items = [item for item in items if not should_ignore_path(item)]
                
                # Process folders first, then files
                folders = sorted([p for p in items if p.is_dir()], key=lambda p: p.name.lower())
                files = sorted([p for p in items if p.is_file()], key=lambda p: p.name.lower())
                
                # Add summary of folder contents
                if folders or files:
                    markdown_str += f"*Contains: {len(folders)} folders, {len(files)} files*\n\n"
                
                # Process folders recursively
                for item in folders:
                    if not self.cancel_processing:
                        markdown_str += self.get_markdown_for_path(item, max_depth, current_depth + 1)
                
                # Process files
                for item in files:
                    if not self.cancel_processing:
                        markdown_str += self.get_markdown_for_path(item, max_depth, current_depth + 1)
                    
            except Exception as e:
                markdown_str += f"Cannot read folder: {e}\n\n"
            return markdown_str
        else:
            return ""
    
    def process_selections(self, selections: List[str]) -> str:
        """Process multiple selected items and generate combined markdown."""
        full_markdown = ""
        for item_id in selections:
            full_path = Path(item_id)
            markdown = self.get_markdown_for_path(full_path)
            if self.cancel_processing:
                return "Operation cancelled."
            full_markdown += markdown
        return full_markdown 