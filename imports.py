"""Shared imports for the RBC Community Map (modular snapshot)."""

#!/usr/bin/env python3
# Filename: main_0.10.1

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
the city map of RavenBlack City, a text-based vampire game. It includes features such as
zooming in and out, setting and saving destinations, viewing the closest points of interest,
managing user characters, customizing the application theme, and dynamically interacting
with map data. The map data is stored and managed using an SQLite database, with support
for refreshing data scraped from the 'A View in the Dark' website.

Modules:
- sys: Provides access to system-specific parameters and functions.
- os: Used for interacting with the operating system (e.g., file and directory management).
- requests: Allows sending HTTP requests to interact with external websites (used in AVITDScraper).
- re: Provides regular expression matching operations for parsing HTML and text.
- datetime: Supplies classes for manipulating dates and times, used in database timestamps and scraping.
- bs4 (BeautifulSoup): Used for parsing HTML and XML documents (used in AVITDScraper).
- PySide6: Provides a set of Python bindings for the Qt application framework, powering the GUI.
- sqlite3: Interface for SQLite database management, central to data persistence.
- webbrowser: Enables opening URLs in the default web browser for external links.
- math: Provides mathematical functions used in damage calculations within DamageCalculator.
- logging: Used for logging debug, information, warning, and error messages across the application.

Classes:
- **RBCCommunityMap**: The core class that initializes and manages the entire application, including
  the user interface, character management, web scraping integration, shopping list generation,
  minimap functionalities, and theme customization. It serves as the main window and orchestrates
  all interactions.
  - **__init__**: Initializes the main window, sets up UI components, loads initial data, and starts
    the AVITD scraper.
  - **load_theme_settings**: Loads theme settings from the SQLite database, applying defaults if missing.
  - **save_theme_settings**: Saves customized theme settings to the SQLite database.
  - **apply_theme**: Applies the current theme settings to the application's UI stylesheet.
  - **change_theme**: Opens the theme customization dialog and applies selected changes.
  - **open_css_customization_dialog**: Opens the CSS customization dialog for webview styling.
  - **setup_cookie_handling**: Configures cookie management for the webview, connecting signals.
  - **load_cookies**: Loads saved cookies from the database into the webview profile.
  - **on_cookie_added**: Handles new cookies added to the webview, saving them to the database.
  - **setup_ui_components**: Sets up the main UI layout, including minimap, webview, and character list.
  - **go_back**: Navigates the webview to the previous page (currently unused).
  - **go_forward**: Navigates the webview to the next page (currently unused).
  - **refresh_page**: Reloads the current webview page (currently unused).
  - **create_menu_bar**: Creates the top menu bar with File, Settings, Tools, and Help options.
  - **zoom_in_browser**: Increases the zoom level of the webview content.
  - **zoom_out_browser**: Decreases the zoom level of the webview content.
  - **setup_console_logging**: Sets up web channel for capturing JavaScript console messages.
  - **inject_console_logging**: Injects JavaScript to log console messages (currently unused).
  - **handle_console_message**: Logs JavaScript console messages received via the web channel.
  - **save_webpage_screenshot**: Saves a screenshot of the webview content to a file.
  - **save_app_screenshot**: Saves a screenshot of the entire application window to a file.
  - **open_shopping_list_tool**: Opens the shopping list generator for the selected character.
  - **open_damage_calculator_tool**: Opens the damage calculator dialog for combat planning.
  - **display_shopping_list**: Displays a generated shopping list from the damage calculator (currently unused).
  - **open_powers_dialog**: Opens the powers reference dialog with character coordinates.
  - **load_characters**: Loads character data from the database into the UI list.
  - **save_characters**: Saves character data to the database in plaintext.
  - **on_character_selected**: Handles selection of a character from the list, triggering login/logout.
  - **logout_current_character**: Logs out the current character via the webview.
  - **login_selected_character**: Logs in the selected character using JavaScript form submission.
  - **firstrun_character_creation**: Creates the first character on application startup if none exist.
  - **add_new_character**: Adds a new character to the list and database.
  - **modify_character**: Modifies the selected character's details in the list and database.
  - **delete_character**: Deletes the selected character from the list and database.
  - **save_last_active_character**: Saves the ID of the last active character to the database.
  - **load_last_active_character**: Loads and logs in the last active character on startup.
  - **refresh_webview**: Reloads the webview content (currently unused).
  - **apply_custom_css**: Injects custom CSS into the webview based on database settings.
  - **on_webview_load_finished**: Handles webview load completion, triggering HTML processing and login.
  - **process_html**: Processes webview HTML to extract coordinates and coin data.
  - **extract_coordinates_from_html**: Extracts character coordinates from HTML inputs or forms.
  - **extract_coins_from_html**: Extracts and updates coin counts from HTML content.
  - **draw_minimap**: Draws the minimap with grid, locations, and lines to nearest points.
  - **update_minimap**: Updates the minimap display and info frame content.
  - **find_nearest_location**: Calculates distances to nearest locations of a given type.
  - **find_nearest_tavern**: Finds the nearest tavern to the character's position.
  - **find_nearest_bank**: Finds the nearest bank to the character's position.
  - **find_nearest_transit**: Finds the nearest transit station to the character's position.
  - **set_destination**: Opens the set destination dialog (stub, replaced by open_set_destination_dialog).
  - **get_current_destination**: Retrieves the latest destination from the database.
  - **load_destination**: Loads the last set destination into memory and updates the minimap.
  - **zoom_in**: Zooms in the minimap, centering on the character.
  - **zoom_out**: Zooms out the minimap, centering on the character.
  - **save_zoom_level_to_database**: Saves the current zoom level to the database.
  - **load_zoom_level_from_database**: Loads the saved zoom level from the database on startup.
  - **recenter_minimap**: Centers the minimap on the character's current position.
  - **go_to_location**: Moves the minimap to a selected location from dropdowns.
  - **mousePressEvent**: Handles mouse clicks on the minimap to recenter it.
  - **open_set_destination_dialog**: Opens the dialog for setting a new destination.
  - **save_to_recent_destinations**: Saves a destination to the recent destinations list.
  - **calculate_ap_cost**: Calculates Action Point (AP) cost between two coordinates.
  - **update_info_frame**: Updates the info frame with nearest locations and AP costs.
  - **get_intersection_name**: Converts coordinates to a readable intersection name.
  - **open_discord**: Opens the RBC Discord invite link in the default browser.
  - **open_website**: Opens the RBC website in the default browser.
  - **show_about_dialog**: Displays an about dialog with application version and details.
  - **show_credits_dialog**: Displays a credits dialog with contributor information.
  - **open_database_viewer**: Opens the database viewer to inspect SQLite tables.
  - **fetch_table_data**: Fetches column names and data from a database table (redundant standalone version).
  - **generate_custom_css**: Generates a CSS string from saved customizations (redundant in this class).

