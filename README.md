# CodeContextor Portable

![CodeContextor Interface](img.jpg)

A specialized Python desktop application designed to prepare and send source code to LLM chats. CodeContextor helps developers scan project directories, calculate token usage, and format entire codebases for AI analysis and modifications.

## 🏗️ Architecture & Modularization

CodeContextor has evolved from a monolithic single-file application (1487 lines) to a **professional modular architecture** for better maintainability, scalability, and team development.

### Project Structure
```
CodeContextor/
├── main.py                 # Main entry point
├── prototype.py            # Original monolithic code (backup)
├── core/                   # Core functionality
│   ├── constants.py        # Configuration and ignore patterns
│   ├── utils.py           # Helper functions
│   ├── token_counter.py   # Token counting with caching
│   ├── cache_manager.py   # Directory and file caching
│   └── file_handler.py    # File operations and markdown generation
├── workers/               # Thread management
│   └── thread_manager.py  # Background task processing
├── localization/          # Multi-language system
│   └── translations.py    # 10 language translations
└── ui/                    # User interface
    ├── styles.py          # shadcn/ui inspired styling
    └── main_window.py     # Complete UI implementation
```

## ✨ What's New in v2

### 🎨 Modern Design (shadcn/ui Inspired)
- **Clean White Background**: Minimal, professional appearance (#ffffff)
- **Modern Typography**: Inter and JetBrains Mono fonts
- **Card-based Layout**: Subtle borders and organized sections
- **Responsive Design**: Adaptive UI components
- **Emoji-free Interface**: Clean, professional look

### 🚫 Smart Cache Ignore System
- **Automatic Filtering**: Ignores `node_modules`, `__pycache__`, `.git`, etc.
- **Performance Boost**: Dramatically reduces token calculation time
- **Toggle Visibility**: Show/hide ignored items as needed
- **Comprehensive Patterns**: 25+ ignore patterns for common build/cache directories

### 🌍 Enhanced Multi-language Support
Now supporting **10 languages**:
- English (EN), Turkish (TR), Russian (RU), Spanish (ES)
- Portuguese (PT), French (FR), Italian (IT), Ukrainian (UA)
- German (DE), Dutch (NL)

### 🚀 Performance & Technical Improvements
- **Multi-threading**: Background processing prevents UI freezing
- **Smart Caching**: File contents, token counts, and directory listings
- **Progressive Loading**: Efficient handling of large directory structures
- **Type Safety**: Comprehensive type hints throughout codebase
- **Error Handling**: Robust error management and recovery

### 📊 Advanced Features
- **Real-time Search**: Filter files and folders instantly
- **Token Optimization**: Exclude unnecessary files from token calculations
- **Progress Indicators**: Visual feedback with cancellation support
- **Tree View**: Modern file browser with type and size information
- **Syntax Highlighting**: Enhanced markdown and code visualization

## 🔧 Core Features

- 🔍 **Project Scanning**: Comprehensive source code collection
- 📊 **Token Counting**: Real-time LLM token estimation (tiktoken integration)
- 📁 **Smart Filtering**: Intelligent directory traversal with ignore patterns
- ⚡ **Quick Export**: Copy to clipboard or save to file
- 🌐 **Multi-language**: Support for 10 languages
- 💡 **Context Preparation**: Optimized formatting for AI analysis
- 🎯 **Selective Processing**: Choose specific files or entire directories

## 🛠️ Technical Stack

- **Python 3.x** with comprehensive type hints
- **Tkinter/ttk** with modern shadcn/ui inspired styling
- **Multi-threading** for responsive UI
- **pathlib** for modern file operations
- **tiktoken** for accurate LLM token counting (with fallback)
- **Modular Architecture** for maintainability and scalability

## 📦 Installation

### Prerequisites
- Python 3.7+
- tkinter (usually included with Python)

### Setup
```bash
git clone https://github.com/yourusername/CodeContextor.git
cd CodeContextor
pip install tiktoken  # Optional: for accurate token counting
```

### Optional Dependencies
```bash
pip install tiktoken  # For accurate LLM token counting
```

## 🚀 Usage

### Quick Start
```bash
python main.py
```

### Features Overview

1. **Browse Files**: Navigate through your project structure
2. **Smart Filtering**: Use search or toggle ignored files
3. **Select Content**: Choose files/folders for context generation
4. **Generate Context**: Automatic markdown formatting with syntax highlighting
5. **Export**: Copy to clipboard or save as `llm.txt`

### Performance Tips

- **Use Search**: Filter large directories for specific files
- **Toggle Ignored**: Hide cache/build directories for better performance
- **Cancel Operations**: Stop long-running processes if needed
- **Depth Limiting**: Automatic recursion limits prevent infinite loops
- **Background Processing**: Continue using UI while files are processed

## 🏆 Modularization Benefits

### For Developers
- **Maintainability**: Each module has specific responsibilities
- **Testability**: Modules can be tested independently
- **Scalability**: Easy to add new features
- **Code Organization**: Clear separation of concerns
- **Team Development**: Multiple developers can work on different modules

### For Users
- **Reliability**: Better error handling and stability
- **Performance**: Optimized resource usage
- **Responsiveness**: Non-blocking UI operations
- **Consistency**: Uniform behavior across features

## 📈 Performance Metrics

- **Startup Time**: < 2 seconds
- **Large Directories**: Handles 1000+ files efficiently
- **Memory Usage**: Optimized caching with size limits
- **Token Calculation**: 90% faster with ignore patterns
- **UI Responsiveness**: Non-blocking operations

## 🔍 Cache Ignore Patterns

Automatically ignores common build and cache directories:

```python
# Directories
'node_modules', '__pycache__', '.git', '.vscode', 'dist', 'build'

# File Extensions  
'.log', '.tmp', '.pyc', '.so', '.dll', '.exe'
```

## 🎯 Use Cases

- **AI Code Review**: Prepare entire codebases for LLM analysis
- **Documentation**: Generate comprehensive project overviews
- **Code Migration**: Context for refactoring and modernization
- **Learning**: Understand project structure and patterns
- **Debugging**: Provide context for troubleshooting

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to new functions
- Include docstrings for public methods
- Test your changes thoroughly
- Update documentation as needed

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **shadcn/ui** for design inspiration
- **tiktoken** for accurate token counting
- **Python community** for excellent libraries and tools

---

**CodeContextor Portable** - Professional, modular, and user-friendly tool for LLM context preparation. 