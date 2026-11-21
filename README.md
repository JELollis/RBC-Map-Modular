# RBC Community Map — 0.7.3

> **Archived snapshot.** This branch preserves version 0.7.3 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.7.3: Componentization, multi-dialog system, JS injection

Massive Refactor:

App now includes:

DatabaseViewer for tab-based DB browsing

ThemeCustomizationDialog for visual tuning

SetDestinationDialog and CharacterDialog modularized

JavaScript logging via inject_console_logging()

Supports reading JS console logs from WebView.

Expanded load_data() to include new POIs.

**🧱 RBCMap becomes a modular, maintainable toolkit, not just a map viewer.**

See the [Changelog](Changelog.md#version-073--componentization-multi-dialog-system-js-injection) for details and earlier history.

## Requirements

- Python 3
- UI toolkit: PySide6 (Qt 6)

Third-party packages (also listed in [`requirements.txt`](requirements.txt)):
- PySide6
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
python main_0.7.3.py
```

- This version reads its location data from a remote MySQL database through PyMySQL. The server it was written for may no longer be reachable, so parts of the app may not load data.

## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
