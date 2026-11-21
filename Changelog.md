# Changelog — RBC Community Map

Release history up to **0.8.0**, oldest first.

- This branch (`version/0.8.0`) is an archived snapshot of 0.8.0 as `main_0.8.0.py`.
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


---

## Version 0.4.3 — Destination logic & visual feedback

**Major additions:**

Implements:

Persistent destination setting via pickle

Green path to destination drawn on minimap

Restores draw_location() abstraction, applies to all entity types.

Adds find_nearest_*() logic to draw paths to closest pub, bank, transit.

Maintains full parsing/rendering integrity from earlier versions.

🎯 Feature complete version for:

Destination persistence

Full nearest-location visual feedback

Refined GUI controls


---

## Version 0.5.0 — First database-driven release

**Highlights:**

Introduced connect_to_database() with fallback to remote host.

Loaded columns, rows, banks, taverns, transits, user buildings, and color_mappings from MySQL.

draw_minimap() adjusted to reflect color mappings from DB (color_map).

HTML extraction now pulls from `<span class='intersect'>`.

✅ First integration of live data from a structured MySQL schema.


---

## Version 0.5.1 — Qt color fix & code clarity

**Changes:**

Converts color strings from DB directly into QColor objects in color_map.

Ensures all dynamic visual updates (e.g. edges, alleys, etc.) honor the loaded palette.

Renamed color_map -> self.color_map inside the class for scope clarity.

🧠 Improved visual configuration and reduced hardcoded rendering logic.


---

## Version 0.5.2 — Shops & guilds integrated

**Additions:**

Loads shops and guilds from the database.

Parses their coordinates and next update timestamps.

Includes logic for rendering shop/guild icons on minimap.

Drawn using same draw_location() routine with new categories.

🎯 Adds merchant and faction overlays with live update hooks (timestamp support).


---

## Version 0.5.3 — Improved HTML coordinate extraction

**Enhancements:**

Improved fallback HTML parsing:

Now checks for `<input name="x">` and `<input name="y">` if `<span class='intersect'>` is missing.

Alternative fallback: parses `<td class='street'>` block with embedded `<form>`.

More robust against A View in the Dark HTML variations.

🛡️ Enhanced HTML fault tolerance in response to inconsistent site markup.


---

## Version 0.5.4 — Data scraper & next-update forecasting

Major New Logic:

Adds scrape_avitd_data():

Scrapes guilds and shops from the A View in the Dark site.

Updates DB rows with next update timestamps.

Adds:

extract_next_update_time()

update_guild(), update_shop()

update_guilds(), update_shops()

get_next_update_times() exposed for use in UI/notifications.

**🔄 Fully automated sync of key game structures to app backend via web scraping.**


---

## Version 0.6.0 — Modular cleanup + persistence prep

**Changes:**

Cleaned database schema queries, including color_mappings, shops, and guilds with next_update.

Refactored data loading into load_data() with tight dictionary comprehensions.

get_next_update_times() pulls guilds and shops update cycles.

🔗 Reliable DB-backed backend with clean data type safety.


---

## Version 0.6.1 — placesofinterest & fault-resilient DB reads

Improvements:

Integrated placesofinterest table from DB.

Improved resilience on coordinate mapping: filters out entries with None from failed columns.get(...).

Reduced potential for GUI crashes from missing data.

🛡️ Adds soft failure protections in data loading.


---

## Version 0.6.2 — Setup scripts & AP cost UI

**Key additions:**

Added automatic module installation prompt (pip install) with delay-based relaunch (great for first-time users).

load_characters() tied into dropdown, allowing users to select, add, or remove characters.

Minor GUI tweaks for padding and layout alignment.

**📦 Packs usability improvements and setup streamlining.**


---

## Version 0.6.3 — Character login + logging system

**Major upgrades:**

🔑 Character login/logout via in-game site using QWebEngineView JS injection.

Logs out current character → injects name/password → logs back in

**🧾 Logging system added:**

logs/rbc_YYYY-MM-DD.log

Uses logging.debug, info, warning, error

**🗃 Character list transitioned from QComboBox → QListWidget for better interactivity.**

🎨 GUI polish: Highlighted labels (banks, taverns, destination), “Coming Soon” website dialog.

**📁 Added ensure_directories_exist() to create logs/ and sessions/ if missing.**

🧠 Smart automation, session persistence, and robust logging define this release.


---

## Version 0.7.0 — Final PyQt5 build

The last release on PyQt5. It refines the A View in the Dark scraping
helpers (`update_guilds()`, `update_shops()`) and the "Coming Soon" website
dialog ahead of the toolkit change.

> **Correction:** earlier copies of this changelog listed the PySide6
> migration under 0.7.0. The archived `main_0.7.0.py` still imports PyQt5;
> the switch to PySide6 shipped in 0.7.1.


---

## Version 0.7.1 — Migration to PySide6, theme customization & persistent cookies

**Toolkit migration:**

Switched from PyQt5 to PySide6.

Introduced QWebEngineProfile for persistent cookies.

Modularized HTML, database, and logging setup.

Persistent character management with a fallback when no characters exist.

**New Features:**

Added load_theme_settings() and apply_theme() for UI color theming.

Implemented persistent QWebEngineProfile with stored cookies in sessions/cookies.

Abstracted cookie handling:

Load/save cookies via pickle

Auto-reapply cookies to quiz.ravenblack.net

🎨 Theming + 🍪 cookies = UX enhancement and session persistency.


---

## Version 0.7.2 — SQLite cookie storage & character persistence

**Upgrades:**

Replaced pickle-based cookies with SQLite-backed cookie DB (cookies.db).

Introduced:

initialize_cookie_db(), save_cookie_to_db(), load_cookies_from_db()

Character persistence logic now loads last active character automatically.

AVITDScraper integrated into app load to update DB automatically.

💾 First use of SQLite local state. Better for scaling.


---

## Version 0.7.3 — Componentization, multi-dialog system, JS injection

Massive Refactor:

App now includes:

DatabaseViewer for tab-based DB browsing

ThemeCustomizationDialog for visual tuning

SetDestinationDialog and CharacterDialog modularized

JavaScript logging via inject_console_logging()

Supports reading JS console logs from WebView.

Expanded load_data() to include new POIs.

**🧱 RBCMap becomes a modular, maintainable toolkit, not just a map viewer.**


---

## Version 0.8.0 — SQLite conversion & persistent UX foundation

**Changes:**

Fully transitioned backend from MySQL to SQLite for offline and portable deployment.

connect_to_database() and load_data() now point to local rbc_map_data.db.

Introduced theme, coin, and cookie persistence tables under a centralized sessions/ directory.

Modularized:

initialize_cookie_db()

initialize_coins_db()

initialize_database() with full schema validation.

**🔄 Major pivot from cloud-bound to standalone desktop-first architecture.**

