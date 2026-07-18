from imports import *
from splash import *

# -----------------------
# Global Constants
# -----------------------

BASE_DIR = Path(__file__).resolve().parent

LOG_DIR = BASE_DIR / "logs"
SESSIONS_DIR = BASE_DIR / "sessions"
IMAGES_DIR = BASE_DIR / "images"

DB_PATH = SESSIONS_DIR / "rbc_map_data.db"

REQUIRED_DIRECTORIES = [
    LOG_DIR,
    SESSIONS_DIR,
    IMAGES_DIR,
]

VERSION_NUMBER = "0.13.3.0"

# -----------------------
# Logging Configuration
# -----------------------

DEFAULT_LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# -----------------------
# Keybinding Defaults
# -----------------------

DEFAULT_KEYBINDS = {
    "move_up": "W",
    "move_down": "S",
    "move_left": "A",
    "move_right": "D",
    "zoom_in": "PageUp",
    "zoom_out": "PageDown",
}

# -----------------------
# Building Metadata
# -----------------------

BUILDING_CLASS_MAP = {
    "bank":    {"table": "banks",            "name_col": "Name"},
    "pub":     {"table": "taverns",          "name_col": "Name"},
    "shop":    {"table": "shops",            "name_col": "Name"},
    "transit": {"table": "transits",         "name_col": "Name"},
    "arena":   {"table": "placesofinterest", "name_col": "Name"},
    "grave":   {"table": "placesofinterest", "name_col": "Name"},
    "lair":    {"table": "userbuildings",    "name_col": "Name"},
    "alchemy": {"table": "placesofinterest", "name_col": "Name"},
    # intentionally excluded: pk, human variants, object, sewer, bind, intersect
}

# -----------------------
# Dependency Metadata (Validation Only)
# -----------------------

required_modules = {
    "PySide6.QtCore": "PySide6",
    "PySide6.QtGui": "PySide6",
    "PySide6.QtNetwork": "PySide6",
    "PySide6.QtWebChannel": "PySide6",
    "PySide6.QtWebEngineWidgets": "PySide6",
    "PySide6.QtWidgets": "PySide6",
    "bs4": "beautifulsoup4",
    "requests": "requests",
}

# -----------------------
# Application Icon
# -----------------------

APP_ICON = PySide6.QtGui.QIcon()
