#!/usr/bin/env python3
# Filename: main_0.7.0
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
This application provides a graphical interface to view a city map of RavenBlack City.
It includes features such as viewing the map, zooming in and out, setting destinations,
and refreshing the map with updated data from the 'A View in the Dark' website.

Modules:
- sys
- pickle
- pymysql
- requests
- datetime
- bs4 (BeautifulSoup)
- PyQt5

Classes:
- CityMapApp: Main application class for the RBC City Map.

Functions:
- connect_to_database: Establish a connection to the MySQL database.
- load_data: Load data from the database and return it as various dictionaries and lists.
- scrape_avitd_data: Scrape guilds and shops data from 'A View in the Dark' and update the database with next update timestamps.
- extract_next_update_time: Extract the next update time from the text and calculate the next update timestamp.
- update_guild: Update a single guild in the database.
- update_shop: Update a single shop in the database.
- update_guilds: Update the guilds data in the database.
- update_shops: Update the shops data in the database.
- get_next_update_times: Retrieve the next update times for guilds and shops from the database.

To install all required modules, run the following command:
 pip install pymysql requests bs4 PyQt5 PyQtWebEngine
"""

try:
    import sys
    import pickle
    import pymysql
    import requests
    import re
    import os
    import time
    import sqlite3
    import webbrowser
    from datetime import datetime, timedelta
    from bs4 import BeautifulSoup
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QComboBox, QLabel, QFrame, QSizePolicy, QLineEdit, QDialog, QFormLayout, QListWidget, QListWidgetItem,
        QMessageBox
    )
    from PyQt5.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QPen, QIcon
    from PyQt5.QtCore import QUrl, Qt
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    import logging

except ModuleNotFoundError as e:
    run = True
    while run:
        print(f"I believe you are missing some modules, copy and paste the line below.\n")
        installPip = input(f"Would you like me to install those for you? (Y/N): ")
        if installPip.lower() == "y":
            os.system(f"pip install PyQtWebEngine pymysql requests PyQt5 bs4 PyQt5")
            timer = 10
            for times in range(0, timer):
                print(f"The Program will run in {timer - times} seconds")
                times += 1
                time.sleep(1)
            import sys
            import pickle
            import pymysql
            import requests
            import re
            import os
            import time
            import sqlite3
            import webbrowser
            from datetime import datetime, timedelta
            from bs4 import BeautifulSoup
            from PyQt5.QtWidgets import (
                QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                QPushButton, QComboBox, QLabel, QFrame, QSizePolicy, QLineEdit, QDialog, QFormLayout, QListWidget,
                QListWidgetItem, QMessageBox
            )
            from PyQt5.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QPen, QIcon
            from PyQt5.QtCore import QUrl, Qt
            from PyQt5.QtWebEngineWidgets import QWebEngineView
            import logging
            break

        elif installPip.lower() == "n":
            print(f"\nYou may use this line to install what is needed if you want.\n")
            print(f"pip install pymysql requests PyQt5 bs4 PyQtWebEngine")
            sys.exit()
        else:
            print(f"\nThis was not yes or no.....\n")
            continue

except Exception as e:
    print(f"Something broke and idk why...")

# -----------------------
# Directory setup
# -----------------------

def ensure_directories_exist():
    """
    Ensure that the required directories exist. If they don't, create them.
    """
    required_dirs = ['logs', 'sessions']
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

# Call the function to ensure directories are present
ensure_directories_exist()

# -----------------------
# Logging setup
# -----------------------

def setup_logging():
    """
    Setup logging configuration to save logs in the 'logs' directory with the filename 'rbc_{date}.log'.
    """
    log_filename = datetime.now().strftime('logs/rbc_%Y-%m-%d.log')
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_filename,
        filemode='a'  # Append to the log file if it exists
    )
    print(f"Logging to: {log_filename}")

# Call the logging setup
setup_logging()

# -----------------------
# Database connection
# -----------------------

# Server information
LOCAL_HOST = "127.0.0.1"
REMOTE_HOST = "lollis-home.ddns.net"
USER = "rbc_maps"
PASSWORD = "RBC_Community_Map"
DATABASE = "city_map"

def connect_to_database():
    """
    Connect to the MySQL database.

    Returns:
        pymysql.Connection: Database connection object.
    """
    try:
        connection = pymysql.connect(
            host=LOCAL_HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        logging.info("Connected to local MySQL instance")
        return connection
    except pymysql.MySQLError as err:
        logging.error("Connection to local MySQL instance failed: %s", err)
        # Attempt to connect to the remote server
        try:
            connection = pymysql.connect(
                host=REMOTE_HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE
            )
            logging.info("Connected to remote MySQL instance")
            return connection
        except pymysql.MySQLError as err:
            logging.error("Connection to remote MySQL instance failed: %s", err)
            return None

# -----------------------
# Load Data from Database
# -----------------------

def load_data():
    """
    Load data from the database and return it as various dictionaries and lists.

    Returns:
        tuple: Contains columns, rows, banks_coordinates, taverns_coordinates,
               transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates
    """
    connection = connect_to_database()
    if not connection:
        sys.exit("Failed to connect to the database.")

    cursor = connection.cursor()

    # Fetch columns
    cursor.execute("SELECT `Name`, `Coordinate` FROM `columns`")
    columns_data = cursor.fetchall()
    columns = {name: int(coordinate) for name, coordinate in columns_data}

    # Fetch rows
    cursor.execute("SELECT `Name`, `Coordinate` FROM `rows`")
    rows_data = cursor.fetchall()
    rows = {name: int(coordinate) for name, coordinate in rows_data}

    # Fetch coordinates from banks table
    cursor.execute("SELECT `Column`, `Row` FROM banks")
    banks_data = cursor.fetchall()
    banks_coordinates = [
        (columns.get(col) + 1 if columns.get(col) is not None else None,
         rows.get(row) + 1 if rows.get(row) is not None else None)
        for col, row in banks_data
    ]
    banks_coordinates = [(col, row) for col, row in banks_coordinates if col is not None and row is not None]

    # Fetch taverns
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM taverns")
    taverns_data = cursor.fetchall()
    taverns_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in taverns_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch transits
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM transits")
    transits_data = cursor.fetchall()
    transits_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in transits_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch user buildings
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM userbuildings")
    user_buildings_data = cursor.fetchall()
    user_buildings_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in user_buildings_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch color mappings
    cursor.execute("SELECT `Type`, `Color` FROM color_mappings")
    color_mappings_data = cursor.fetchall()
    color_mappings = {type_: QColor(color) for type_, color in color_mappings_data}

    # Fetch shops
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM shops")
    shops_data = cursor.fetchall()
    shops_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in shops_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch guilds
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM guilds")
    guilds_data = cursor.fetchall()
    guilds_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in guilds_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch places of interest
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM placesofinterest")
    places_of_interest_data = cursor.fetchall()
    places_of_interest_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in places_of_interest_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    connection.close()

    return columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates

# Load the data and ensure that color_mappings is initialized before the CityMapApp class is used
columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates = load_data()

# -----------------------
# CityMapApp Main Class
# -----------------------

class CityMapApp(QMainWindow):
    """
    Main application class for the RBC City Map.
    """

    def __init__(self):
        """
        Initialize the CityMapApp and its components.
        """
        super().__init__()

        self.setWindowIcon(QIcon('favicon.ico'))
        self.setWindowTitle('RBC City Map')
        self.setGeometry(100, 100, 1200, 800)

        # Load the data
        self.columns, self.rows, self.banks_coordinates, self.taverns_coordinates, self.transits_coordinates, self.user_buildings_coordinates, self.color_mappings, self.shops_coordinates, self.guilds_coordinates, self.places_of_interest_coordinates = load_data()

        self.zoom_level = 3
        self.minimap_size = 280
        self.column_start = 0
        self.row_start = 0
        self.destination = None
        self.color_mappings = self.color_mappings

        # Initialize characters list and character_list widget early to avoid attribute errors
        self.characters = []
        self.character_list = QListWidget()

        self.load_characters()

        if not self.characters:
            self.add_new_character()
            if not self.characters:
                # Exit if no characters are added
                sys.exit("No characters added. Exiting the application.")

        # Now continue initializing the rest of the UI components
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Main layout for map and controls
        map_layout = QHBoxLayout()
        main_layout.addLayout(map_layout)

        # Left layout containing the minimap and control buttons
        left_layout = QVBoxLayout()
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.Box)
        left_frame.setFixedWidth(300)
        left_frame.setLayout(left_layout)

        # Frame for the minimap
        minimap_frame = QFrame()
        minimap_frame.setFrameShape(QFrame.Box)
        minimap_frame.setFixedSize(self.minimap_size, self.minimap_size)
        minimap_layout = QVBoxLayout()
        minimap_layout.setContentsMargins(0, 0, 0, 0)
        minimap_frame.setLayout(minimap_layout)

        # Label to display the minimap
        self.minimap_label = QLabel()
        self.minimap_label.setFixedSize(self.minimap_size, self.minimap_size)
        self.minimap_label.setStyleSheet("background-color: lightgrey;")
        minimap_layout.addWidget(self.minimap_label)
        left_layout.addWidget(minimap_frame)

        # Information frame to display closest locations and AP costs
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Box)
        info_frame.setFixedHeight(195)
        info_layout = QVBoxLayout()
        info_frame.setLayout(info_layout)
        left_layout.addWidget(info_frame)

        # Labels to display closest locations and destination
        self.bank_label = QLabel()
        self.bank_label.setAlignment(Qt.AlignLeft)
        self.bank_label.setStyleSheet("background-color: blue; color: white;font-weight: bold;")
        self.bank_label.setWordWrap(True)
        self.bank_label.setFixedHeight(40)
        info_layout.addWidget(self.bank_label)

        self.transit_label = QLabel()
        self.transit_label.setAlignment(Qt.AlignLeft)
        self.transit_label.setStyleSheet("background-color: red; color: white;font-weight: bold;")
        self.transit_label.setWordWrap(True)
        self.transit_label.setFixedHeight(40)
        info_layout.addWidget(self.transit_label)

        self.tavern_label = QLabel()
        self.tavern_label.setAlignment(Qt.AlignLeft)
        self.tavern_label.setStyleSheet("background-color: orange; color: white;font-weight: bold;")
        self.tavern_label.setWordWrap(True)
        self.tavern_label.setFixedHeight(40)
        info_layout.addWidget(self.tavern_label)

        self.destination_label = QLabel()
        self.destination_label.setAlignment(Qt.AlignLeft)
        self.destination_label.setStyleSheet("background-color: green; color: white;font-weight: bold;")
        self.destination_label.setWordWrap(True)
        self.destination_label.setFixedHeight(40)
        info_layout.addWidget(self.destination_label)

        # Layout for column and row selection with Go button
        combo_go_layout = QHBoxLayout()
        combo_go_layout.setSpacing(5)

        self.combo_columns = QComboBox()
        self.combo_columns.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_columns.addItems(self.columns.keys())

        self.combo_rows = QComboBox()
        self.combo_rows.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_rows.addItems(self.rows.keys())

        go_button = QPushButton('Go')
        go_button.setFixedSize(25, 25)
        go_button.clicked.connect(self.go_to_location)

        combo_go_layout.addWidget(self.combo_columns)
        combo_go_layout.addWidget(self.combo_rows)
        combo_go_layout.addWidget(go_button)

        left_layout.addLayout(combo_go_layout)

        # Layout for zoom and set destination buttons
        zoom_layout = QHBoxLayout()
        button_size = (self.minimap_size - 10) // 3

        zoom_in_button = QPushButton('Zoom in')
        zoom_in_button.setFixedSize(button_size, 25)
        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(zoom_in_button)

        zoom_out_button = QPushButton('Zoom out')
        zoom_out_button.setFixedSize(button_size, 25)
        zoom_out_button.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(zoom_out_button)

        set_destination_button = QPushButton('Set Destination')
        set_destination_button.setFixedSize(button_size, 25)
        set_destination_button.clicked.connect(self.set_destination)
        zoom_layout.addWidget(set_destination_button)

        left_layout.addLayout(zoom_layout)

        # Layout for refresh, discord, and website buttons
        action_layout = QHBoxLayout()

        refresh_button = QPushButton('Refresh')
        refresh_button.setFixedSize(button_size, 25)
        refresh_button.clicked.connect(self.refresh_webview)
        action_layout.addWidget(refresh_button)

        discord_button = QPushButton('Discord')
        discord_button.setFixedSize(button_size, 25)
        discord_button.clicked.connect(self.open_discord)
        action_layout.addWidget(discord_button)

        website_button = QPushButton('Website')
        website_button.setFixedSize(button_size, 25)
        website_button.clicked.connect(self.show_coming_soon_popup)
        action_layout.addWidget(website_button)

        left_layout.addLayout(action_layout)

        # Frame for character list and management buttons
        character_frame = QFrame()
        character_frame.setFrameShape(QFrame.Box)
        character_layout = QVBoxLayout()
        character_frame.setLayout(character_layout)

        character_list_label = QLabel('Character List')
        character_layout.addWidget(character_list_label)

        self.character_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.character_list.setFixedHeight(100)
        self.character_list.itemClicked.connect(self.on_character_selected)
        character_layout.addWidget(self.character_list)

        character_buttons_layout = QHBoxLayout()
        new_button = QPushButton('New')
        new_button.setFixedSize(75, 25)
        new_button.clicked.connect(self.add_new_character)
        modify_button = QPushButton('Modify')
        modify_button.setFixedSize(75, 25)
        modify_button.clicked.connect(self.modify_character)
        delete_button = QPushButton('Delete')
        delete_button.setFixedSize(75, 25)
        delete_button.clicked.connect(self.delete_character)
        character_buttons_layout.addWidget(new_button)
        character_buttons_layout.addWidget(modify_button)
        character_buttons_layout.addWidget(delete_button)
        character_layout.addLayout(character_buttons_layout)

        left_layout.addWidget(character_frame)

        # Web engine view
        map_layout.addWidget(left_frame)

        # Frame for displaying the website
        self.website_frame = QWebEngineView()
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl'))
        self.website_frame.loadFinished.connect(self.on_webview_load_finished)
        map_layout.addWidget(self.website_frame)

        self.show()
        self.update_minimap()

    def on_character_selected(self, item):
        """
        Handle character selection from the list.

        Args:
            item (QListWidgetItem): The selected item in the list.
        """
        character_name = item.text()
        selected_character = next((char for char in self.characters if char['name'] == character_name), None)
        if selected_character:
            logging.debug(f"Selected character: {character_name}")
            self.selected_character = selected_character
            self.logout_current_character()

    def logout_current_character(self):
        """
        Logout the current character.
        """
        logging.debug("Logging out current character.")
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl?action=logout'))

        # Delay login to allow logout to complete
        self.website_frame.loadFinished.connect(self.login_selected_character)

    def login_selected_character(self):
        """
        Log in the selected character after logging out the current one.
        """
        if not self.selected_character:
            logging.warning("No character selected for login.")
            return

        logging.debug(f"Logging in character: {self.selected_character['name']}")
        name = self.selected_character['name']
        password = self.selected_character['password']

        login_script = f"""
            var loginForm = document.querySelector('form');
            if (loginForm) {{
                loginForm.iam.value = '{name}';
                loginForm.passwd.value = '{password}';
                loginForm.submit();
            }} else {{
                console.error('Login form not found.');
            }}
        """
        self.website_frame.page().runJavaScript(login_script)

    def on_webview_load_finished(self):
        """
        Handle the event when the webview finishes loading.
        """
        self.website_frame.page().toHtml(self.process_html)

    def process_html(self, html):
        """
        Process the HTML content of the webview to extract coordinates and update the minimap.

        Args:
            html (str): HTML content as a string.
        """
        x_coord, y_coord = self.extract_coordinates_from_html(html)
        if x_coord is not None and y_coord is not None:
            self.column_start = x_coord
            self.row_start = y_coord
            self.update_minimap()

    def extract_coordinates_from_html(self, html):
        """
        Extract coordinates from the HTML content.

        Args:
            html (str): HTML content as a string.

        Returns:
            tuple: x and y coordinates.
        """
        soup = BeautifulSoup(html, 'html.parser')
        x_input = soup.find('input', {'name': 'x'})
        y_input = soup.find('input', {'name': 'y'})
        if x_input and y_input:
            return int(x_input['value']), int(y_input['value'])

        current_location_td = soup.find('td', {'class': 'street', 'style': 'border: solid 1px white;'})

        if current_location_td:
            form = current_location_td.find('form')
            if form:
                x_value = int(form.find('input', {'name': 'x'})['value'])
                y_value = int(form.find('input', {'name': 'y'})['value'])
                return x_value, y_value

        return None, None

    def refresh_webview(self):
        """
        Refresh the webview content.
        """
        self.website_frame.reload()

    def save_characters(self):
        """
        Save characters to a pickle file in the 'sessions' directory.
        """
        try:
            # Ensure the 'sessions' directory exists
            os.makedirs('sessions', exist_ok=True)

            with open('sessions/characters.pkl', 'wb') as f:
                pickle.dump(self.characters, f)
                logging.debug("Characters saved successfully to file.")
        except Exception as e:
            logging.error(f"Failed to save characters: {e}")

    def load_characters(self):
        """
        Load characters from a pickle file in the 'sessions' directory.
        """
        try:
            with open('sessions/characters.pkl', 'rb') as f:
                self.characters = pickle.load(f)
                self.character_list.clear()
                for character in self.characters:
                    self.character_list.addItem(QListWidgetItem(character['name']))
                logging.debug("Characters loaded successfully from file.")
        except FileNotFoundError:
            logging.warning("Characters file not found. No characters loaded.")
            self.characters = []
        except Exception as e:
            logging.error(f"Failed to load characters: {e}")
            self.characters = []

    def add_new_character(self):
        """
        Add a new character.
        """
        logging.debug("Adding a new character.")
        dialog = CharacterDialog(self)
        if dialog.exec_():
            name = dialog.name_edit.text()
            password = dialog.password_edit.text()
            self.characters.append({'name': name, 'password': password})
            self.save_characters()
            self.character_list.addItem(QListWidgetItem(name))
            logging.debug(f"Character {name} added.")

    def modify_character(self):
        """
        Modify the selected character.
        """
        current_item = self.character_list.currentItem()
        if current_item is None:
            logging.warning("No character selected for modification.")
            return

        name = current_item.text()
        character = next((char for char in self.characters if char['name'] == name), None)
        if character:
            logging.debug(f"Modifying character: {name}")
            dialog = CharacterDialog(self, character)
            if dialog.exec_():
                character['name'] = dialog.name_edit.text()
                character['password'] = dialog.password_edit.text()
                self.save_characters()
                current_item.setText(character['name'])
                logging.debug(f"Character {name} modified.")

    def delete_character(self):
        """
        Delete the selected character.
        """
        current_item = self.character_list.currentItem()
        if current_item is None:
            logging.warning("No character selected for deletion.")
            return

        name = current_item.text()
        self.characters = [char for char in self.characters if char['name'] != name]
        self.save_characters()
        self.character_list.takeItem(self.character_list.row(current_item))
        logging.debug(f"Character {name} deleted.")

    # -----------------------
    # Minimap Drawing and Update
    # -----------------------

    def draw_minimap(self):
        """
        Draws the minimap with various features such as special locations and lines to nearest locations.
        """
        pixmap = QPixmap(self.minimap_size, self.minimap_size)
        painter = QPainter(pixmap)
        painter.fillRect(0, 0, self.minimap_size, self.minimap_size, QColor('lightgrey'))

        block_size = self.minimap_size // self.zoom_level
        border_size = 1  # Size of the border around each cell
        font = painter.font()
        font.setPointSize(8)  # Adjust font size as needed
        painter.setFont(font)

        # Calculate font metrics for centering text
        font_metrics = QFontMetrics(font)

        def draw_location(column_index, row_index, color, label_text=None):
            """
            Draws a location on the minimap.

            Args:
                column_index (int): Column index of the location.
                row_index (int): Row index of the location.
                color (QColor): Color to fill the location.
                label_text (str, optional): Label text to draw at the location. Defaults to None.
            """
            x0 = (column_index - self.column_start) * block_size
            y0 = (row_index - self.row_start) * block_size

            # Draw a smaller rectangle within the cell
            inner_margin = block_size // 4
            painter.fillRect(x0 + inner_margin, y0 + inner_margin,
                             block_size - 2 * inner_margin, block_size - 2 * inner_margin, color)

            if label_text:
                text_rect = font_metrics.boundingRect(label_text)
                text_x = x0 + (block_size - text_rect.width()) // 2
                text_y = y0 + (block_size + text_rect.height()) // 2 - font_metrics.descent()
                painter.setPen(QColor('white'))
                painter.drawText(text_x, text_y, label_text)

        for i in range(self.zoom_level):
            for j in range(self.zoom_level):
                column_index = self.column_start + j
                row_index = self.row_start + i

                x0, y0 = j * block_size, i * block_size

                # Draw the cell background
                painter.setPen(QColor('white'))
                painter.drawRect(x0, y0, block_size - border_size, block_size - border_size)

                column_name = next((name for name, coord in self.columns.items() if coord == column_index), None)
                row_name = next((name for name, coord in self.rows.items() if coord == row_index), None)

                # Draw cell background color
                if column_index < min(self.columns.values()) or column_index > max(self.columns.values()) or row_index < min(
                        self.rows.values()) or row_index > max(self.rows.values()):
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, self.color_mappings["edge"])
                elif (column_index % 2 == 1) or (row_index % 2 == 1):
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, self.color_mappings["alley"])
                else:
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, self.color_mappings["default"])

                # Draw labels only at intersections of named streets
                if column_name and row_name:
                    label_text = f"{column_name} & {row_name}"
                    text_rect = font_metrics.boundingRect(label_text)
                    text_x = x0 + (block_size - text_rect.width()) // 2
                    text_y = y0 + (block_size + text_rect.height()) // 2 - font_metrics.descent()
                    painter.setPen(QColor('white'))
                    painter.drawText(text_x, text_y, label_text)

        # Draw special locations
        for (column_index, row_index) in self.banks_coordinates:
            draw_location(column_index, row_index, self.color_mappings["bank"], "Bank")

        for name, (column_index, row_index) in self.taverns_coordinates.items():
            draw_location(column_index, row_index, self.color_mappings["tavern"], name)

        for name, (column_index, row_index) in self.transits_coordinates.items():
            draw_location(column_index, row_index, self.color_mappings["transit"], name)

        for name, (column_index, row_index) in self.user_buildings_coordinates.items():
            draw_location(column_index, row_index, self.color_mappings["user_building"], name)

        for name, (column_index, row_index) in self.shops_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["shop"], name)
            else:
                logging.warning(f"Skipping shop '{name}' due to missing coordinates")

        for name, (column_index, row_index) in self.guilds_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["guild"], name)
            else:
                logging.warning(f"Skipping guild '{name}' due to missing coordinates")

        for name, (column_index, row_index) in self.places_of_interest_coordinates.items():
            if column_index is not None and row_index is not None:
                draw_location(column_index, row_index, self.color_mappings["placesofinterest"], name)
            else:
                logging.warning(f"Skipping place of interest '{name}' due to missing coordinates")

        # Get current location
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2

        # Find and draw lines to nearest locations
        nearest_tavern = self.find_nearest_tavern(current_x, current_y)
        nearest_bank = self.find_nearest_bank(current_x, current_y)
        nearest_transit = self.find_nearest_transit(current_x, current_y)

        if nearest_tavern:
            nearest_tavern = nearest_tavern[0][1]
            painter.setPen(QPen(QColor('orange'), 3))  # Set pen color to orange and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_tavern[0] - self.column_start) * block_size + block_size // 2,
                (nearest_tavern[1] - self.row_start) * block_size + block_size // 2
            )

        if nearest_bank:
            nearest_bank = nearest_bank[0][1]
            painter.setPen(QPen(QColor('blue'), 3))  # Set pen color to blue and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_bank[0] - self.column_start) * block_size + block_size // 2,
                (nearest_bank[1] - self.row_start) * block_size + block_size // 2
            )

        if nearest_transit:
            nearest_transit = nearest_transit[0][1]
            painter.setPen(QPen(QColor('red'), 3))  # Set pen color to red and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_transit[0] - self.column_start) * block_size + block_size // 2,
                (nearest_transit[1] - self.row_start) * block_size + block_size // 2
            )

        # Draw destination line
        if self.destination:
            painter.setPen(QPen(QColor('green'), 3))  # Set pen color to green and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (self.destination[0] - self.column_start) * block_size + block_size // 2,
                (self.destination[1] - self.row_start) * block_size + block_size // 2
            )

        painter.end()
        self.minimap_label.setPixmap(pixmap)

    def update_minimap(self):
        """
        Update the minimap.
        """
        self.draw_minimap()
        self.update_info_frame()

    def find_nearest_location(self, x, y, locations):
        """
        Find the nearest location to the given coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.
            locations (list): List of location coordinates.

        Returns:
            list: List of distances and corresponding coordinates.
        """
        distances = []
        for loc in locations:
            lx, ly = loc
            dist = max(abs(lx - x), abs(ly - y))  # Using Chebyshev distance
            distances.append((dist, (lx, ly)))
        distances.sort()
        return distances

    def find_nearest_tavern(self, x, y):
        """
        Find the nearest tavern to the given coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            list: List of distances and corresponding coordinates.
        """
        return self.find_nearest_location(x, y, list(self.taverns_coordinates.values()))

    def find_nearest_bank(self, x, y):
        """
        Find the nearest bank to the given coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            list: List of distances and corresponding coordinates.
        """
        return self.find_nearest_location(x, y, self.banks_coordinates)

    def find_nearest_transit(self, x, y):
        """
        Find the nearest transit station to the given coordinates.

        Args:
            x (int): X coordinate.
            y (int): Y coordinate.

        Returns:
            list: List of distances and corresponding coordinates.
        """
        return self.find_nearest_location(x, y, list(self.transits_coordinates.values()))

    def set_destination(self):
        """
        Set the destination to the current location.
        """
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2
        if self.destination == (current_x, current_y):
            self.destination = None
        else:
            self.destination = (current_x, current_y)
        self.save_destination()
        self.update_minimap()
        self.refresh_webview()

    def save_destination(self):
        """
        Save the destination to a file.
        """
        with open('destination.pkl', 'wb') as f:
            pickle.dump(self.destination, f)
            pickle.dump(datetime.now(), f)

    def load_destination(self):
        """
        Load the destination from a file.
        """
        try:
            with open('destination.pkl', 'rb') as f:
                self.destination = pickle.load(f)
                self.scrape_timestamp = pickle.load(f)
        except FileNotFoundError:
            self.destination = None
            self.scrape_timestamp = datetime.min

    def zoom_in(self):
        """
        Zoom in the minimap.
        """
        if self.zoom_level > 3:
            self.zoom_level -= 1
            self.update_minimap()

    def zoom_out(self):
        """
        Zoom out the minimap.
        """
        if self.zoom_level < 10:
            self.zoom_level += 1
            self.update_minimap()

    def go_to_location(self):
        """
        Go to the selected location.
        """
        column_name = self.combo_columns.currentText()
        row_name = self.combo_rows.currentText()
        if column_name in self.columns:
            self.column_start = self.columns[column_name] - self.zoom_level // 2
        if row_name in self.rows:
            self.row_start = self.rows[row_name] - self.zoom_level // 2
        self.update_minimap()

    def mousePressEvent(self, event):
        """
        Handle mouse press event to update the minimap location.

        Args:
            event (QMouseEvent): Mouse event.
        """
        if event.x() < self.minimap_label.width() and event.y() < self.minimap_label.height():
            x = event.x()
            y = event.y()

            block_size = self.minimap_size // self.zoom_level
            col_clicked = x // block_size
            row_clicked = y // block_size

            new_column_start = self.column_start + col_clicked - self.zoom_level // 2
            new_row_start = self.row_start + row_clicked - self.zoom_level // 2

            if -1 <= new_column_start <= 201 - self.zoom_level + 1:
                self.column_start = new_column_start
            if -1 <= new_row_start <= 201 - self.zoom_level + 1:
                self.row_start = new_row_start

            self.update_minimap()

    def calculate_ap_cost(self, start, end):
        """
        Calculate the AP cost of moving from start to end using the Chebyshev distance.

        Args:
            start (tuple): Starting coordinates (x, y).
            end (tuple): Ending coordinates (x, y).

        Returns:
            int: AP cost of moving from start to end.
        """
        return max(abs(start[0] - end[0]), abs(start[1] - end[1]))  # Using Chebyshev distance

    def update_info_frame(self):
        """
        Update the information frame with the closest locations and AP costs.
        """
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2

        # Find nearest locations
        nearest_tavern = self.find_nearest_tavern(current_x, current_y)
        nearest_bank = self.find_nearest_bank(current_x, current_y)
        nearest_transit = self.find_nearest_transit(current_x, current_y)

        # Get details for nearest tavern
        if nearest_tavern:
            tavern_coords = nearest_tavern[0][1]
            tavern_name = next(name for name, coords in self.taverns_coordinates.items() if coords == tavern_coords)
            tavern_ap_cost = self.calculate_ap_cost((current_x, current_y), tavern_coords)
            tavern_intersection = self.get_intersection_name(tavern_coords)
            self.tavern_label.setText(f"{tavern_name} - {tavern_intersection} - AP: {tavern_ap_cost}")

        # Get details for nearest bank
        if nearest_bank:
            bank_coords = nearest_bank[0][1]
            bank_ap_cost = self.calculate_ap_cost((current_x, current_y), bank_coords)
            bank_intersection = self.get_intersection_name(bank_coords)
            self.bank_label.setText(f"OmniBank - {bank_intersection} - AP: {bank_ap_cost}")

        # Get details for nearest transit
        if nearest_transit:
            transit_coords = nearest_transit[0][1]
            transit_name = next(name for name, coords in self.transits_coordinates.items() if coords == transit_coords)
            transit_ap_cost = self.calculate_ap_cost((current_x, current_y), transit_coords)
            transit_intersection = self.get_intersection_name(transit_coords)
            self.transit_label.setText(f"{transit_name} - {transit_intersection} - AP: {transit_ap_cost}")

        # Get details for set destination
        if self.destination:
            destination_coords = self.destination
            destination_ap_cost = self.calculate_ap_cost((current_x, current_y), destination_coords)
            destination_intersection = self.get_intersection_name(destination_coords)
            self.destination_label.setText(f"Destination - {destination_intersection} - AP: {destination_ap_cost}")
        else:
            self.destination_label.setText("No Destination Set")

    def get_intersection_name(self, coords):
        """
        Get the intersection name for the given coordinates, including special cases for map edges.

        Args:
            coords (tuple): Coordinates (x, y).

        Returns:
            str: Intersection name.
        """
        x, y = coords

        # Special cases for edges of the map
        if x == 0:
            column_name = "WCL"
        elif x == 200:
            column_name = "ECL"
        else:
            x = x if x % 2 != 0 else x - 1
            column_name = next((name for name, coord in self.columns.items() if coord == x), "")

        if y == 0:
            row_name = "NCL"
        elif y == 200:
            row_name = "SCL"
        else:
            y = y if y % 2 != 0 else y - 1
            row_name = next((name for name, coord in self.rows.items() if coord == y), "")

        return f"{column_name} & {row_name}"

    def open_discord(self):
        """
        Open the Discord link in the default web browser.
        """
        webbrowser.open("https://discord.gg/ktdG9FZ")

    def show_coming_soon_popup(self):
        """
        Show a popup indicating that the website feature is coming soon.
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("We have not yet deployed the website for this program, but it is coming soon! Please check back in the next version!")
        msg.setWindowTitle("Coming Soon")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


