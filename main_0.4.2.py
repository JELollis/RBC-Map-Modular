# Filename: main 0.4.2.py

#!/usr/bin/env python3
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
RBC City Map Application

This application displays a city map with various features such as zooming,
tracking nearest locations (pubs, banks, transits), and integrating with a web view.

Classes:
    CityMapApp(QMainWindow): Main application class for the city map.

Functions:
    on_webview_load_finished(self): Callback when the web view finishes loading.
    process_html(self, html): Processes the HTML content from the web view.
    extract_coordinates_from_html(self, html): Extracts coordinates from HTML content.
    refresh_webview(self): Refreshes the web view.
    draw_minimap(self): Draws the minimap with various features.
    update_minimap(self): Updates the minimap.
    find_nearest_location(self, x, y, locations): Finds the nearest location from a list of locations.
    find_nearest_pub(self, x, y): Finds the nearest pub from the current location.
    find_nearest_bank(self, x, y): Finds the nearest bank from the current location.
    find_nearest_transit(self, x, y): Finds the nearest transit from the current location.
    zoom_in(self): Zooms in the minimap.
    zoom_out(self): Zooms out the minimap.
    go_to_location(self): Moves the minimap to a selected location.
    mousePressEvent(self, event): Handles mouse press events on the minimap.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFontMetrics, QPen
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView

from variables import *

