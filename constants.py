from imports import *

# -----------------------
# Global Constants
# -----------------------
# Database Path
DB_PATH = 'sessions/rbc_map_data.db'


# Logging Configuration
LOG_DIR = 'logs'

DEFAULT_LOG_LEVEL = logging.DEBUG

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


VERSION_NUMBER = "0.12.0"


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
    'requests': 'requests',
    're': 're',  # Built-in, no pip install needed
    'time': 'time',  # Built-in
    'sqlite3': 'sqlite3',  # Built-in
    'webbrowser': 'webbrowser',  # Built-in
    'datetime': 'datetime',  # Built-in
    'bs4': 'beautifulsoup4',
    'PySide6.QtWidgets': 'PySide6',
    'PySide6.QtGui': 'PySide6',
    'PySide6.QtCore': 'PySide6',
    'PySide6.QtWebEngineWidgets': 'PySide6',
    'PySide6.QtWebChannel': 'PySide6',
    'PySide6.QtNetwork': 'PySide6'
}


# -----------------------
# Define App Icon
# -----------------------

APP_ICON = QIcon()
