# RBC Community Map — 0.6.3

> **Archived snapshot.** This branch preserves version 0.6.3 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.6.3: Character login + logging system

**Major upgrades:**

🔑 Character login/logout via in-game site using QWebEngineView JS injection.

Logs out current character → injects name/password → logs back in

**🧾 Logging system added:**

logs/rbc_YYYY-MM-DD.log

Uses logging.debug, info, warning, error

**🗃 Character list transitioned from QComboBox → QListWidget for better interactivity.**

🎨 GUI polish: Highlighted labels (banks, taverns, destination), “Coming Soon” website dialog.

**📁 Added ensure_directories_exist() to create logs/ and sessions/ if missing.**

🧠 Smart automation, session persistence, and robust logging define this release.

See the [Changelog](Changelog.md#version-063--character-login--logging-system) for details and earlier history.

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
python main_0.6.3.py
```

- This version reads its location data from a remote MySQL database through PyMySQL. The server it was written for may no longer be reachable, so parts of the app may not load data.

## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
