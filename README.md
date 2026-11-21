# RBC Community Map — 0.13.2

> **Archived snapshot.** This branch preserves version 0.13.2 for reference; it is not maintained.
> For current use, see the latest release, [1.0.0](https://github.com/JELollis/RBC-Map/tree/version/1.0.0),
> or the [`dev`](https://github.com/JELollis/RBC-Map/tree/dev) branch for ongoing development.

RBC Community Map is a Python desktop companion for **Vampires! The Dark Alleyway** in
[RavenBlack City](https://quiz.ravenblack.net/blood.pl).

## About 0.13.2: Security & robustness update

Version 0.13.2 is a small security and robustness update on v0.13.1, still
packaged as a single file.

#### ✅ Key Changes in v0.13.2
- 🔒 **Safer login injection**: login form JavaScript is now built with
  `json.dumps`, preventing accidental/unsafe JS string construction from
  character names or passwords.
- ⏱️ **Request timeouts**: external HTTP calls use a default 10s timeout so a
  slow or dead endpoint can no longer block background threads.
- 📦 **Fail-fast dependencies**: removed runtime pip auto-install; missing
  dependencies are now reported clearly and packagers must provide them.

#### 💡 Notable Internal Work
- Refactored imports and reorganized SQLite table/data setup.
- Updated Qt color usage and tightened type hints in the main script.
- Cleaned up external API URLs (removed the `/wsgi/` path segment).

See the [Changelog](Changelog.md#version-0132--security--robustness-update) for details and earlier history.

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
python main_0.13.2.py
```


## License

Licensed under the [Apache License 2.0](License.txt). See [Contributors.md](Contributors.md) for credits.
