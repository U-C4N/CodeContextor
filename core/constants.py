"""
Constants and ignore patterns for CodeContextor.

This module defines the patterns and extensions that should be ignored
when scanning directories for source code files.
"""

from pathlib import Path
from typing import Set

# Ignore patterns for cache/build directories and files
IGNORE_PATTERNS: Set[str] = {
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
IGNORE_EXTENSIONS: Set[str] = {
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