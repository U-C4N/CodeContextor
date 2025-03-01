# CodeContextor v2

![CodeContextor Interface](img.jpg)

A specialized tool for preparing and sending source code to LLM chats. CodeContextor helps you scan project directories, calculate token usage, and format entire codebases for AI analysis and modifications.

## What's New in v2

- 🚀 **Performance Optimizations**: Significantly faster processing of large markdown files
- 🧵 **Multi-threading**: Background processing prevents UI freezing during heavy operations
- 💾 **Smart Caching**: Efficient caching for file contents, token counts, and directory listings
- 🔍 **Search Functionality**: Quick filtering of files and folders 
- 📊 **Enhanced UI**: Modern interface with better visualization and organization
- 🌲 **Tree View**: Improved file/folder display with type and size information
- 🎨 **Syntax Highlighting**: Better markdown and code visualization
- ⏱️ **Progress Indicators**: Visual feedback during long operations with cancellation support
- 🔄 **Lazy Loading**: Smart depth limiting to handle large directory structures

## Features

- 🔍 Scan and collect entire project source code
- 📊 Real-time token counting for different LLM models
- 📁 Smart directory traversal and file filtering
- ⚡ Quick copy-paste to LLM chat interfaces
- 🌐 Multi-language support (English, Turkish, Russian)
- 💡 Intelligent context preparation for code modifications

## Technical Stack

- Python 3.x with type hints
- Modern Python practices (pathlib, dataclasses)
- Tkinter for GUI with ttk styling
- Multi-threading for background processing
- Cache optimization strategies
- Source code parsing and formatting
- Token estimation for popular LLM models

## Installation

```bash
git clone https://github.com/yourusername/CodeContextor.git
cd CodeContextor
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

### Performance Tips

- Use the search functionality to filter large directories
- Cancel long-running operations if they're taking too long
- The application automatically limits directory depth to prevent excessive recursion
- Large files are processed in the background, allowing you to continue using the interface

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details
