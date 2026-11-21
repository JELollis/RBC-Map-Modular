from imports import *

# List of required modules
required_modules = [
    'pickle', 'pymysql', 'requests', 're', 'time', 'sqlite3',
    'webbrowser', 'datetime', 'bs4', 'PySide6.QtWidgets',
    'PySide6.QtGui', 'PySide6.QtCore', 'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebChannel', 'PySide6.QtNetwork'
]


# -----------------------
# Database Connection
# -----------------------

# Server information
REMOTE_HOST = "lollis-home.ddns.net"

LOCAL_HOST = "127.0.0.1"

USER = "rbc_maps"

PASSWORD = "RBC_Community_Map"

DATABASE = "city_map"



# Call the function to connect to the database
database_connection = connect_to_database()


# Load the data and ensure that color_mappings is initialized before the CityMapApp class is used
columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates = load_data()


# -----------------------
# SQLite Storage Setup
# -----------------------

COOKIE_DB_PATH = 'sessions/cookies.db'  # Path to the SQLite database for storing cookies

COINS_DB_PATH = 'sessions/coins.db'  # Path to the SQLite Database for storing coin information
