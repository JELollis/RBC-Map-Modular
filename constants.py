from imports import *

# List of required modules
required_modules = [
    'pickle', 'pymysql', 'requests', 're', 'time', 'sqlite3',
    'webbrowser', 'datetime', 'bs4', 'PySide6.QtWidgets',
    'PySide6.QtGui', 'PySide6.QtCore', 'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebChannel', 'PySide6.QtNetwork'
]


# -----------------------
# Database connection
# -----------------------

# Server information
LOCAL_HOST = "127.0.0.1"

REMOTE_HOST = "lollis-home.ddns.net"

USER = "rbc_maps"

PASSWORD = "RBC_Community_Map"

DATABASE = "city_map"



# Load the data and ensure that color_mappings is initialized before the CityMapApp class is used
columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates = load_data()


# -----------------------
# Cookie Storage
# -----------------------

COOKIE_FILE_PATH = 'sessions/cookies.pkl'
