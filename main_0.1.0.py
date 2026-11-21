#!/usr/bin/python3
#Filename main 0.1.0.py
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


# Placeholder function for refreshing the map
def refresh_map():
    update_minimap()


# Placeholder function for zooming in
def zoom_in():
    global zoom_level
    if zoom_level > 3:
        zoom_level -= 1
        update_minimap()


# Placeholder function for zooming out
def zoom_out():
    global zoom_level
    if zoom_level < 10:
        zoom_level += 1
        update_minimap()


# Placeholder function for setting the destination
def set_destination():
    pass


# Placeholder function for opening a webpage
def open_webpage():
    pass


# Placeholder function for opening Discord link
def open_discord():
    pass


# Function to update the minimap with labels
def update_minimap():
    block_size = minimap_size // zoom_level
    minimap_canvas.delete("all")

    for i in range(zoom_level):
        for j in range(zoom_level):
            x0, y0 = i * block_size, j * block_size
            x1, y1 = (i + 1) * block_size, (j + 1) * block_size

            # Calculate indices including alleyways
            ew_index = (ew_start + i) // 2
            ns_index = (ns_start + j) // 2

            if i % 2 == 1 or j % 2 == 1:
                color = "blue"
                label = ""
            elif ew_index < len(ew_streets) and ns_index < len(ns_streets):
                ew_street = ew_streets[ew_index]
                ns_street = ns_streets[ns_index]
                color = "gray"
                label = f"{ew_street}/{ns_street}"
            else:
                color = "blue"
                label = ""

            minimap_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")
            if label:
                minimap_canvas.create_text(x0 + block_size // 2, y0 + block_size // 2,
                                           text=label, fill="black", font=("Arial", 8))


# Function to move the minimap to the selected location
def go_to_location():
    global ew_start, ns_start
    ew_street = ew_var.get()
    ns_street = ns_var.get()
    if ew_street in ew_streets:
        ew_start = ew_streets.index(ew_street) * 2
    if ns_street in ns_streets:
        ns_start = ns_streets.index(ns_street) * 2
    update_minimap()


# Function to handle clicking on the minimap
def on_minimap_click(event):
    global ew_start, ns_start
    block_size = minimap_size // zoom_level
    clicked_col = event.x // block_size
    clicked_row = event.y // block_size

    ew_start = (ew_start + clicked_col * 2) - zoom_level + 1
    ns_start = (ns_start + clicked_row * 2) - zoom_level + 1

    ew_start = max(0, min(ew_start, len(ew_streets) * 2 - zoom_level))
    ns_start = max(0, min(ns_start, len(ns_streets) * 2 - zoom_level))

    update_minimap()


# Correct E-W street naming logic
def generate_ew_streets():
    ew_streets = []
    for i in range(1, 101):
        if i % 10 == 1 and i != 11:
            suffix = "st"
        elif i % 10 == 2 and i != 12:
            suffix = "nd"
        elif i % 10 == 3 and i != 13:
            suffix = "rd"
        else:
            suffix = "th"
        ew_streets.append(f"{i}{suffix}")
    return ew_streets


# List of E-W and N-S streets
ew_streets = generate_ew_streets()
ns_streets = ["Aardvark", "Alder", "Buzzard", "Beech", "Cormorant", "Cedar", "Duck", "Dogwood",
              "Eagle", "Elm", "Ferret", "Fir", "Gibbon", "Gum", "Haddock", "Holly", "Iguana", "Ivy",
              "Jackal", "Juniper", "Kracken", "Knotweed", "Lion", "Larch", "Mongoose", "Maple",
              "Nightingale", "Nettle", "Octopus", "Olive", "Pilchard", "Pine", "Quail", "Quince",
              "Raven", "Ragweed", "Squid", "Sycamore", "Tapir", "Teasel", "Unicorn", "Umbrella",
              "Vulture", "Vervain", "Walrus", "Willow", "Yak", "Yew", "Zebra", "Zelkova", "Amethyst",
              "Anguish", "Beryl", "Bleak", "Cobalt", "Chagrin", "Diamond", "Despair", "Emerald",
              "Ennui", "Flint", "Fear", "Gypsum", "Gloom", "Hessite", "Horror", "Ivory", "Ire",
              "Jet", "Jaded", "Kyanite", "Killjoy", "Lead", "Lonely", "Malachite", "Malaise", "Nickel",
              "Nervous", "Obsidian", "Oppression", "Pyrites", "Pessimism", "Quartz", "Qualms", "Ruby",
              "Regret", "Steel", "Sorrow", "Turquoise", "Torment", "Uranium", "Unctuous", "Vauxite",
              "Vexation", "Wulfenite", "Woe", "Yuksporite", "Yearning", "Zinc", "Zestless"]

