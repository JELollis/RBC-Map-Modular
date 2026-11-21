# RBC Community Map — 0.5.4

> **Archived snapshot.** This branch preserves version 0.5.4 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.5.4: Data scraper & next-update forecasting

Major New Logic:

Adds scrape_avitd_data():

Scrapes guilds and shops from the A View in the Dark site.

Updates DB rows with next update timestamps.

Adds:

extract_next_update_time()

update_guild(), update_shop()

update_guilds(), update_shops()

get_next_update_times() exposed for use in UI/notifications.

**🔄 Fully automated sync of key game structures to app backend via web scraping.**

See the [Changelog](Changelog.md#version-054--data-scraper--next-update-forecasting) for details and earlier history.

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
python main_0.5.4.py
```

- This version reads its location data from a remote MySQL database through PyMySQL. The server it was written for may no longer be reachable, so parts of the app may not load data.

## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
