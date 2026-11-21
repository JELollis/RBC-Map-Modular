"""Shared imports for the RBC Community Map (modular snapshot)."""

#!/usr/bin/env python3
# Filename: main_0.8.1
# Copyright 2024 RBC Community Map Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
=========================
RBC Community Map Application
=========================
The RBC Community Map Application provides a graphical interface for navigating
the city map of RavenBlack City. It includes features such as zooming, setting and saving destinations,
viewing points of interest (such as banks, taverns, and guilds), and managing user characters.
Map data is dynamically fetched from an SQLite database, with some components refreshed via web scraping.

Main Features:
- Zooming in and out of the map with dynamic label adjustments.
- Setting, saving, and loading destinations with AP cost calculation.
- Viewing closest points of interest, including banks, taverns, and transits.
- Managing multiple user characters, with automatic login for the last active character.
- Persistent sessions and cookies managed via an SQLite database.
- Coin and bank balance tracking with automatic updates based on in-game actions.
- Customizable themes, including colors for UI and minimap components.

Modules:
- sys: Provides access to system-specific parameters and functions.
- os: Used for interacting with the operating system (e.g., directory and file management).
- pickle: Facilitates the serialization and deserialization of Python objects.
- sqlite3: Interface for SQLite database management, used for session data, cookies, coins, and theme settings.
- requests: Allows sending HTTP requests to interact with external websites.
- re: Provides regular expression matching operations, useful for HTML parsing.
- datetime: Supplies classes for manipulating dates and times.
- bs4 (BeautifulSoup): Used for parsing HTML and XML documents.
- PySide6: Provides Python bindings for the Qt application framework, including UI components.
- PySide6.QtWebEngineWidgets: Provides web view functionality to render in-game pages.

Classes:
- RBCCommunityMap: The main application class, responsible for initializing and managing the user interface,
  web scraping, character management, and map functionalities.
- DatabaseViewer: Displays the contents of SQLite database tables in a tabbed view for inspection.
- CharacterDialog: A dialog class for adding, modifying, or deleting user characters.
- ThemeCustomizationDialog: A dialog class that allows users to customize the application's theme.
- SetDestinationDialog: A dialog class for setting destinations on the map.
- AVITDScraper: A web scraper class for fetching and updating data for guilds and shops from 'A View in the Dark'.

Key Functions:
- connect_to_database: Establishes a connection to the SQLite database and handles connection errors.
- load_data: Loads map data from the SQLite database, including coordinates for banks, taverns, transits, shops, and guilds.
- initialize_cookie_db: Sets up an SQLite database for managing cookies.
- save_cookie_to_db: Saves individual cookies from web sessions to the SQLite database.
- load_cookies_from_db: Loads cookies from the SQLite database into the web engine for persistent sessions.
- clear_cookie_db: Clears all cookies from the SQLite database.
- fetch_table_data: Retrieves column names and data from a specified SQLite database table.
- extract_coordinates_from_html: Extracts in-game map coordinates from loaded HTML content.
- find_nearest_location: Finds the nearest point of interest based on a set of coordinates.
- calculate_ap_cost: Calculates the Action Point (AP) cost between two locations on the map.
- update_guilds: Scrapes and updates guilds data in the SQLite database.
- update_shops: Scrapes and updates shops data in the SQLite database.
- get_next_update_times: Retrieves the next update times for guilds and shops from the database.
- inject_console_logging: Injects JavaScript into web pages to capture and log console messages.
- apply_theme: Applies the selected theme to the application UI components.
- save_theme_settings: Saves customized theme settings to the SQLite database.
- load_theme_settings: Loads saved theme settings from the SQLite database.
- show_about_dialog: Displays an 'About' dialog with details about the application and its version.
- show_credits_dialog: Displays a scrolling 'Credits' dialog with contributors to the project.

To install all required modules, run the following command:
 pip install pymysql requests bs4 PySide6 PySide6-WebEngine
"""



import importlib.util

import os

# -----------------------
# Imports Handling
# -----------------------
import sys


# Proceed with the rest of the imports and program setup
import logging

import pymysql

import requests

import re

import webbrowser

from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QComboBox, QLabel, QFrame, QSizePolicy, QLineEdit, QDialog, QFormLayout, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QColorDialog, QTabWidget, QScrollArea, QTableWidget, QTableWidgetItem, QInputDialog
)

from PySide6.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QPen, QIcon, QAction

from PySide6.QtCore import QUrl, Qt, QRect, QEasingCurve, QPropertyAnimation, QSize, QTimer, QDateTime

from PySide6.QtCore import Slot as pyqtSlot

from PySide6.QtWebEngineWidgets import QWebEngineView

from PySide6.QtWebChannel import QWebChannel

from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile

from PySide6.QtNetwork import QNetworkCookie

import sqlite3

from cryptography.fernet import Fernet
