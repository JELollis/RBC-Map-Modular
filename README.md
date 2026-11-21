# RBC Community Map — 0.4.0

> **Archived snapshot.** This branch preserves version 0.4.0 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.4.0: Enhanced HTML integration & drawing logic

**Key changes:**

Adds extract_coordinates_from_html() using BeautifulSoup.

Pulls player coordinates dynamically from the embedded web view.

Minimap centers based on real in-game location.

Introduced structured minimap drawing via draw_minimap(), with:

Street overlays

Color-coded special locations (banks, pubs, transits, user buildings)

Destination setting stub added (Set Destination button).

✅ Introduced web-integrated positioning and a persistent GUI foundation.

See the [Changelog](Changelog.md#version-040--enhanced-html-integration--drawing-logic) for details and earlier history.

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
python main_0.4.0.py
```

- Keep `variables.py` next to the main script; it holds shared data the app imports.

## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