# -----------------------
# Character Dialog
# -----------------------

class CharacterDialog(QDialog):
    """
    Dialog for adding or modifying a character.
    """
    def __init__(self, parent=None, character=None):
        """
        Initialize the CharacterDialog.

        Args:
            parent (QWidget): Parent widget.
            character (dict, optional): Character data to populate the fields. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle('Character')
        self.setFixedSize(300, 150)

        layout = QFormLayout(self)

        self.name_edit = QLineEdit(self)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.Password)

        layout.addRow('Name:', self.name_edit)
        layout.addRow('Password:', self.password_edit)

        if character:
            self.name_edit.setText(character['name'])
            self.password_edit.setText(character['password'])

        buttons_layout = QHBoxLayout()

        ok_button = QPushButton('OK', self)
        ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_button)

        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addRow(buttons_layout)

# -----------------------
# Data Scraping and Update
# -----------------------

def scrape_avitd_data():
    """
    Scrape guilds and shops data from A View in the Dark and update the database with next update timestamps.
    """
    url = "https://aviewinthedark.net/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    connection = connect_to_database()
    if not connection:
        sys.exit("Failed to connect to the database.")

    cursor = connection.cursor()

    # Extract the time for next update
    guilds_next_update_text = None
    shops_next_update_text = None

    next_change_divs = soup.find_all('div', class_='next_change')
    for div in next_change_divs:
        if "Guilds" in div.text:
            guilds_next_update_text = div.text
        elif "Shops" in div.text:
            shops_next_update_text = div.text

    if not guilds_next_update_text or not shops_next_update_text:
        sys.exit("Failed to find the next update times for guilds and shops.")

    print("Guilds next update text:", guilds_next_update_text)
    print("Shops next update text:", shops_next_update_text)

    guilds_next_update_time = extract_next_update_time(guilds_next_update_text)
    shops_next_update_time = extract_next_update_time(shops_next_update_text)

    update_guilds(cursor, soup, guilds_next_update_time)
    update_shops(cursor, soup, shops_next_update_time)

    connection.commit()
    connection.close()

def extract_next_update_time(text):
    """
    Extract the next update time from the text and calculate the next update timestamp.

    Args:
        text (str): Text containing the update time.

    Returns:
        datetime: The next update timestamp.
    """
    # Regular expression to find all integers followed by time units
    matches = re.findall(r'(\d+)\s*(days?|h|m|s)', text)

    # Initialize time components
    days = hours = minutes = seconds = 0

    # Assign values based on time units
    for value, unit in matches:
        value = int(value)
        if 'day' in unit:
            days = value
        elif 'h' in unit:
            hours = value
        elif 'm' in unit:
            minutes = value
        elif 's' in unit:
            seconds = value

    # Calculate the next update time
    next_update = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    next_update = next_update.replace(second=0, microsecond=0) + timedelta(minutes=1)
    return next_update

def update_guild(cursor, name, location, next_update_time):
    """
    Update a single guild in the database.

    Args:
        cursor (pymysql.cursors.Cursor): Database cursor.
        name (str): Name of the guild.
        location (str): Location of the guild.
        next_update_time (datetime): The next update timestamp.
    """
    col, row = location.split(' and ')
    cursor.execute("""
        UPDATE guilds 
        SET `Column`=%s, `Row`=%s, next_update=%s 
        WHERE Name=%s
    """, (col, row, next_update_time, name))

def update_shop(cursor, name, location, next_update_time):
    """
    Update a single shop in the database.

    Args:
        cursor (pymysql.cursors.Cursor): Database cursor.
        name (str): Name of the shop.
        location (str): Location of the shop.
        next_update_time (datetime): The next update timestamp.
    """
    col, row = location.split(' and ')
    cursor.execute("""
        UPDATE shops 
        SET `Column`=%s, `Row`=%s, next_update=%s 
        WHERE Name=%s
    """, (col, row, next_update_time, name))

def update_guilds(cursor, soup, guilds_coordinates, next_update_time):
    """
    Update the guilds data in the database.

    Args:
        cursor (pymysql.cursors.Cursor): Database cursor.
        soup (BeautifulSoup): BeautifulSoup object containing the HTML data.
        guilds_coordinates (dict): Dictionary of guild names and their coordinates.
        next_update_time (datetime): The next update timestamp.
    """
    for name in guilds_coordinates:
        location_tag = soup.find('td', string=name)
        if location_tag:
            location = location_tag.find_next_sibling('td').text.replace('SE of ', '').strip()
            update_guild(cursor, name, location, next_update_time)
        else:
            print(f"Guild '{name}' not found in the table.")


def update_shops(cursor, soup, shops_coordinates, next_update_time):
    """
    Update the shops data in the database.

    Args:
        cursor (pymysql.cursors.Cursor): Database cursor.
        soup (BeautifulSoup): BeautifulSoup object containing the HTML data.
        shops_coordinates (dict): Dictionary of shop names and their coordinates.
        next_update_time (datetime): The next update timestamp.
    """
    for name in shops_coordinates:
        location_tag = soup.find('td', string=name)
        if location_tag:
            location = location_tag.find_next_sibling('td').text.replace('SE of ', '').strip()
            update_shop(cursor, name, location, next_update_time)
        else:
            print(f"Shop '{name}' not found in the table.")

# -----------------------
# Main Entry Point
# -----------------------

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    app = QApplication(sys.argv)
    window = CityMapApp()
    sys.exit(app.exec_())