- **DatabaseViewer**: A utility class that displays the contents of SQLite database tables in a tabbed view,
  allowing users to browse persistent data.
  - **__init__**: Initializes the viewer window and populates tabs with table data.
  - **get_table_data**: Fetches column names and data for a specific table.
  - **add_table_tab**: Adds a tab to the viewer for a given table’s data.
  - **closeEvent**: Closes the database connection when the viewer is closed.

- **CharacterDialog**: A dialog class for adding or modifying user characters, handling name and password input.
  - **__init__**: Initializes the dialog with optional pre-filled character data.

- **ThemeCustomizationDialog**: A dialog class for customizing the application’s UI and minimap theme colors.
  - **__init__**: Initializes the dialog with tabs for UI and minimap customization.
  - **setup_ui_tab**: Sets up the UI customization tab with color selection options.
  - **setup_minimap_tab**: Sets up the minimap customization tab with color selection options.
  - **change_color**: Opens a color picker to update a specific element’s color.
  - **apply_theme**: Applies the selected theme to the application (unused directly, called via parent).

- **CSSCustomizationDialog**: A dialog for customizing the webview’s CSS, allowing color and image modifications.
  - **__init__**: Initializes the dialog with tabs for CSS elements and customization options.
  - **initialize_css_table**: Creates the custom_css table in the database if it doesn’t exist.
  - **add_tab**: Adds a tab for a category of CSS elements (e.g., General, Tables).
  - **pick_color**: Opens a color picker to set a background color for a CSS element.
  - **pick_image**: Opens a file dialog to set a background image for a CSS element.
  - **save_css_item**: Saves a CSS customization to the database.
  - **load_existing_customizations**: Loads saved CSS customizations into the UI.
  - **save_and_apply_changes**: Saves changes and applies them to the webview.
  - **apply_custom_css**: Injects custom CSS into the webview via the parent.
  - **generate_custom_css**: Generates a CSS string from database customizations.
  - **upload_css_file**: Uploads and applies an external CSS file.
  - **clear_all_customizations**: Clears all saved CSS customizations.

- **AVITDScraper**: A scraper class that fetches guild and shop data from 'A View in the Dark' to update the database.
  - **__init__**: Initializes the scraper with URL, headers, and database connection.
  - **scrape_guilds_and_shops**: Scrapes guild and shop data and updates the database.
  - **scrape_section**: Scrapes a specific section (guilds or shops) from the website.
  - **extract_next_update_time**: Extracts the next update time for guilds or shops.
  - **display_results**: Logs scraped data for debugging purposes.
  - **update_database**: Updates the SQLite database with scraped guild or shop data.
  - **close_connection**: Closes the database connection (currently unused).

