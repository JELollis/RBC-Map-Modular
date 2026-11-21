#!/usr/bin/python3
#Filename main 0.3.2.py
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
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QLabel, QFrame, QSizePolicy
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtWebEngineWidgets import QWebEngineView
import pickle
import os

from variables import *  # Import your variables here

class CityMapApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle('City Map App')
        self.setGeometry(100, 100, 1200, 800)

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
        minimap_square_size = 280  # Combined size for minimap and buttons to form a square
        minimap_frame = QFrame()
        minimap_frame.setFrameShape(QFrame.Box)
        minimap_frame.setFixedSize(minimap_square_size, minimap_square_size)
        minimap_layout = QHBoxLayout()
        minimap_frame.setLayout(minimap_layout)

        # Add minimap
        self.minimap_label = QLabel()
        self.minimap_label.setPixmap(QPixmap(180, 180))
        self.minimap_label.setFixedSize(180, 180)
        self.minimap_label.setStyleSheet("background-color: lightgrey;")
        minimap_layout.addWidget(self.minimap_label)

        # Add closest locations buttons
        closest_buttons_layout = QVBoxLayout()
        button_size = QSize(60, 80)  # Adjusted size to fit in the square

        btn1 = QPushButton('1st Closest\nLocations')
        btn1.setFixedSize(button_size)
        btn1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn1.setStyleSheet("QPushButton { text-align: center; }")
        closest_buttons_layout.addWidget(btn1)

        btn2 = QPushButton('2nd Closest\nLocations')
        btn2.setFixedSize(button_size)
        btn2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn2.setStyleSheet("QPushButton { text-align: center; }")
        closest_buttons_layout.addWidget(btn2)

        btn3 = QPushButton('3rd Closest\nLocations')
        btn3.setFixedSize(button_size)
        btn3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn3.setStyleSheet("QPushButton { text-align: center; }")
        closest_buttons_layout.addWidget(btn3)

        minimap_layout.addLayout(closest_buttons_layout)
        left_layout.addWidget(minimap_frame)

        # Combo boxes and Go button layout
        combo_go_layout = QHBoxLayout()
        combo_go_layout.setSpacing(5)

        combo_streets = QComboBox()
        combo_streets.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        combo_numbers = QComboBox()
        combo_numbers.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        go_button = QPushButton('Go')
        go_button.setFixedSize(50, 30)

        combo_go_layout.addWidget(combo_streets)
        combo_go_layout.addWidget(combo_numbers)
        combo_go_layout.addWidget(go_button)

        left_layout.addLayout(combo_go_layout)

        # Zoom and set destination buttons
        zoom_layout = QHBoxLayout()
        zoom_in_button = QPushButton('Zoom in')
        zoom_out_button = QPushButton('Zoom out')
        set_destination_button = QPushButton('Set Destination')
        zoom_layout.addWidget(zoom_in_button)
        zoom_layout.addWidget(zoom_out_button)
        zoom_layout.addWidget(set_destination_button)
        left_layout.addLayout(zoom_layout)

        # Refresh, Discord, and Website buttons
        action_layout = QHBoxLayout()
        refresh_button = QPushButton('Refresh')
        discord_button = QPushButton('Discord')
        website_button = QPushButton('Website')
        action_layout.addWidget(refresh_button)
        action_layout.addWidget(discord_button)
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
        main_layout.addWidget(self.website_frame)

        self.show()

    def load_minimap(self):
        # Load the minimap with banks and other locations
        pass

    def load_credentials(self):
        # Load credentials from a pickle file
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CityMapApp()
    sys.exit(app.exec_())
