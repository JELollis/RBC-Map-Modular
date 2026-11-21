# RBC-Map release packaging

Release builds use Python 3.13 and are produced by the controlled GitHub Actions
workflow from the immutable `github.sha` associated with the selected workflow
run ref. Local builds are for recipe validation only.

- Windows: Nuitka onedir, followed by NSIS. The installer installs application
  files under `%LOCALAPPDATA%\Programs\RBC-Map` and preserves user data under
  `%LOCALAPPDATA%\RBC-Map` when uninstalled.
- Linux and macOS: PyInstaller onedir using `rbc-map.spec` unless a platform
  workflow documents a more suitable native freezer.
- Every frozen build must include the `keyring` distribution metadata and its
  platform backends. A smoke test must verify that the frozen app does not use
  `fail.Keyring`.
- Packages must contain `images/`, `css/`, and `docs/help/` beside the executable.
- Do not include `sessions/`, databases, logs, or other machine-specific data.

Windows artifacts are currently unsigned. SignPath Foundation signing may be
added only after project acceptance and owner approval of the protected signing
workflow.
