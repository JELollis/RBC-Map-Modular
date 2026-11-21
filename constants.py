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


VERSION_NUMBER = "0.13.1"


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


# Buildings
BUILDING_CLASS_MAP = {
    "bank":    {"table": "banks",            "name_col": "Name"},
    "pub":     {"table": "taverns",          "name_col": "Name"},
    "shop":    {"table": "shops",            "name_col": "Name"},
    "transit": {"table": "transits",         "name_col": "Name"},
    "arena":   {"table": "placesofinterest", "name_col": "Name"},
    "grave":   {"table": "placesofinterest", "name_col": "Name"},
    "lair":    {"table": "userbuildings",    "name_col": "Name"},
    "alchemy": {"table": "placesofinterest", "name_col": "Name"},
    # intentionally exclude: pk, human variants, object, sever, bind, intersect
}


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


# -----------------------
# Define App Icon
# -----------------------

APP_ICON = PySide6.QtGui.QIcon()
