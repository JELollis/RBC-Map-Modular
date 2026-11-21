# RBC Community Map — 0.3.3

> **Archived snapshot.** This branch preserves version 0.3.3 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.3.3: Minimap rendering engine implemented

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

See the [Changelog](Changelog.md#version-033--minimap-rendering-engine-implemented) for details and earlier history.

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
python main_0.3.3.py
```

- Keep `variables.py` next to the main script; it holds shared data the app imports.

## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
