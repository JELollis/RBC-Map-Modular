from imports import *

# List of required modules
required_modules = [
    'pickle', 'pymysql', 'requests', 're', 'time', 'sqlite3',
    'webbrowser', 'datetime', 'bs4', 'PySide6.QtWidgets',
    'PySide6.QtGui', 'PySide6.QtCore', 'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebChannel', 'PySide6.QtNetwork','cryptography', 'hashlib'
]


# Initialize Fernet encryption using the loaded key
key = b'Kslt2S6mlIeMRsRhfnZ2k2PjFjI98rOUpNE9H8bLywE='  # Replace with your actual key

cipher_suite = Fernet(key)


# -----------------------
# SQLite Setup
# -----------------------

# Local Database path
DB_PATH = 'sessions/rbc_map_data.db'


# Load the data and ensure that color_mappings is initialized before the CityMapApp class is used
columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates = load_data(DB_PATH)
