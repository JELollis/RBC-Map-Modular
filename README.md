# RBC Community Map — 0.10.0

> **Archived snapshot.** This branch preserves version 0.10.0 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.10.0: Unified application structure

**Highlights:**

Refactored RBCCommunityMap into a comprehensive, class-based application core.

Integrated:

Encrypted character handling

Cookie/session persistence

Theme and CSS injection

Full webview interaction via JS + HTML parsing

Created tools:

Damage Calculator

Shopping List Tool

Database Viewer

Powers and Guilds UI

🎯 Sets the gold standard structure for all major features in a centralized GUI shell

See the [Changelog](Changelog.md#version-0100--unified-application-structure) for details and earlier history.

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
python main_0.10.0.py
```


## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
