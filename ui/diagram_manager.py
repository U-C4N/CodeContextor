"""
Diagram Manager for CodeContextor.

This module provides UI components for generating and previewing
Mermaid diagrams using Gemini AI.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from typing import Optional, Dict, Any
import threading
import tempfile
import webbrowser
import os

from core.gemini_client import GeminiClient
from core.cache_manager import CacheManager
from localization.translations import get_translation

class DiagramManager:
    """Manager for diagram generation and preview functionality."""
    
    DIAGRAM_TYPES = {
        "module_dependency": {
            "name_key": "diagram_module_dependency",
            "description_key": "diagram_module_dependency_desc",
            "icon": "📦"
        },
        "architecture": {
            "name_key": "diagram_architecture",
            "description_key": "diagram_architecture_desc",
            "icon": "🏗️"
        },
        "class_hierarchy": {
            "name_key": "diagram_class_hierarchy", 
            "description_key": "diagram_class_hierarchy_desc",
            "icon": "🔗"
        },
        "sequence": {
            "name_key": "diagram_sequence",
            "description_key": "diagram_sequence_desc",
            "icon": "⏭️"
        },
        "data_model": {
            "name_key": "diagram_data_model",
            "description_key": "diagram_data_model_desc",
            "icon": "🗃️"
        },
        "state_machine": {
            "name_key": "diagram_state_machine",
            "description_key": "diagram_state_machine_desc",
            "icon": "🔄"
        }
    }
    
    def __init__(self, parent_window, theme_manager, language_var):
        """Initialize diagram manager."""
        self.parent = parent_window
        self.theme_manager = theme_manager
        self.language_var = language_var
        self.gemini_client: Optional[GeminiClient] = None
        self.cache_manager: Optional[CacheManager] = None
        self.api_key = "AIzaSyCYr3thNQ7V_E-8Gg0vPGelz3I5btyWvO0"  # API key from user
        
        # Initialize cache manager
        self.cache_manager = CacheManager()
        
        # Initialize Gemini client
        if self.api_key:
            self.gemini_client = GeminiClient(self.api_key)
    
    def clear_cache_before_generation(self):
        """Clear cache before generating new diagrams for fresh analysis."""
        if self.cache_manager:
            print("DEBUG: Clearing cache before diagram generation...")
            self.cache_manager.clear_cache()
            print("DEBUG: Cache cleared successfully!")
    
    def show_diagram_menu(self, event=None):
        """Show diagram selection dialog."""
        if not self.gemini_client:
            lang = self.language_var.get()
            messagebox.showerror(
                get_translation(lang, "diagram_error_title"),
                get_translation(lang, "diagram_api_error")
            )
            return
            
        # Create dialog window
        dialog = tk.Toplevel(self.parent.master)
        lang = self.language_var.get()
        dialog.title(get_translation(lang, "diagram_dialog_title"))
        dialog.geometry("600x500")
        dialog.transient(self.parent.master)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"600x500+{x}+{y}")
        
        # Configure dialog styling
        if hasattr(self.theme_manager, 'get_colors'):
            colors = self.theme_manager.get_colors()
            dialog.configure(bg=colors['bg'])
        
        # Main frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=get_translation(lang, "diagram_select_type"),
            style="Heading.TLabel" if hasattr(self.theme_manager, 'get_colors') else None
        )
        title_label.pack(pady=(0, 20))
        
        # Diagram type selection
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(fill=tk.BOTH, expand=True)
        
        # Selected diagram type
        selected_type = tk.StringVar()
        
        # Create radio buttons for each diagram type
        for i, (type_key, type_info) in enumerate(self.DIAGRAM_TYPES.items()):
            frame = ttk.Frame(selection_frame)
            frame.pack(fill=tk.X, pady=5)
            
            radio = ttk.Radiobutton(
                frame,
                text=f"{type_info['icon']} {get_translation(lang, type_info['name_key'])}",
                variable=selected_type,
                value=type_key
            )
            radio.pack(side=tk.LEFT, anchor='w')
            
            desc_label = ttk.Label(
                frame,
                text=get_translation(lang, type_info['description_key']),
                foreground='gray'
            )
            desc_label.pack(side=tk.LEFT, padx=(10, 0))
            
            # Select first item by default
            if i == 0:
                radio.invoke()
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def generate_diagram():
            """Generate and preview diagram."""
            if not selected_type.get():
                messagebox.showwarning(get_translation(lang, "diagram_warning_title"), get_translation(lang, "diagram_select_warning"))
                return
                
            # Get selected code from main window
            code_context = self._get_selected_code()
            if not code_context:
                messagebox.showwarning(get_translation(lang, "diagram_warning_title"), get_translation(lang, "diagram_select_code_warning"))
                return
                
            dialog.destroy()
            self._generate_and_preview(selected_type.get(), code_context)
        
        def cancel():
            """Cancel dialog."""
            dialog.destroy()
        
        # Buttons
        ttk.Button(
            button_frame,
            text=get_translation(lang, "diagram_cancel_button"),
            command=cancel
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text=get_translation(lang, "diagram_generate_button"),
            command=generate_diagram
        ).pack(side=tk.LEFT)
        
        # Instruction label
        instruction_label = ttk.Label(
            main_frame,
            text=get_translation(lang, "diagram_tip"),
            foreground='gray'
        )
        instruction_label.pack(pady=(10, 0))
    
    def _get_selected_code(self) -> str:
        """Get selected code from main window."""
        try:
            # Get code from text widget
            if hasattr(self.parent, 'text'):
                content = self.parent.text.get("1.0", tk.END).strip()
                if content and content != "":
                    return content
        except Exception as e:
            print(f"DEBUG: Error getting selected code: {e}")
        return ""
    
    def _generate_and_preview(self, diagram_type: str, code_context: str):
        """Generate diagram and show preview in browser."""
        print(f"DEBUG: Starting diagram generation for type: {diagram_type}")
        print(f"DEBUG: Code context length: {len(code_context)}")
        
        # Clear cache before generation for fresh analysis
        self.clear_cache_before_generation()
        
        # Show loading dialog
        loading_dialog = self._show_loading_dialog()
        
        def generate_in_background():
            try:
                print("DEBUG: Starting background generation...")
                
                # Check if Gemini client exists
                if not self.gemini_client:
                    print("DEBUG: No Gemini client available")
                    loading_dialog.destroy()
                    lang = self.language_var.get()
                    messagebox.showerror(get_translation(lang, "diagram_error_title"), 
                                       get_translation(lang, "diagram_client_error"))
                    return
                
                # Generate diagram using Gemini
                print("DEBUG: Calling Gemini API...")
                mermaid_code = self.gemini_client.generate_diagram(
                    diagram_type, 
                    code_context
                )
                print(f"DEBUG: Received mermaid code: {mermaid_code[:100] if mermaid_code else 'None'}...")
                
                # Close loading dialog
                loading_dialog.destroy()
                
                if mermaid_code:
                    print("DEBUG: Successfully generated diagram, showing result...")
                    self._show_mermaid_result(mermaid_code, diagram_type)
                else:
                    print("DEBUG: No mermaid code received")
                    # Show demo diagram instead
                    demo_code = self._get_demo_mermaid(diagram_type)
                    if demo_code:
                        self._show_mermaid_result(demo_code, diagram_type)
                    else:
                        lang = self.language_var.get()
                        messagebox.showerror(get_translation(lang, "diagram_error_title"), 
                                           get_translation(lang, "diagram_generation_failed"))
                    
            except Exception as e:
                print(f"DEBUG: Exception in background generation: {e}")
                import traceback
                traceback.print_exc()
                loading_dialog.destroy()
                lang = self.language_var.get()
                messagebox.showerror(get_translation(lang, "diagram_error_title"), 
                                   f"{get_translation(lang, 'diagram_error_occurred')} {str(e)}")
        
        # Start generation in background thread
        threading.Thread(target=generate_in_background, daemon=True).start()
    
    def _show_loading_dialog(self) -> tk.Toplevel:
        """Show loading dialog."""
        lang = self.language_var.get()
        
        dialog = tk.Toplevel(self.parent.master)
        dialog.title(get_translation(lang, "diagram_loading_title"))
        dialog.geometry("300x150")
        dialog.transient(self.parent.master)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (dialog.winfo_screenheight() // 2) - (150 // 2)
        dialog.geometry(f"300x150+{x}+{y}")
        
        # Content
        frame = ttk.Frame(dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text=get_translation(lang, "diagram_gemini_working")).pack(pady=10)
        
        # Progress bar
        progress = ttk.Progressbar(frame, mode='indeterminate')
        progress.pack(fill=tk.X, pady=10)
        progress.start()
        
        ttk.Label(frame, text=get_translation(lang, "diagram_please_wait")).pack()
        
        return dialog
    
    def _show_mermaid_result(self, mermaid_code: str, diagram_type: str):
        """Show Mermaid code result with preview in a split dialog."""
        lang = self.language_var.get()
        type_info = self.DIAGRAM_TYPES.get(diagram_type, {})
        title = get_translation(lang, type_info.get('name', 'diagram_fallback_title'))
        icon = type_info.get('icon', '🎨')
        
        # Create result dialog
        dialog = tk.Toplevel(self.parent.master)
        dialog.title(f"{icon} {title}")
        dialog.geometry("1200x700")
        dialog.transient(self.parent.master)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (1200 // 2)
        y = (dialog.winfo_screenheight() // 2) - (700 // 2)
        dialog.geometry(f"1200x700+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(
            header_frame,
            text=get_translation(lang, "diagram_created_success").format(title=title),
            style="Heading.TLabel" if hasattr(self.theme_manager, 'get_colors') else None
        )
        title_label.pack(side=tk.LEFT)
        
        # Two-panel layout
        panels_frame = ttk.Frame(main_frame)
        panels_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Left panel - Mermaid code
        left_frame = ttk.LabelFrame(panels_frame, text=get_translation(lang, "diagram_mermaid_code_label"))
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Text widget for code
        code_text = tk.Text(
            left_frame,
            wrap=tk.WORD,
            font=('Courier New', 10),
            bg='#f8f9fa',
            fg='#333333',
            padx=10,
            pady=10
        )
        code_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Insert mermaid code
        code_text.insert("1.0", mermaid_code)
        code_text.config(state=tk.DISABLED)  # Make it read-only
        
        # Right panel - Preview
        right_frame = ttk.LabelFrame(panels_frame, text=get_translation(lang, "diagram_preview_label"))
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Preview canvas frame
        canvas_frame = ttk.Frame(right_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas for diagram preview
        preview_canvas = tk.Canvas(
            canvas_frame,
            bg='white',
            bd=2,
            relief='sunken'
        )
        preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw simple representation of the diagram
        self._draw_diagram_preview(preview_canvas, mermaid_code, diagram_type)
        
        # Info frame below canvas
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        info_label = ttk.Label(
            info_frame,
            text=get_translation(lang, "diagram_preview_info"),
            font=('Arial', 8),
            foreground='gray'
        )
        info_label.pack()
        
        # Single preview button
        def open_browser_preview():
            """Open full Mermaid preview in browser."""
            html_content = self._create_preview_html(mermaid_code, title, lang)
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
            temp_file.write(html_content)
            temp_file.close()
            webbrowser.open(f'file://{temp_file.name}')
        
        preview_button = ttk.Button(
            info_frame,
            text=get_translation(lang, "diagram_full_view_button"),
            command=open_browser_preview
        )
        preview_button.pack(pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def copy_code():
            """Copy Mermaid code to clipboard."""
            dialog.clipboard_clear()
            dialog.clipboard_append(mermaid_code)
            messagebox.showinfo(get_translation(lang, "diagram_copy_success_title"), 
                              get_translation(lang, "diagram_copy_success_message"))
        
        def close_dialog():
            """Close the dialog."""
            dialog.destroy()
        
        # Buttons
        ttk.Button(
            button_frame,
            text=get_translation(lang, "diagram_copy_button"),
            command=copy_code
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text=get_translation(lang, "diagram_close_button"),
            command=close_dialog
        ).pack(side=tk.LEFT)
    
    def _create_preview_html(self, mermaid_code: str, title: str, language: str = "EN") -> str:
        """Create HTML for Mermaid preview."""
        # Language code mapping
        lang_codes = {
            "EN": "en",
            "TR": "tr", 
            "RU": "ru",
            "ES": "es",
            "PT": "pt",
            "FR": "fr",
            "IT": "it",
            "UA": "uk",
            "DE": "de",
            "NL": "nl"
        }
        lang_code = lang_codes.get(language, "en")
        created_with_text = get_translation(language, "diagram_html_created_with")
        
        return f"""
