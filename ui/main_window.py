"""
Main window for CodeContextor.

This module contains the FileExplorer class which provides the main user interface
including file browser, text editor, and all UI interactions.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from pathlib import Path
from typing import Any, Dict, List, Optional
import threading
from queue import Queue

# Import from our new modular structure
from core import (
    FileHandler, CacheManager, count_tokens, threaded, 
    IGNORE_PATTERNS, IGNORE_EXTENSIONS, should_ignore_path, APP_VERSION
)
from localization import TRANSLATIONS, get_translation
from workers import ThreadManager
from .styles import UIStyles
from .theme_manager import ThemeManager
from .shortcut_manager import ShortcutManager
from .error_handler import ErrorHandler
from .diagram_manager import DiagramManager
# from .animations import AnimationManager

class FileExplorer:
    """Main application window for CodeContextor."""
    
    def __init__(self, master: tk.Tk) -> None:
        """Initialize the File & Folder Viewer with LLM context token counter and theme support."""
        self.master: tk.Tk = master
        self.master.title("Code Contextor Portable")
        self.master.geometry("1200x800")
        self.master.minsize(800, 600)
        
        # Initialize theme and styling
        self.theme_manager = ThemeManager()
        self.ui_styles = UIStyles(self.theme_manager)
        
        # Initialize core components
        self.file_handler = FileHandler()
        self.cache_manager = CacheManager()
        self.thread_manager = ThreadManager()
        
        # Set up paths
        self.base_path: Path = self.file_handler.base_path
        self.current_path: Path = self.file_handler.current_path
        
        # UI state
        self.show_ignored = False
        self.language_var: tk.StringVar = tk.StringVar(value="EN")
        
        # Initialize UI enhancement components
        self.shortcut_manager = ShortcutManager(self)
        self.error_handler = ErrorHandler(self.master, self.language_var.get())
        self.diagram_manager = DiagramManager(self, self.theme_manager, self.language_var)
        # self.animation_manager = AnimationManager(self.master)
        
        # Register theme change callback
        self.theme_manager.add_theme_change_callback(self.on_theme_change)
        
        # Setup UI and start
        self.setup_ui()
        
        # Set initial theme button text
        self.update_theme_button_text()
        self.setup_event_handlers()
        self.populate_listbox()
        
        # Start background processing
        self.thread_manager.set_progress_callback(self.update_progress_callback)
        self.thread_manager.set_completion_callback(self.completion_callback)
        self.thread_manager.start_processing()
    
    def setup_ui(self) -> None:
        """Setup the user interface with modern styling and theme support."""
        # Configure styling with theme support
        self.ui_styles.configure_root_window(self.master)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create main layout
        self._create_main_layout()
        self._create_left_panel()
        self._create_right_panel()
    
    def _create_menu_bar(self) -> None:
        """Create the application menu bar."""
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)
        
        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=get_translation("EN", "menu_file"), menu=self.file_menu)
        self.file_menu.add_command(label=get_translation("EN", "menu_select_folder"), command=self.select_folder, accelerator="Ctrl+O")
        self.file_menu.add_separator()
        self.file_menu.add_command(label=get_translation("EN", "menu_exit"), command=self.master.quit, accelerator="Ctrl+Q")
        
        # Diagrams menu
        self.diagrams_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="🎨 Diyagramlar", menu=self.diagrams_menu)
        
        # Add diagram types to menu
        diagram_types = {
            "module_dependency": ("📦", "Modül/Bağımlılık Grafiği"),
            "architecture": ("🏗️", "Yüksek‑Düzey Mimari"),
            "class_hierarchy": ("🔗", "Sınıf Hiyerarşisi"),
            "sequence": ("⏭️", "Akış Diyagramı"),
            "data_model": ("🗃️", "Veri Modeli (ER)"),
            "state_machine": ("🔄", "Durum Makinesi")
        }
        
        for diagram_type, (icon, name) in diagram_types.items():
            self.diagrams_menu.add_command(
                label=f"{icon} {name}",
                command=lambda dt=diagram_type: self._generate_specific_diagram(dt)
            )
        
        self.diagrams_menu.add_separator()
        self.diagrams_menu.add_command(label="✨ Diyagram Sihirbazı", command=self.diagram_manager.show_diagram_menu)
        
        # Version menu
        self.version_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=get_translation("EN", "menu_version"), menu=self.version_menu)
        self.version_menu.add_command(label=f"{get_translation('EN', 'menu_current_version')} {APP_VERSION}", state="disabled")
        self.version_menu.add_separator()
        self.version_menu.add_command(label=get_translation("EN", "menu_about"), command=self.show_about)
    
    def _create_main_layout(self) -> None:
        """Create the main layout structure."""
        # Main container
        self.main_container = self.ui_styles.create_card_frame(self.master)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Paned window for left/right split
        self.paned = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
    
    def _create_left_panel(self) -> None:
        """Create the left panel with file browser."""
        # Left container
        left_container = self.ui_styles.create_card_frame(self.paned)
        self.paned.add(left_container, weight=2)
        
        # Header
        header_frame = self.ui_styles.create_card_frame(left_container)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and theme toggle
        title_container = self.ui_styles.create_card_frame(header_frame)
        title_container.pack(fill=tk.X)
        
        self.left_label = ttk.Label(
            title_container, 
            text=get_translation("EN", "directory_content"),
            style="Heading.TLabel"
        )
        self.left_label.pack(side=tk.LEFT, anchor="w")
        
        # Theme toggle button
        self.theme_toggle_button = ttk.Button(
            title_container,
            text="🌙 Dark",
            command=self.toggle_theme,
            style="Modern.TButton",
            width=10
        )
        self.theme_toggle_button.pack(side=tk.RIGHT, padx=(8, 0))
        
        # Up directory button
        self.up_button = ttk.Button(
            title_container,
            text="↑ " + get_translation("EN", "up_directory"),
            command=self.go_up_directory,
            style="Modern.TButton"
        )
        self.up_button.pack(side=tk.RIGHT, padx=(0, 8))
        

        
        # Current path label
        self.current_path_label = ttk.Label(
            left_container,
            text="",
            style="Muted.TLabel"
        )
        self.current_path_label.pack(anchor="w", pady=(0, 16))
        
        # Search section
        self._create_search_section(left_container)
        
        # File tree
        self._create_file_tree(left_container)
        
        # Control buttons
        self._create_control_buttons(left_container)
    
    def _create_search_section(self, parent: tk.Widget) -> None:
        """Create search and filter controls."""
        search_frame = self.ui_styles.create_card_frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            style="Modern.TEntry"
        )
        self.search_entry.pack(fill=tk.X, ipady=4)
        self.search_entry.insert(0, get_translation("EN", "search_placeholder"))
        
        # Show ignored toggle
        ignore_frame = self.ui_styles.create_card_frame(parent)
        ignore_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.show_ignored_var = tk.BooleanVar(value=False)
        self.show_ignored_check = ttk.Checkbutton(
            ignore_frame,
            text=get_translation("EN", "show_ignored"),
            variable=self.show_ignored_var,
            command=self.toggle_ignored_items,
            style="Modern.TCheckbutton"
        )
        self.show_ignored_check.pack(anchor="w")
    
    def _create_file_tree(self, parent: tk.Widget) -> None:
        """Create the file tree view."""
        list_container = self.ui_styles.create_card_frame(parent)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        
        # Tree view
        self.tree = ttk.Treeview(
            list_container,
            columns=("type", "size"),
            show="tree headings",
            selectmode="extended",
            style="Modern.Treeview"
        )
        
        # Configure columns
        self.tree.heading("#0", text="Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("size", text="Size")
        self.tree.column("#0", width=280, stretch=True)
        self.tree.column("type", width=80, stretch=False)
        self.tree.column("size", width=100, anchor="e", stretch=False)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        self.list_scrollbar = self.ui_styles.create_scrollbar(
            list_container, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=self.list_scrollbar.set)
    
    def _create_control_buttons(self, parent: tk.Widget) -> None:
        """Create control buttons."""
        button_frame = self.ui_styles.create_card_frame(parent)
        button_frame.pack(fill=tk.X)
        
        self.select_all_button = ttk.Button(
            button_frame,
            text=get_translation("EN", "select_all"),
            command=self.select_all,
            style="Modern.TButton"
        )
        self.select_all_button.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        
        self.clear_selection_button = ttk.Button(
            button_frame,
            text=get_translation("EN", "clear_selection"),
            command=self.clear_selection,
            style="Modern.TButton"
        )
        self.clear_selection_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_right_panel(self) -> None:
        """Create the right panel with text editor."""
        # Right container
        right_container = self.ui_styles.create_card_frame(self.paned)
        self.paned.add(right_container, weight=3)
        
        # Header with controls
        self._create_right_header(right_container)
        
        # Text editor
        self._create_text_editor(right_container)
        
        # Status bar
        self._create_status_bar(right_container)
    
    def _create_right_header(self, parent: tk.Widget) -> None:
        """Create right panel header with controls."""
        header_frame = self.ui_styles.create_card_frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        self.right_label = ttk.Label(
            header_frame,
            text=get_translation("EN", "source_code"),
            style="Heading.TLabel"
        )
        self.right_label.pack(side=tk.LEFT, anchor="w")
        
        # Controls
        controls_frame = self.ui_styles.create_card_frame(header_frame)
        controls_frame.pack(side=tk.RIGHT)
        
        # Language selector
        self.language_combobox = ttk.Combobox(
            controls_frame,
            values=["EN", "TR", "RU", "ES", "PT", "FR", "IT", "UA", "DE", "NL"],
            state="readonly",
            width=8,
            textvariable=self.language_var,
            style="Modern.TCombobox"
        )
        self.language_combobox.pack(side=tk.LEFT, padx=(0, 8))
        
        # Action buttons
        self.copy_button = ttk.Button(
            controls_frame,
            text=get_translation("EN", "copy"),
            command=self.copy_to_clipboard,
            style="Modern.TButton"
        )
        self.copy_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.save_button = ttk.Button(
            controls_frame,
            text=get_translation("EN", "save"),
            command=self.save_to_file,
            style="Modern.TButton"
        )
        self.save_button.pack(side=tk.LEFT)
    
    def _create_text_editor(self, parent: tk.Widget) -> None:
        """Create the text editor area."""
        text_container = self.ui_styles.create_card_frame(parent)
        text_container.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        
        # Text widget with styling
        self.text = self.ui_styles.create_text_widget(text_container)
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        self.text_scrollbar_y = self.ui_styles.create_scrollbar(
            text_container, orient=tk.VERTICAL, command=self.text.yview
        )
        self.text_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_scrollbar_x = self.ui_styles.create_scrollbar(
            text_container, orient=tk.HORIZONTAL, command=self.text.xview
        )
        self.text_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.text.config(
            yscrollcommand=self.text_scrollbar_y.set,
            xscrollcommand=self.text_scrollbar_x.set
        )
    
    def _create_status_bar(self, parent: tk.Widget) -> None:
        """Create the status bar."""
        self.status_frame = self.ui_styles.create_card_frame(parent)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Token count
        self.token_count_label = ttk.Label(
            self.status_frame,
            text=get_translation("EN", "total_tokens") + "0",
            style="Modern.TLabel"
        )
        self.token_count_label.pack(side=tk.RIGHT, padx=20)
        
        # Status text
        self.status_label = ttk.Label(
            self.status_frame,
            text="Ready to explore your codebase",
            style="Muted.TLabel"
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
    
    def setup_event_handlers(self) -> None:
        """Setup event handlers."""
        # Tree events
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_item_double_click)
        
        # Search events
        self.search_entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)
        
        # Variable traces
        self.language_var.trace_add("write", self.on_language_change)
        self.search_var.trace_add("write", self.on_search_change)
        
        # Text events
        self.text.bind("<<Modified>>", self.on_text_modified)
        
        # Menu keyboard shortcuts
        self.master.bind("<Control-o>", lambda e: self.select_folder())
        self.master.bind("<Control-O>", lambda e: self.select_folder())
        self.master.bind("<Control-q>", lambda e: self.master.quit())
        self.master.bind("<Control-Q>", lambda e: self.master.quit()) 

    # Event handlers and functionality methods
    def on_search_focus_in(self, event):
        """Clear placeholder text when search entry gets focus"""
        placeholder = get_translation(self.language_var.get(), "search_placeholder")
        if self.search_entry.get() == placeholder:
            self.search_entry.delete(0, tk.END)
    
    def on_search_focus_out(self, event):
        """Restore placeholder text when search entry loses focus"""
        if not self.search_entry.get():
            placeholder = get_translation(self.language_var.get(), "search_placeholder")
            self.search_entry.insert(0, placeholder)
    
    def on_search_change(self, *args: Any) -> None:
        """Filter the listbox content based on search term"""
        self.populate_listbox()
    
    def on_language_change(self, *args: Any) -> None:
        """Update the UI elements when the language selection changes."""
        lang: str = self.language_var.get()
        
        # Update error handler language
        self.error_handler.set_language(lang)
        
        self.master.title(get_translation(lang, "title"))
        self.left_label.config(text=get_translation(lang, "directory_content"))
        self.up_button.config(text="↑ " + get_translation(lang, "up_directory"))
        self.select_all_button.config(text=get_translation(lang, "select_all"))
        self.clear_selection_button.config(text=get_translation(lang, "clear_selection"))
        self.right_label.config(text=get_translation(lang, "source_code"))
        self.copy_button.config(text=get_translation(lang, "copy"))
        self.save_button.config(text=get_translation(lang, "save"))
        
        # Update search placeholder
        current_search = self.search_entry.get()
        placeholder = get_translation(lang, "search_placeholder")
        if not current_search or any(current_search == get_translation(l, "search_placeholder") for l in ["EN", "TR", "RU", "ES", "PT", "FR", "IT", "UA", "DE", "NL"]):
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, placeholder)
        
        # Update ignored items toggle text
        if self.show_ignored:
            self.show_ignored_check.config(text=get_translation(lang, "hide_ignored"))
        else:
            self.show_ignored_check.config(text=get_translation(lang, "show_ignored"))
        
        # Update token count
        self.token_count_label.config(
            text=get_translation(lang, "total_tokens") + str(count_tokens(self.text.get("1.0", tk.END)))
        )
        
        # Update menu labels
        self.menubar.entryconfig(0, label=get_translation(lang, "menu_file"))
        self.menubar.entryconfig(1, label="🎨 Diyagramlar")
        self.menubar.entryconfig(2, label=get_translation(lang, "menu_version"))
        
        # Update File menu items
        self.file_menu.entryconfig(0, label=get_translation(lang, "menu_select_folder"))
        self.file_menu.entryconfig(2, label=get_translation(lang, "menu_exit"))
        
        # Update Version menu items
        self.version_menu.entryconfig(0, label=f"{get_translation(lang, 'menu_current_version')} {APP_VERSION}")
        self.version_menu.entryconfig(2, label=get_translation(lang, "menu_about"))
        
        self.populate_listbox()
    
    def toggle_ignored_items(self):
        """Toggle showing ignored items"""
        self.show_ignored = self.show_ignored_var.get()
        self.populate_listbox()
        
        # Update button text
        lang = self.language_var.get()
        if self.show_ignored:
            self.show_ignored_check.config(text=get_translation(lang, "hide_ignored"))
        else:
            self.show_ignored_check.config(text=get_translation(lang, "show_ignored"))
    
    def populate_listbox(self) -> None:
        """List files and folders in the current directory."""
        if not hasattr(self, 'tree'):
            return
            
        try:
            # Clear the tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Get directory listing using file handler
            items = self.file_handler.list_directory(self.current_path, self.show_ignored)
            
            # Filter by search term if provided
            search_term = self.search_var.get().lower()
            placeholder = get_translation(self.language_var.get(), "search_placeholder").lower()
            if search_term and search_term != placeholder:
                items = [item for item in items if search_term in item.name.lower()]
            
            # Separate folders and files
            folders = [item for item in items if item.is_dir()]
            files = [item for item in items if item.is_file()]
            
            # Add folders to tree
            for folder in folders:
                self.tree.insert("", "end", iid=str(folder), 
                               text=folder.name, 
                               values=(get_translation(self.language_var.get(), "folder"), ""))
            
            # Add files to tree
            for file in files:
                file_type = file.suffix[1:].upper() if file.suffix else "File"
                size_str = self.file_handler.get_file_size_str(file)
                self.tree.insert("", "end", iid=str(file), 
                               text=file.name, 
                               values=(file_type, size_str))
            
            # Update current path display
            self.current_path_label.config(text=str(self.current_path))
            
        except Exception as e:
            print(f"Error populating list: {e}")
    
    def on_select(self, event: Any) -> None:
        """Handle file/folder selection in the tree."""
        selections = [self.tree.item(item)['text'] for item in self.tree.selection()]
        if selections:
            self.process_selection(selections)
    
    def on_item_double_click(self, event: Any) -> None:
        """Handle double-click on tree items."""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        item_text = self.tree.item(selected_items[0])['text']
        item_path = self.current_path / item_text
        
        if item_path.is_dir():
            self.file_handler.set_current_path(item_path)
            self.current_path = item_path
            self.populate_listbox()
    
    def go_up_directory(self) -> None:
        """Navigate up one directory level."""
        if self.file_handler.go_up_directory():
            self.current_path = self.file_handler.get_current_path()
            self.populate_listbox()
        else:
            lang = self.language_var.get()
            messagebox.showinfo("Info", get_translation(lang, "root_dir_info"))
    
    def select_all(self) -> None:
        """Select all items in the tree."""
        for item in self.tree.get_children():
            self.tree.selection_add(item)
    
    def clear_selection(self) -> None:
        """Clear all selections in the tree."""
        self.tree.selection_remove(self.tree.selection())
    
    def process_selection(self, selections: List[str]) -> None:
        """Process selected files and generate markdown."""
        if not selections:
            return
            
        def generate_task():
            markdown_parts = []
            total_tokens = 0
            
            for filename in selections:
                file_path = self.current_path / filename
                if file_path.is_file() and self.file_handler.is_text_file(file_path):
                    content = self.file_handler.read_file_content(file_path)
                    if content:
                        # Generate markdown section
                        relative_path = file_path.as_posix()
                        file_extension = file_path.suffix.lower()
                        
                        # Determine syntax highlighting
                        syntax_map = {
                            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                            '.html': 'html', '.css': 'css', '.json': 'json',
                            '.md': 'markdown', '.txt': 'text', '.sh': 'bash',
                            '.sql': 'sql', '.xml': 'xml', '.yaml': 'yaml', '.yml': 'yaml'
                        }
                        syntax = syntax_map.get(file_extension, 'text')
                        
                        markdown_parts.append(f"## {relative_path}\n")
                        markdown_parts.append(f"```{syntax}\n{content}\n```\n\n")
                        
                        # Count tokens
                        section_tokens = count_tokens(content)
                        total_tokens += section_tokens
            
            # Combine all parts
            full_markdown = "".join(markdown_parts)
            return {'markdown': full_markdown, 'total_tokens': total_tokens}
        
        self.thread_manager.add_task(generate_task)
    
    def copy_to_clipboard(self) -> None:
        """Copy text content to clipboard."""
        try:
            content = self.text.get("1.0", tk.END)
            self.master.clipboard_clear()
            self.master.clipboard_append(content)
            lang = self.language_var.get()
            messagebox.showinfo("Success", get_translation(lang, "copy_success"))
        except Exception as e:
            lang = self.language_var.get()
            messagebox.showerror("Error", get_translation(lang, "copy_error") + str(e))
    
    def save_to_file(self) -> None:
        """Save text content to file."""
        try:
            content = self.text.get("1.0", tk.END)
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                lang = self.language_var.get()
                messagebox.showinfo("Success", get_translation(lang, "save_success") + file_path)
        except Exception as e:
            lang = self.language_var.get()
            messagebox.showerror("Error", get_translation(lang, "save_error") + str(e))
    
    def on_text_modified(self, event: Any) -> None:
        """Handle text modification event."""
        if self.text.edit_modified():
            self.update_token_count()
            self.text.edit_modified(False)
    
    def update_token_count(self) -> None:
        """Update token count display."""
        content = self.text.get("1.0", tk.END)
        token_count = count_tokens(content)
        lang = self.language_var.get()
        self.token_count_label.config(
            text=get_translation(lang, "total_tokens") + str(token_count)
        )
    
    # Callback methods for thread manager
    def update_progress_callback(self, message: str) -> None:
        """Callback for progress updates."""
        self.status_label.config(text=message)
    
    def completion_callback(self, result: Any) -> None:
        """Callback for task completion."""
        if result and isinstance(result, dict):
            if 'markdown' in result:
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", result['markdown'])
                self.update_token_count()
            self.status_label.config(text="Ready to explore your codebase")
    
    # Theme management methods
    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        new_theme = self.theme_manager.toggle_theme()
        self.update_theme_button_text()
    
    def update_theme_button_text(self) -> None:
        """Update theme toggle button text based on current theme."""
        if self.theme_manager.is_dark_theme():
            self.theme_toggle_button.config(text="☀️ Light")
        else:
            self.theme_toggle_button.config(text="🌙 Dark")
    
    def on_theme_change(self, old_theme: str, new_theme: str) -> None:
        """Handle theme change event - Update ALL UI elements."""
        try:
            # 1. Update TTK styles first
            self.ui_styles.apply_current_theme()
            
            # 2. Update root window
            colors = self.theme_manager.get_theme_colors()
            self.master.configure(bg=colors['background_primary'])
            
            # 3. Update all Frame widgets recursively
            self._update_all_frames_recursive(self.master, colors)
            
            # 4. Update specific Text widgets
            if hasattr(self, 'text'):
                self.text.configure(
                    bg=colors['background_card'],
                    fg=colors['text_primary'], 
                    insertbackground=colors['accent'],
                    selectbackground=colors['accent']
                )
            
            # 5. Update scrollbars
            self._update_scrollbars(colors)
            
            # 6. Update theme button text
            self.update_theme_button_text()
            
        except Exception as e:
            print(f"Error updating theme: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_all_frames_recursive(self, widget, colors):
        """Recursively update all Frame widgets with new theme colors."""
        try:
            # Update current widget if it's a Frame
            if isinstance(widget, tk.Frame):
                widget.configure(
                    bg=colors['background_card'],
                    highlightbackground=colors['border']
                )
            
            # Recursively update all children
            for child in widget.winfo_children():
                self._update_all_frames_recursive(child, colors)
                
        except Exception as e:
            print(f"Error updating widget {widget}: {e}")
    
    def _update_scrollbars(self, colors):
        """Update all scrollbar colors."""
        try:
            # Update text scrollbars
            if hasattr(self, 'text_scrollbar_y'):
                self.text_scrollbar_y.configure(
                    bg=colors['scrollbar_thumb'],
                    troughcolor=colors['scrollbar_bg'],
                    activebackground=colors['border_hover']
                )
            
            if hasattr(self, 'text_scrollbar_x'):
                self.text_scrollbar_x.configure(
                    bg=colors['scrollbar_thumb'],
                    troughcolor=colors['scrollbar_bg'],
                    activebackground=colors['border_hover']
                )
            
            # Update list scrollbar
            if hasattr(self, 'list_scrollbar'):
                self.list_scrollbar.configure(
                    bg=colors['scrollbar_thumb'],
                    troughcolor=colors['scrollbar_bg'],
                    activebackground=colors['border_hover']
                )
                
        except Exception as e:
            print(f"Error updating scrollbars: {e}")
    
    # Menu handler methods
    def select_folder(self) -> None:
        """Open folder selection dialog and navigate to selected folder."""
        try:
            folder_path = filedialog.askdirectory(
                title="Select Folder",
                initialdir=str(self.current_path)
            )
            
            if folder_path:
                new_path = Path(folder_path)
                if new_path.exists() and new_path.is_dir():
                    self.file_handler.set_current_path(new_path)
                    self.current_path = new_path
                    self.populate_listbox()
                    self.status_label.config(text=f"Navigated to: {folder_path}")
                else:
                    lang = self.language_var.get()
                    messagebox.showerror("Error", f"Invalid folder path: {folder_path}")
        except Exception as e:
            lang = self.language_var.get()
            messagebox.showerror("Error", f"Failed to select folder: {str(e)}")
    
    def show_about(self) -> None:
        """Show about dialog with application information."""
        about_text = f"""CodeContextor Portable {APP_VERSION}

A specialized Python desktop application designed to prepare and send source code to LLM chats.

Features:
• Project scanning and source code collection
• Real-time LLM token estimation
• Smart filtering with ignore patterns
• Multi-language support (10 languages)
• Dark/Light theme toggle
• Modern, professional UI
• AI-powered Mermaid diagram generation

Developer: CodeContextor Team
License: MIT License

Visit our GitHub repository for more information."""
        
        messagebox.showinfo("About CodeContextor", about_text)
    
    def _generate_specific_diagram(self, diagram_type: str) -> None:
        """Generate specific diagram type directly."""
        # Get selected code from text widget
        code_context = ""
        try:
            if hasattr(self, 'text'):
                code_context = self.text.get("1.0", tk.END).strip()
        except:
            pass
        
        if not code_context:
            messagebox.showwarning(
                "Uyarı", 
                "Lütfen önce sol panelden dosyaları seçin ve kod analiz edilsin."
            )
            return
        
        # Generate diagram using diagram manager
        self.diagram_manager._generate_and_preview(diagram_type, code_context) 