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
# Location update API
# -----------------------

# Default timeout (seconds) for outbound HTTP calls in the update flow.
HTTP_REQUEST_TIMEOUT = 10

# Preferred path is the tokenless /refresh endpoint; the token URLs below are
# retained only for the legacy fallback used against older API servers.
UPDATE_REFRESH_URL = "https://lollis-home.ddns.net/api/refresh"
UPDATE_TOKEN_URL = "https://lollis-home.ddns.net/api/request-token.py"
UPDATE_TRIGGER_URL = "https://lollis-home.ddns.net/api/trigger-update.py"
UPDATE_LOCATIONS_URL = "https://lollis-home.ddns.net/api/locations.json"
# Crowdsourced non-mover buildings (banks/taverns/transits/POI/lairs) contributed
# by other clients; pulled down and merged into the local building tables.
UPDATE_COMMUNITY_URL = "https://lollis-home.ddns.net/api/community_buildings.json"
# Complete regular-building backup used when the accumulating community file
# is empty or temporarily unavailable (first-run bootstrap).
UPDATE_SEED_URL = "https://lollis-home.ddns.net/api/buildings_seed.json"

# After triggering a scrape we poll locations.json until its "last_updated"
# field advances (i.e. the bot finished), instead of a fixed blind sleep.
REFRESH_POLL_MAX_SECONDS = 20.0
REFRESH_POLL_INTERVAL_SECONDS = 1.5

# -----------------------
# Crowdsourced location reporting (report-back)
# -----------------------

# Endpoint that receives locations this client discovers on the game page, so
# the scraper bot can keep shared data current between AVITD reveal cycles.
# Gated by the user's opt-in preference; POST is fire-and-forget and any
# failure is logged, never fatal. Inert until the server exposes the route.
# See docs/crowdsourced-location-reporting.md.
REPORT_LOCATION_URL = "https://lollis-home.ddns.net/api/report-location"

# Timeout (seconds) for the report POST. Kept short so a slow/down endpoint
# never delays page processing.
REPORT_TIMEOUT = 5

# -----------------------
# Minimap colors from the in-game CSS
# -----------------------

# Which in-game CSS selector supplies each minimap color (its background-color).
# The minimap reads the active/custom CSS first and falls back to the default
# palette below. Keys with no game-CSS equivalent (guild, alley, ...) are left
# to the theme's color_mappings.
CSS_MINIMAP_SELECTORS = {
    "background": "body",
    "bank": "span.bank",
    "tavern": "span.pub",
    "transit": "span.transit",
    "shop": "span.shop",
    "user_building": "span.lair",
    "placesofinterest": "span.arena",
    "alchemy": "span.alchemy",
    "bind": "span.bind",
    "sever": "span.sever",
    "graveyard": "span.grave",
    "intersect": "span.intersect",
    "street": "td.street",
    "alley": "td.city",
    "edge": "td.cityblock",
}

# RBC's stock blood.css palette - the default when the active CSS doesn't
# specify a given selector, so the minimap reads like the real in-game map.
DEFAULT_MINIMAP_COLORS = {
    "bank": "#0000ff",
    "tavern": "#887700",
    "transit": "#880000",
    "shop": "#004488",
    "user_building": "#660022",
    "placesofinterest": "#ff0000",
    "alchemy": "#660022",
    "bind": "transparent",
    "sever": "transparent",
    "graveyard": "#888888",
    "intersect": "#008800",
    "street": "#444444",
    "alley": "#000000",
    "edge": "#0000dd",
}

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
