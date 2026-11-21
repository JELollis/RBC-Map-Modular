# RBC Community Map — 0.2.0

> **Archived snapshot.** This branch preserves version 0.2.0 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.2.0: Data-driven landmark overlays

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

See the [Changelog](Changelog.md#version-020--data-driven-landmark-overlays) for details and earlier history.

## Requirements

- Python 3
- UI toolkit: tkinter

Third-party packages (also listed in [`requirements.txt`](requirements.txt)):
- PyQt5

## Run

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**macOS / Linux:**
```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

```bash
python main_0.2.0.py
```

- Keep `variables.py` next to the main script; it holds shared data the app imports.
- This is an early tkinter prototype; it predates the embedded game browser.
- Although the app itself uses tkinter, the bundled `variables.py` imports `PyQt5.QtGui.QColor`, so PyQt5 must be installed for it to start.

## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
