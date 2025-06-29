import re
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from pathlib import Path
from typing import Any, Dict, List, Tuple, Set, Optional
import threading
import time
import functools
from queue import Queue

# Ignore patterns for cache/build directories and files
IGNORE_PATTERNS = {
    # Directories to ignore completely
    'node_modules', '__pycache__', '.next', '.cache', '.git', '.vscode', '.vs', 
    'dist', 'build', 'out', '.nuxt', '.vitepress', '.svelte-kit', 'target', 
    'vendor', '.gradle', '.idea', 'bin', 'obj', '.angular', '.turbo',
    '.parcel-cache', '.tmp', 'tmp', 'temp', '.temp', 'coverage', '.coverage',
    '.pytest_cache', '.mypy_cache', '.tox', 'venv', '.venv', 'env', '.env',
    '.virtualenv', 'virtualenv', 'Pods', 'DerivedData', '.expo', '.meteor',
    '.serverless', '.terraform', '.vagrant', 'logs', '.logs', '.sass-cache',
    '.rpt2_cache', '.nyc_output', 'bower_components', 'jspm_packages',
    'web_modules', '.yarn', '.pnp', '.pnp.js', 'lerna-debug.log*',
    'npm-debug.log*', 'yarn-debug.log*', 'yarn-error.log*', '.DS_Store',
    'Thumbs.db', '.cursor', 'debug'
}

# File extensions to ignore
IGNORE_EXTENSIONS = {
    '.log', '.tmp', '.temp', '.bak', '.backup', '.swp', '.swo', '.orig',
    '.rej', '.patch', '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
    '.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.tar.gz', '.zip',
    '.rar', '.7z', '.iso', '.img', '.bin', '.dat', '.dump', '.lock'
}

def should_ignore_path(path: Path) -> bool:
    """Check if a path should be ignored based on ignore patterns."""
    # Check if it's a directory with ignored name
    if path.is_dir() and path.name.lower() in IGNORE_PATTERNS:
        return True
    
    # Check if it's a file with ignored extension
    if path.is_file() and path.suffix.lower() in IGNORE_EXTENSIONS:
        return True
    
    # Check if it's a hidden file (starts with .) except for some common ones
    if path.name.startswith('.') and path.name not in {'.gitignore', '.env.example', '.env.template', '.editorconfig', '.dockerignore', '.htaccess'}:
        return True
        
    return False

# Token counting function: Uses tiktoken if available; otherwise falls back to a regex-based method.
try:
    import tiktoken
    
    # Enhanced cache for token counts with TTL and size management
    token_cache = {}
    cache_timestamps = {}
    MAX_CACHE_SIZE = 200
    CACHE_TTL = 300  # 5 minutes
    
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
    MAX_CACHE_SIZE = 100
    CACHE_TTL = 300  # 5 minutes
    
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
            if len(token_cache) >= MAX_CACHE_SIZE:
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

def threaded(fn):
    """Decorator to run a function in a separate thread"""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper


