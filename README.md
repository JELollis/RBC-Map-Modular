# RBC Community Map — 0.1.0

> **Archived snapshot.** This branch preserves version 0.1.0 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.1.0: Tkinter prototype

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

See the [Changelog](Changelog.md#version-010--tkinter-prototype) for details and earlier history.

## Requirements

- Python 3
- UI toolkit: tkinter

Third-party packages (also listed in [`requirements.txt`](requirements.txt)):
- None beyond Python 3 itself; tkinter ships with the standard library on most installs.

## Run

```bash
python main_0.1.0.py
```

- This is an early tkinter prototype; it predates the embedded game browser.

## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
