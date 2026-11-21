# RBC Community Map — 0.9.0

> **Archived snapshot.** This branch preserves version 0.9.0 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.9.0: Encrypted local state & database formalization

**Key enhancements:**

Switched to fully encrypted storage for sensitive data (e.g., character passwords) using cryptography.Fernet.

Finalized SQLite schema:

Adds powers, placesofinterest, shop_items, and recent_destinations.

Adds foreign key constraints and default population for banks, colors, guilds, powers, POIs, etc.

Resilient modular initialization:

initialize_database() builds all tables with INSERT OR IGNORE seeding.

Extensive documentation headers added to all sections.

**🧱 Formalized DB schema, added encryption, and enhanced modular infrastructure.**

See the [Changelog](Changelog.md#version-090--encrypted-local-state--database-formalization) for details and earlier history.

## Requirements

- Python 3
- UI toolkit: PySide6 (Qt 6)

Third-party packages (also listed in [`requirements.txt`](requirements.txt)):
- PySide6
- beautifulsoup4
- requests
- PyMySQL
- cryptography

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
python main_0.9.0.py
```

- This version reads its location data from a remote MySQL database through PyMySQL. The server it was written for may no longer be reachable, so parts of the app may not load data.

## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
