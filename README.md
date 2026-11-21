# RBC Community Map — 0.13.1

> **Archived snapshot.** This branch preserves version 0.13.1 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.13.1: Minimap & stability fixes

A small maintenance release on top of 0.13.0's monolithic rewrite, focused on
minimap rendering correctness and general cleanup.

#### ✅ Key Changes in v0.13.1
- 🗺️ **Minimap rendering fix**: corrected label/grid drawing issues that could
  appear at certain zoom levels.
- 🧹 Iterative fixes and `.gitignore` housekeeping across the testing build.

> 0.13.1 is the baseline the subsequent 0.13.2 security work builds on.

See the [Changelog](Changelog.md#version-0131--minimap--stability-fixes) for details and earlier history.

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
python main_0.13.1.py
```


## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
