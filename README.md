# RBC Community Map — 0.11.0

> **Archived snapshot.** This branch preserves version 0.11.0 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.11.0: Feature consolidation & keyboard navigation

**Additions:**

Introduced WASD keybindings with database-configurable modes.

All major tools — Minimap, Powers, Damage Calculator, Shopping List — consolidated into main UI.

RBCCommunityMap now supports:

move_character(), setup_keybindings(), zoom_in/out

Major module imports refactored into clean sections for readability.

Documentation headers massively improved.

📌 Solidifies RBCMap as a full-featured modular app

See the [Changelog](Changelog.md#version-0110--feature-consolidation--keyboard-navigation) for details and earlier history.

## Requirements

- Python 3
- UI toolkit: PySide6 (Qt 6)

Third-party packages (also listed in [`requirements.txt`](requirements.txt)):
- PySide6
- beautifulsoup4
- requests

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
python main_0.11.0.py
```


## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
