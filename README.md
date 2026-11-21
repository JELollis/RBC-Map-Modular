# RBC Community Map — 0.10.3

> **Archived snapshot.** This branch preserves version 0.10.3 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.10.3: Feature polishing & schema finalization

**Final additions:**

Hardened initialize_database() with:

Over a dozen normalized tables (banks, cookies, shop_items, coins, POIs, guilds, etc.)

INSERT OR IGNORE bootstrap logic for default records

check_required_modules() now validates environment dependencies at launch.

Fully documented top-level application, classes, and methods (self-contained docset).

**🧱 Locked in a fully seeded local database, supports upgrades without manual user intervention.**

See the [Changelog](Changelog.md#version-0103--feature-polishing--schema-finalization) for details and earlier history.

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
python main_0.10.3.py
```


## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
