# RBC Community Map — 0.12.0

> **Archived snapshot.** This branch preserves version 0.12.0 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.12.0: Monolithic architecture with enhanced modularity

- **Monolithic structure** retained in `main_0.12.0.py` with improved internal modularity for maintainability.
- **`create_tables()` and `insert_initial_data()`** define and seed all SQLite tables, eliminating manual pre-seeding.
- **`check_and_install_modules()`** ensures required Python packages are installed at startup.
- **QSplashScreen** splash screen enhances startup UX with loading feedback.

#### 🛠️ Core Features Solidified

- **RBCCommunityMap** unifies key UI components:
  - Minimap rendering with dynamic overlays
  - Zoom and movement logic
  - WASD keyboard navigation
  - Theme application
  - Character persistence
- **Persistent data** for characters, cookies, destinations, coins, and logging settings via SQLite.
- **Expanded dialog system** integrates modular tools:
  - `DamageCalculator`, `ShoppingListTool`, `ThemeCustomizationDialog`, `CSSCustomizationDialog`, `DatabaseViewer`, `PowersDialog`, `SetDestinationDialog`, `CharacterDialog`
  - Each tool operates independently with DB hooks, input validation, and polished UI.

#### 💡 New Technical Capabilities

- **Logging** uses `logging.FileHandler` with dynamic log level from DB.
- **Auto-directory setup** creates `logs/`, `sessions/`, and `images/` at launch.
- **Real-time JavaScript logging and CSS injection** for webview interaction.
- **Coordinate mapping and color customization** stored in DB, extensible via `color_mappings` and `css_profiles`.

#### 🧬 Schema and Data Foundations

- Over 20 SQLite tables, including `characters`, `coins`, `banks`, `shops`, `guilds`, `taverns`, `placesofinterest`, `color_mappings`, `custom_css`, `rows`, `columns`, `powers`, `discord_servers`.
- Tables seeded with default data using `INSERT OR IGNORE` for first-time installs and upgrade-safe bootstrapping.

See the [Changelog](Changelog.md#version-0120--monolithic-architecture-with-enhanced-modularity) for details and earlier history.

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
python main_0.12.0.py
```


## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
