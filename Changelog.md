# Changelog — RBC Community Map

Release history up to **0.3.1**, oldest first.

- This branch (`version/0.3.1`) is an archived snapshot of 0.3.1 as `main_0.3.1.py`.
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


---

## Version 0.2.0 — Data-driven landmark overlays

🚀 Summary
Version 0.2.0 introduces data-driven enhancements to the map rendering logic and begins to externalize key configuration data, indicating a move toward modularity and semantic enrichment of the map. It remains procedural and GUI-based, using tkinter, but introduces data overlay logic and better street metadata.

📌 Key Enhancements Over 0.1.0
1. Landmark Overlays
Introduced color-coding for specific locations:

blue → Banks

orange → Pubs

red → Transit points

gray → Normal intersections

Determined by checking (ns_street, ew_street) membership in banks, pubs, and transits.

2. Data Externalization
New import: from variables import *

Suggests landmark data (banks, pubs, transits) now reside in a separate variables.py module.

Moves away from hardcoding everything in main, enabling easier expansion/maintenance.

3. Visual Refinement
Changed alley color from blue → black, clearly separating structural roads from data-flagged locations.

Cleaned up layout by switching label order in dropdowns to N-S first, then E-W (likely for readability).

🧠 Architectural Implications
Although still not object-oriented, this update clearly shows domain-aware thinking — streets are now data-bearing, not just labels.

The minimap canvas becomes semantically meaningful beyond layout, taking first steps toward a GIS-style data layer system.

🧭 GUI & Interaction Logic
GUI layout and functionality are largely unchanged from 0.1.0.

Retains the same controls, buttons, and logic for zoom, refresh, and movement.

Placeholder functions (set_destination, open_discord, open_webpage) still do nothing — their implementation remains pending.


---

## Version 0.3.0 — Initial refactor (Tkinter OOP)

**Key changes:**

First version to introduce class-based design with CityMapApp.

Clean separation of:

GUI setup (setup_gui)

Logic for zooming, refreshing, and updating maps

Integrated proximity logic: nearest bank/pub/transit display.

Map display using two canvases (map_canvas, minimap_canvas).

Dropdowns for selecting X/Y streets (rows/columns).

Uses rows and columns dicts for grid logic.

> **Assessment:** Experimental OO version, still using tkinter, but paving the way for future Qt refactor.


---

## Version 0.3.1 — Partial rework + abstracted map logic

**Key changes:**

Introduced a Map class encapsulating core minimap data (zoom, center).

Partial backslide to procedural code in UI setup.

Minimap placeholder logic present, but not implemented.

Suggests a transitional stage from 0.3.0 to something Qt-based.

> **Assessment:** Attempt to modularize backend (Map class) before a full GUI transition.

