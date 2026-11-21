# Changelog — RBC Community Map

Release history up to **0.1.0**, oldest first.

- This branch (`version/0.1.0`) is an archived snapshot of 0.1.0 as `main_0.1.0.py`.
- **Latest release:** [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0); the full history is in its [Changelog](https://github.com/JELollis/RBC-Map/blob/version/1.0.0/Changelog.md).

Entries for versions before 0.12.0 were reconstructed from the archived source
files and are less detailed than later entries.

---

## Version 0.1.0 — Tkinter prototype

**💡 Summary**

Version 0.1.0 of the RBCMap app is a functional prototype built with tkinter, focusing on a minimap interface and manual street navigation using dropdowns and zooming. This version is highly procedural and uses no class-based structure.

**🧩 Key Features in 0.1.0**

🗺️ Minimap
Grid-style minimap rendered using a Canvas.

Visualizes intersections of N-S and E-W streets.

Dynamically adjusts based on zoom_level.

Clickable grid allows repositioning the viewport (on_minimap_click).

🧭 Zoom Controls
Buttons for "Zoom In" and "Zoom Out".

Zoom affects how many streets are shown in the viewport (range 3–10).

🏙️ Street Navigation
Dropdowns for selecting a specific N-S and E-W intersection.

“Go” button jumps the map to that location via go_to_location().

📌 Map Refresh & Extra Buttons
Buttons included:

“Refresh Map” – calls update_minimap().

“Discord” – placeholder for community link.

“Modify Buildings” – placeholder for webpage/editor.

**📦 Placeholder Functions**

Functions like open_webpage(), open_discord(), and set_destination() exist but are unimplemented — suggesting planned features like building editing, community integration, and character destination logic.

**🛠️ Utilities**

generate_ew_streets() builds E-W street names from 1st to 100th with ordinal suffixes.

Static N-S street list contains both natural and thematic naming (e.g., “Pine”, “Torment”, “Despair”).

**🧱 Technical Notes**

Hardcoded GUI using absolute grid placements.

Pure procedural code — no object-oriented design.

No data persistence or external file/database integration.

Initial zoom logic and bounds checking are in place for stability.