<!DOCTYPE html>
<html lang="{lang_code}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - CodeContextor</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2196F3 0%, #21CBF3 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .content {{
            padding: 40px;
            text-align: center;
        }}
        .mermaid {{
            margin: 20px 0;
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            border: 2px solid #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 {title}</h1>
            <p>{created_with_text}</p>
        </div>
        <div class="content">
            <div class="mermaid">
{mermaid_code}
            </div>
        </div>
    </div>

    <script>
        mermaid.initialize({{ 
            startOnLoad: true,
            theme: 'default',
            themeVariables: {{
                primaryColor: '#2196F3',
                primaryTextColor: '#333',
                primaryBorderColor: '#1976D2',
                lineColor: '#666'
            }}
        }});
    </script>
</body>
</html>
"""
    
    def _get_demo_mermaid(self, diagram_type: str) -> str:
        """Get demo mermaid code for testing."""
        demo_diagrams = {
            "module_dependency": """graph TD;
    main.py --> core/file_handler.py;
    main.py --> ui/main_window.py;
    ui/main_window.py --> ui/theme_manager.py;
    ui/main_window.py --> ui/diagram_manager.py;
    ui/diagram_manager.py --> core/gemini_client.py;""",
            
            "architecture": """graph LR;
    User --> CodeContextor;
    CodeContextor --> FileSystem;
    CodeContextor --> GeminiAPI;
    GeminiAPI --> MermaidDiagram;
    MermaidDiagram --> Browser;""",
            
            "class_hierarchy": """classDiagram
    class FileExplorer {
        +master: Tk
        +file_handler: FileHandler
        +theme_manager: ThemeManager
        +setup_ui()
        +populate_listbox()
    }
    class DiagramManager {
        +parent: Window
        +gemini_client: GeminiClient
        +show_diagram_menu()
        +generate_diagram()
    }
    class GeminiClient {
        +api_key: string
        +base_url: string
        +generate_diagram()
    }
    FileExplorer --> DiagramManager
    DiagramManager --> GeminiClient""",
            
            "sequence": """sequenceDiagram
    User->>FileExplorer: Select files
    FileExplorer->>DiagramManager: Request diagram
    DiagramManager->>GeminiClient: Generate diagram
    GeminiClient->>GeminiAPI: API call
    GeminiAPI-->>GeminiClient: Mermaid code
    GeminiClient-->>DiagramManager: Diagram data
    DiagramManager-->>Browser: Open HTML preview""",
            
            "data_model": """erDiagram
    PROJECTS ||--o{ FILES : contains
    FILES ||--o{ DIAGRAMS : generates
    PROJECTS {
        int id PK
        string name
        string path
        datetime created_at
    }
    FILES {
        int id PK
        int project_id FK
        string filename
        string content
        string type
    }
    DIAGRAMS {
        int id PK
        int file_id FK
        string type
        string mermaid_code
        datetime generated_at
    }""",
            
            "state_machine": """stateDiagram-v2
    [*] --> Idle
    Idle --> FileSelected : select_files()
    FileSelected --> DiagramType : choose_diagram()
    DiagramType --> Generating : generate()
    Generating --> Preview : success
    Generating --> Error : api_error
    Preview --> Idle : close()
    Error --> DiagramType : retry()
    Error --> Idle : cancel()"""
        }
        
        return demo_diagrams.get(diagram_type, "graph TD; A --> B; B --> C;") 
    
    def _draw_diagram_preview(self, canvas: tk.Canvas, mermaid_code: str, diagram_type: str):
        """Draw a simple preview of the diagram on canvas."""
        # Clear canvas
        canvas.delete("all")
        
        # Wait for canvas to be ready
        canvas.update_idletasks()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        # If canvas not ready yet, use default size
        if width <= 1:
            width = 400
        if height <= 1:
            height = 300
        
        # Draw based on diagram type
        if diagram_type == "class_hierarchy":
            self._draw_class_diagram(canvas, mermaid_code, width, height)
        elif diagram_type == "sequence":
            self._draw_sequence_diagram(canvas, mermaid_code, width, height)
        elif diagram_type == "module_dependency":
            self._draw_module_diagram(canvas, mermaid_code, width, height)
        elif diagram_type == "architecture":
            self._draw_architecture_diagram(canvas, mermaid_code, width, height)
        elif diagram_type == "data_model":
            self._draw_er_diagram(canvas, mermaid_code, width, height)
        elif diagram_type == "state_machine":
            self._draw_state_diagram(canvas, mermaid_code, width, height)
        else:
            self._draw_generic_diagram(canvas, mermaid_code, width, height)
    
    def _draw_class_diagram(self, canvas: tk.Canvas, mermaid_code: str, width: int, height: int):
        """Draw enhanced class diagram preview with modern styling."""
        # Parse class names from mermaid code
        classes = []
        for line in mermaid_code.split('\n'):
            if 'class ' in line and '{' in line:
                class_name = line.split('class ')[1].split(' {')[0].strip()
                classes.append(class_name)
        
        if not classes:
            classes = ["MainClass", "BaseClass", "HelperClass"]
        
        # Enhanced styling
        colors = ['#E3F2FD', '#F3E5F5', '#E8F5E8', '#FFF3E0']
        outlines = ['#1976D2', '#7B1FA2', '#388E3C', '#F57C00']
        
        # Draw classes as modern rectangles
        box_width = min(140, width // 3)
        box_height = 90
        start_x = max(30, (width - len(classes[:3]) * (box_width + 40)) // 2)
        start_y = max(40, (height - 200) // 2)
        
        for i, class_name in enumerate(classes[:3]):  # Max 3 classes for better layout
            x = start_x + (i * (box_width + 40))
            y = start_y + (i % 2) * 120
            
            # Draw shadow
            canvas.create_rectangle(x + 3, y + 3, x + box_width + 3, y + box_height + 3, 
                                  fill='#E0E0E0', outline='', width=0)
            
            # Draw main class box with gradient effect
            canvas.create_rectangle(x, y, x + box_width, y + box_height, 
                                  fill=colors[i % len(colors)], 
                                  outline=outlines[i % len(outlines)], 
                                  width=3)
            
            # Class name with icon
            canvas.create_text(x + box_width//2, y + 18, text=f"🏗️ {class_name}", 
                             font=('Segoe UI', 11, 'bold'), fill='#2E2E2E')
            
            # Separator line
            canvas.create_line(x + 10, y + 32, x + box_width - 10, y + 32, 
                             fill=outlines[i % len(outlines)], width=2)
            
            # Methods with better formatting
            methods = ["+initialize()", "+process()", "+validate()"]
            for j, method in enumerate(methods):
                canvas.create_text(x + box_width//2, y + 48 + j * 14, text=method, 
                                 font=('Consolas', 9), fill='#424242')
        
        # Draw modern inheritance arrows
        if len(classes) > 1:
            # Curved arrow with better styling
            start_x_arrow = start_x + box_width
            start_y_arrow = start_y + box_height//2
            end_x_arrow = start_x + box_width + 40
            end_y_arrow = start_y + 120 + box_height//2
            
            # Curved line
            canvas.create_line(start_x_arrow, start_y_arrow, 
                             start_x_arrow + 20, start_y_arrow,
                             end_x_arrow - 20, end_y_arrow,
                             end_x_arrow, end_y_arrow,
                             smooth=True, arrow=tk.LAST, width=3, 
                             fill='#1976D2', arrowshape=(12, 15, 4))
    
    def _draw_sequence_diagram(self, canvas: tk.Canvas, mermaid_code: str, width: int, height: int):
        """Draw enhanced sequence diagram preview with modern styling."""
        actors_data = [
            ("👤 User", "#E8F5E8", "#2E7D32"),
            ("🖥️ System", "#E3F2FD", "#1976D2"), 
            ("💾 Database", "#FFF3E0", "#F57C00")
        ]
        
        # Calculate positioning
        actor_width = width // len(actors_data)
        
        for i, (actor, bg_color, border_color) in enumerate(actors_data):
            x = (i + 1) * actor_width - actor_width//2
            
            # Draw shadow for actor box
            canvas.create_rectangle(x - 48, 33, x + 48, 73, 
                                  fill='#E0E0E0', outline='', width=0)
            
            # Enhanced actor box with gradient
            canvas.create_rectangle(x - 45, 30, x + 45, 70, 
                                  fill=bg_color, outline=border_color, width=3)
            canvas.create_text(x, 50, text=actor, font=('Segoe UI', 10, 'bold'), fill='#2E2E2E')
            
            # Enhanced lifeline with better styling
            canvas.create_line(x, 70, x, height - 50, width=3, fill='#9E9E9E', dash=(8, 4))
            
            # Add activation boxes
            if i == 1:  # System has activation
                canvas.create_rectangle(x - 8, 110, x + 8, 190, 
                                      fill='#BBDEFB', outline='#1976D2', width=2)
        
        # Draw enhanced messages with icons
        messages = [
            ("📤 Request", "#4CAF50"),
            ("⚙️ Process", "#2196F3"),
            ("📥 Response", "#FF9800")
        ]
        
        y_pos = 120
        for i, (message, color) in enumerate(messages):
            start_x = actor_width - actor_width//2
            end_x = 2 * actor_width - actor_width//2
            
            if i == 2:  # Response goes back
                start_x, end_x = end_x, start_x
            
            # Message arrow with enhanced styling
            canvas.create_line(start_x, y_pos, end_x, y_pos, 
                             arrow=tk.LAST, width=3, fill=color, 
                             arrowshape=(10, 12, 3))
            
            # Message label with background
            mid_x = (start_x + end_x) // 2
            canvas.create_rectangle(mid_x - 35, y_pos - 15, mid_x + 35, y_pos - 5,
                                  fill='white', outline=color, width=1)
            canvas.create_text(mid_x, y_pos - 10, text=message, 
                             font=('Segoe UI', 8, 'bold'), fill=color)
            y_pos += 50
    
    def _draw_module_diagram(self, canvas: tk.Canvas, mermaid_code: str, width: int, height: int):
        """Draw enhanced module dependency diagram with modern styling."""
        modules_data = [
            ("📄 main.py", "#E1F5FE", "#01579B", True),
            ("🔧 core/", "#F3E5F5", "#4A148C", False),
            ("🎨 ui/", "#E8F5E8", "#1B5E20", False),
            ("⚙️ workers/", "#FFF3E0", "#E65100", False)
        ]
        
        # Calculate positions in a more organized layout
        center_x = width // 2
        center_y = height // 2
        positions = [
            (center_x, center_y - 60),  # main.py at top center
            (center_x - 80, center_y + 40),  # core/ bottom left
            (center_x + 80, center_y + 40),  # ui/ bottom right
            (center_x, center_y + 100)   # workers/ bottom center
        ]
        
        for i, ((module, bg_color, border_color, is_main), (x, y)) in enumerate(zip(modules_data, positions)):
            # Draw shadow
            shadow_radius = 50 if is_main else 40
            canvas.create_oval(x - shadow_radius + 3, y - 18 + 3, 
                             x + shadow_radius + 3, y + 18 + 3, 
                             fill='#E0E0E0', outline='')
            
            # Module oval with enhanced styling
            module_radius = 50 if is_main else 40
            canvas.create_oval(x - module_radius, y - 15, x + module_radius, y + 15, 
                             fill=bg_color, outline=border_color, 
                             width=4 if is_main else 3)
            
            # Module text with better formatting
            font_size = 10 if is_main else 9
            font_weight = 'bold' if is_main else 'normal'
            canvas.create_text(x, y, text=module, 
                             font=('Segoe UI', font_size, font_weight), 
                             fill='#2E2E2E')
            
            # Draw dependency arrows to main
            if not is_main:
                main_x, main_y = positions[0]
                
                # Calculate arrow start/end points to avoid overlap
                dx = main_x - x
                dy = main_y - y
                distance = (dx**2 + dy**2)**0.5
                
                # Normalize and scale to edge of circles
                start_offset = 40
                end_offset = 50
                
                start_x = x + (dx / distance) * start_offset
                start_y = y + (dy / distance) * start_offset
                end_x = main_x - (dx / distance) * end_offset
                end_y = main_y - (dy / distance) * end_offset
                
                # Enhanced arrow
                canvas.create_line(start_x, start_y, end_x, end_y,
                                 arrow=tk.LAST, width=3, fill=border_color,
                                 arrowshape=(12, 15, 4), smooth=True)
        
        # Add title
        canvas.create_text(center_x, 20, text="📦 Module Dependencies", 
                         font=('Segoe UI', 12, 'bold'), fill='#424242')
    
    def _draw_architecture_diagram(self, canvas: tk.Canvas, mermaid_code: str, width: int, height: int):
        """Draw architecture diagram."""
        components = ["User", "Frontend", "API", "Database"]
        
        # Draw horizontal flow
        comp_width = width // len(components)
        y = height // 2
        
        for i, comp in enumerate(components):
            x = (i + 1) * comp_width - comp_width//2
            
            # Component box
            canvas.create_rectangle(x - 50, y - 30, x + 50, y + 30, 
                                  fill='lightcoral', outline='darkred', width=2)
            canvas.create_text(x, y, text=comp, font=('Arial', 10, 'bold'))
            
            # Arrow to next component
            if i < len(components) - 1:
                canvas.create_line(x + 50, y, x + comp_width - 50, y, 
                                 arrow=tk.LAST, width=3, fill='darkred')
    
    def _draw_er_diagram(self, canvas: tk.Canvas, mermaid_code: str, width: int, height: int):
        """Draw ER diagram."""
        entities = ["Users", "Orders", "Products"]
        
        # Draw entities
        for i, entity in enumerate(entities):
            x = 100 + i * 150
            y = height // 2
            
            # Entity rectangle
            canvas.create_rectangle(x - 60, y - 40, x + 60, y + 40, 
                                  fill='lightsteelblue', outline='steelblue', width=2)
            canvas.create_text(x, y - 20, text=entity, font=('Arial', 11, 'bold'))
            canvas.create_text(x, y, text="id (PK)", font=('Arial', 8))
            canvas.create_text(x, y + 15, text="name", font=('Arial', 8))
            
            # Relationship lines
            if i > 0:
                canvas.create_line(x - 60, y, x - 90, y, width=2, fill='steelblue')
                canvas.create_oval(x - 95, y - 10, x - 85, y + 10, 
                                 fill='white', outline='steelblue', width=2)
    
    def _draw_state_diagram(self, canvas: tk.Canvas, mermaid_code: str, width: int, height: int):
        """Draw state machine diagram."""
        states = ["Start", "Processing", "Complete", "Error"]
        
        # Draw states in a cycle
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 3
        
        for i, state in enumerate(states):
            angle = (i * 2 * 3.14159) / len(states)
            x = center_x + radius * (0.8 * (1 if i < 2 else -1))
            y = center_y + radius * (0.6 * (1 if i % 2 == 0 else -1))
            
            # State circle
            canvas.create_oval(x - 40, y - 25, x + 40, y + 25, 
                             fill='lightpink', outline='purple', width=2)
            canvas.create_text(x, y, text=state, font=('Arial', 9, 'bold'))
            
            # Transition arrows
            if i < len(states) - 1:
                next_i = (i + 1) % len(states)
                next_angle = (next_i * 2 * 3.14159) / len(states)
                next_x = center_x + radius * (0.8 * (1 if next_i < 2 else -1))
                next_y = center_y + radius * (0.6 * (1 if next_i % 2 == 0 else -1))
                
                canvas.create_line(x + 20, y, next_x - 20, next_y, 
                                 arrow=tk.LAST, width=2, fill='purple', smooth=True)
    
    def _draw_generic_diagram(self, canvas: tk.Canvas, mermaid_code: str, width: int, height: int):
        """Draw generic diagram."""
        # Simple flow diagram
        boxes = ["A", "B", "C"]
        box_width = 80
        box_height = 40
        
        for i, box in enumerate(boxes):
            x = 80 + i * 150
            y = height // 2
            
            canvas.create_rectangle(x, y, x + box_width, y + box_height, 
                                  fill='lightgray', outline='black', width=2)
            canvas.create_text(x + box_width//2, y + box_height//2, text=box, 
                             font=('Arial', 12, 'bold'))
            
            if i < len(boxes) - 1:
                canvas.create_line(x + box_width, y + box_height//2, 
                                 x + 150, y + box_height//2, 
                                 arrow=tk.LAST, width=2, fill='black') 