- **set_destination_dialog**: A dialog for setting a destination on the map, with options for predefined and custom locations.
  - **__init__**: Initializes the dialog with dropdowns and buttons for destination selection.
  - **populate_recent_destinations**: Populates the recent destinations dropdown for the selected character.
  - **populate_dropdown**: Populates a dropdown with items from a data source.
  - **update_comboboxes**: Updates dropdowns with fresh data from the scraper and database.
  - **show_notification**: Displays a temporary notification message.
  - **clear_destination**: Clears the current destination for the selected character.
  - **set_destination**: Sets a new destination based on user selection.
  - **get_selected_destination**: Retrieves coordinates of the selected destination.
  - **set_external_destination**: Sets a destination programmatically (stub, not implemented).
  - **show_error_dialog**: Displays an error message dialog.

- **ShoppingListTool**: A tool for generating shopping lists, calculating costs based on shop items and charisma levels.
  - **__init__**: Initializes the tool with character name and database path.
  - **setup_ui**: Sets up the UI with shop selection, item lists, and buttons.
  - **add_item**: Adds a selected item to the shopping list with a specified quantity.
  - **remove_item**: Removes or reduces the quantity of an item from the shopping list.
  - **populate_shop_dropdown**: Populates the shop dropdown with database data.
  - **load_items**: Loads available items for the selected shop and charisma level.
  - **update_shopping_list_prices**: Updates prices in the shopping list based on charisma level.
  - **update_total**: Calculates and displays the total cost of the shopping list.
  - **coins_in_pocket**: Retrieves the character’s pocket coin count from the database.
  - **coins_in_bank**: Retrieves the character’s bank coin count from the database.

- **DamageCalculator**: A dialog for calculating damage dealt to characters based on blood points (BP) and weapon costs.
  - **__init__**: Initializes the dialog with BP input and charisma selection.
  - **update_charisma_level**: Updates the charisma level based on dropdown selection.
  - **calculate_damage**: Calculates the weapons needed to reduce target BP to zero.

- **PowersDialog**: A dialog for viewing power information and setting guild destinations based on character position.
  - **__init__**: Initializes the dialog with a powers list and details panel.
  - **create_labeled_field**: Creates a labeled field for displaying power details.
  - **load_powers**: Loads all powers from the database into the list.
  - **load_power_info**: Displays detailed information for a selected power.
  - **enable_nearest_peacekeeper_mission**: Enables the destination button for the nearest Peacekeeper’s Mission.
  - **configure_destination_button**: Configures the destination button with guild location data.
  - **set_destination**: Sets a guild location as the destination and updates the minimap.
  - **closeEvent**: Closes the database connection when the dialog is closed.

Functions:
- **initialize_database**: Sets up the SQLite database schema and initial data.
- **save_cookie_to_db**: Saves individual cookies to the SQLite database.
- **load_cookies_from_db**: Loads cookies from the database into the web engine.
- **clear_cookie_db**: Clears all cookies from the database (currently unused).
- **load_data**: Loads map-related data (columns, rows, locations) from the database.
- **check_required_modules**: Checks if required Python modules are installed.
- **ensure_directories_exist**: Creates required directories (logs, sessions, images) if missing.
- **setup_logging**: Configures logging to save logs in the 'logs' directory.
- **main**: Entry point to instantiate and run the QApplication.

Key Features:
- Dynamic minimap with zoom functionality, edge-case handling, and grid-based rendering.
- Database-backed storage for settings, themes, character data, and cookies using SQLite.
- Integration with 'A View in the Dark' for data scraping and updating in-game information.
- Support for customizing themes and dynamically updating the application's appearance.
- Ability to calculate damage dealt to characters and generate shopping lists based on in-game needs.

To install all required modules, run the following command:
 pip install requests bs4 PySide6 PySide6-WebEngine
"""


# -----------------------
# Imports Handling
# -----------------------

import importlib.util

import math

import os

import sys


# Proceed with the rest of the imports and program setup
import logging

import logging.handlers

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

from PySide6.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QPen, QIcon, QAction, QIntValidator, QMouseEvent, \
    QKeySequence, QShortcut

from PySide6.QtCore import QUrl, Qt, QRect, QEasingCurve, QPropertyAnimation, QSize, QTimer, QDateTime

from PySide6.QtCore import Slot as pyqtSlot

from PySide6.QtWebEngineWidgets import QWebEngineView

from PySide6.QtWebChannel import QWebChannel

from PySide6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile

from PySide6.QtNetwork import QNetworkCookie

import sqlite3
