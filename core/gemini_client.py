"""
Gemini API client for diagram generation.

This module provides integration with Google's Gemini API for generating
Mermaid diagrams from code analysis.
"""

import json
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path

class GeminiClient:
    """Client for Google Gemini API integration."""
    
    def __init__(self, api_key: str):
        """Initialize Gemini client with API key."""
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        
    def generate_diagram(self, 
                        diagram_type: str, 
                        code_context: str, 
                        project_files: List[Dict[str, Any]] = None) -> Optional[str]:
        """
        Generate Mermaid diagram based on code context.
        
        Args:
            diagram_type: Type of diagram to generate
            code_context: The source code context
            project_files: List of project files with metadata
            
        Returns:
            Generated Mermaid diagram syntax or None if failed
        """
        
        # Diagram type specific prompts
        prompts = {
            "module_dependency": self._get_module_dependency_prompt(),
            "architecture": self._get_architecture_prompt(),
            "class_hierarchy": self._get_class_hierarchy_prompt(),
            "sequence": self._get_sequence_prompt(),
            "data_model": self._get_data_model_prompt(),
            "state_machine": self._get_state_machine_prompt()
        }
        
        if diagram_type not in prompts:
            return None
            
        # Build complete prompt
        system_prompt = prompts[diagram_type]
        user_prompt = f"""
Kod analizi:

{code_context}

Lütfen yukarıdaki kod için {diagram_type} tipinde bir Mermaid diyagramı oluştur.
Sadece mermaid sözdizimini döndür, başka açıklama ekleme.
"""

        try:
            # Prepare request
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": f"{system_prompt}\n\n{user_prompt}"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 2048,
                }
            }
            
            # Make API request
            url = f"{self.base_url}?key={self.api_key}"
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    extracted = self._extract_mermaid_code(content)
                    return extracted
            elif response.status_code == 429:
                # Quota exceeded - return smart demo diagram
                return self._get_demo_diagram(diagram_type, code_context)
            else:
                print(f"DEBUG: API Error response: {response.text}")
            
            return None
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None
    
    def _get_demo_diagram(self, diagram_type: str, code_context: str = "") -> str:
        """Return intelligent demo diagram based on code analysis when API quota is exceeded."""
        # Try to create context-aware demo based on code
        if code_context:
            return self._create_context_aware_demo(diagram_type, code_context)
        
        # Fallback to static demos
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
    
    def _create_context_aware_demo(self, diagram_type: str, code_context: str) -> str:
        """Create demo diagram based on actual code context."""
        print(f"DEBUG: Creating context-aware demo for {diagram_type}")
        
        if diagram_type == "module_dependency":
            return self._extract_module_dependencies(code_context)
        elif diagram_type == "architecture":
            return self._extract_architecture_components(code_context)
        elif diagram_type == "class_hierarchy":
            return self._extract_class_hierarchy(code_context)
        elif diagram_type == "sequence":
            return self._extract_sequence_flow(code_context)
        elif diagram_type == "data_model":
            return self._extract_data_models(code_context)
        elif diagram_type == "state_machine":
            return self._extract_state_machine(code_context)
        
        return "graph TD; A --> B; B --> C;"
    
    def _extract_module_dependencies(self, code: str) -> str:
        """Extract actual module dependencies from code."""
        imports = []
        lines = code.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        
        if not imports:
            return """graph TD;
    main.py --> core/
    main.py --> ui/
    core/ --> utils/
    ui/ --> components/"""
        
        # Build dependency graph from actual imports
        graph_lines = ["graph TD;"]
        current_file = "current_file"
        
        for imp in imports[:10]:  # Limit to avoid too complex diagrams
            if 'from ' in imp and ' import ' in imp:
                parts = imp.split(' import ')
                module = parts[0].replace('from ', '').strip()
                imported = parts[1].strip()
                graph_lines.append(f"    {current_file} --> {module}")
            elif 'import ' in imp:
                module = imp.replace('import ', '').strip()
                if ',' in module:
                    modules = [m.strip() for m in module.split(',')]
                    for m in modules[:5]:
                        graph_lines.append(f"    {current_file} --> {m}")
                else:
                    graph_lines.append(f"    {current_file} --> {module}")
        
        return '\n'.join(graph_lines)
    
    def _extract_architecture_components(self, code: str) -> str:
        """Extract architecture components from code."""
        has_ui = any(keyword in code.lower() for keyword in ['tkinter', 'ui', 'window', 'button', 'widget', 'react', 'vue'])
        has_api = any(keyword in code.lower() for keyword in ['requests', 'http', 'api', 'endpoint', 'flask', 'fastapi'])
        has_db = any(keyword in code.lower() for keyword in ['database', 'sql', 'mongo', 'redis', 'cache'])
        has_file = any(keyword in code.lower() for keyword in ['file', 'path', 'read', 'write', 'open'])
        
        graph = ["graph TB"]
        
        if has_ui:
            graph.append('    User[👤 User] --> UI[🖥️ User Interface]')
            
        if has_api:
            if has_ui:
                graph.append('    UI --> API[📡 API Layer]')
            else:
                graph.append('    User[👤 User] --> API[📡 API Layer]')
                
        if has_file:
            graph.append('    API --> Files[📁 File System]' if has_api else '    UI --> Files[📁 File System]')
            
        if has_db:
            graph.append('    API --> DB[(💾 Database)]' if has_api else '    Files --> DB[(💾 Database)]')
        
        if not graph[1:]:  # If no components found
            graph.extend([
                '    User[👤 User] --> App[📱 Application]',
                '    App --> Logic[⚙️ Business Logic]',
                '    Logic --> Data[💾 Data Storage]'
            ])
        
        return '\n'.join(graph)
    
    def _extract_class_hierarchy(self, code: str) -> str:
        """Extract class hierarchy from code."""
        classes = []
        lines = code.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('class '):
                class_def = line.replace('class ', '').replace(':', '')
                if '(' in class_def:  # Has inheritance
                    class_name, parent = class_def.split('(', 1)
                    parent = parent.replace(')', '').strip()
                    classes.append((class_name.strip(), parent))
                else:
                    classes.append((class_def.strip(), None))
        
        if not classes:
            return """classDiagram
    class MainClass {
        +method1()
        +method2()
    }
    class HelperClass {
        +helper_method()
    }
    MainClass --> HelperClass"""
        
        diagram = ["classDiagram"]
        
        for class_name, parent in classes:
            diagram.append(f"    class {class_name} {{")
            diagram.append("        +method()")
            diagram.append("    }")
            
            if parent:
                diagram.append(f"    {parent} <|-- {class_name}")
        
        return '\n'.join(diagram)
    
    def _extract_sequence_flow(self, code: str) -> str:
        """Extract sequence flow from code."""
        has_user_interaction = any(keyword in code.lower() for keyword in ['input', 'click', 'select', 'button'])
        has_file_ops = any(keyword in code.lower() for keyword in ['open', 'read', 'write', 'file'])
        has_api_calls = any(keyword in code.lower() for keyword in ['request', 'post', 'get', 'api'])
        
        diagram = [
            "sequenceDiagram",
            "    participant User as 👤 User",
            "    participant App as 📱 Application"
        ]
        
        if has_file_ops:
            diagram.append("    participant File as 📁 File System")
            
        if has_api_calls:
            diagram.append("    participant API as 📡 External API")
        
        # Add interactions
        if has_user_interaction:
            diagram.append("    User->>App: User action")
            
        if has_file_ops:
            diagram.append("    App->>File: Read/Write data")
            diagram.append("    File-->>App: Data response")
            
        if has_api_calls:
            diagram.append("    App->>API: API request")
            diagram.append("    API-->>App: API response")
            
        diagram.append("    App-->>User: Display result")
        
        return '\n'.join(diagram)
    
    def _extract_data_models(self, code: str) -> str:
        """Extract data models from code."""
        # Look for class attributes that look like data fields
        lines = code.split('\n')
        current_class = None
        classes_with_fields = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('class '):
                current_class = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                classes_with_fields[current_class] = []
            elif current_class and ('=' in line or 'self.' in line):
                if 'self.' in line and '=' in line:
                    field = line.split('self.')[1].split('=')[0].strip()
                    classes_with_fields[current_class].append(field)
        
        if not classes_with_fields:
            return """erDiagram
    USER {
        int id PK
        string name
        string email
    }
    ORDER {
        int id PK
        int user_id FK
        datetime created_at
    }
    USER ||--o{ ORDER : "has" """
        
        diagram = ["erDiagram"]
        
        for class_name, fields in classes_with_fields.items():
            if fields:
                diagram.append(f"    {class_name.upper()} {{")
                diagram.append("        int id PK")
                for field in fields[:5]:  # Limit fields
                    diagram.append(f"        string {field}")
                diagram.append("    }")
        
        return '\n'.join(diagram)
    
    def _extract_state_machine(self, code: str) -> str:
        """Extract state machine from code."""
        has_states = any(keyword in code.lower() for keyword in ['state', 'status', 'phase', 'mode'])
        has_events = any(keyword in code.lower() for keyword in ['event', 'trigger', 'handle', 'process'])
        
        if has_states:
            return """stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start()
    Processing --> Complete : finish()
    Processing --> Error : error()
    Complete --> [*]
    Error --> Idle : reset()"""
        else:
            return """stateDiagram-v2
    [*] --> Initial
    Initial --> Active : activate()
    Active --> Inactive : deactivate()
    Inactive --> Active : reactivate()
    Active --> [*] : terminate()"""
    
    def _get_module_dependency_prompt(self) -> str:
        """Get prompt for module dependency diagram."""
        return """
Sen bir senior software engineer ve kod analiz uzmanısın. Python/JavaScript kodlarını analiz ederek modül bağımlılık diyagramları oluşturuyorsun.

GÖREV: Verilen koddan import/require ilişkilerini çıkararak Mermaid diagram oluştur.

ANALİZ KURALLARI:
1. Her import/from/require satırını incele
2. Dosya yollarını ve modül isimlerini tespit et
3. Döngüsel bağımlılıkları işaretle
4. Ana entry point'leri belirle (main.py, index.js vb.)
5. Leaf node'ları (hiç import etmeyen modüller) göster
6. Ortak bağımlılıkları grup halinde göster

MERMAID SYNTAX KURALLARI:
- graph TD kullan (Top-Down)
- Dosya isimleri için: filename.py formatında
- Dizinler için: folder/ formatında  
- Döngüsel bağımlılık varsa kırmızı ok: A -.->|circular| B
- Ana entry point'i koyu renk: A:::main
- Leaf node'ları yeşil: B:::leaf
- Ortak dependencies'i sarı: C:::shared

ÖRNEK:
```mermaid
graph TD;
    main.py:::main --> core/file_handler.py
    main.py --> ui/main_window.py
    ui/main_window.py --> ui/theme_manager.py:::shared
    ui/main_window.py --> core/cache_manager.py:::shared
    core/file_handler.py --> core/utils.py:::leaf
    
    classDef main fill:#e1f5fe,stroke:#01579b,stroke-width:3px
    classDef shared fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef leaf fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
```

ÇOK ÖNEMLİ: Sadece mermaid kod bloğunu döndür, başka hiçbir açıklama yapma!
"""
    
    def _get_architecture_prompt(self) -> str:
        """Get prompt for high-level architecture diagram."""
        return """
Sen bir senior sistem mimarı ve solution architect'sın. Koddan yüksek seviye sistem mimarisi çıkarıyorsun.

GÖREV: Verilen koddan sistem bileşenlerini, katmanları ve veri akışını çıkararak mimari diagram oluştur.

ANALİZ KURALLARI:
1. Presentation Layer: UI, web interface, desktop app katmanı
2. Business Logic Layer: Core işlemler, servisler, algoritmalar
3. Data Access Layer: Database, file system, cache erişimi
4. External Services: API'ler, third-party servisler
5. Infrastructure: Queue, caching, logging sistemleri
6. Authentication & Authorization: Güvenlik katmanları
7. Data Flow Direction: Veri akış yönlerini belirle

COMPONENT TİPLERİ:
- Frontend: React/Vue/Angular/Tkinter vb.
- Backend: Express/Flask/Django/FastAPI vb.
- Database: PostgreSQL/MongoDB/SQLite vb.
- Cache: Redis/Memcached vb.
- Queue: RabbitMQ/Kafka/Celery vb.
- APIs: REST/GraphQL/gRPC vb.
- Files: Config/Static/Uploads vb.

MERMAID SYNTAX:
- graph TB kullan (Top-Bottom)
- Subgraph'lar kullan: subgraph "Layer Name"
- İkonlar ekle: 🌐 Web, 💾 Database, 🔄 Cache, 📡 API
- Renk kodları: Frontend:blue, Backend:green, Data:orange
- Ok tipleri: --> (normal), -.-> (optional), ==> (heavy traffic)

ÖRNEK:
```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[🌐 Web Interface]
        Desktop[🖥️ Desktop App]
    end
    
    subgraph "Business Logic"
        API[📡 REST API]
        Auth[🔐 Authentication]
        Core[⚙️ Core Services]
    end
    
    subgraph "Data Layer"
        DB[(💾 Database)]
        Cache[🔄 Redis Cache]
        Files[📁 File Storage]
    end
    
    subgraph "External"
        Email[📧 Email Service]
        Cloud[☁️ Cloud Storage]
    end
    
    UI ==> API
    Desktop ==> API
    API --> Auth
    API --> Core
    Core --> DB
    Core -.-> Cache
    Core --> Files
    API --> Email
    Files --> Cloud
    
    classDef frontend fill:#e3f2fd,stroke:#1976d2
    classDef backend fill:#e8f5e8,stroke:#388e3c
    classDef data fill:#fff3e0,stroke:#f57c00
    
    class UI,Desktop frontend
    class API,Auth,Core backend
    class DB,Cache,Files data
```

ÇOK ÖNEMLİ: Sadece mermaid kod bloğunu döndür, başka hiçbir açıklama yapma!
"""
    
    def _get_class_hierarchy_prompt(self) -> str:
        """Get prompt for class hierarchy diagram."""
        return """
Sen bir senior OOP developer ve design pattern uzmanısın. Koddan sınıf yapılarını ve ilişkilerini çıkarıyorsun.

GÖREV: Verilen koddan sınıfları, kalıtım, kompozisyon ve bağımlılık ilişkilerini çıkararak UML class diagram oluştur.

ANALİZ KURALLARI:
1. Tüm class tanımlarını bul
2. Inheritance ilişkilerini tespit et (extends, super, parent)
3. Composition/Aggregation ilişkilerini bul (has-a relationship)
4. Interface/Abstract class'ları belirle
5. Public/Private/Protected member'ları ayır
6. Method'ların parameter ve return type'larını çıkar
7. Attribute'ların data type'larını belirle
8. Design pattern'leri tespit et

VISIBILITY NOTASYONU:
+ Public methods/attributes
- Private methods/attributes
# Protected methods/attributes
~ Package methods/attributes
$ Static methods/attributes

İLİŞKİ TİPLERİ:
<|-- : Inheritance (extends)
<|.. : Interface implementation
*-- : Composition (strong has-a)
o-- : Aggregation (weak has-a)
--> : Association (uses)
..> : Dependency (imports)

DATA TİPLERİ:
- string, int, bool, float (primitive)
- List~Type~, Dict~Key,Value~ (collections)
- Optional~Type~ (nullable)
- Custom classes

ÖRNEK:
```mermaid
classDiagram
    class FileExplorer {
        -master: Tk
        -cache_manager: CacheManager
        -theme_manager: ThemeManager
        +__init__(root: Tk)
        +setup_ui(): void
        +select_folder(): void
        +populate_listbox(path: Path): void
        -_create_menu_bar(): void
    }
    
    class CacheManager {
        -cache: Dict~str,Any~
        -timestamps: Dict~str,float~
        +__init__(max_size: int)
        +get_cached(key: string): Optional~Any~
        +cache_item(key: string, value: Any): void
        +clear_cache(): void
    }
    
    class ThemeManager {
        <<abstract>>
        +current_theme: string
        +get_colors(): Dict~str,str~
        +apply_theme(widget: Widget): void*
    }
    
    class DarkTheme {
        +get_colors(): Dict~str,str~
        +apply_theme(widget: Widget): void
    }
    
    class LightTheme {
        +get_colors(): Dict~str,str~
        +apply_theme(widget: Widget): void
    }
    
    FileExplorer *-- CacheManager : contains
    FileExplorer *-- ThemeManager : contains
    ThemeManager <|-- DarkTheme : implements
    ThemeManager <|-- LightTheme : implements
    FileExplorer ..> Path : imports
    
    note for FileExplorer "Main UI Controller"
    note for ThemeManager "Strategy Pattern"
```

ÇOK ÖNEMLİ: Sadece mermaid kod bloğunu döndür, başka hiçbir açıklama yapma!
"""
    
    def _get_sequence_prompt(self) -> str:
        """Get prompt for sequence diagram."""
        return """
Sen bir senior business analyst ve system flow uzmanısın. Koddan iş akışlarını ve etkileşim senaryolarını çıkarıyorsun.

GÖREV: Verilen koddan ana iş akışlarını, method çağrılarını ve sistem etkileşimlerini çıkararak sequence diagram oluştur.

ANALİZ KURALLARI:
1. Ana aktörleri belirle (User, System, External Services)
2. Method çağrı zincirlerini takip et
3. Asenkron vs senkron işlemleri ayır
4. Error handling flow'larını dahil et
5. Loop'ları ve condition'ları göster
6. Database/API çağrılarını önemle
7. Authentication/Authorization adımlarını dahil et
8. File I/O ve cache işlemlerini göster

ACTOR TİPLERİ:
- User: Son kullanıcı
- Frontend: UI katmanı
- Backend: Business logic
- Database: Veri katmanı
- Cache: Önbellek sistemi
- ExternalAPI: Dış servisler
- FileSystem: Dosya sistemi
- Queue: Mesaj kuyruğu

MESAJ TİPLERİ:
->>  : Asenkron mesaj
-->> : Asenkron response
->>+ : Activate participant
-->>- : Deactivate participant
-x   : Lost message
->   : Open arrow (no response)

CONTROL STRUCTURES:
- alt/else/end : Şartlı dallanma
- opt/end : İsteğe bağlı
- loop/end : Döngü
- par/and/end : Paralel işlem
- rect/end : Kritik bölge

ÖRNEK:
```mermaid
sequenceDiagram
    participant User as 👤 User
    participant UI as 🖥️ Frontend
    participant Auth as 🔐 Auth Service
    participant API as 📡 Backend API
    participant Cache as 🔄 Cache
    participant DB as 💾 Database
    participant File as 📁 File System
    
    User->>UI: Select files
    UI->>Auth: Validate session
    Auth-->>UI: Session valid
    
    UI->>API: Request file analysis
    activate API
    
    API->>Cache: Check cached result
    Cache-->>API: Cache miss
    
    API->>File: Read file content
    File-->>API: File data
    
    API->>API: Process file
    
    loop For each import
        API->>File: Read dependency
        File-->>API: Dependency data
    end
    
    API->>Cache: Store result
    API-->>UI: Analysis complete
    deactivate API
    
    UI->>User: Display results
    
    rect Critical: Error Handling
        API-xFile: File not found
        API-->>UI: Error response
        UI-->>User: Show error
    end
    
    note over API,Cache: Results cached for 5 minutes
    note over User,UI: Real-time updates via WebSocket
```

ÇOK ÖNEMLİ: Sadece mermaid kod bloğunu döndür, başka hiçbir açıklama yapma!
"""
    
    def _get_data_model_prompt(self) -> str:
        """Get prompt for data model diagram."""
        return """
Sen bir senior database architect ve data modeling uzmanısın. Koddan veri yapılarını ve ilişkilerini çıkarıyorsun.

GÖREV: Verilen koddan veri modellerini, class'ları, struct'ları ve ilişkilerini çıkararak ER diagram oluştur.

ANALİZ KURALLARI:
1. Class'lardaki attribute'ları tespit et
2. Data class, model class, entity class'ları bul
3. Foreign key ilişkilerini çıkar
4. One-to-One, One-to-Many, Many-to-Many ilişkileri belirle
5. Primary key ve unique constraint'leri tespit et
6. Index'lenen alanları belirle
7. Nullable vs Non-nullable field'ları ayır
8. Enum ve değer constraint'lerini dahil et
9. JSON/Array field'ları göster

FIELD TİPLERİ:
- int, bigint, smallint (sayısal)
- string, varchar, text (metin)
- datetime, date, time, timestamp (zaman)
- boolean, bool (mantıksal)
- float, decimal, numeric (ondalık)
- json, jsonb (yapılandırılmış)
- array, list (çoklu değer)
- enum (sabit değerler)

KEY NOTASYONU:
- PK: Primary Key
- FK: Foreign Key  
- UK: Unique Key
- IX: Index
- NN: Not Null

RELATIONSHIP CARDINALITY:
||--|| : One-to-One
||--o{ : One-to-Many  
}o--|| : Many-to-One
}o--o{ : Many-to-Many
||--o| : One-to-Zero-or-One
}|--|| : One-or-Many-to-One

ÖRNEK:
```mermaid
erDiagram
    USER ||--o{ ORDER : "places"
    USER ||--o{ REVIEW : "writes"
    ORDER ||--o{ ORDER_ITEM : "contains"
    PRODUCT ||--o{ ORDER_ITEM : "included_in"
    PRODUCT ||--o{ REVIEW : "receives"
    CATEGORY ||--o{ PRODUCT : "has"
    
    USER {
        bigint id PK "Auto-increment"
        string email UK "Required, max 255"
        string password_hash NN "BCrypt hashed"
        string first_name NN "max 100"
        string last_name NN "max 100"
        datetime created_at NN "Default now()"
        datetime updated_at "Auto-update"
        boolean is_active "Default true"
        enum role "admin, user, moderator"
        json preferences "User settings"
    }
    
    ORDER {
        bigint id PK
        bigint user_id FK
        enum status "pending, paid, shipped, delivered"
        decimal total_amount NN "2 decimal places"
        string shipping_address NN
        datetime order_date NN
        datetime shipped_date
        string tracking_number UK
        json metadata "Extra order info"
    }
    
    PRODUCT {
        bigint id PK
        bigint category_id FK
        string name NN IX "Searchable"
        text description
        decimal price NN "2 decimal places"
        int stock_quantity NN "Default 0"
        array~string~ tags "Product tags"
        boolean is_active "Default true"
        datetime created_at NN
    }
    
    ORDER_ITEM {
        bigint order_id FK
        bigint product_id FK
        int quantity NN "Min 1"
        decimal unit_price NN "Price at time of order"
        decimal total_price NN "quantity * unit_price"
    }
    
    CATEGORY {
        bigint id PK
        string name UK NN "max 100"
        string slug UK IX "URL-friendly"
        text description
        bigint parent_id FK "Self-reference for hierarchy"
        boolean is_active "Default true"
    }
    
    REVIEW {
        bigint id PK
        bigint user_id FK
        bigint product_id FK
        int rating NN "1-5 stars"
        text comment "Optional review text"
        datetime created_at NN
        boolean is_verified "Verified purchase"
    }
```

ÇOK ÖNEMLİ: Sadece mermaid kod bloğunu döndür, başka hiçbir açıklama yapma!
"""
    
    def _get_state_machine_prompt(self) -> str:
        """Get prompt for state machine diagram."""
        return """
Sen bir senior software engineer ve finite state machine uzmanısın. Koddan durum makinelerini ve iş akışlarını çıkarıyorsun.

GÖREV: Verilen koddan durum geçişlerini, lifecycle'ları ve workflow'ları çıkararak state diagram oluştur.

ANALİZ KURALLARI:
1. Enum değerlerini incele (status, state, phase)
2. Boolean flag kombinasyonlarını tespit et
3. Conditional statement'larda state geçişlerini bul
4. Event handler'larda trigger'ları belirle
5. Validation rule'ları ve guard condition'ları çıkar
6. Error state'leri ve recovery path'leri dahil et
7. Initial ve final state'leri belirle
8. Concurrent state'leri (paralel işlemler) tespit et

STATE TİPLERİ:
- Simple states: Basit durumlar
- Composite states: Alt durumları olan
- Choice states: Şartlı dallanma
- Fork/Join: Paralel işlem başlangıç/bitiş
- History states: Önceki durumu hatırlama
- Entry/Exit points: Giriş/çıkış noktaları

TRANSITION TİPLERİ:
--> : Normal geçiş
--x : Guard condition ile geçiş
--> event : Event trigger ile geçiş
--> event / action : Event + action
--> [condition] : Şartlı geçiş
--> event [guard] / action : Tam syntax

SPECIAL NOTATIONS:
[*] : Initial state
[*] : Final state
[H] : History state
[C] : Choice point
note : Açıklama
state composite { } : Composite state

ÖRNEK:
```mermaid
stateDiagram-v2
    [*] --> Idle : Application Start
    
    state "File Selection" as FileSelect {
        [*] --> NoFiles
        NoFiles --> FilesSelected : select_files()
        FilesSelected --> Processing : analyze()
        Processing --> Results : [analysis_complete]
        Results --> FilesSelected : select_different_files()
        
        state Processing {
            [*] --> Reading
            Reading --> Parsing : [file_read_success]
            Parsing --> Analyzing : [parse_success]
            Analyzing --> Complete : [analysis_done]
            Reading --> Error : [file_read_error]
            Parsing --> Error : [parse_error]
            Analyzing --> Error : [analysis_error]
            Error --> [*] : reset()
            Complete --> [*]
        }
    }
    
    state "Diagram Generation" as DiagramGen {
        [*] --> Idle_Gen : waiting
        Idle_Gen --> TypeSelection : show_menu()
        TypeSelection --> Generating : [type_selected]
        Generating --> Preview : [generation_success] / display_result()
        Generating --> Failed : [generation_failed] / show_error()
        Preview --> Idle_Gen : close_preview()
        Failed --> TypeSelection : retry()
        Failed --> Idle_Gen : cancel()
        
        state Generating {
            [*] --> CacheCheck
            CacheCheck --> APICall : [cache_miss]
            CacheCheck --> Complete : [cache_hit] / load_cached()
            APICall --> Processing_AI : [api_connected]
            Processing_AI --> Complete : [response_received]
            APICall --> APIError : [connection_failed]
            Processing_AI --> APIError : [timeout] 
            APIError --> [*] : [retry_limit_reached]
            Complete --> [*]
        }
    }
    
    Idle --> FileSelect : user_action
    FileSelect --> DiagramGen : [files_analyzed]
    DiagramGen --> FileSelect : select_new_files()
    DiagramGen --> [*] : exit_application()
    
    state ErrorHandling {
        [*] --> Recoverable
        [*] --> Critical
        Recoverable --> Idle : auto_recover()
        Critical --> [*] : force_exit()
    }
    
    FileSelect --> ErrorHandling : [error_occurred]
    DiagramGen --> ErrorHandling : [error_occurred]
    ErrorHandling --> Idle : [recovery_successful]
    
    note for FileSelect : "Handles file operations and validation"
    note for DiagramGen : "AI-powered diagram generation workflow"
    note for Processing : "Multi-threaded analysis pipeline"
```

ÇOK ÖNEMLİ: Sadece mermaid kod bloğunu döndür, başka hiçbir açıklama yapma!
"""
    
    def _extract_mermaid_code(self, content: str) -> str:
        """Extract Mermaid code from AI response."""
        # Remove markdown code block markers
        content = content.strip()
        
        # Find mermaid code block
        if "```mermaid" in content:
            start = content.find("```mermaid") + 10
            end = content.find("```", start)
            if end != -1:
                return content[start:end].strip()
        
        # If no code block, try to find graph/classDiagram/etc.
        lines = content.split('\n')
        diagram_lines = []
        in_diagram = False
        
        for line in lines:
            line = line.strip()
            if any(keyword in line for keyword in ['graph', 'classDiagram', 'sequenceDiagram', 'erDiagram', 'stateDiagram']):
                in_diagram = True
            
            if in_diagram:
                diagram_lines.append(line)
                
            # Stop if we find an empty line after starting
            if in_diagram and not line and diagram_lines:
                break
        
        return '\n'.join(diagram_lines) if diagram_lines else content 