"""
Main window implementation for CodeContextor.
Contains the complete UI and application logic.
"""

import re
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set, Optional
import threading
import time
import functools

from core import should_ignore_path, get_file_size_str, count_tokens, CacheManager, FileHandler
from workers import ThreadManager
from localization import TRANSLATIONS, TranslationManager
from .styles import StyleManager


class MainWindow:
    """Main application window for CodeContextor."""
    
    def __init__(self, master: tk.Tk) -> None:
        """Initialize the File & Folder Viewer with LLM context token counter."""
        self.master: tk.Tk = master
        self.master.title("Code Contextor Portable")
        self.master.geometry("1200x800")
        self.master.minsize(800, 600)
        
        # Base directory: using pathlib to get the directory where this file is located.
        self.base_path: Path = Path(__file__).resolve().parent.parent
        self.current_path: Path = self.base_path
        
        # Initialize managers
        self.cache_manager = CacheManager()
        self.file_handler = FileHandler(self.base_path, self.cache_manager)
        self.thread_manager = ThreadManager()
        self.translation_manager = TranslationManager()
        
        # Show ignored items toggle
        self.show_ignored = False
        
        # Initialize language_var before setup_ui
        self.language_var: tk.StringVar = tk.StringVar(value="EN")
        
        # Initialize style manager
        self.style_manager = StyleManager(self.master)
        
        self.setup_ui()
        
        # Add traces after UI is fully set up
        self.language_var.trace_add("write", self.on_language_change)
        self.search_var.trace_add("write", self.on_search_change)
        
        self.populate_listbox()
    
    def setup_ui(self) -> None:
        """Setup the user interface with shadcn/ui inspired design."""
        # Create main container with padding
        main_container = ttk.Frame(self.master, style="Background.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create main panels with card-like appearance
        self.paned: ttk.PanedWindow = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # LEFT PANEL: File explorer card
        left_container = ttk.Frame(self.paned, style="Background.TFrame")
        self.paned.add(left_container, weight=2)
        
        self.left_frame: ttk.Frame = ttk.Frame(left_container, style="Card.TFrame", padding=20)
        self.left_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Header section
        header_frame: ttk.Frame = ttk.Frame(self.left_frame, style="Card.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.left_label: ttk.Label = ttk.Label(
            header_frame, text=TRANSLATIONS["EN"]["directory_content"], style="Heading.TLabel"
        )
        self.left_label.pack(side=tk.LEFT, anchor="w")
        
        self.up_button: ttk.Button = ttk.Button(
            header_frame, text="↑ " + TRANSLATIONS["EN"]["up_directory"], 
            command=self.go_up_directory, style="Ghost.TButton"
        )
        self.up_button.pack(side=tk.RIGHT)
        
        # Current path with muted style
        self.current_path_label: ttk.Label = ttk.Label(
            self.left_frame, text="", style="Muted.TLabel"
        )
        self.current_path_label.pack(anchor="w", pady=(0, 16))
        
        # Search section with shadcn/ui input style
        search_frame = ttk.Frame(self.left_frame, style="Card.TFrame")
        search_frame.pack(fill=tk.X, pady=(0, 12))
        
        self.search_var = tk.StringVar()
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, 
                               style="ShadcnUI.TEntry")
        search_entry.pack(fill=tk.X, ipady=4)
        search_entry.insert(0, TRANSLATIONS["EN"]["search_placeholder"])
        search_entry.bind("<FocusIn>", self.on_search_focus_in)
        search_entry.bind("<FocusOut>", self.on_search_focus_out)
        self.search_entry = search_entry
        
        # Toggle for showing ignored items with shadcn/ui checkbox style
        ignore_frame = ttk.Frame(self.left_frame, style="Card.TFrame")
        ignore_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.show_ignored_var = tk.BooleanVar(value=False)
        self.show_ignored_check = ttk.Checkbutton(
            ignore_frame, 
            text=TRANSLATIONS["EN"]["show_ignored"],
            variable=self.show_ignored_var,
            command=self.toggle_ignored_items,
            style="ShadcnUI.TCheckbutton"
        )
        self.show_ignored_check.pack(anchor="w")
        
        # Directory listing with clean tree view
        list_container = ttk.Frame(self.left_frame, style="Card.TFrame")
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        
        # Add border frame for treeview
        tree_border = ttk.Frame(list_container, style="Card.TFrame", relief="solid", borderwidth=1)
        tree_border.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(tree_border, columns=("type", "size"), 
                                show="tree headings", selectmode="extended", 
                                style="ShadcnUI.Treeview")
        self.tree.heading("#0", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")
        self.tree.column("#0", width=280, stretch=True)
        self.tree.column("type", width=80, stretch=False)
        self.tree.column("size", width=100, anchor="e", stretch=False)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar with minimal style
        self.list_scrollbar: ttk.Scrollbar = ttk.Scrollbar(
            tree_border, orient=tk.VERTICAL, command=self.tree.yview)
        self.list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=self.list_scrollbar.set)
        
        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_item_double_click)
        
        # Control buttons with shadcn/ui style
        self.left_button_frame: ttk.Frame = ttk.Frame(self.left_frame, style="Card.TFrame")
        self.left_button_frame.pack(fill=tk.X)
        
        self.select_all_button: ttk.Button = ttk.Button(
            self.left_button_frame, text=TRANSLATIONS["EN"]["select_all"], 
            command=self.select_all, style="ShadcnUI.TButton"
        )
        self.select_all_button.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        
        self.clear_selection_button: ttk.Button = ttk.Button(
            self.left_button_frame, text=TRANSLATIONS["EN"]["clear_selection"], 
            command=self.clear_selection, style="ShadcnUI.TButton"
        )
        self.clear_selection_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # RIGHT PANEL: Content display card
        right_container = ttk.Frame(self.paned, style="Background.TFrame")
        self.paned.add(right_container, weight=3)
        
        self.right_frame: ttk.Frame = ttk.Frame(right_container, style="Card.TFrame", padding=20)
        self.right_frame.pack(fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Top section with clean layout
        top_right_frame: ttk.Frame = ttk.Frame(self.right_frame, style="Card.TFrame")
        top_right_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.right_label: ttk.Label = ttk.Label(
            top_right_frame, text=TRANSLATIONS["EN"]["source_code"], style="Heading.TLabel"
        )
        self.right_label.grid(row=0, column=0, sticky="w")
        
        # Progress section with minimal design
        self.progress_frame = ttk.Frame(top_right_frame, style="Card.TFrame")
        self.progress_frame.grid(row=0, column=1, sticky="e", padx=(20, 0))
        
        self.progress_label = ttk.Label(self.progress_frame, text="", style="Muted.TLabel")
        self.progress_label.pack(side=tk.LEFT, padx=(0, 12))
        
        self.cancel_button = ttk.Button(
            self.progress_frame, text=TRANSLATIONS["EN"]["cancel"], 
            command=self.cancel_current_task, state=tk.DISABLED, style="Ghost.TButton"
        )
        self.cancel_button.pack(side=tk.LEFT)
        
        # Hide progress frame initially
        self.progress_frame.grid_remove()
        
        # Language and action controls with shadcn/ui style
        controls_frame = ttk.Frame(top_right_frame, style="Card.TFrame")
        controls_frame.grid(row=0, column=2, sticky="e")
        
        language_combobox: ttk.Combobox = ttk.Combobox(
            controls_frame, values=["EN", "TR", "RU", "ES", "PT", "FR", "IT", "UK", "DE", "NL"], 
            state="readonly", width=8, textvariable=self.language_var, font=("Inter", 9)
        )
        language_combobox.pack(side=tk.LEFT, padx=(0, 8))
        
        self.copy_button: ttk.Button = ttk.Button(
            controls_frame, text=TRANSLATIONS["EN"]["copy"], 
            command=self.copy_to_clipboard, style="Success.TButton"
        )
        self.copy_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.save_button: ttk.Button = ttk.Button(
            controls_frame, text=TRANSLATIONS["EN"]["save"], 
            command=self.save_to_file, style="Primary.TButton"
        )
        self.save_button.pack(side=tk.LEFT)
        
        top_right_frame.columnconfigure(1, weight=1)
        
        # Text widget with clean styling
        text_container = ttk.Frame(self.right_frame, style="Card.TFrame")
        text_container.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        
        # Add border frame for text widget
        text_border = tk.Frame(text_container, 
                             bg=self.style_manager.colors['border_color'], 
                             highlightthickness=1, 
                             highlightbackground=self.style_manager.colors['border_color'])
        text_border.pack(fill=tk.BOTH, expand=True)
        
        text_config = self.style_manager.get_text_widget_config()
        self.text: tk.Text = tk.Text(text_border, wrap=tk.NONE, **text_config)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars with minimal style
        self.text_scrollbar_y: ttk.Scrollbar = ttk.Scrollbar(
            text_border, orient=tk.VERTICAL, command=self.text.yview)
        self.text_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_scrollbar_x: ttk.Scrollbar = ttk.Scrollbar(
            text_container, orient=tk.HORIZONTAL, command=self.text.xview)
        self.text_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X, pady=(4, 0))
        
        self.text.config(
            yscrollcommand=self.text_scrollbar_y.set,
            xscrollcommand=self.text_scrollbar_x.set
        )
        
        # Configure syntax highlighting with subtle colors
        tags_config = self.style_manager.get_text_tags_config()
        for tag, config in tags_config.items():
            self.text.tag_configure(tag, **config)
        
        # Bottom status bar with minimal design
        status_config = self.style_manager.get_status_bar_config()
        self.bottom_frame: tk.Frame = tk.Frame(self.right_frame, bg=status_config['bg'], height=48)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.bottom_frame.pack_propagate(False)
        
        # Add subtle top border to status bar
        border_line = tk.Frame(self.bottom_frame, bg=status_config['border_color'], height=1)
        border_line.pack(side=tk.TOP, fill=tk.X)
        
        # Token count display with clean style
        self.token_count_label: tk.Label = tk.Label(
            self.bottom_frame,
            text=TRANSLATIONS["EN"]["total_tokens"] + "0",
            font=("Inter", 10, "bold"),
            bg=status_config['bg'],
            fg=status_config['text_primary'],
            pady=14
        )
        self.token_count_label.pack(side=tk.RIGHT, padx=20)
        
        # Status info with muted style
        self.status_label: tk.Label = tk.Label(
            self.bottom_frame,
            text="Ready to explore your codebase",
            font=("Inter", 9),
            bg=status_config['bg'],
            fg=status_config['text_secondary'],
            pady=14
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Bind text modification event
        self.text.bind("<<Modified>>", self.on_text_modified)
    
    def on_search_focus_in(self, event):
        """Clear placeholder text when search entry gets focus"""
        if self.search_entry.get() == self.translation_manager.get_translation("search_placeholder"):
            self.search_entry.delete(0, tk.END)
    
    def on_search_focus_out(self, event):
        """Restore placeholder text when search entry loses focus"""
        if not self.search_entry.get():
            self.search_entry.insert(0, self.translation_manager.get_translation("search_placeholder"))
    
    def toggle_ignored_items(self):
        """Toggle showing ignored items"""
        self.show_ignored = self.show_ignored_var.get()
        self.file_handler.set_show_ignored(self.show_ignored)
        self.populate_listbox()
        
        # Update button text
        if self.show_ignored:
            self.show_ignored_check.config(text=self.translation_manager.get_translation("hide_ignored"))
        else:
            self.show_ignored_check.config(text=self.translation_manager.get_translation("show_ignored"))
    
    def on_language_change(self, *args: Any) -> None:
        """Update the UI elements when the language selection changes."""
        lang: str = self.language_var.get()
        self.translation_manager.set_language(lang)
        
        translations = self.translation_manager.get_all_translations()
        
        self.master.title(translations["title"])
        self.left_label.config(text=translations["directory_content"])
        self.up_button.config(text="↑ " + translations["up_directory"])
        self.select_all_button.config(text=translations["select_all"])
        self.clear_selection_button.config(text=translations["clear_selection"])
        self.right_label.config(text=translations["source_code"])
        self.copy_button.config(text=translations["copy"])
        self.save_button.config(text=translations["save"])
        self.cancel_button.config(text=translations["cancel"])
        
        # Update search placeholder
        current_search = self.search_entry.get()
        if not current_search or current_search in [t["search_placeholder"] for t in TRANSLATIONS.values()]:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, translations["search_placeholder"])
        
        # Update ignored items toggle text
        if self.show_ignored:
            self.show_ignored_check.config(text=translations["hide_ignored"])
        else:
            self.show_ignored_check.config(text=translations["show_ignored"])
        
        # Update token count
        self.token_count_label.config(
            text=translations["total_tokens"] + str(count_tokens(self.text.get("1.0", tk.END)))
        )
        
        # Update progress label if visible
        if self.thread_manager.is_task_running():
            self.progress_label.config(text=translations["processing"])
        
        self.populate_listbox()  # Update the current directory label and status
    
    def on_search_change(self, *args: Any) -> None:
        """Filter the listbox content based on search term"""
        self.populate_listbox()
    
    def populate_listbox(self) -> None:
        """
        List files and folders in the current directory in alphabetical order.
        Implements search filtering, ignore patterns, and caching for better performance.
        """
        # Safety check: ensure tree widget exists
        if not hasattr(self, 'tree'):
            return
            
        try:
            # Clear the tree
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Get items from cache or directory
            items = self.cache_manager.get_directory_listing(self.current_path)
                
            # Filter ignored items unless specifically showing them
            if not self.show_ignored:
                items = [item for item in items if not should_ignore_path(item)]
                
            # Sort items (folders first, then files)
            folders = sorted([p for p in items if p.is_dir()], key=lambda p: p.name.lower())
            files = sorted([p for p in items if p.is_file()], key=lambda p: p.name.lower())
            
            # Filter by search term if provided
            search_term = self.search_var.get().lower()
            if search_term and search_term != self.translation_manager.get_translation("search_placeholder").lower():
                folders = [f for f in folders if search_term in f.name.lower()]
                files = [f for f in files if search_term in f.name.lower()]
            
            # Count ignored items for status
            ignored_count = 0
            if not self.show_ignored:
                all_items = self.cache_manager.get_directory_listing(self.current_path)
                ignored_count = len([item for item in all_items if should_ignore_path(item)])
            
            # Add folders to tree with minimal style
            for folder in folders:
                try:
                    # Simple folder display
                    self.tree.insert("", "end", iid=str(folder), 
                                   text=folder.name, 
                                   values=("Folder", ""),
                                   tags=("folder",) if not should_ignore_path(folder) else ("ignored",))
                except Exception:
                    self.tree.insert("", "end", iid=str(folder), 
                                   text=folder.name, 
                                   values=("Folder", ""))
                
            # Add files to tree with minimal style
            for file in files:
                try:
                    size = file.stat().st_size
                    # Determine file type based on extension
                    ext = file.suffix.lower()
                    file_type = ext[1:].upper() if ext else "File"
                    
                    self.tree.insert("", "end", iid=str(file), 
                                   text=file.name, 
                                   values=(file_type, get_file_size_str(size)),
                                   tags=("file",) if not should_ignore_path(file) else ("ignored",))
                except Exception:
                    self.tree.insert("", "end", iid=str(file), 
                                   text=file.name, 
                                    values=("Error", "Unknown"))
            
            # Update status and path display
            try:
                rel_current = str(self.current_path.relative_to(self.base_path))
            except ValueError:
                rel_current = str(self.current_path)
            if rel_current == ".":
                rel_current = self.base_path.name
            
            current_dir = self.translation_manager.get_translation("current_dir")
            if hasattr(self, 'current_path_label'):
                self.current_path_label.config(text=f"{current_dir}{rel_current}")
            
            # Update status with counts
            total_items = len(folders) + len(files)
            status_text = f"{len(folders)} folders · {len(files)} files"
            if ignored_count > 0:
                status_text += f" · {ignored_count} hidden"
            if hasattr(self, 'status_label'):
                self.status_label.config(text=status_text)
            
            # Update navigation button state
            if hasattr(self, 'up_button'):
                if self.current_path == self.base_path:
                    self.up_button.state(["disabled"])
                else:
                    self.up_button.state(["!disabled"])
                
        except Exception as e:
            error_msg = self.translation_manager.get_translation("list_error")
            messagebox.showerror("Error", f"{error_msg}{e}")
    
    def process_selection(self, selections: List[str]) -> None:
        """Process the selected items and update the text widget with markdown content"""
        # Show progress indicator
        self.show_progress()
        
        def generate_markdown(selections):
            self.file_handler.set_cancel_flag(False)
            return self.file_handler.process_selections(selections)
        
        def update_text(markdown):
            self.text.delete("1.0", tk.END)
            if markdown:
                self.text.insert(tk.END, markdown)
                self.highlight_markdown()
            self.update_token_count()
        
        # Add the task to the queue
        self.thread_manager.add_task(generate_markdown, (selections,), update_text)
    
    def highlight_markdown(self) -> None:
        """Apply syntax highlighting to the markdown text"""
        content = self.text.get("1.0", tk.END)
        
        # Clear existing tags
        for tag in ["header", "code_block", "code_marker"]:
            self.text.tag_remove(tag, "1.0", tk.END)
        
        # Highlight headers (## text)
        pos = "1.0"
        while True:
            header_start = self.text.search("^## ", pos, tk.END, regexp=True)
            if not header_start:
                break
            header_end = self.text.search("\n", header_start, tk.END)
            if not header_end:
                header_end = tk.END
            self.text.tag_add("header", header_start, header_end)
            pos = header_end
        
        # Highlight code blocks
        pos = "1.0"
        in_code_block = False
        start_pos = None
        
        while True:
            marker_pos = self.text.search("```", pos, tk.END)
            if not marker_pos:
                break
                
            marker_end = f"{marker_pos}+3c"
            
            # Add tag for the code marker itself
            self.text.tag_add("code_marker", marker_pos, marker_end)
            
            if not in_code_block:
                # Start of code block
                start_pos = marker_end
                in_code_block = True
            else:
                # End of code block
                self.text.tag_add("code_block", start_pos, marker_pos)
                in_code_block = False
                
            pos = marker_end
    
    def on_select(self, event: Any) -> None:
        """
        When an item is selected in the tree, insert the Markdown content 
        of the selected file(s) or folder(s) into the Text widget.
        Uses threading to prevent UI freezing for large files/folders.
        """
        selections = self.tree.selection()
        if not selections:
            self.text.delete("1.0", tk.END)
            self.update_token_count()
            return
            
        self.process_selection(selections)
    
    def on_item_double_click(self, event: Any) -> None:
        """
        If a folder is double-clicked in the tree, navigate into that folder.
        """
        selection = self.tree.selection()
        if not selection:
            return
        item_id = selection[0]
        full_path = Path(item_id)
        if full_path.is_dir():
            self.current_path = full_path
            self.populate_listbox()
            self.text.delete("1.0", tk.END)
            self.update_token_count()
    
    def go_up_directory(self) -> None:
        """
        Navigate to the parent directory (preventing navigation outside the base directory).
        """
        if self.current_path == self.base_path:
            info_msg = self.translation_manager.get_translation("root_dir_info")
            messagebox.showinfo("Info", info_msg)
            return
        new_path: Path = self.current_path.parent
        try:
            new_path.relative_to(self.base_path)
        except ValueError:
            error_msg = self.translation_manager.get_translation("root_dir_error")
            messagebox.showerror("Error", error_msg)
            return
        self.current_path = new_path
        self.populate_listbox()
        self.text.delete("1.0", tk.END)
        self.update_token_count()
    
    def select_all(self) -> None:
        """Select all items in the tree."""
        for item in self.tree.get_children():
            self.tree.selection_add(item)
        self.on_select(None)
    
    def clear_selection(self) -> None:
        """Clear the selection in the tree and clear the Text widget."""
        self.tree.selection_remove(self.tree.selection())
        self.text.delete("1.0", tk.END)
        self.update_token_count()
    
    def save_to_file(self) -> None:
        """Save the Markdown content from the Text widget to 'llm.txt' in the base directory."""
        content: str = self.text.get("1.0", tk.END)
        file_path: Path = self.base_path / "llm.txt"
        
        try:
            file_path.write_text(content, encoding="utf-8")
            success_msg = self.translation_manager.get_translation("save_success")
            messagebox.showinfo("Success", f"{success_msg}{str(file_path)}")
        except Exception as e:
            error_msg = self.translation_manager.get_translation("save_error")
            messagebox.showerror("Error", f"{error_msg}{e}")
    
    def copy_to_clipboard(self) -> None:
        """Copy the Markdown content from the Text widget to clipboard."""
        content: str = self.text.get("1.0", tk.END)
        
        try:
            self.master.clipboard_clear()
            self.master.clipboard_append(content)
            self.master.update()  # Ensure clipboard is updated
            success_msg = self.translation_manager.get_translation("copy_success")
            messagebox.showinfo("Success", success_msg)
        except Exception as e:
            error_msg = self.translation_manager.get_translation("copy_error")
            messagebox.showerror("Error", f"{error_msg}{e}")
    
    def show_progress(self) -> None:
        """Show progress indicator for long operations"""
        processing_msg = self.translation_manager.get_translation("processing")
        self.progress_label.config(text=processing_msg)
        self.progress_frame.grid()
        self.cancel_button.config(state=tk.NORMAL)
    
    def hide_progress(self) -> None:
        """Hide progress indicator when operation completes"""
        self.progress_frame.grid_remove()
        self.cancel_button.config(state=tk.DISABLED)
    
    def cancel_current_task(self) -> None:
        """Cancel the currently running task"""
        self.thread_manager.cancel_current_task()
        self.file_handler.set_cancel_flag(True)
    
    def update_token_count(self) -> None:
        """Calculate the token count of the text and update the token count label with improved stability."""
        content: str = self.text.get("1.0", tk.END)
        
        # Improved token counting with better error handling and caching
        def count_in_background(text):
            try:
                # Clean the text by removing excessive whitespace but preserve structure
                cleaned_text = text.strip()
                if not cleaned_text:
                    return 0
                return count_tokens(cleaned_text)
            except Exception as e:
                print(f"Token counting error: {e}")
                # Fallback to simple word count if token counting fails
                return len(cleaned_text.split())
            
        def update_label(count):
            try:
                token_text = self.translation_manager.get_translation("total_tokens")
                self.token_count_label.config(text=f"{token_text}{count:,}")
            except Exception as e:
                print(f"Label update error: {e}")
                # Fallback to English if language retrieval fails
                self.token_count_label.config(text=f"Tokens: {count:,}")
            
        # For very small texts, count directly to avoid thread overhead
        if len(content) < 5000:
            try:
                count = count_tokens(content.strip()) if content.strip() else 0
                update_label(count)
            except:
                # Fallback for direct counting
                count = len(content.split()) if content.strip() else 0
                update_label(count)
        else:
            # Use background processing for larger texts
            self.thread_manager.add_task(count_in_background, (content,), update_label)
    
    def on_text_modified(self, event: Any) -> None:
        """
        Triggered when the <<Modified>> event occurs in the Text widget;
        updates the token count after text changes.
        Note: The event may trigger twice in some cases, so the modified flag is reset.
        """
        self.update_token_count()
        self.text.edit_modified(False) 