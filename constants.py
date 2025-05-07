from imports import *
from splash import *
# -----------------------
# Global Constants
# -----------------------
# Database Path
DB_PATH = 'sessions/rbc_map_data.db'

# Logging Configuration
LOG_DIR = 'logs'
DEFAULT_LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

VERSION_NUMBER = "0.12.1"

# Keybinding Defaults
DEFAULT_KEYBINDS = {
    "move_up": "W",
    "move_down": "S",
    "move_left": "A",
    "move_right": "D",
    "zoom_in": "PageUp",
    "zoom_out": "PageDown",
}

# Required Directories
REQUIRED_DIRECTORIES = ['logs', 'sessions', 'images']

# List of required modules with pip package names (some differ from import names)
required_modules = {
    'PySide6.QtCore': 'PySide6',
    'PySide6.QtGui': 'PySide6',
    'PySide6.QtNetwork': 'PySide6',
    'PySide6.QtWebChannel': 'PySide6',
    'PySide6.QtWebEngineWidgets': 'PySide6',
    'PySide6.QtWidgets': 'PySide6',
    'bs4': 'beautifulsoup4',
    'datetime': 'datetime',        # Built-in
    're': 're',                    # Built-in
    'requests': 'requests',
    'sqlite3': 'sqlite3',          # Built-in
    'time': 'time',                # Built-in
    'webbrowser': 'webbrowser'     # Built-in
}

APP_ICON_PATH = 'images/favicon.ico'
