# RBC Community Map — 0.6.2

> **Archived snapshot.** This branch preserves version 0.6.2 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.6.2: Setup scripts & AP cost UI

**Key additions:**

Added automatic module installation prompt (pip install) with delay-based relaunch (great for first-time users).

load_characters() tied into dropdown, allowing users to select, add, or remove characters.

Minor GUI tweaks for padding and layout alignment.

**📦 Packs usability improvements and setup streamlining.**

See the [Changelog](Changelog.md#version-062--setup-scripts--ap-cost-ui) for details and earlier history.

## Requirements

- Python 3
- UI toolkit: PyQt5 (Qt 5)

Third-party packages (also listed in [`requirements.txt`](requirements.txt)):
- PyQt5
- PyQtWebEngine
- beautifulsoup4
- requests
- PyMySQL

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
python main_0.6.2.py
```

- This version reads its location data from a remote MySQL database through PyMySQL. The server it was written for may no longer be reachable, so parts of the app may not load data.

## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
