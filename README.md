# RBC Community Map — 0.7.1

> **Archived snapshot.** This branch preserves version 0.7.1 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.7.1: Migration to PySide6, theme customization & persistent cookies

**Toolkit migration:**

Switched from PyQt5 to PySide6.

Introduced QWebEngineProfile for persistent cookies.

Modularized HTML, database, and logging setup.

Persistent character management with a fallback when no characters exist.

**New Features:**

Added load_theme_settings() and apply_theme() for UI color theming.

Implemented persistent QWebEngineProfile with stored cookies in sessions/cookies.

Abstracted cookie handling:

Load/save cookies via pickle

Auto-reapply cookies to quiz.ravenblack.net

🎨 Theming + 🍪 cookies = UX enhancement and session persistency.

See the [Changelog](Changelog.md#version-071--migration-to-pyside6-theme-customization--persistent-cookies) for details and earlier history.

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
python main_0.7.1.py
```

- This version reads its location data from a remote MySQL database through PyMySQL. The server it was written for may no longer be reachable, so parts of the app may not load data.

## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
