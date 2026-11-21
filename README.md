# RBC Community Map Application

**Release 1.0.0** (this branch) · Development continues on [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) · [Repository](https://github.com/JELollis/RBC-Map) · [Changelog](Changelog.md)

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in [RavenBlack City](https://quiz.ravenblack.net/blood.pl). It combines an interactive minimap, character management, community-maintained location information, and in-game planning tools.

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
- Restore destinations, themes, and other preferences between sessions.
- Choose **WASD** or **arrow keys** for movement; movement shortcuts are suppressed while typing into input fields.

![New user dialog](Screenshots/New%20User%20Dialog.png)

### Planning and reference tools

| Tool | What it does |
| --- | --- |
| **Shopping list** | Build item lists, calculate total cost, compare against available coins, and view the countdown to the next shop update. |
| **Damage calculator** | Estimate damage required to bring a target to staking level and compare item combinations. |
| **Power information** | Review game powers, descriptions, costs, effects, and the countdown to the next guild move. |
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

## Getting started

### Requirements
The Python runtime dependencies listed in [`requirements.txt`](requirements.txt) are:
- PySide6 (including the Qt WebEngine components used by the embedded browser)
- beautifulsoup4
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
python main_1.0.0.py
```

For a packaged build, check the repository's [releases](https://github.com/JELollis/RBC-Map/releases) for available downloads and release-specific instructions.

## Data and privacy

Character information, credentials, session state, and application preferences are stored in a local SQLite database. The app keeps its logs, sessions, and database in a per-user data folder (`%LOCALAPPDATA%\RBC-Map` on Windows, `$XDG_DATA_HOME/RBC-Map`, by default `~/.local/share/RBC-Map`, on macOS and Linux), outside the repository. Don't commit or share that folder.

The documented community reporting feature (**Contribute Discovered Locations**) is **opt-in** and is intended to send only newly discovered non-moving locations, not login credentials. Review the application's settings before enabling reporting, and protect your local database and device as you would other stored credentials.

## Versions and branches

This `version/1.0.0` branch is the fixed snapshot of release 1.0.0 (`main_1.0.0.py`). Ongoing development happens on [`dev`](https://github.com/JELollis/RBC-Map/tree/dev); each earlier version is preserved on its own `version/<number>` branch with a README and changelog for that version. Version tags and [releases](https://github.com/JELollis/RBC-Map/releases) mark published builds.

## Repository layout

| Path | Purpose |
| --- | --- |
| `main_1.0.0.py` | The application (release 1.0.0), packaged as a single file. |
| `requirements.txt` | Runtime dependencies. |
| `images/`, `css/` | Icons, artwork, and stylesheets used by the app. |
| `docs/help/` | Help documentation (HTML, PDF, CHM, EPUB, DOCX). |
| `Screenshots/` | Screenshots used in this README. |

## Documentation, support, and contributions

- [Changelog](Changelog.md) — release history.
- [Help documentation](docs/help/RBC_Map_Help.html) — application help topics.
- [GitHub issues](https://github.com/JELollis/RBC-Map/issues) — report bugs and suggest improvements.
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
