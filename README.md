# RBC Community Map Application (Modular)

**Current development version: 1.0.4** · [Repository](https://github.com/JELollis/RBC-Map-Modular) · [Changelog](Changelog.md)

This is the **modular build** of RBC Community Map — the same application as the
[monolithic RBC-Map repository](https://github.com/JELollis/RBC-Map), decomposed
into one module per component. It is a Python desktop companion for
**Vampires! The Dark Alleyway** in [RavenBlack City](https://quiz.ravenblack.net/blood.pl).
It combines an interactive minimap, character management, community-maintained
location information, and in-game planning tools.

![Main application](Screenshots/Main%20Application.png)

## Features

### Interactive minimap
- Follow the character's current position using the game's right-hand frame.
- Show routes to the nearest **transit station** (red), **bank** (blue), and **pub** (orange).
- Choose a **3×3** (default), **5×5**, **7×7**, or **9×9** view.
- Recenter by clicking a map cell or choosing a location from the dropdowns and selecting **Go**.
- Use **Set Destination** to mark a destination and display its route in green.
- Customize the minimap theme; fallback rendering helps maintain usability in zoomed views.
- Refresh destination choices when the destination dialog opens.

![Minimap theme](Screenshots/Minimap%20Theme.png)

### Community location data
- Synchronize guild and shop movements and community-supplied buildings, points of interest, arenas, alchemy locations, lairs, and halls.
- Optionally enable **Contribute Discovered Locations** to report newly discovered non-moving locations anonymously. You can turn this setting off at any time.
- Continue using previously synchronized local location data when the update service is unavailable.

### Characters and controls
- Store character login details locally and switch between characters.
- Resize the navigation panel using its divider. The panel has a minimum width to keep the character buttons visible.
- Sign in automatically with a saved password when no session cookie is available; stale sign-in callbacks from a previously selected character are discarded.
- Restore destinations, themes, and other preferences between sessions.
- Choose **WASD** or **arrow keys** for movement; movement shortcuts are suppressed while typing into input fields.

![New user dialog](Screenshots/New%20User%20Dialog.png)

### Planning and reference tools

| Tool | What it does |
| --- | --- |
| **Shopping list** | Build item lists with Charisma-level prices, calculate total cost, compare against available coins, and view the countdown to the next shop update. |
| **Damage calculator** | Estimate damage required to bring a target to staking level and compare item combinations. |
| **Power information** | Review each power’s name, guild, cost, quest requirements, and effects, along with the countdown to the next guild move. |
| **Database viewer** | Inspect and manage underlying data tables (intended for advanced users). |

![Shopping list tool](Screenshots/Shopping%20List%20Tool.png)
![Damage calculator](Screenshots/Damage%20Calculator.png)
![Power information](Screenshots/Power%20Information.png)
![Database viewer](Screenshots/Database%20Viewer.png)

### Appearance customization
- Customize interface and minimap themes.
- Use the CSS customization tool for styling, including fonts, box shadows, and background images, with a live preview.

![CSS customization tool](Screenshots/CSS%20Customization%20Dialog.png)
![Interface theme](Screenshots/Interface%20Theme.png)

The damage calculator can use a shop’s inventory even when its map location is unknown.

## Getting started

### Requirements
The Python runtime dependencies listed in [`requirements.txt`](requirements.txt) are:
- PySide6 (including the Qt WebEngine components used by the embedded browser)
- beautifulsoup4
- keyring
- requests

A working Python 3 installation and an environment capable of running a Qt desktop application are required.

### Install dependencies

From a checkout of this branch, create and activate a virtual environment, then install the declared dependencies:

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

### Run

```bash
python main.py
```

When running from source, keep the folders it loads at runtime —
`images/` (interface and minimap artwork), `css/` (optional sample themes you
can import through the CSS dialog), and `docs/help/` (help files) — in the
same directory as `main.py`. The per-user data folder
(`%LOCALAPPDATA%\RBC-Map` on Windows, `~/.local/share/RBC-Map` on macOS and
Linux) is created automatically and does not need to sit next to the script.

### Self-checks

`main.py` supports the same headless self-check flags as the monolithic
build:

```bash
python main.py --self-check                    # resources + keyring backend
python main.py --self-check-gui                # GUI render check
```

## Data and privacy

Character information, session metadata, and application preferences are stored in a local SQLite database. Passwords and session-cookie values are stored through the operating system credential store via `keyring` when that store is available; after a successful migration, the database keeps only non-secret metadata. If the credential store is unavailable or locked, migration fails closed and deliberately leaves existing plaintext credentials in SQLite so they are not lost; resolve the credential-store problem and restart the app before treating the data as protected. On first launch, data from an older version kept next to the script (`sessions/` or `testing/sessions/`) is copied into the per-user data folder automatically; the originals are left in place. The app keeps its logs, sessions, and database in a per-user data folder (`%LOCALAPPDATA%\RBC-Map` on Windows, `$XDG_DATA_HOME/RBC-Map`, by default `~/.local/share/RBC-Map`, on macOS and Linux), outside the repository. Don't commit or share that folder.

On Linux, the keyring needs an available, unlocked Secret Service collection. If it does not respond, the app stops waiting and retries the backend only after a restart. If you cannot use a keyring, launch with `RBC_MAP_CREDENTIAL_STORAGE=sqlite python main.py` to use a separate `RBC-Map-SQLite` profile. Add your characters again in that profile. Its SQLite database stores saved passwords and session cookies in plaintext. Launch without the environment variable to return to the original keyring-backed profile. See the [Linux installation guide](docs/help/Linux_Installation.html) for package requirements and workarounds.

After confirming your characters, settings, and sign-in work in the new data folder, consider deleting the old copies in `sessions/` or `testing/sessions/` next to the old installation and any `rbc_map_data.db.pre-migration` backup in the new sessions folder. These backups may contain plaintext passwords or session cookies. Keep them if you still need rollback, and protect any copies you retain.

The documented community reporting feature (**Contribute Discovered Locations**) is **opt-in** and is intended to send only newly discovered non-moving locations, not login credentials. Review the application's settings before enabling reporting, and protect your local database and device as you would other stored credentials.

## Versions and branches

| Branch | Contents |
| --- | --- |
| `master` | Active development, currently tracking the monolithic 1.0.4 codebase in modular form. |
| `version/0.13.3.0` | The faithful modular decomposition of monolith v0.13.3.0. |
| `version/0.12.1` | The earlier modular split at v0.12.1. |

`version/<number>` branches are snapshots for reference and are not maintained.
For the full version history of the application itself, see the
[monolithic repository](https://github.com/JELollis/RBC-Map) and its
[`version/*` branches](https://github.com/JELollis/RBC-Map/branches/all?query=version%2F).

## Repository layout

| Path | Purpose |
| --- | --- |
| `main.py` | Application entry point (`python main.py`). |
| `imports.py` | Shared imports and QtWebEngine environment setup. |
| `constants.py` | Paths, version, and shared constants. |
| `secrets.py` | OS credential-store (keyring) helpers and secret migration. |
| `directories.py` | Data-directory setup, permissions, and legacy-data migration. |
| `logging_setup.py` | Logging configuration. |
| `database.py` | SQLite schema, migrations, and startup data load. |
| `cookies.py` | Cookie persistence. |
| `splash.py` | Splash screen and theme helpers. |
| `rbc_community_map.py` | Main window, update client, and map logic. |
| `*_dialog.py`, `*_tool.py`, `compass_overlay.py` | Dialogs and tools. |
| `requirements.txt` | Runtime dependencies. |
| `images/`, `css/` | Icons, artwork, and stylesheets used by the app. |
| `docs/help/` | Help documentation (HTML, PDF, CHM, EPUB, DOCX). |
| `Screenshots/` | Screenshots used in this README. |

## Documentation, support, and contributions

- [Changelog](Changelog.md) — release history.
- [Help documentation](docs/help/RBC_Map_Help.html) — application help topics.
- [crowdsourced-location-reporting.md](docs/crowdsourced-location-reporting.md) — community location reporting design notes.
- [GitHub issues](https://github.com/JELollis/RBC-Map-Modular/issues) — report bugs and suggest improvements.
- [Community Discord](https://discord.gg/rKamEZvK6X) — community discussion (the server has a joining process).

Contributions and feedback are welcome. When reporting a problem, include the application version, operating system, steps to reproduce, and relevant error details; do not include passwords or session credentials.

## License

The project is documented as licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

## Contributors

**Development team**
- **Windows compatibility:** Jonathan Lollis (Nesmuth), Justin Solivan
- **macOS compatibility:** Joseph Lemois
- **Linux compatibility:** Josh "Blaskewitts" Corse, Fern Lovebond
- **Design and layout:** Shuvi, Blair Wilson (Ikunnaprinsess)

**Special thanks**
- [LIAM²](http://liam2.leprichaunproductions.com/home.php) by Cain "Leprechaun" McBride — inspiration for this project.
- [A View in the Dark](https://aviewinthedark.net/) by Cliff Burton — shop and guild data.
- [RavenBlack Wiki](https://ravenblack.city/) contributors.
- Anders — RBNav and ongoing support.
- [Vespertine's City Crawler](https://vampires.terrible.engineering/) — additional shop and guild data.
