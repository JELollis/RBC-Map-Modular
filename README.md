# RBC Community Map — 0.11.2

> **Archived snapshot.** This branch preserves version 0.11.2 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.11.2: Splash screen & loading feedback

**New Features:**

Added SplashScreen class using QSplashScreen, visually indicating loading status.

Webview error handling improved — logs load issues more precisely.

Ensured compatibility of web engine initialization on slower machines (fixes some black-screen issues).

First version where startup dependencies are shown as "loading..." at splash.

🎨 First steps toward full UX onboarding flow and startup feedback

See the [Changelog](Changelog.md#version-0112--splash-screen--loading-feedback) for details and earlier history.

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
python main_0.11.2.py
```


## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
