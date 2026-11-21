# RBC Community Map — 0.13.0

> **Archived snapshot.** This branch preserves version 0.13.0 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.13.0: Major internal refactor

Version 0.13.0 introduces substantial internal changes while retaining a monolithic file structure. All location scraping logic has been **fully removed** and replaced with a modern system that pulls shop and guild data from a live Discord bot-powered JSON endpoint (`locations.json`).

#### ✅ Key Changes in v0.13.0

- 🔁 **Scraper Replaced**: No more scraping from AVITD or Terrible API in-app. Now syncs to `locations.json` from the Discord bot.
- 🧭 **Countdown Timers**: Set Destination and Powers dialogs now show **next shop/guild move time** and **live countdowns**.
- 🏷️ **Nickname-Based Dropdowns**: Canonical building names now normalized to internal nicknames in all dropdowns (e.g., "Ace Pawn" → "Ace Porn").
- 🖌️ **Minimap Rendering Stabilized**: Refined `draw_minimap()` logic ensures label rendering is clean and consistent at all zoom levels.
- 🪵 **Log Viewer Improved**: Filterable logs now support persistent logging level preference and visibility toggling in-app.
- 🧠 **SetDestinationDialog Improvements**:
  - Auto-fetches latest data on open
  - Manual "Update Data" triggers external API scrape via the bot
  - Countdown to next update clearly displayed
- 🛡️ **Startup and Error Handling**:
  - Webview loads are validated and logged
  - Nickname normalization handled on input and dropdown population

#### 💡 Notable Refactor Milestones
- Replaced all instances of `scrape_*()` logic with `fetch_locations_json()`.
- Added persistent log level storage in the database.
- Updated schema to track last scrape time per source.
- Optimized coordinate display logic for improved grid clarity.

> This is the final monolithic version before future potential modularization or mobile/packaged deployment revisions.

See the [Changelog](Changelog.md#version-0130--major-internal-refactor) for details and earlier history.

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
python main_0.13.0.py
```


## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
