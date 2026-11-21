# RBC Community Map — 0.3.0

> **Archived snapshot.** This branch preserves version 0.3.0 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.3.0: Initial refactor (Tkinter OOP)

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

See the [Changelog](Changelog.md#version-030--initial-refactor-tkinter-oop) for details and earlier history.

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
python main_0.3.0.py
```

- Keep `variables.py` next to the main script; it holds shared data the app imports.
- This is an early tkinter prototype; it predates the embedded game browser.
- Although the app itself uses tkinter, the bundled `variables.py` imports `PyQt5.QtGui.QColor`, so PyQt5 must be installed for it to start.

## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