# Setup main application window
root = tk.Tk()
root.title("Map Interface")
root.geometry("800x600")

# Initialize zoom level and minimap size
zoom_level = 3
minimap_size = 200

# Initial values for E-W and N-S starts
ew_start = 0
ns_start = 0

# Top left: Minimap
minimap_frame = tk.Frame(root)
minimap_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

minimap_label = tk.Label(minimap_frame, text="Minimap")
minimap_label.pack()

minimap_canvas = tk.Canvas(minimap_frame, width=minimap_size, height=minimap_size)
minimap_canvas.pack()

# Bind the click event to the minimap
minimap_canvas.bind("<Button-1>", on_minimap_click)

# Initial update of minimap
update_minimap()

# Below minimap: Dropdowns for selecting street intersection
dropdown_frame = tk.Frame(root)
dropdown_frame.grid(row=2, column=0, padx=10, pady=10)

ew_label = tk.Label(dropdown_frame, text="E-W Streets")
ew_label.pack(side=tk.LEFT)

ew_var = tk.StringVar()
ew_dropdown = ttk.Combobox(dropdown_frame, textvariable=ew_var, values=ew_streets)
ew_dropdown.pack(side=tk.LEFT)

ns_label = tk.Label(dropdown_frame, text="N-S Streets")
ns_label.pack(side=tk.LEFT)

ns_var = tk.StringVar()
ns_dropdown = ttk.Combobox(dropdown_frame, textvariable=ns_var, values=ns_streets)
ns_dropdown.pack(side=tk.LEFT)

go_button = tk.Button(dropdown_frame, text="Go", command=go_to_location)
go_button.pack(side=tk.LEFT)

# Below dropdowns: Zoom in, zoom out, set destination buttons
zoom_frame = tk.Frame(root)
zoom_frame.grid(row=3, column=0, padx=10, pady=10)

zoom_in_button = tk.Button(zoom_frame, text="Zoom In", command=zoom_in)
zoom_in_button.pack(side=tk.LEFT, padx=5)

zoom_out_button = tk.Button(zoom_frame, text="Zoom Out", command=zoom_out)
zoom_out_button.pack(side=tk.LEFT, padx=5)

set_destination_button = tk.Button(zoom_frame, text="Set Destination", command=set_destination)
set_destination_button.pack(side=tk.LEFT, padx=5)

# Below zoom buttons: refresh map, discord link, modify buildings buttons
extra_buttons_frame = tk.Frame(root)
extra_buttons_frame.grid(row=4, column=0, padx=10, pady=10)

refresh_button = tk.Button(extra_buttons_frame, text="Refresh Map", command=refresh_map)
refresh_button.pack(side=tk.LEFT, padx=5)

discord_button = tk.Button(extra_buttons_frame, text="Discord", command=open_discord)
discord_button.pack(side=tk.LEFT, padx=5)

modify_buildings_button = tk.Button(extra_buttons_frame, text="Modify Buildings", command=open_webpage)
modify_buildings_button.pack(side=tk.LEFT, padx=5)

# Right side: Buttons for closest items
button_frame = tk.Frame(root)
button_frame.grid(row=0, column=1, padx=10, pady=10)

first_closest_button = tk.Button(button_frame, text="1st Closest Items")
first_closest_button.pack(pady=5)

second_closest_button = tk.Button(button_frame, text="2nd Closest Items")
second_closest_button.pack(pady=5)

third_closest_button = tk.Button(button_frame, text="3rd Closest Items")
third_closest_button.pack(pady=5)

# Start the main event loop
root.mainloop()
