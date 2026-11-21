#!/usr/bin/python3
#Filename main 0.3.0.py
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
from variables import *


class CityMapApp:
    def __init__(self, root):
        self.root = root
        self.zoom_level = 5
        self.selected_x = 0
        self.selected_y = 0

        # GUI setup
        self.setup_gui()

    def setup_gui(self):
        self.root.title("City Map")

        self.map_canvas = tk.Canvas(self.root, width=600, height=600, bg="white")
        self.map_canvas.grid(row=0, column=1, rowspan=10, columnspan=4)

        self.minimap_canvas = tk.Canvas(self.root, width=300, height=300, bg="white")
        self.minimap_canvas.grid(row=0, column=0, rowspan=5, columnspan=1)

        self.street_dropdown_x = ttk.Combobox(self.root, values=list(rows.keys()), state="readonly")
        self.street_dropdown_x.set("Select X Street")
        self.street_dropdown_x.grid(row=5, column=0)
        self.street_dropdown_x.bind("<<ComboboxSelected>>", self.update_selected_x)

        self.street_dropdown_y = ttk.Combobox(self.root, values=list(columns.keys()), state="readonly")
        self.street_dropdown_y.set("Select Y Street")
        self.street_dropdown_y.grid(row=6, column=0)
        self.street_dropdown_y.bind("<<ComboboxSelected>>", self.update_selected_y)

        self.nearest_bank_label = tk.Label(self.root, text="Nearest Bank: N/A")
        self.nearest_bank_label.grid(row=7, column=0)

        self.nearest_pub_label = tk.Label(self.root, text="Nearest Pub: N/A")
        self.nearest_pub_label.grid(row=8, column=0)

        self.nearest_transit_label = tk.Label(self.root, text="Nearest Transit: N/A")
        self.nearest_transit_label.grid(row=9, column=0)

        self.zoom_in_button = tk.Button(self.root, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.grid(row=10, column=0)

        self.zoom_out_button = tk.Button(self.root, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.grid(row=11, column=0)

        self.go_button = tk.Button(self.root, text="Go", command=self.update_map)
        self.go_button.grid(row=12, column=0)

        self.refresh_button = tk.Button(self.root, text="Refresh", command=self.refresh_map)
        self.refresh_button.grid(row=13, column=0)

        self.discord_button = tk.Button(self.root, text="Discord", command=self.open_discord)
        self.discord_button.grid(row=14, column=0)

        self.webpage_button = tk.Button(self.root, text="Webpage", command=self.open_webpage)
        self.webpage_button.grid(row=15, column=0)

    def update_selected_x(self, event):
        self.selected_x = rows[self.street_dropdown_x.get()]

    def update_selected_y(self, event):
        self.selected_y = columns[self.street_dropdown_y.get()]

    def zoom_in(self):
        if self.zoom_level > zoom_levels[0]:
            self.zoom_level -= 2
        self.update_map()

    def zoom_out(self):
        if self.zoom_level < zoom_levels[-1]:
            self.zoom_level += 2
        self.update_map()

    def update_map(self):
        self.map_canvas.delete("all")
        self.minimap_canvas.delete("all")

        min_x = max(0, self.selected_x - self.zoom_level)
        max_x = min(199, self.selected_x + self.zoom_level)
        min_y = max(0, self.selected_y - self.zoom_level)
        max_y = min(199, self.selected_y + self.zoom_level)

        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                street_x = next((k for k, v in rows.items() if v == x), None)
                street_y = next((k for k, v in columns.items() if v == y), None)
                if street_x and street_y:
                    self.minimap_canvas.create_text((x - min_x) * 30, (y - min_y) * 30, anchor=tk.NW,
                                                    text=f"{street_y}\n{street_x}", font=("Arial", 8))

        self.refresh_main_map()

    def refresh_main_map(self):
        self.map_canvas.delete("all")

        nearest_bank = self.find_nearest(banks)
        nearest_pub = self.find_nearest(pubs)
        nearest_transit = self.find_nearest(transits)

        self.nearest_bank_label.config(text=f"Nearest Bank: {nearest_bank}")
        self.nearest_pub_label.config(text=f"Nearest Pub: {nearest_pub}")
        self.nearest_transit_label.config(text=f"Nearest Transit: {nearest_transit}")

    def find_nearest(self, locations):
        nearest_location = None
        shortest_distance = float('inf')
        for loc in locations:
            loc_x = rows[loc[1]]
            loc_y = columns[loc[0]]
            distance = abs(loc_x - self.selected_x) + abs(loc_y - self.selected_y)
            if distance < shortest_distance:
                shortest_distance = distance
                nearest_location = f"{loc[0]} & {loc[1]}"
        return nearest_location

    def refresh_map(self):
        self.update_map()

    def open_discord(self):
        pass

    def open_webpage(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = CityMapApp(root)
    root.mainloop()