class CityMapApp(QMainWindow):
    """
    Main application class for the RBC City Map.
    """

    def __init__(self):
        """
        Initializes the CityMapApp class, sets up the UI, and initializes the minimap.
        """
        super().__init__()

        # Set up the main window
        self.setWindowTitle('RBC City Map')
        self.setGeometry(100, 100, 1200, 800)

        # Initialize minimap parameters
        self.zoom_level = 3  # Default zoom level
        self.minimap_size = 280  # Size of the minimap
        self.column_start = 0
        self.row_start = 0

        # Create the central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left side layout
        left_layout = QVBoxLayout()
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.Box)
        left_frame.setFixedWidth(300)
        left_frame.setLayout(left_layout)

        # Create the minimap area
        minimap_frame = QFrame()
        minimap_frame.setFrameShape(QFrame.Box)
        minimap_frame.setFixedSize(self.minimap_size, self.minimap_size)
        minimap_layout = QVBoxLayout()
        minimap_layout.setContentsMargins(0, 0, 0, 0)  # Remove padding
        minimap_frame.setLayout(minimap_layout)

        # Add minimap
        self.minimap_label = QLabel()
        self.minimap_label.setFixedSize(self.minimap_size, self.minimap_size)
        self.minimap_label.setStyleSheet("background-color: lightgrey;")
        minimap_layout.addWidget(self.minimap_label)
        left_layout.addWidget(minimap_frame)

        # Combo boxes and Go button layout
        combo_go_layout = QHBoxLayout()
        combo_go_layout.setSpacing(5)

        self.combo_columns = QComboBox()
        self.combo_columns.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_columns.addItems(columns.keys())  # Populate with column names

        self.combo_rows = QComboBox()
        self.combo_rows.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.combo_rows.addItems(rows.keys())  # Populate with row names

        go_button = QPushButton('Go')
        go_button.setFixedSize(50, 30)
        go_button.clicked.connect(self.go_to_location)  # Connect to go_to_location method

        combo_go_layout.addWidget(self.combo_columns)
        combo_go_layout.addWidget(self.combo_rows)
        combo_go_layout.addWidget(go_button)

        left_layout.addLayout(combo_go_layout)

        # Zoom and set destination buttons
        zoom_layout = QHBoxLayout()
        button_size = (self.minimap_size - 10) // 3  # Adjusted size to fit in the row with padding

        zoom_in_button = QPushButton('Zoom in')
        zoom_in_button.setFixedSize(button_size, 40)
        zoom_in_button.clicked.connect(self.zoom_in)  # Connect to zoom_in method
        zoom_layout.addWidget(zoom_in_button)

        zoom_out_button = QPushButton('Zoom out')
        zoom_out_button.setFixedSize(button_size, 40)
        zoom_out_button.clicked.connect(self.zoom_out)  # Connect to zoom_out method
        zoom_layout.addWidget(zoom_out_button)

        set_destination_button = QPushButton('Set Destination')
        set_destination_button.setFixedSize(button_size, 40)
        zoom_layout.addWidget(set_destination_button)

        left_layout.addLayout(zoom_layout)

        # Closest locations buttons
        """
        closest_buttons_layout = QHBoxLayout()

        btn1 = QPushButton('1st Closest\nLocations')
        btn1.setFixedSize(button_size, 40)
        btn1.setStyleSheet("QPushButton { text-align: center; }")
        closest_buttons_layout.addWidget(btn1)

        btn2 = QPushButton('2nd Closest\nLocations')
        btn2.setFixedSize(button_size, 40)
        btn2.setStyleSheet("QPushButton { text-align: center; }")
        closest_buttons_layout.addWidget(btn2)

        btn3 = QPushButton('3rd Closest\nLocations')
        btn3.setFixedSize(button_size, 40)
        btn3.setStyleSheet("QPushButton { text-align: center; }")
        closest_buttons_layout.addWidget(btn3)

        left_layout.addLayout(closest_buttons_layout)

        # Connect closest location buttons
        self.closest_level = 1

        btn1.clicked.connect(lambda: self.set_closest_level(1))
        btn2.clicked.connect(lambda: self.set_closest_level(2))
        btn3.clicked.connect(lambda: self.set_closest_level(3))
        """

        # Refresh, Discord, and Website buttons
        action_layout = QHBoxLayout()

        refresh_button = QPushButton('Refresh')
        refresh_button.setFixedSize(button_size, 40)
        refresh_button.clicked.connect(self.refresh_webview)  # Connect to refresh_webview method
        action_layout.addWidget(refresh_button)

        discord_button = QPushButton('Discord')
        discord_button.setFixedSize(button_size, 40)
        action_layout.addWidget(discord_button)

        website_button = QPushButton('Website')
        website_button.setFixedSize(button_size, 40)
        action_layout.addWidget(website_button)

        left_layout.addLayout(action_layout)

        # Character list frame
        character_frame = QFrame()
        character_frame.setFrameShape(QFrame.Box)
        character_layout = QVBoxLayout()
        character_frame.setLayout(character_layout)

        character_list_label = QLabel('Character List')
        character_layout.addWidget(character_list_label)

        # Placeholder for character list and buttons
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

        # Add the website frame on the right
        self.website_frame = QWebEngineView()
        self.website_frame.setUrl(QUrl('https://quiz.ravenblack.net/blood.pl'))
        self.website_frame.loadFinished.connect(self.on_webview_load_finished)
        main_layout.addWidget(self.website_frame)

        self.show()

        # Initial minimap update
        self.update_minimap()

    def on_webview_load_finished(self):
        """
        Callback function triggered when the web view finishes loading.
        """
        self.website_frame.page().toHtml(self.process_html)

    def process_html(self, html):
        """
        Processes the HTML content from the web view to extract coordinates.

        Args:
            html (str): HTML content of the web page.
        """
        x_coord, y_coord = self.extract_coordinates_from_html(html)
        if x_coord is not None and y_coord is not None:
            self.column_start = x_coord
            self.row_start = y_coord
            self.update_minimap()

    def extract_coordinates_from_html(self, html):
        """
        Extracts coordinates from the HTML content.

        Args:
            html (str): HTML content of the web page.

        Returns:
            tuple: Coordinates (x, y) if found, otherwise (None, None).
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
        Refreshes the web view.
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
                                     block_size - 2 * border_size, color_map["edge"])
                elif (column_index % 2 == 1) or (row_index % 2 == 1):
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, color_map["alley"])
                else:
                    painter.fillRect(x0 + border_size, y0 + border_size, block_size - 2 * border_size,
                                     block_size - 2 * border_size, color_map["default"])

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
            draw_location(column_index + 1, row_index + 1, color_map["bank"], "Bank")

        for (column_index, row_index) in pubs_coordinates:
            draw_location(column_index + 1, row_index + 1, color_map["pub"], "Pub")

        for (column_index, row_index) in transits_coordinates:
            draw_location(column_index + 1, row_index + 1, color_map["transit"], "Transit")

        for name, (column_index, row_index) in user_buildings_coordinates.items():
            draw_location(column_index + 1, row_index + 1, QColor("purple"), name)

        # Get current location
        current_x, current_y = self.column_start + self.zoom_level // 2, self.row_start + self.zoom_level // 2

        # Find and draw lines to nearest locations
        nearest_pub = self.find_nearest_pub(current_x, current_y)
        nearest_bank = self.find_nearest_bank(current_x, current_y)
        nearest_transit = self.find_nearest_transit(current_x, current_y)

        if nearest_pub:
            nearest_pub = nearest_pub[0][1]
            painter.setPen(QPen(QColor('orange'), 3))  # Set pen color to orange and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_pub[0] - self.column_start + 1) * block_size + block_size // 2,
                (nearest_pub[1] - self.row_start + 1) * block_size + block_size // 2
            )

        if nearest_bank:
            nearest_bank = nearest_bank[0][1]
            painter.setPen(QPen(QColor('blue'), 3))  # Set pen color to blue and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_bank[0] - self.column_start + 1) * block_size + block_size // 2,
                (nearest_bank[1] - self.row_start + 1) * block_size + block_size // 2
            )

        if nearest_transit:
            nearest_transit = nearest_transit[0][1]
            painter.setPen(QPen(QColor('red'), 3))  # Set pen color to red and width to 3
            painter.drawLine(
                (current_x - self.column_start) * block_size + block_size // 2,
                (current_y - self.row_start) * block_size + block_size // 2,
                (nearest_transit[0] - self.column_start + 1) * block_size + block_size // 2,
                (nearest_transit[1] - self.row_start + 1) * block_size + block_size // 2
            )

        painter.end()
        self.minimap_label.setPixmap(pixmap)

    def update_minimap(self):
        """
        Updates the minimap by calling the draw_minimap method.
        """
        self.draw_minimap()

    def find_nearest_location(self, x, y, locations):
        """
        Finds the nearest location from a list of locations.

        Args:
            x (int): X coordinate of the current location.
            y (int): Y coordinate of the current location.
            locations (list): List of locations to search from.

        Returns:
            list: List of tuples containing distances and coordinates of nearest locations.
        """
        distances = []
        for loc in locations:
            lx, ly = loc
            dist = abs(lx - x) + abs(ly - y)
            distances.append((dist, (lx, ly)))
        distances.sort()
        return distances

    def find_nearest_pub(self, x, y):
        """
        Finds the nearest pub from the current location.

        Args:
            x (int): X coordinate of the current location.
            y (int): Y coordinate of the current location.

        Returns:
            list: List of tuples containing distances and coordinates of nearest pubs.
        """
        return self.find_nearest_location(x, y, pubs_coordinates)

    def find_nearest_bank(self, x, y):
        """
        Finds the nearest bank from the current location.

        Args:
            x (int): X coordinate of the current location.
            y (int): Y coordinate of the current location.

        Returns:
            list: List of tuples containing distances and coordinates of nearest banks.
        """
        return self.find_nearest_location(x, y, banks_coordinates)

    def find_nearest_transit(self, x, y):
        """
        Finds the nearest transit from the current location.

        Args:
            x (int): X coordinate of the current location.
            y (int): Y coordinate of the current location.

        Returns:
            list: List of tuples containing distances and coordinates of nearest transits.
        """
        return self.find_nearest_location(x, y, transits_coordinates)

    # Commenting out the set_closest_level method for now
    # def set_closest_level(self, level):
    #     """
    #     Sets the level of closest location to display (1st, 2nd, or 3rd).
    #
    #     Args:
    #         level (int): Level of closest location to display.
    #     """
    #     self.closest_level = level
    #     self.update_minimap()

    def zoom_in(self):
        """
        Zooms in the minimap by decreasing the zoom level.
        """
        if self.zoom_level > 3:
            self.zoom_level -= 1
            self.update_minimap()

    def zoom_out(self):
        """
        Zooms out the minimap by increasing the zoom level.
        """
        if self.zoom_level < 10:
            self.zoom_level += 1
            self.update_minimap()

    def go_to_location(self):
        """
        Moves the minimap to the location selected in the combo boxes.
        """
        column_name = self.combo_columns.currentText()
        row_name = self.combo_rows.currentText()
        if column_name in columns:
            self.column_start = columns[column_name]
        if row_name in rows:
            self.row_start = rows[row_name]
        self.update_minimap()

    def mousePressEvent(self, event):
        """
        Handles mouse press events on the minimap to center the map on the clicked location.

        Args:
            event (QMouseEvent): Mouse event.
        """
        x = event.x()
        y = event.y()

        if x < self.minimap_size and y < self.minimap_size:
            block_size = self.minimap_size // self.zoom_level
            col_clicked = x // block_size
            row_clicked = y // block_size

            new_column_start = self.column_start + col_clicked - self.zoom_level // 2
            new_row_start = self.row_start + row_clicked - self.zoom_level // 2

            # Ensure the new start positions are within the valid range
            if -1 <= new_column_start <= 201 - self.zoom_level + 1:
                self.column_start = new_column_start
            if -1 <= new_row_start <= 201 - self.zoom_level + 1:
                self.row_start = new_row_start

            self.update_minimap()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CityMapApp()
    sys.exit(app.exec_())
