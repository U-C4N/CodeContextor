import re
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path
from typing import Any, Dict

# Token counting function: Uses tiktoken if available; otherwise falls back to a regex-based method.
try:
    import tiktoken

    def count_tokens(text: str) -> int:
        """
        Returns the token count of the given text using the "cl100k_base" encoding,
        which is appropriate for LLM contexts.
        """
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return len(tokens)
except ImportError:
    def count_tokens(text: str) -> int:
        """
        Fallback method for token counting using regex when tiktoken is not available.
        """
        tokens = re.findall(r"\w+|[^\w\s]", text, re.UNICODE)
        return len(tokens)


class FileExplorer:
    def __init__(self, master: tk.Tk) -> None:
        """Initialize the File & Folder Viewer with LLM context token counter."""
        self.master: tk.Tk = master
        self.master.title("File & Folder Viewer - LLM Context Token Counter")
        self.master.geometry("900x600")
        
        # Base directory: using pathlib to get the directory where this file is located.
        self.base_path: Path = Path(__file__).resolve().parent
        self.current_path: Path = self.base_path
        
        # Language translations
        self.translations: Dict[str, Dict[str, str]] = {
            "EN": {
                "title": "File & Folder Viewer - LLM Context Token Counter",
                "directory_content": "Directory Content",
                "up_directory": "Up Directory",
                "current_dir": "Current Directory: ",
                "select_all": "Select All",
                "clear_selection": "Clear Selection",
                "source_code": "Source Code (Markdown)",
                "save": "Save (llm.txt)",
                "total_tokens": "Total Token Count: ",
                "folder": "Folder",
                "file_read_error": "File could not be read: ",
                "folder_read_error": "Error: Folder could not be read: ",
                "root_dir_info": "Already in root directory.",
                "root_dir_error": "Cannot go outside root directory.",
                "save_success": "'llm.txt' file saved:\n",
                "save_error": "File could not be saved: ",
                "list_error": "Directory content could not be listed: "
            },
            "TR": {
                "title": "Dosya & Klasör Görüntüleyici - LLM Context Token Sayacı",
                "directory_content": "Dizin İçeriği",
                "up_directory": "Üst Dizin",
                "current_dir": "Mevcut Dizin: ",
                "select_all": "Tümünü Seç",
                "clear_selection": "Seçimi Temizle",
                "source_code": "Kaynak Kod (Markdown)",
                "save": "Kaydet (llm.txt)",
                "total_tokens": "Toplam Token Sayısı: ",
                "folder": "Klasör",
                "file_read_error": "Dosya okunamadı: ",
                "folder_read_error": "Hata: Klasör okunamadı: ",
                "root_dir_info": "Zaten kök dizindesiniz.",
                "root_dir_error": "Kök dizinin dışına çıkamazsınız.",
                "save_success": "'llm.txt' dosyası kaydedildi:\n",
                "save_error": "Dosya kaydedilemedi: ",
                "list_error": "Dizin içeriği listelenemedi: "
            },
            "RU": {
                "title": "Просмотрщик файлов и папок - Счетчик токенов LLM Context",
                "directory_content": "Содержимое каталога",
                "up_directory": "Вверх",
                "current_dir": "Текущий каталог: ",
                "select_all": "Выбрать все",
                "clear_selection": "Очистить выбор",
                "source_code": "Исходный код (Markdown)",
                "save": "Сохранить (llm.txt)",
                "total_tokens": "Общее количество токенов: ",
                "folder": "Папка",
                "file_read_error": "Не удалось прочитать файл: ",
                "folder_read_error": "Ошибка: Не удалось прочитать папку: ",
                "root_dir_info": "Уже в корневом каталоге.",
                "root_dir_error": "Нельзя выйти за пределы корневого каталога.",
                "save_success": "Файл 'llm.txt' сохранен:\n",
                "save_error": "Не удалось сохранить файл: ",
                "list_error": "Не удалось получить содержимое каталога: "
            }
        }
        
        self.setup_ui()
        self.populate_listbox()
        
        # Listen for language changes
        self.language_var.trace_add("write", self.on_language_change)
    
    def setup_ui(self) -> None:
        """Setup the user interface."""
        # Create main panels using PanedWindow (left: list, right: content)
        self.paned: ttk.PanedWindow = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # LEFT PANEL: Area listing directory contents and navigation buttons
        self.left_frame: ttk.Frame = ttk.Frame(self.paned, padding=10)
        self.paned.add(self.left_frame, weight=1)
        
        header_frame: ttk.Frame = ttk.Frame(self.left_frame)
        header_frame.pack(fill=tk.X)
        
        self.left_label: ttk.Label = ttk.Label(
            header_frame, text=self.translations["EN"]["directory_content"], font=("Arial", 12, "bold")
        )
        self.left_label.pack(side=tk.LEFT, anchor="w")
        
        self.up_button: ttk.Button = ttk.Button(
            header_frame, text=self.translations["EN"]["up_directory"], command=self.go_up_directory
        )
        self.up_button.pack(side=tk.RIGHT)
        
        self.current_path_label: ttk.Label = ttk.Label(self.left_frame, text="", font=("Arial", 10))
        self.current_path_label.pack(anchor="w", pady=(5, 5))
        
        self.list_frame: ttk.Frame = ttk.Frame(self.left_frame)
        self.list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.listbox: tk.Listbox = tk.Listbox(self.list_frame, selectmode=tk.EXTENDED, font=("Consolas", 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.list_scrollbar: ttk.Scrollbar = ttk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=self.list_scrollbar.set)
        
        # Bind selection and double-click events to the listbox
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        self.listbox.bind("<Double-Button-1>", self.on_item_double_click)
        
        # Additional selection control buttons
        self.left_button_frame: ttk.Frame = ttk.Frame(self.left_frame)
        self.left_button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.select_all_button: ttk.Button = ttk.Button(
            self.left_button_frame, text=self.translations["EN"]["select_all"], command=self.select_all
        )
        self.select_all_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_selection_button: ttk.Button = ttk.Button(
            self.left_button_frame, text=self.translations["EN"]["clear_selection"], command=self.clear_selection
        )
        self.clear_selection_button.pack(side=tk.LEFT)
        
        # RIGHT PANEL: Displays the source code in Markdown format and the LLM context token count
        self.right_frame: ttk.Frame = ttk.Frame(self.paned, padding=10)
        self.paned.add(self.right_frame, weight=3)
        
        # Top section: Layout for the header area of the right panel using grid
        top_right_frame: ttk.Frame = ttk.Frame(self.right_frame)
        top_right_frame.pack(fill=tk.X)
        
        self.right_label: ttk.Label = ttk.Label(
            top_right_frame, text=self.translations["EN"]["source_code"], font=("Arial", 12, "bold")
        )
        self.right_label.grid(row=0, column=0, sticky="w")
        
        # Language mode select box in the top right corner (default "EN", options: EN, TR, RU)
        self.language_var: tk.StringVar = tk.StringVar(value="EN")
        language_combobox: ttk.Combobox = ttk.Combobox(
            top_right_frame, values=["EN", "TR", "RU"], state="readonly", width=5, textvariable=self.language_var
        )
        language_combobox.grid(row=0, column=3, sticky="e", padx=(0, 5))
        
        self.save_button: ttk.Button = ttk.Button(
            top_right_frame, text=self.translations["EN"]["save"], command=self.save_to_file
        )
        self.save_button.grid(row=0, column=2, sticky="e", padx=(5, 5))
        
        top_right_frame.columnconfigure(1, weight=1)
        
        # Text widget for Markdown source code
        self.text: tk.Text = tk.Text(self.right_frame, wrap=tk.NONE, font=("Consolas", 10))
        self.text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.text_scrollbar: ttk.Scrollbar = ttk.Scrollbar(self.right_frame, orient=tk.VERTICAL, command=self.text.yview)
        self.text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=self.text_scrollbar.set)
        
        # Bottom frame for token count label so it is not hidden by the text widget
        self.bottom_frame: tk.Frame = tk.Frame(self.right_frame, bg="#222222")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Use tk.Label here (instead of ttk) to allow custom background and foreground colors.
        self.token_count_label: tk.Label = tk.Label(
            self.bottom_frame,
            text=self.translations["EN"]["total_tokens"] + "0",
            font=("Arial", 10, "bold"),
            bg="#222222",
            fg="#FFFFFF"
        )
        self.token_count_label.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Bind the <<Modified>> virtual event to update token count when the text content changes
        self.text.bind("<<Modified>>", self.on_text_modified)
    
    def on_language_change(self, *args: Any) -> None:
        """Update the UI elements when the language selection changes."""
        lang: str = self.language_var.get()
        self.master.title(self.translations[lang]["title"])
        self.left_label.config(text=self.translations[lang]["directory_content"])
        self.up_button.config(text=self.translations[lang]["up_directory"])
        self.select_all_button.config(text=self.translations[lang]["select_all"])
        self.clear_selection_button.config(text=self.translations[lang]["clear_selection"])
        self.right_label.config(text=self.translations[lang]["source_code"])
        self.save_button.config(text=self.translations[lang]["save"])
        self.token_count_label.config(
            text=self.translations[lang]["total_tokens"] + str(count_tokens(self.text.get("1.0", tk.END)))
        )
        self.populate_listbox()  # Update the current directory label
    
    def populate_listbox(self) -> None:
        """
        List files and folders in the current directory in alphabetical order.
        """
        try:
            items = sorted([p.name for p in self.current_path.iterdir()], key=lambda s: s.lower())
            self.listbox.delete(0, tk.END)
            for item in items:
                self.listbox.insert(tk.END, item)
            # Get the relative current path with respect to the base directory
            try:
                rel_current = str(self.current_path.relative_to(self.base_path))
            except ValueError:
                rel_current = str(self.current_path)
            if rel_current == ".":
                rel_current = self.base_path.name
            lang: str = self.language_var.get()
            self.current_path_label.config(text=f"{self.translations[lang]['current_dir']}{rel_current}")
            if self.current_path == self.base_path:
                self.up_button.state(["disabled"])
            else:
                self.up_button.state(["!disabled"])
        except Exception as e:
            lang = self.language_var.get()
            messagebox.showerror("Error", f"{self.translations[lang]['list_error']}{e}")
    
    def get_markdown_for_path(self, path: Path) -> str:
        """
        Generate Markdown content for the given file or folder path.
          - File: Uses the relative path as a header and includes its content inside a code block.
          - Folder: Uses the folder name as a header and recursively includes all files/folders inside.
        """
        try:
            rel_path = path.relative_to(self.base_path)
        except ValueError:
            rel_path = path
        display_path: str = f"{self.base_path.name}/{rel_path.as_posix()}"
        lang: str = self.language_var.get()
        
        if path.is_file():
            try:
                content: str = path.read_text(encoding="utf-8")
            except Exception as e:
                content = f"{self.translations[lang]['file_read_error']}{e}"
            markdown_str: str = f"## {display_path}\n\n```python\n{content}\n```\n\n"
            return markdown_str
        elif path.is_dir():
            markdown_str: str = f"## {display_path} ({self.translations[lang]['folder']})\n\n"
            try:
                for item in sorted(path.iterdir(), key=lambda p: p.name.lower()):
                    markdown_str += self.get_markdown_for_path(item)
            except Exception as e:
                markdown_str += f"{self.translations[lang]['folder_read_error']}{e}\n\n"
            return markdown_str
        else:
            return ""
    
    def on_select(self, event: Any) -> None:
        """
        When an item is selected in the listbox, insert the Markdown content 
        of the selected file(s) or folder(s) into the Text widget.
        """
        widget = getattr(event, "widget", self.listbox)
        selections = widget.curselection()
        self.text.delete("1.0", tk.END)
        if not selections:
            self.update_token_count()
            return
        full_markdown: str = ""
        for index in selections:
            item_name: str = self.listbox.get(index)
            full_path: Path = self.current_path / item_name
            full_markdown += self.get_markdown_for_path(full_path)
        self.text.insert(tk.END, full_markdown)
        self.update_token_count()
    
    def on_item_double_click(self, event: Any) -> None:
        """
        If a folder is double-clicked in the listbox, navigate into that folder.
        """
        selection = self.listbox.curselection()
        if not selection:
            return
        index: int = selection[0]
        item_name: str = self.listbox.get(index)
        full_path: Path = self.current_path / item_name
        if full_path.is_dir():
            self.current_path = full_path
            self.populate_listbox()
            self.text.delete("1.0", tk.END)
            self.update_token_count()
    
    def go_up_directory(self) -> None:
        """
        Navigate to the parent directory (preventing navigation outside the base directory).
        """
        lang: str = self.language_var.get()
        if self.current_path == self.base_path:
            messagebox.showinfo("Info", self.translations[lang]["root_dir_info"])
            return
        new_path: Path = self.current_path.parent
        try:
            new_path.relative_to(self.base_path)
        except ValueError:
            messagebox.showerror("Error", self.translations[lang]["root_dir_error"])
            return
        self.current_path = new_path
        self.populate_listbox()
        self.text.delete("1.0", tk.END)
        self.update_token_count()
    
    def select_all(self) -> None:
        """Select all items in the listbox."""
        self.listbox.select_set(0, tk.END)
        # Create a dummy event object with a 'widget' attribute set to self.listbox.
        dummy_event = type("DummyEvent", (), {})()
        dummy_event.widget = self.listbox
        self.on_select(dummy_event)
    
    def clear_selection(self) -> None:
        """Clear the selection in the listbox and clear the Text widget."""
        self.listbox.select_clear(0, tk.END)
        self.text.delete("1.0", tk.END)
        self.update_token_count()
    
    def save_to_file(self) -> None:
        """Save the Markdown content from the Text widget to 'llm.txt' in the base directory."""
        content: str = self.text.get("1.0", tk.END)
        file_path: Path = self.base_path / "llm.txt"
        lang: str = self.language_var.get()
        try:
            file_path.write_text(content, encoding="utf-8")
            messagebox.showinfo("Success", f"{self.translations[lang]['save_success']}{str(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"{self.translations[lang]['save_error']}{e}")
    
    def update_token_count(self) -> None:
        """Calculate the token count of the text and update the token count label."""
        content: str = self.text.get("1.0", tk.END)
        token_count: int = count_tokens(content)
        lang: str = self.language_var.get()
        self.token_count_label.config(text=f"{self.translations[lang]['total_tokens']}{token_count}")
    
    def on_text_modified(self, event: Any) -> None:
        """
        Triggered when the <<Modified>> event occurs in the Text widget;
        updates the token count after text changes.
        Note: The event may trigger twice in some cases, so the modified flag is reset.
        """
        self.update_token_count()
        self.text.edit_modified(False)


def main() -> None:
    """Main function to run the File Explorer application."""
    root: tk.Tk = tk.Tk()
    # Set the overall window transparency to 95%
    root.attributes("-alpha", 0.95)
    style: ttk.Style = ttk.Style(root)
    style.theme_use("clam")
    app = FileExplorer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
