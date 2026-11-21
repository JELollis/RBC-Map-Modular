#!/usr/bin/env python3
# 0.5.1.py
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

import sys
import pickle
import pymysql
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QPen
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView

# Database connection parameters
LOCAL_HOST = "127.0.0.1"
REMOTE_HOST = "lollis-home.ddns.net"
USER = "rbc_maps"
PASSWORD = "RBC_Community_Map"
DATABASE = "city_map"


def connect_to_database():
    """
    Connects to the MySQL database.

    Tries to connect to the local database first, and if it fails,
    it attempts to connect to the remote database.

    Returns:
        connection (pymysql.connections.Connection): The database connection object.
    """
    try:
        connection = pymysql.connect(
            host=LOCAL_HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        print("Connected to local MySQL instance")
        return connection
    except pymysql.MySQLError as err:
        print("Connection to local MySQL instance failed:", err)
        try:
            connection = pymysql.connect(
                host=REMOTE_HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE
            )
            print("Connected to remote MySQL instance")
            return connection
        except pymysql.MySQLError as err:
            print("Connection to remote MySQL instance failed:", err)
            return None


def load_data():
    """
    Loads data from the database.

    Retrieves columns, rows, banks, taverns, transits, user buildings,
    and color mappings from the database and processes them into dictionaries
    and lists for easy access.

    Returns:
        tuple: Contains dictionaries and lists with coordinates and names of various locations.
    """
    connection = connect_to_database()
    if not connection:
        sys.exit("Failed to connect to the database.")

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM `columns`")
    columns_data = cursor.fetchall()
    columns = {name: coordinate for _, name, coordinate in columns_data}

    cursor.execute("SELECT * FROM `rows`")
    rows_data = cursor.fetchall()
    rows = {name: coordinate for _, name, coordinate in rows_data}

    cursor.execute("SELECT * FROM banks")
    banks_data = cursor.fetchall()
    banks_coordinates = [(columns[col], rows[row]) for _, col, row in banks_data]

    cursor.execute("SELECT * FROM taverns")
    taverns_data = cursor.fetchall()
    taverns_coordinates = {name: (columns.get(col), rows.get(row)) for _, col, row, name in taverns_data}

    cursor.execute("SELECT * FROM transits")
    transits_data = cursor.fetchall()
    transits_coordinates = {name: (columns.get(col), rows.get(row)) for _, col, row, name in transits_data}

    cursor.execute("SELECT * FROM userbuildings")
    user_buildings_data = cursor.fetchall()
    user_buildings_coordinates = {name: (columns.get(col), rows.get(row)) for _, name, col, row in user_buildings_data}

    cursor.execute("SELECT * FROM color_mappings")
    color_mappings_data = cursor.fetchall()
    color_map = {type_: QColor(color) for _, type_, color in color_mappings_data}

    connection.close()

    return columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_map


# Load data from the database
columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_map = load_data()


class CityMapApp(QMainWindow):
    def __init__(self):
        """
        Initializes the CityMapApp.

        Sets up the main window, layouts, and widgets, and loads the initial minimap.
        """
        super().__init__()

        self.setWindowTitle('RBC City Map')
        self.setGeometry(100, 100, 1200, 800)

        self.zoom_level = 3
        self.minimap_size = 280
        self.column_start = 0
        self.row_start = 0
        self.destination = None
        self.load_destination()

        self.color_map = color_map

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        left_layout = QVBoxLayout()
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.Box)
        left_frame.setFixedWidth(300)
        left_frame.setLayout(left_layout)

        minimap_frame = QFrame()
        minimap_frame.setFrameShape(QFrame.Box)
        minimap_frame.setFixedSize(self.minimap_size, self.minimap_size)
        minimap_layout = QVBoxLayout()
        minimap_layout.setContentsMargins(0, 0, 0, 0)
        minimap_frame.setLayout(minimap_layout)

        self.minimap_label = QLabel()
        self.minimap_label.setFixedSize(self.minimap_size, self.minimap_size)
        self.minimap_label.setStyleSheet("background-color: lightgrey;")
        minimap_layout.addWidget(self.minimap_label)
        left_layout.addWidget(minimap_frame)

        combo_go_layout = QHBoxLayout()
        combo_go_layout.setSpacing(5)

        self.combo_columns = QComboBox()
        self.combo_columns.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_columns.addItems(columns.keys())

        self.combo_rows = QComboBox()
        self.combo_rows.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_rows.addItems(rows.keys())

        go_button = QPushButton('Go')
        go_button.setFixedSize(50, 30)
        go_button.clicked.connect(self.go_to_location)

        combo_go_layout.addWidget(self.combo_columns)
        combo_go_layout.addWidget(self.combo_rows)
        combo_go_layout.addWidget(go_button)

        left_layout.addLayout(combo_go_layout)

        zoom_layout = QHBoxLayout()
        button_size = (self.minimap_size - 10) // 3

        zoom_in_button = QPushButton('Zoom in')
        zoom_in_button.setFixedSize(button_size, 40)
        zoom_in_button.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(zoom_in_button)

        zoom_out_button = QPushButton('Zoom out')
        zoom_out_button.setFixedSize(button_size, 40)
        zoom_out_button.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(zoom_out_button)

        set_destination_button = QPushButton('Set Destination')
        set_destination_button.setFixedSize(button_size, 40)
        set_destination_button.clicked.connect(self.set_destination)
        zoom_layout.addWidget(set_destination_button)

        left_layout.addLayout(zoom_layout)

        action_layout = QHBoxLayout()

        refresh_button = QPushButton('Refresh')
        refresh_button.setFixedSize(button_size, 40)
        refresh_button.clicked.connect(self.refresh_webview)
        action_layout.addWidget(refresh_button)

        discord_button = QPushButton('Discord')
        discord_button.setFixedSize(button_size, 40)
        action_layout.addWidget(discord_button)

        website_button = QPushButton('Website')
        website_button.setFixedSize(button_size, 40)
        action_layout.addWidget(website_button)

        left_layout.addLayout(action_layout)

        character_frame = QFrame()
        character_frame.setFrameShape(QFrame.Box)
        character_layout = QVBoxLayout()
        character_frame.setLayout(character_layout)

        character_list_label = QLabel('Character List')
        character_layout.addWidget(character_list_label)

        character_list = QLabel()
        character_layout.addWidget(character_list)

        character_buttons_layout = QHBoxLayout()
        new_button = QPushButton('New')
        modify_button = QPushButton('Modify')
        delete_button = QPushButton('Delete')
        character_buttons_layout.addWidget(new_button)
        character_buttons_layout.addWidget(modify_button)
        character_buttons_layout.addWidget(delete_button)
        character_layout.addLayout(character_buttons_layout)

        left_layout.addWidget(character_frame)

        main_layout.addWidget(left_frame)

        self.website_frame = QWebEngineView()
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl'))
        self.website_frame.loadFinished.connect(self.on_webview_load_finished)
        main_layout.addWidget(self.website_frame)

        self.show()
        self.update_minimap()

    def on_webview_load_finished(self):
        """
        Slot called when the webview finishes loading.

        Converts the page to HTML and processes it.
        """
        self.website_frame.page().toHtml(self.process_html)

    def process_html(self, html):
        """
        Processes the HTML content of the webview.

        Extracts coordinates from the HTML content and updates the minimap.

        Args:
            html (str): The HTML content of the webview.
        """
        x_coord, y_coord = self.extract_coordinates_from_html(html)
        if x_coord is not None and y_coord is not None:
            self.column_start = x_coord
            self.row_start = y_coord
            self.update_minimap()

    def extract_coordinates_from_html(self, html):
        """
        Extracts coordinates from the HTML content using BeautifulSoup.

        Args:
            html (str): The HTML content of the webview.

        Returns:
            tuple: Coordinates (column, row) if found, otherwise (None, None).
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')
        intersect_span = soup.find('span', class_='intersect')
        if intersect_span:
            text = intersect_span.get_text()
            if ' and ' in text:
                column_name, row_name = text.split(' and ')
                if column_name in columns and row_name in rows:
                    return columns[column_name], rows[row_name]
        return None, None

    def refresh_webview(self):
        """
        Reloads the webview content.
        """
        self.website_frame.reload()

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

                column_name = next((name for name, coord in columns.items() if coord == column_index), None)
                row_name = next((name for name, coord in rows.items() if coord == row_index), None)

                # Draw cell background color
                if column_index < min(columns.values()) or column_index > max(columns.values()) or row_index < min(
                        rows.values()) or row_index > max(rows.values()):
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, self.color_map["edge"])
                elif (column_index % 2 == 1) or (row_index % 2 == 1):
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, self.color_map["alley"])
                else:
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, self.color_map["default"])

                # Draw labels only at intersections of named streets
                if column_name and row_name:
                    label_text = f"{column_name} & {row_name}"
                    text_rect = font_metrics.boundingRect(label_text)
                    text_x = x0 + (block_size - text_rect.width()) // 2
                    text_y = y0 + (block_size + text_rect.height()) // 2 - font_metrics.descent()
                    painter.setPen(QColor('white'))
                    painter.drawText(text_x, text_y, label_text)

        # Draw special locations
        for (column_index, row_index) in banks_coordinates:
            draw_location(column_index + 1, row_index + 1, self.color_map["bank"], "Bank")

        for (column_index, row_index) in taverns_coordinates.values():
            draw_location(column_index + 1, row_index + 1, self.color_map["tavern"], "Tavern")

        for (column_index, row_index) in transits_coordinates.values():
            draw_location(column_index + 1, row_index + 1, self.color_map["transit"], "Transit")

        for name, (column_index, row_index) in user_buildings_coordinates.items():
            draw_location(column_index + 1, row_index + 1, self.color_map["user_building"], name)

        # Get current location
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2

        # Find and draw lines to nearest locations
        nearest_tavern = self.find_nearest_tavern(current_x, current_y)
        nearest_bank = self.find_nearest_bank(current_x, current_y)
        nearest_transit = self.find_nearest_transit(current_x, current_y)

        if nearest_tavern:
            nearest_tavern = nearest_tavern[0][1]
            painter.setPen(QPen(self.color_map['tavern'], 3))  # Set pen color to orange and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_tavern[0] - self.column_start + 1) * block_size + block_size // 2,
                (nearest_tavern[1] - self.row_start + 1) * block_size + block_size // 2
            )

        if nearest_bank:
            nearest_bank = nearest_bank[0][1]
            painter.setPen(QPen(self.color_map['bank'], 3))  # Set pen color to blue and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_bank[0] - self.column_start + 1) * block_size + block_size // 2,
                (nearest_bank[1] - self.row_start + 1) * block_size + block_size // 2
            )

        if nearest_transit:
            nearest_transit = nearest_transit[0][1]
            painter.setPen(QPen(self.color_map['transit'], 3))  # Set pen color to red and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_transit[0] - self.column_start + 1) * block_size + block_size // 2,
                (nearest_transit[1] - self.row_start + 1) * block_size + block_size // 2
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
        Updates the minimap by redrawing it.
        """
        self.draw_minimap()

    def find_nearest_location(self, x, y, locations):
        """
        Finds the nearest location from a list of locations based on Manhattan distance.

        Args:
            x (int): X-coordinate to compare.
            y (int): Y-coordinate to compare.
            locations (list): List of locations as (x, y) tuples.

        Returns:
            list: Sorted list of distances and locations.
        """
        distances = []
        for loc in locations:
            lx, ly = loc
            dist = abs(lx - x) + abs(ly - y)
            distances.append((dist, (lx, ly)))
        distances.sort()
        return distances

    def find_nearest_tavern(self, x, y):
        """
        Finds the nearest tavern from the current coordinates.

        Args:
            x (int): Current x-coordinate.
            y (int): Current y-coordinate.

        Returns:
            list: Nearest tavern location.
        """
        return self.find_nearest_location(x, y, list(taverns_coordinates.values()))

    def find_nearest_bank(self, x, y):
        """
        Finds the nearest bank from the current coordinates.

        Args:
            x (int): Current x-coordinate.
            y (int): Current y-coordinate.

        Returns:
            list: Nearest bank location.
        """
        return self.find_nearest_location(x, y, banks_coordinates)

    def find_nearest_transit(self, x, y):
        """
        Finds the nearest transit from the current coordinates.

        Args:
            x (int): Current x-coordinate.
            y (int): Current y-coordinate.

        Returns:
            list: Nearest transit location.
        """
        return self.find_nearest_location(x, y, list(transits_coordinates.values()))

    def set_destination(self):
        """
        Sets or unsets the destination to the current center of the minimap.
        """
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2
        if self.destination == (current_x, current_y):
            self.destination = None
        else:
            self.destination = (current_x, current_y)
        self.save_destination()
        self.update_minimap()

    def save_destination(self):
        """
        Saves the destination and current timestamp to a file.
        """
        with open('destination.pkl', 'wb') as f:
            pickle.dump(self.destination, f)
            pickle.dump(datetime.now(), f)

    def load_destination(self):
        """
        Loads the destination and timestamp from a file, if it exists.
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
        Zooms in the minimap, decreasing the zoom level.
        """
        if self.zoom_level > 3:
            self.zoom_level -= 1
            self.update_minimap()

    def zoom_out(self):
        """
        Zooms out the minimap, increasing the zoom level.
        """
        if self.zoom_level < 10:
            self.zoom_level += 1
            self.update_minimap()

    def go_to_location(self):
        """
        Navigates the minimap to the selected location from the combo boxes.
        """
        column_name = self.combo_columns.currentText()
        row_name = self.combo_rows.currentText()
        if column_name in columns:
            self.column_start = columns[column_name] - self.zoom_level // 2
        if row_name in rows:
            self.row_start = rows[row_name] - self.zoom_level // 2
        self.update_minimap()

    def mousePressEvent(self, event):
        """
        Handles mouse press events to navigate the minimap.

        Args:
            event (QMouseEvent): The mouse event.
        """
        x = event.x()
        y = event.y()

        if x < self.minimap_size and y < self.minimap_size:
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CityMapApp()
    sys.exit(app.exec_())