class FileExplorer:
    def __init__(self, master: tk.Tk) -> None:
        """Initialize the File & Folder Viewer with LLM context token counter."""
        self.master: tk.Tk = master
        self.master.title("Code Contextor Portable")
        self.master.geometry("1200x800")
        self.master.minsize(800, 600)
        
        # Base directory: using pathlib to get the directory where this file is located.
        self.base_path: Path = Path(__file__).resolve().parent
        self.current_path: Path = self.base_path
        
        # Threading and task management
        self.task_queue = Queue()
        self.is_processing = False
        self.cancel_processing = False
        
        # Cache for directory listings and file contents
        self.dir_cache: Dict[Path, List[Path]] = {}
        self.file_content_cache: Dict[Path, str] = {}
        self.max_cache_size = 50  # Maximum number of files to cache
        
        # Language translations with clean minimal strings
        self.translations: Dict[str, Dict[str, str]] = {
            "EN": {
                "title": "Code Contextor Portable",
                "directory_content": "Files",
                "up_directory": "Up",
                "current_dir": "",
                "select_all": "Select All",
                "clear_selection": "Clear",
                "source_code": "Source Code",
                "save": "Save",
                "copy": "Copy",
                "total_tokens": "Tokens: ",
                "folder": "folder",
                "file_read_error": "Cannot read file: ",
                "folder_read_error": "Cannot read folder: ",
                "root_dir_info": "Already in root directory",
                "root_dir_error": "Cannot go outside root directory",
                "save_success": "Saved to: ",
                "save_error": "Save failed: ",
                "copy_success": "Copied to clipboard!",
                "copy_error": "Copy failed: ",
                "list_error": "Cannot list directory: ",
                "processing": "Processing...",
                "cancel": "Cancel",
                "search_placeholder": "Search...",
                "ignored_items": "Ignored items",
                "show_ignored": "Show ignored",
                "hide_ignored": "Hide ignored"
            },
            "TR": {
                "title": "Code Contextor Portable",
                "directory_content": "Dosyalar",
                "up_directory": "Yukarı",
                "current_dir": "",
                "select_all": "Tümünü Seç",
                "clear_selection": "Temizle",
                "source_code": "Kaynak Kod",
                "save": "Kaydet",
                "copy": "Kopyala",
                "total_tokens": "Token: ",
                "folder": "klasör",
                "file_read_error": "Dosya okunamadı: ",
                "folder_read_error": "Klasör okunamadı: ",
                "root_dir_info": "Zaten kök dizinde",
                "root_dir_error": "Kök dizin dışına çıkılamaz",
                "save_success": "Kaydedildi: ",
                "save_error": "Kayıt başarısız: ",
                "copy_success": "Panoya kopyalandı!",
                "copy_error": "Kopyalama başarısız: ",
                "list_error": "Dizin listelenemedi: ",
                "processing": "İşleniyor...",
                "cancel": "İptal",
                "search_placeholder": "Ara...",
                "ignored_items": "Gizlenen öğeler",
                "show_ignored": "Gizlenenleri göster",
                "hide_ignored": "Gizlenenleri sakla"
            },
            "RU": {
                "title": "Code Contextor Portable",
                "directory_content": "Файлы",
                "up_directory": "Вверх",
                "current_dir": "",
                "select_all": "Выбрать все",
                "clear_selection": "Очистить",
                "source_code": "Исходный код",
                "save": "Сохранить",
                "copy": "Копировать",
                "total_tokens": "Токены: ",
                "folder": "папка",
                "file_read_error": "Не удалось прочитать файл: ",
                "folder_read_error": "Не удалось прочитать папку: ",
                "root_dir_info": "Уже в корневом каталоге",
                "root_dir_error": "Нельзя выйти за пределы корневого каталога",
                "save_success": "Сохранено в: ",
                "save_error": "Ошибка сохранения: ",
                "copy_success": "Скопировано в буфер обмена!",
                "copy_error": "Ошибка копирования: ",
                "list_error": "Не удалось получить список: ",
                "processing": "Обработка...",
                "cancel": "Отмена",
                "search_placeholder": "Поиск...",
                "ignored_items": "Скрытые элементы",
                "show_ignored": "Показать скрытые",
                "hide_ignored": "Скрыть скрытые"
            },
            "ES": {
                "title": "Code Contextor Portable",
                "directory_content": "Archivos",
                "up_directory": "Arriba",
                "current_dir": "",
                "select_all": "Seleccionar todo",
                "clear_selection": "Limpiar",
                "source_code": "Código fuente",
                "save": "Guardar",
                "copy": "Copiar",
                "total_tokens": "Tokens: ",
                "folder": "carpeta",
                "file_read_error": "No se puede leer el archivo: ",
                "folder_read_error": "No se puede leer la carpeta: ",
                "root_dir_info": "Ya en directorio raíz",
                "root_dir_error": "No se puede salir del directorio raíz",
                "save_success": "Guardado en: ",
                "save_error": "Error al guardar: ",
                "copy_success": "¡Copiado al portapapeles!",
                "copy_error": "Error al copiar: ",
                "list_error": "No se puede listar el directorio: ",
                "processing": "Procesando...",
                "cancel": "Cancelar",
                "search_placeholder": "Buscar...",
                "ignored_items": "Elementos ignorados",
                "show_ignored": "Mostrar ignorados",
                "hide_ignored": "Ocultar ignorados"
            },
            "PT": {
                "title": "Code Contextor Portable",
                "directory_content": "Arquivos",
                "up_directory": "Acima",
                "current_dir": "",
                "select_all": "Selecionar tudo",
                "clear_selection": "Limpar",
                "source_code": "Código fonte",
                "save": "Salvar",
                "copy": "Copiar",
                "total_tokens": "Tokens: ",
                "folder": "pasta",
                "file_read_error": "Não é possível ler o arquivo: ",
                "folder_read_error": "Não é possível ler a pasta: ",
                "root_dir_info": "Já no diretório raiz",
                "root_dir_error": "Não é possível sair do diretório raiz",
                "save_success": "Salvo em: ",
                "save_error": "Erro ao salvar: ",
                "copy_success": "Copiado para a área de transferência!",
                "copy_error": "Erro ao copiar: ",
                "list_error": "Não é possível listar o diretório: ",
                "processing": "Processando...",
                "cancel": "Cancelar",
                "search_placeholder": "Pesquisar...",
                "ignored_items": "Itens ignorados",
                "show_ignored": "Mostrar ignorados",
                "hide_ignored": "Ocultar ignorados"
            },
            "FR": {
                "title": "Code Contextor Portable",
                "directory_content": "Fichiers",
                "up_directory": "Haut",
                "current_dir": "",
                "select_all": "Tout sélectionner",
                "clear_selection": "Effacer",
                "source_code": "Code source",
                "save": "Enregistrer",
                "copy": "Copier",
                "total_tokens": "Tokens: ",
                "folder": "dossier",
                "file_read_error": "Impossible de lire le fichier: ",
                "folder_read_error": "Impossible de lire le dossier: ",
                "root_dir_info": "Déjà dans le répertoire racine",
                "root_dir_error": "Impossible de sortir du répertoire racine",
                "save_success": "Enregistré dans: ",
                "save_error": "Erreur de sauvegarde: ",
                "copy_success": "Copié dans le presse-papiers!",
                "copy_error": "Erreur de copie: ",
                "list_error": "Impossible de lister le répertoire: ",
                "processing": "Traitement...",
                "cancel": "Annuler",
                "search_placeholder": "Rechercher...",
                "ignored_items": "Éléments ignorés",
                "show_ignored": "Afficher ignorés",
                "hide_ignored": "Masquer ignorés"
            },
            "IT": {
                "title": "Code Contextor Portable",
                "directory_content": "File",
                "up_directory": "Su",
                "current_dir": "",
                "select_all": "Seleziona tutto",
                "clear_selection": "Cancella",
                "source_code": "Codice sorgente",
                "save": "Salva",
                "copy": "Copia",
                "total_tokens": "Token: ",
                "folder": "cartella",
                "file_read_error": "Impossibile leggere il file: ",
                "folder_read_error": "Impossibile leggere la cartella: ",
                "root_dir_info": "Già nella directory radice",
                "root_dir_error": "Impossibile uscire dalla directory radice",
                "save_success": "Salvato in: ",
                "save_error": "Errore di salvataggio: ",
                "copy_success": "Copiato negli appunti!",
                "copy_error": "Errore di copia: ",
                "list_error": "Impossibile elencare la directory: ",
                "processing": "Elaborazione...",
                "cancel": "Annulla",
                "search_placeholder": "Cerca...",
                "ignored_items": "Elementi ignorati",
                "show_ignored": "Mostra ignorati",
                "hide_ignored": "Nascondi ignorati"
            },
            "UA": {
                "title": "Code Contextor Portable",
                "directory_content": "Файли",
                "up_directory": "Вгору",
                "current_dir": "",
                "select_all": "Вибрати все",
                "clear_selection": "Очистити",
                "source_code": "Вихідний код",
                "save": "Зберегти",
                "copy": "Копіювати",
                "total_tokens": "Токени: ",
                "folder": "папка",
                "file_read_error": "Неможливо прочитати файл: ",
                "folder_read_error": "Неможливо прочитати папку: ",
                "root_dir_info": "Вже в кореневому каталозі",
                "root_dir_error": "Неможливо вийти за межі кореневого каталогу",
                "save_success": "Збережено в: ",
                "save_error": "Помилка збереження: ",
                "copy_success": "Скопійовано в буфер обміну!",
                "copy_error": "Помилка копіювання: ",
                "list_error": "Неможливо отримати список каталогу: ",
                "processing": "Обробка...",
                "cancel": "Скасувати",
                "search_placeholder": "Пошук...",
                "ignored_items": "Проігноровані елементи",
                "show_ignored": "Показати проігноровані",
                "hide_ignored": "Сховати проігноровані"
            },
            "DE": {
                "title": "Code Contextor Portable",
                "directory_content": "Dateien",
                "up_directory": "Hoch",
                "current_dir": "",
                "select_all": "Alle auswählen",
                "clear_selection": "Löschen",
                "source_code": "Quellcode",
                "save": "Speichern",
                "copy": "Kopieren",
                "total_tokens": "Token: ",
                "folder": "ordner",
                "file_read_error": "Datei kann nicht gelesen werden: ",
                "folder_read_error": "Ordner kann nicht gelesen werden: ",
                "root_dir_info": "Bereits im Stammverzeichnis",
                "root_dir_error": "Kann Stammverzeichnis nicht verlassen",
                "save_success": "Gespeichert in: ",
                "save_error": "Speicherfehler: ",
                "copy_success": "In die Zwischenablage kopiert!",
                "copy_error": "Kopierfehler: ",
                "list_error": "Verzeichnis kann nicht aufgelistet werden: ",
                "processing": "Verarbeitung...",
                "cancel": "Abbrechen",
                "search_placeholder": "Suchen...",
                "ignored_items": "Ignorierte Elemente",
                "show_ignored": "Ignorierte anzeigen",
                "hide_ignored": "Ignorierte verbergen"
            },
            "NL": {
                "title": "Code Contextor Portable",
                "directory_content": "Bestanden",
                "up_directory": "Omhoog",
                "current_dir": "",
                "select_all": "Alles selecteren",
                "clear_selection": "Wissen",
                "source_code": "Broncode",
                "save": "Opslaan",
                "copy": "Kopiëren",
                "total_tokens": "Tokens: ",
                "folder": "map",
                "file_read_error": "Kan bestand niet lezen: ",
                "folder_read_error": "Kan map niet lezen: ",
                "root_dir_info": "Al in hoofdmap",
                "root_dir_error": "Kan hoofdmap niet verlaten",
                "save_success": "Opgeslagen in: ",
                "save_error": "Fout bij opslaan: ",
                "copy_success": "Gekopieerd naar klembord!",
                "copy_error": "Fout bij kopiëren: ",
                "list_error": "Kan map niet weergeven: ",
                "processing": "Verwerken...",
                "cancel": "Annuleren",
                "search_placeholder": "Zoeken...",
                "ignored_items": "Genegeerde items",
                "show_ignored": "Genegeerde tonen",
                "hide_ignored": "Genegeerde verbergen"
            }
        }
        
        # Show ignored items toggle
        self.show_ignored = False
        
        # Initialize language_var before setup_ui
        self.language_var: tk.StringVar = tk.StringVar(value="EN")
        
        self.setup_ui()
        
        # Add traces after UI is fully set up
        self.language_var.trace_add("write", self.on_language_change)
        self.search_var.trace_add("write", self.on_search_change)
        
        self.populate_listbox()
        
        # Start the task processing thread
        self.process_tasks_thread = threading.Thread(target=self.process_tasks, daemon=True)
        self.process_tasks_thread.start()
    
    def setup_ui(self) -> None:
        """Setup the user interface with shadcn/ui inspired design."""
        # Configure modern style with shadcn/ui inspired colors
        style = ttk.Style()
        style.theme_use("clam")
        
        # shadcn/ui inspired color scheme - completely white background
        bg_primary = "#ffffff"      # White background
        bg_secondary = "#ffffff"    # Completely white background (changed from #f9fafb)
        bg_card = "#ffffff"         # Card background
        border_color = "#e5e7eb"    # Soft gray border
        text_primary = "#111827"    # Almost black text
        text_secondary = "#6b7280"  # Gray text
        text_muted = "#9ca3af"      # Muted text
        accent_color = "#3b82f6"    # Blue accent
        accent_hover = "#2563eb"    # Darker blue on hover
        success_color = "#10b981"   # Green
        danger_color = "#ef4444"    # Red
        
        # Configure main window background - completely white
        self.master.configure(bg=bg_primary)
        
        # Configure styles with shadcn/ui design
        style.configure("Card.TFrame", 
                       background=bg_card, 
                       relief="flat",
                       borderwidth=1)
        
        style.configure("Background.TFrame", 
                       background=bg_primary,  # Changed to completely white
                       relief="flat")
        
        style.configure("ShadcnUI.TButton", 
                       padding=(12, 8), 
                       font=("Inter", 9),
                       borderwidth=1,
                       relief="flat",
                       focuscolor="none")
        style.map("ShadcnUI.TButton",
                 background=[("active", "#f8fafc"), ("!active", bg_card)],
                 foreground=[("active", text_primary), ("!active", text_primary)],
                 bordercolor=[("focus", accent_color), ("!focus", border_color)])
                 
        style.configure("Primary.TButton", 
                       padding=(12, 8), 
                       font=("Inter", 9, "bold"),
                       borderwidth=0,
                       relief="flat",
                       focuscolor="none")
        style.map("Primary.TButton",
                 background=[("active", accent_hover), ("!active", accent_color)],
                 foreground=[("active", "white"), ("!active", "white")])
        
        style.configure("Success.TButton", 
                       padding=(12, 8), 
                       font=("Inter", 9, "bold"),
                       borderwidth=0,
                       relief="flat",
                       focuscolor="none")
        style.map("Success.TButton",
                 background=[("active", "#059669"), ("!active", success_color)],
                 foreground=[("active", "white"), ("!active", "white")])
        
        style.configure("Ghost.TButton", 
                       padding=(12, 8), 
                       font=("Inter", 9),
                       borderwidth=0,
                       relief="flat",
                       focuscolor="none")
        style.map("Ghost.TButton",
                 background=[("active", "#f8fafc"), ("!active", "transparent")],
                 foreground=[("active", text_primary), ("!active", text_primary)])
        
        style.configure("ShadcnUI.TLabel", 
                       background=bg_card, 
                       foreground=text_primary,
                       font=("Inter", 10))
        style.configure("Heading.TLabel", 
                       font=("Inter", 16, "bold"),
                       foreground=text_primary,
                       background=bg_card)
        style.configure("Muted.TLabel", 
                       font=("Inter", 9),
                       foreground=text_muted,
                       background=bg_card)
        
        # Configure Treeview with shadcn/ui look
        style.configure("ShadcnUI.Treeview",
                       background=bg_card,
                       foreground=text_primary,
                       fieldbackground=bg_card,
                       borderwidth=1,
                       relief="solid",
                       font=("Inter", 9))
        style.configure("ShadcnUI.Treeview.Heading",
                       background="#f8fafc",
                       foreground=text_secondary,
                       font=("Inter", 9),
                       borderwidth=0,
                       relief="flat")
        style.map("ShadcnUI.Treeview",
                 background=[("selected", "#eff6ff")],
                 foreground=[("selected", text_primary)])
        
        # Configure Entry with shadcn/ui style
        style.configure("ShadcnUI.TEntry",
                       fieldbackground=bg_card,
                       borderwidth=1,
                       relief="solid",
                       insertcolor=text_primary,
                       font=("Inter", 10))
        style.map("ShadcnUI.TEntry",
                 bordercolor=[("focus", accent_color), ("!focus", border_color)])
        
        # Configure Checkbutton
        style.configure("ShadcnUI.TCheckbutton",
                       background=bg_card,
                       foreground=text_primary,
                       focuscolor="none",
                       font=("Inter", 9))
        
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
            header_frame, text=self.translations["EN"]["directory_content"], style="Heading.TLabel"
        )
        self.left_label.pack(side=tk.LEFT, anchor="w")
        
        self.up_button: ttk.Button = ttk.Button(
            header_frame, text="↑ " + self.translations["EN"]["up_directory"], 
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
        search_entry.insert(0, self.translations["EN"]["search_placeholder"])
        search_entry.bind("<FocusIn>", self.on_search_focus_in)
        search_entry.bind("<FocusOut>", self.on_search_focus_out)
        self.search_entry = search_entry
        
        # Toggle for showing ignored items with shadcn/ui checkbox style
        ignore_frame = ttk.Frame(self.left_frame, style="Card.TFrame")
        ignore_frame.pack(fill=tk.X, pady=(0, 16))
        
        self.show_ignored_var = tk.BooleanVar(value=False)
        self.show_ignored_check = ttk.Checkbutton(
            ignore_frame, 
            text=self.translations["EN"]["show_ignored"],
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
            self.left_button_frame, text=self.translations["EN"]["select_all"], 
            command=self.select_all, style="ShadcnUI.TButton"
        )
        self.select_all_button.pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
        
        self.clear_selection_button: ttk.Button = ttk.Button(
            self.left_button_frame, text=self.translations["EN"]["clear_selection"], 
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
            top_right_frame, text=self.translations["EN"]["source_code"], style="Heading.TLabel"
        )
        self.right_label.grid(row=0, column=0, sticky="w")
        
        # Progress section with minimal design
        self.progress_frame = ttk.Frame(top_right_frame, style="Card.TFrame")
        self.progress_frame.grid(row=0, column=1, sticky="e", padx=(20, 0))
        
        self.progress_label = ttk.Label(self.progress_frame, text="", style="Muted.TLabel")
        self.progress_label.pack(side=tk.LEFT, padx=(0, 12))
        
        self.cancel_button = ttk.Button(
            self.progress_frame, text=self.translations["EN"]["cancel"], 
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
            controls_frame, text=self.translations["EN"]["copy"], 
            command=self.copy_to_clipboard, style="Success.TButton"
        )
        self.copy_button.pack(side=tk.LEFT, padx=(0, 8))
        
        self.save_button: ttk.Button = ttk.Button(
            controls_frame, text=self.translations["EN"]["save"], 
            command=self.save_to_file, style="Primary.TButton"
        )
        self.save_button.pack(side=tk.LEFT)
        
        top_right_frame.columnconfigure(1, weight=1)
        
        # Text widget with clean styling
        text_container = ttk.Frame(self.right_frame, style="Card.TFrame")
        text_container.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
        
        # Add border frame for text widget
        text_border = tk.Frame(text_container, bg=border_color, highlightthickness=1, highlightbackground=border_color)
        text_border.pack(fill=tk.BOTH, expand=True)
        
        self.text: tk.Text = tk.Text(
            text_border, wrap=tk.NONE, font=("JetBrains Mono", 10), 
            bg=bg_card, fg=text_primary, insertbackground=accent_color,
            selectbackground="#dbeafe", selectforeground=text_primary,
            borderwidth=0, highlightthickness=0,
            padx=16, pady=16
        )
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
        self.text.tag_configure("header", foreground=accent_color, font=("JetBrains Mono", 12, "bold"))
        self.text.tag_configure("code_block", foreground=text_primary, background="#f9fafb")
        self.text.tag_configure("code_marker", foreground=text_muted, font=("JetBrains Mono", 9))
        self.text.tag_configure("filename", foreground=accent_color, font=("JetBrains Mono", 11))
        
        # Bottom status bar with minimal design
        self.bottom_frame: tk.Frame = tk.Frame(self.right_frame, bg=bg_primary, height=48)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.bottom_frame.pack_propagate(False)
        
        # Add subtle top border to status bar
        border_line = tk.Frame(self.bottom_frame, bg=border_color, height=1)
        border_line.pack(side=tk.TOP, fill=tk.X)
        
        # Token count display with clean style
        self.token_count_label: tk.Label = tk.Label(
            self.bottom_frame,
            text=self.translations["EN"]["total_tokens"] + "0",
            font=("Inter", 10, "bold"),
            bg=bg_primary,
            fg=text_primary,
            pady=14
        )
        self.token_count_label.pack(side=tk.RIGHT, padx=20)
        
        # Status info with muted style
        self.status_label: tk.Label = tk.Label(
            self.bottom_frame,
            text="Ready to explore your codebase",
            font=("Inter", 9),
            bg=bg_primary,
            fg=text_secondary,
            pady=14
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Bind text modification event
        self.text.bind("<<Modified>>", self.on_text_modified)
    
    def on_search_focus_in(self, event):
        """Clear placeholder text when search entry gets focus"""
        if self.search_entry.get() == self.translations[self.language_var.get()]["search_placeholder"]:
            self.search_entry.delete(0, tk.END)
    
    def on_search_focus_out(self, event):
        """Restore placeholder text when search entry loses focus"""
        if not self.search_entry.get():
            self.search_entry.insert(0, self.translations[self.language_var.get()]["search_placeholder"])
    
    def toggle_ignored_items(self):
        """Toggle showing ignored items"""
        self.show_ignored = self.show_ignored_var.get()
        self.populate_listbox()
        
        # Update button text
        lang = self.language_var.get()
        if self.show_ignored:
            self.show_ignored_check.config(text=self.translations[lang]["hide_ignored"])
        else:
            self.show_ignored_check.config(text=self.translations[lang]["show_ignored"])
    
    def on_language_change(self, *args: Any) -> None:
        """Update the UI elements when the language selection changes."""
        lang: str = self.language_var.get()
        self.master.title(self.translations[lang]["title"])
        self.left_label.config(text=self.translations[lang]["directory_content"])
        self.up_button.config(text="↑ " + self.translations[lang]["up_directory"])
        self.select_all_button.config(text=self.translations[lang]["select_all"])
        self.clear_selection_button.config(text=self.translations[lang]["clear_selection"])
        self.right_label.config(text=self.translations[lang]["source_code"])
        self.copy_button.config(text=self.translations[lang]["copy"])
        self.save_button.config(text=self.translations[lang]["save"])
        self.cancel_button.config(text=self.translations[lang]["cancel"])
        
        # Update search placeholder
        current_search = self.search_entry.get()
        if not current_search or current_search in [t["search_placeholder"] for t in self.translations.values()]:
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, self.translations[lang]["search_placeholder"])
        
        # Update ignored items toggle text
        if self.show_ignored:
            self.show_ignored_check.config(text=self.translations[lang]["hide_ignored"])
        else:
            self.show_ignored_check.config(text=self.translations[lang]["show_ignored"])
        
        # Update token count
        self.token_count_label.config(
            text=self.translations[lang]["total_tokens"] + str(count_tokens(self.text.get("1.0", tk.END)))
        )
        
        # Update progress label if visible
        if self.is_processing:
            self.progress_label.config(text=self.translations[lang]["processing"])
        
        self.populate_listbox()  # Update the current directory label and status
    
    def on_search_change(self, *args: Any) -> None:
        """Filter the listbox content based on search term"""
        self.populate_listbox()
    
    def get_file_size_str(self, size_bytes: int) -> str:
        """Convert file size in bytes to a human-readable string"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0 or unit == 'GB':
                return f"{size_bytes:.1f} {unit}" if unit != 'B' else f"{size_bytes} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} GB"
    
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
            if self.current_path in self.dir_cache:
                items = self.dir_cache[self.current_path]
            else:
                items = list(self.current_path.iterdir())
                self.dir_cache[self.current_path] = items
                
            # Filter ignored items unless specifically showing them
            if not self.show_ignored:
                items = [item for item in items if not should_ignore_path(item)]
                
            # Sort items (folders first, then files)
            folders = sorted([p for p in items if p.is_dir()], key=lambda p: p.name.lower())
            files = sorted([p for p in items if p.is_file()], key=lambda p: p.name.lower())
            
            # Filter by search term if provided
            search_term = self.search_var.get().lower()
            if search_term and search_term != self.translations[self.language_var.get()]["search_placeholder"].lower():
                folders = [f for f in folders if search_term in f.name.lower()]
                files = [f for f in files if search_term in f.name.lower()]
            
            # Count ignored items for status
            ignored_count = 0
            if not self.show_ignored:
                all_items = list(self.current_path.iterdir()) if self.current_path not in self.dir_cache else self.dir_cache[self.current_path]
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
                                   values=(file_type, self.get_file_size_str(size)),
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
            
            lang: str = self.language_var.get()
            if hasattr(self, 'current_path_label'):
                self.current_path_label.config(text=f"{self.translations[lang]['current_dir']}{rel_current}")
            
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
            lang = self.language_var.get()
            messagebox.showerror("Error", f"{self.translations[lang]['list_error']}{e}")
    
    def read_file_content(self, path: Path) -> str:
        """Read file content with caching for better performance"""
        if path in self.file_content_cache:
            return self.file_content_cache[path]
        
        try:
            content = path.read_text(encoding="utf-8")
            
            # Cache the content (with size management)
            if len(self.file_content_cache) >= self.max_cache_size:
                # Remove the first item (least recently added)
                self.file_content_cache.pop(next(iter(self.file_content_cache)))
            self.file_content_cache[path] = content
            
            return content
        except Exception as e:
            lang = self.language_var.get()
            return f"{self.translations[lang]['file_read_error']}{e}"
    
    def process_tasks(self) -> None:
        """Process tasks from the queue in a background thread"""
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
                        self.master.after(0, lambda: callback(result))
                    
                    self.is_processing = False
                    self.task_queue.task_done()
                    
                    # Hide progress indicator when all tasks are done
                    if self.task_queue.empty():
                        self.master.after(0, self.hide_progress)
            except Exception as e:
                print(f"Error in task processing: {e}")
            
            # Small delay to prevent CPU hogging
            time.sleep(0.01)
    
    def show_progress(self) -> None:
        """Show progress indicator for long operations"""
        lang = self.language_var.get()
        self.progress_label.config(text=self.translations[lang]["processing"])
        self.progress_frame.grid()
        self.cancel_button.config(state=tk.NORMAL)
    
    def hide_progress(self) -> None:
        """Hide progress indicator when operation completes"""
        self.progress_frame.grid_remove()
        self.cancel_button.config(state=tk.DISABLED)
    
    def cancel_current_task(self) -> None:
        """Cancel the currently running task"""
        self.cancel_processing = True
    
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
        lang: str = self.language_var.get()
        
        if path.is_file():
            content = self.read_file_content(path)
            # Get file extension for syntax highlighting
            ext = path.suffix.lower()[1:] if path.suffix else "text"
            
            # Markdown with file size info
            try:
                size = path.stat().st_size
                size_str = self.get_file_size_str(size)
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
                # Get directory items from cache if available
                if path in self.dir_cache:
                    items = self.dir_cache[path]
                else:
                    items = list(path.iterdir())
                    self.dir_cache[path] = items
                
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
                markdown_str += f"{self.translations[lang]['folder_read_error']}{e}\n\n"
            return markdown_str
        else:
            return ""
    
    def process_selection(self, selections: List[str]) -> None:
        """Process the selected items and update the text widget with markdown content"""
        # Show progress indicator
        self.show_progress()
        
        def generate_markdown(selections):
            full_markdown = ""
            for item_id in selections:
                full_path = Path(item_id)
                markdown = self.get_markdown_for_path(full_path)
                if self.cancel_processing:
                    return "Operation cancelled."
                full_markdown += markdown
            return full_markdown
        
        def update_text(markdown):
            self.text.delete("1.0", tk.END)
            if markdown:
                self.text.insert(tk.END, markdown)
                self.highlight_markdown()
            self.update_token_count()
        
        # Add the task to the queue
        self.task_queue.put((generate_markdown, (selections,), update_text))
    
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
        lang: str = self.language_var.get()
        try:
            file_path.write_text(content, encoding="utf-8")
            messagebox.showinfo("Success", f"{self.translations[lang]['save_success']}{str(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"{self.translations[lang]['save_error']}{e}")
    
    def copy_to_clipboard(self) -> None:
        """Copy the Markdown content from the Text widget to clipboard."""
        content: str = self.text.get("1.0", tk.END)
        lang: str = self.language_var.get()
        try:
            self.master.clipboard_clear()
            self.master.clipboard_append(content)
            self.master.update()  # Ensure clipboard is updated
            messagebox.showinfo("Success", self.translations[lang]["copy_success"])
        except Exception as e:
            messagebox.showerror("Error", f"{self.translations[lang]['copy_error']}{e}")
    
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
                lang: str = self.language_var.get()
                self.token_count_label.config(text=f"{self.translations[lang]['total_tokens']}{count:,}")
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
            self.task_queue.put((count_in_background, (content,), update_label))
    
    def on_text_modified(self, event: Any) -> None:
        """
        Triggered when the <<Modified>> event occurs in the Text widget;
        updates the token count after text changes.
        Note: The event may trigger twice in some cases, so the modified flag is reset.
        """
        self.update_token_count()
        self.text.edit_modified(False)


def main() -> None:
    """Main function to run the Code Contextor Portable application with enhanced modern design."""
    root: tk.Tk = tk.Tk()
    
    # Set window properties for modern appearance
    root.attributes("-alpha", 0.98)  # Slight transparency for modern look
    
    # Set window icon and additional properties
    try:
        # Try to set an icon if available
        root.iconbitmap(default="app.ico")
    except:
        pass  # Icon file not found, continue without it
    
    # Center the window on screen
    root.update_idletasks()
    width = 1200
    height = 800
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Configure global ttk style with modern theme
    style: ttk.Style = ttk.Style(root)
    
    # Try to use a modern theme if available
    available_themes = style.theme_names()
    if "vista" in available_themes:
        style.theme_use("vista")  # Windows modern theme
    elif "aqua" in available_themes:
        style.theme_use("aqua")   # macOS theme
    elif "clam" in available_themes:
        style.theme_use("clam")   # Cross-platform modern theme
    else:
        style.theme_use("default")
    
    # Enhanced global style configurations with completely white background
    style.configure(".", 
                   background="#ffffff",  # Completely white
                   foreground="#111827",  # Dark text
                   font=("Inter", 9))
    
    # Configure scrollbars for modern look with white background
    style.configure("Vertical.TScrollbar",
                   background="#f8fafc",
                   troughcolor="#ffffff",  # White trough
                   borderwidth=0,
                   arrowcolor="#6b7280",
                   darkcolor="#f8fafc",
                   lightcolor="#f8fafc")
    
    style.configure("Horizontal.TScrollbar",
                   background="#f8fafc",
                   troughcolor="#ffffff",  # White trough
                   borderwidth=0,
                   arrowcolor="#6b7280",
                   darkcolor="#f8fafc",
                   lightcolor="#f8fafc")
    
    # Configure combobox for modern look
    style.configure("TCombobox",
                   fieldbackground="#ffffff",
                   background="#f8fafc",
                   borderwidth=1,
                   focuscolor="none",
                   font=("Inter", 9))
    style.map("TCombobox",
             focuscolor=[("focus", "#3b82f6")])
    
    # Configure checkbutton for modern look
    style.configure("TCheckbutton",
                   background="#ffffff",  # White background
                   foreground="#111827",
                   focuscolor="none",
                   font=("Inter", 9))
    style.map("TCheckbutton",
             background=[("active", "#f8fafc")],
             foreground=[("active", "#111827")])
    
    # Start the application
    app = FileExplorer(root)
    
    # Configure window close event
    def on_closing():
        """Handle application shutdown gracefully."""
        if app.is_processing:
            app.cancel_processing = True
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the main event loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        on_closing()


if __name__ == "__main__":
    main()
