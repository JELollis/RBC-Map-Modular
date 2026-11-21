# RBC Community Map — 0.3.2

> **Archived snapshot.** This branch preserves version 0.3.2 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.3.2: PyQt5 migration begins

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

See the [Changelog](Changelog.md#version-032--pyqt5-migration-begins) for details and earlier history.

## Requirements

- Python 3
- UI toolkit: PyQt5 (Qt 5)

Third-party packages (also listed in [`requirements.txt`](requirements.txt)):
- PyQt5
- PyQtWebEngine

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
python main_0.3.2.py
```

- Keep `variables.py` next to the main script; it holds shared data the app imports.

## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
