"""Shared imports for the RBC Community Map (modular snapshot)."""

#!/usr/bin/env python3
# Filename: main_0.9.1

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
RBC City Map Application
=========================
This application provides a comprehensive graphical interface for viewing and navigating
the city map of RavenBlack City. It includes features such as zooming in and out, setting
and saving destinations, viewing the closest points of interest, managing user characters,
customizing the application theme, and dynamically interacting with map data. The map data
is stored and managed using an SQLite database, with support for refreshing data scraped
from the 'A View in the Dark' website.

Modules:
- sys: Provides access to system-specific parameters and functions.
- os: Used for interacting with the operating system (e.g., file and directory management).
- pickle: Facilitates the serialization and deserialization of Python objects.
- requests: Allows sending HTTP requests to interact with external websites.
- re: Provides regular expression matching operations.
- datetime: Supplies classes for manipulating dates and times.
- bs4 (BeautifulSoup): Used for parsing HTML and XML documents.
- PySide6: Provides a set of Python bindings for the Qt application framework.
- sqlite3: Interface for SQLite database management.
- webbrowser: Enables the opening of URLs in the default web browser.
- math: Provides mathematical functions used in damage calculations.
- logging: Used for logging debug, information, warning, and error messages.

Classes:
- RBCCommunityMap: The main application class that initializes and manages the user interface,
  character management, web scraping, shopping list generation, minimap functionalities, and theme customization.
- DatabaseViewer: A utility class that displays the contents of database tables in a tabbed view.
- CharacterDialog: A dialog class for adding or modifying user characters.
- ThemeCustomizationDialog: A dialog class for customizing the application theme.
- SetDestinationDialog: A dialog class for setting a destination on the map.
- AVITDScraper: A scraper class that fetches data from 'A View in the Dark' to update guilds
  and shops data in the database.
- ShoppingListTool: A tool for generating shopping lists, including calculating total costs
  based on selected items and character conditions.
- CoinScraper: A class responsible for scraping the current coin count from the character's
  webpage and updating the database with the available coins.
- DamageCalculator: A class for calculating damage dealt to characters based on their blood points (BP).
- DamageCalculatorUI: A user interface for the DamageCalculator, allowing users to calculate
  and analyze damage and optionally add required items to the shopping list.

Functions:
- initialize_database: Sets up the SQLite database for storing map data, character data, settings, and cookies.
- save_cookie_to_db: Saves individual cookies to the SQLite database.
- load_cookies_from_db: Loads cookies from the SQLite database into the web engine.
- clear_cookie_db: Clears all cookies from the SQLite database.
- fetch_table_data: Retrieves and returns the column names and data from a specified database table.
- extract_coordinates_from_html: Extracts map coordinates from the loaded HTML content.
- process_html: Updates map-related data such as character coordinates and coins using extracted HTML data.
- find_nearest_location: Finds the nearest point of interest based on a given set of coordinates.
- calculate_ap_cost: Calculates the Action Point (AP) cost between two map coordinates.
- update_guilds: Updates the guilds data in the SQLite database using scraped data.
- update_shops: Updates the shops data in the SQLite database using scraped data.
- get_next_update_times: Retrieves the next update times for guilds and shops from the SQLite database.
- inject_console_logging: Injects JavaScript into the web page to capture and log console messages.
- apply_theme: Applies the currently selected theme to the application UI.
- save_theme_settings: Saves the customized theme settings to the SQLite database.
- load_theme_settings: Loads the saved theme settings from the SQLite database.
- save_zoom_level_to_database: Saves the minimap zoom level to the SQLite database.
- load_zoom_level_from_database: Loads the minimap zoom level from the SQLite database during application start.
- show_about_dialog: Displays the 'About' dialog with information about the application.
- show_credits_dialog: Displays the 'Credits' dialog with information about contributors.

Key Features:
- Dynamic minimap with zoom functionality, edge-case handling, and grid-based rendering.
- Database-backed storage for settings, themes, character data, and cookies using SQLite.
- Integration with 'A View in the Dark' for data scraping and updating in-game information.
- Support for customizing themes and dynamically updating the application's appearance.
- Ability to calculate damage dealt to characters and generate shopping lists based on in-game needs.

To install all required modules, run the following command:
 pip install requests bs4 PySide6 PySide6-WebEngine
"""


import importlib.util

import math

import os

# -----------------------
# Imports Handling
# -----------------------
import sys


# Proceed with the rest of the imports and program setup
import logging

import requests

import re

import webbrowser

from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QComboBox, QLabel, QFrame, QSizePolicy, QLineEdit, QDialog, QFormLayout, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QColorDialog, QTabWidget, QScrollArea, QTableWidget, QTableWidgetItem, QInputDialog,
    QTextEdit
)

from PySide6.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QPen, QIcon, QAction, QIntValidator, QMouseEvent

from PySide6.QtCore import QUrl, Qt, QRect, QEasingCurve, QPropertyAnimation, QSize, QTimer, QDateTime

from PySide6.QtCore import Slot as pyqtSlot

from PySide6.QtWebEngineWidgets import QWebEngineView

from PySide6.QtWebChannel import QWebChannel

from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile

from PySide6.QtNetwork import QNetworkCookie

import sqlite3
