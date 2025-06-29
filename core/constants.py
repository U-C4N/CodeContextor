"""
Constants and configuration for CodeContextor.
Contains ignore patterns and other global settings.
"""

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

# Cache settings
MAX_CACHE_SIZE = 200
CACHE_TTL = 300  # 5 minutes
MAX_FILE_CACHE_SIZE = 50

# UI settings
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600 