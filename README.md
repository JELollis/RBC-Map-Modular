# RBC Community Map — 0.4.3

> **Archived snapshot.** This branch preserves version 0.4.3 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.4.3: Destination logic & visual feedback

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

See the [Changelog](Changelog.md#version-043--destination-logic--visual-feedback) for details and earlier history.

## Requirements

- Python 3
- UI toolkit: PyQt5 (Qt 5)

Third-party packages (also listed in [`requirements.txt`](requirements.txt)):
- PyQt5
- PyQtWebEngine
- beautifulsoup4

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
python main_0.4.3.py
```

- Keep `variables.py` next to the main script; it holds shared data the app imports.

## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
