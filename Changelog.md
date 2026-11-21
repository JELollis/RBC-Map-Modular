# Changelog — RBC Community Map

Release history up to **0.4.2**, oldest first.

- This branch (`version/0.4.2`) is an archived snapshot of 0.4.2 as `main_0.4.2.py`.
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


---

## Version 0.3.2 — PyQt5 migration begins

**Key changes:**

Switched GUI toolkit from tkinter to PyQt5.

Replaced Canvas with QLabel + QPixmap for drawing.

Introduced sidebar with:

Minimap

Closest location buttons

Combo boxes for street selection

Zoom/Go/Destination controls

Refresh, Discord, and Website buttons

Basic structure for character list panel added.

Map rendering was still placeholder (load_minimap()), no actual drawing logic.

> **Assessment:** Foundation of the modern UI — PyQt5 layout, modular widgets, and QWebEngine for in-game site.


---

## Version 0.3.3 — Minimap rendering engine implemented

**Key changes:**

Fully functional minimap drawing using QPainter on QPixmap.

Differentiates cell types:

Alleys, street edges, banks, pubs, transits, user buildings

Labels added to:

Named intersections

User buildings

Adds click detection on minimap (mouse events).

Combo box to go to a specific location using street names.

> **Assessment:** This version solidified the interactive PyQt-based minimap engine, replacing prior tkinter logic.


---

## Version 0.3.4 — Enhanced Qt layout + post-load coordination

**Key changes:**

Live HTML parsing from embedded WebView using BeautifulSoup.

Extracts player coordinates (x, y) and recenters minimap dynamically.

Greatly improved integration between map UI and game logic.

Map render logic abstracted to draw_minimap(), coordinates validated, text centered precisely.

> **Assessment:** Fully matured prototype of Qt-based RBCMap — bridging game backend data and GUI map interaction.


---

## Version 0.4.0 — Enhanced HTML integration & drawing logic

**Key changes:**

Adds extract_coordinates_from_html() using BeautifulSoup.

Pulls player coordinates dynamically from the embedded web view.

Minimap centers based on real in-game location.

Introduced structured minimap drawing via draw_minimap(), with:

Street overlays

Color-coded special locations (banks, pubs, transits, user buildings)

Destination setting stub added (Set Destination button).

✅ Introduced web-integrated positioning and a persistent GUI foundation.


---

## Version 0.4.1 — Nearest-location line drawing

**Key additions:**

Draws lines to 1st/2nd/3rd closest banks, pubs, and transits from center.

Implements closest_level logic tied to three new buttons.

☠️ Bug note: Selecting closest levels other than 1 causes stack buffer overflow.

⚠️ Functionally ambitious but structurally unstable. Good idea, flawed execution.


---

## Version 0.4.2 — Stability rework, feature isolation

**Changes:**

Removed interactive closest-location levels due to instability.

Simplified to show only nearest (1st) bank/pub/transit.

Preserved:

Map rendering

Real-time location pulling from HTML

Zoom and go-to logic

Prepared code for restoring closest_level logic later.

🔁 Rollback and cleanup patch, focusing on reliability and readiness for persistence.

