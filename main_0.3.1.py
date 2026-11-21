#!/usr/bin/python3
#Filename main 0.3.1.py
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

import tkinter as tk
from tkinter import ttk
from variables import rows, columns, color_map

class Map:
    def __init__(self, size, rows, Columns):
        self.size = size
        self.rows = rows
        self.Columns = Columns
        self.zoom_levels = [3, 5, 7, 9]
        self.current_zoom_level = 0
        self.current_location = (self.size // 2, self.size // 2)
        self.wcl = 0
        self.ncl = 0

    def go_to_location(self, x_street, y_street):
        x = max(0, min(self.rows[x_street] * 2, self.size - 1))
        y = max(0, min(self.Columns[y_street] * 2, self.size - 1))
        self.current_location = (x, y)

    def update_minimap(self):
        # Implement minimap drawing logic here
        pass

# Initialize global variables
zoom_level = 3
minimap_size = 200
ew_start = 0
ns_start = 0

# Create the main application window
root = tk.Tk()
root.title("Map Interface")
root.geometry("800x600")

# Create main frames
map_frame = tk.Frame(root, width=600, height=600)
minimap_frame = tk.Frame(root, width=200, height=200, bg="lightgray")
button_frame = tk.Frame(root, width=200, height=100)
extra_buttons_frame = tk.Frame(root, width=200, height=100)

# Place the frames in the main window
map_frame.grid(row=0, column=0)
minimap_frame.grid(row=0, column=1)
button_frame.grid(row=1, column=0)
extra_buttons_frame.grid(row=2, column=0)

# Create the map instance
map_instance = Map(200, rows, columns)

# Minimap
minimap_canvas = tk.Canvas(minimap_frame, width=minimap_size, height=minimap_size, bg="lightgray")
minimap_canvas.pack()

# Placeholder buttons
closest_locations_button = tk.Button(button_frame, text="Closest Locations")
closest_locations_button.pack(pady=5)
second_closest_button = tk.Button(button_frame, text="2nd Closest Locations")
second_closest_button.pack(pady=5)
third_closest_button = tk.Button(button_frame, text="3rd Closest Locations")
third_closest_button.pack(pady=5)

#set_destination_button = tk.Button(zoom_frame, text="Set Destination")  # Assuming zoom_frame exists
set_destination_button.pack(side=tk.LEFT, padx=5)

refresh_button = tk.Button(extra_buttons_frame, text="Refresh Map")
refresh_button.pack(side=tk.LEFT, padx=5)
discord_button = tk.Button(extra_buttons_frame, text="Discord")
discord_button.pack(side=tk.LEFT, padx=5)
modify_buildings_button = tk.Button(extra_buttons_frame, text="Modify Buildings")
modify_buildings_button.pack(side=tk.LEFT, padx=5)

# ... additional code for UI elements (dropdowns, zoom buttons, etc.) ...

# Start the main event loop
root.mainloop()
