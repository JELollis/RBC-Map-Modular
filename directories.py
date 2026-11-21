from imports import *
from constants import *



# -----------------------
# Directory Setup
# -----------------------

def ensure_directories_exist(
        directories: list[os.PathLike | str] | None = None,
) -> bool:
    """
    Ensure that the required directories exist, creating them if necessary.
    """
    if directories is None:
        directories = REQUIRED_DIRECTORIES

    success = True
    for directory in directories:
        try:
            if not os.path.isdir(directory):
                os.makedirs(directory, exist_ok=True)
                logging.debug("Created directory: %s", directory)
            else:
                logging.debug("Directory already exists: %s", directory)
        except OSError as exc:
            logging.error(
                "Failed to create directory '%s': %s",
                directory,
                exc,
            )
            success = False

    return success



def _secure_data_permissions(
        data_dir: Path = DATA_DIR,
        sessions_dir: Path = SESSIONS_DIR,
) -> None:
    """POSIX-only: keep credential-bearing data private.

    Migration can leave plaintext passwords and cookies in SQLite when the
    keyring is unavailable, so the data and sessions directories are kept at
    0700 and the database family of files at 0600 regardless of umask.
    """
    if os.name != "posix":
        return
    for directory in (data_dir, sessions_dir):
        try:
            if directory.is_dir():
                directory.chmod(0o700)
        except OSError:
            pass
    if not sessions_dir.is_dir():
        return
    try:
        children = list(sessions_dir.iterdir())
    except OSError:
        return
    for path in children:
        if path.name.startswith(LEGACY_DB_NAME):
            try:
                path.chmod(0o600)
            except OSError:
                pass



# Validate directories at startup
if SQLITE_CREDENTIAL_STORAGE:
    DATA_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name == "posix":
        DATA_DIR.chmod(0o700)
    logging.warning("SQLite credential storage is enabled for the separate RBC-Map-SQLite profile.")


if not ensure_directories_exist():
    logging.warning(
        "Some directories could not be created. "
        "Application may encounter issues."
    )

_secure_data_permissions()



# -----------------------
# Legacy Data Migration
# -----------------------

# Before 1.0.0 the app kept its data next to the script: ``sessions/`` at the
# repository root (0.13.x and earlier) or ``testing/sessions/`` (the former
# 0.13.3.x / 0.14.0 development line). 1.0.0 moved it to DATA_DIR. On Windows,
# pre-1.0 installs also kept data under per-user install directories.
def _legacy_sessions_dirs(is_windows: bool | None = None) -> list[Path]:
    dirs = [
        APP_DIR / "sessions",
        APP_DIR / "testing" / "sessions",
    ]
    if is_windows is None:
        is_windows = os.name == "nt"
    if is_windows:
        local_appdata = os.environ.get("LOCALAPPDATA")
        if local_appdata:
            dirs += [
                Path(local_appdata) / "RBC Community Map" / "sessions",
                Path(local_appdata) / "RBCCommunityMap" / "sessions",
            ]
        for var in ("ProgramFiles", "ProgramFiles(x86)"):
            root = os.environ.get(var)
            if root:
                for folder_name in ("RBC-Map", "RBC Community Map"):
                    dirs.append(Path(root) / folder_name / "sessions")
        if local_appdata:
            # UAC file virtualization could redirect pre-1.0 writes here.
            virtual_store = Path(local_appdata) / "VirtualStore"
            for pf in ("Program Files", "Program Files (x86)"):
                for folder_name in ("RBC Community Map", "RBC-Map"):
                    dirs.append(virtual_store / pf / folder_name / "sessions")
    return dirs



LEGACY_SESSIONS_DIRS = _legacy_sessions_dirs()



def _connect_read_only(db_path: Path) -> sqlite3.Connection:
    """Open *db_path* read-only via an encoded file URI (safe for '#', '?', '%')."""
    return sqlite3.connect(f"{db_path.resolve().as_uri()}?mode=ro", uri=True)



def _count_characters(db_path: Path) -> int | None:
    """Return the number of saved characters in *db_path*.

    Returns 0 for an empty or schema-less database (no ``characters``
    table) and None only when the file cannot be read as SQLite at all.
    """
    try:
        conn = _connect_read_only(db_path)
        try:
            has_table = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'characters'"
            ).fetchone()
            if not has_table:
                return 0
            return conn.execute("SELECT COUNT(*) FROM characters").fetchone()[0]
        finally:
            conn.close()
    except sqlite3.Error:
        return None



def _mark_migration_done(sessions_dir: Path, note: str) -> None:
    """Persist that legacy migration is settled; best effort."""
    try:
        (sessions_dir / LEGACY_MIGRATION_MARKER).write_text(note + "\n", encoding="utf-8")
    except OSError:
        pass



def _copy_if_absent(src: str, dst: str) -> str:
    """copytree copy function that leaves an existing destination file alone.

    Copies via a ``.migrating`` sibling and an atomic rename so an interrupted
    copy never leaves a truncated file that would look complete next launch.
    """
    if os.path.lexists(dst):
        return dst
    temp = dst + ".migrating"
    shutil.copy2(src, temp)
    os.replace(temp, dst)
    return dst



def migrate_legacy_data(
        sessions_dir: Path = SESSIONS_DIR,
        legacy_dirs: list[Path] | None = None,
) -> str | None:
    """Copy pre-1.0.0 session data into *sessions_dir* once.

    Runs before anything opens the database. It migrates when the new database
    is missing, or exists but holds no saved characters while a legacy
    database does (a 1.0.0 launch before this fix created an empty one). Only
    legacy databases that contain saved characters are considered. The
    replaced database is kept as a ``.pre-migration`` backup. Web profile
    files already present in *sessions_dir* are kept; only missing ones are
    copied.

    A marker file records when the question is settled: after a successful
    migration, or when the new database already holds characters (or cannot
    be read). Once it exists the migration never runs again, so deleting all
    characters later cannot bring the legacy accounts back.

    Legacy files are only read, never modified. The database is copied last,
    through a temporary file and an atomic rename, so a failed migration leaves
    no partial database and is retried on the next launch.

    Returns a message describing what happened, or None if nothing to do.
    Logging is not configured yet when this runs, so the caller logs it.
    """
    if legacy_dirs is None:
        legacy_dirs = LEGACY_SESSIONS_DIRS

    target_db = sessions_dir / LEGACY_DB_NAME
    if (sessions_dir / LEGACY_MIGRATION_MARKER).exists():
        return None
    candidates = [
        d for d in legacy_dirs
        if (d / LEGACY_DB_NAME).is_file() and d.resolve() != sessions_dir.resolve()
    ]
    # Only legacy databases that actually hold characters are worth
    # migrating; a newer but empty one must not beat an older populated one.
    populated = [
        d for d in candidates
        if (_count_characters(d / LEGACY_DB_NAME) or 0) > 0
    ]
    if not populated:
        return None
    source_dir = max(populated, key=lambda d: (d / LEGACY_DB_NAME).stat().st_mtime)
    source_db = source_dir / LEGACY_DB_NAME

    if target_db.exists():
        target_count = _count_characters(target_db)
        if target_count is None or target_count > 0:
            # The new location holds the user's data (or can't be checked
            # safely): keep it and settle the question for good.
            _mark_migration_done(sessions_dir, f"kept existing data; legacy at {source_dir}")
            return None

    temp_db = target_db.with_name(LEGACY_DB_NAME + ".migrating")
    try:
        sessions_dir.mkdir(parents=True, exist_ok=True)
        # Web profile data (except Chromium cookie databases) first; the
        # database last. Files already in the new profile are kept.
        shutil.copytree(
            source_dir,
            sessions_dir,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(LEGACY_DB_NAME + "*", "Cookies*"),
            copy_function=_copy_if_absent,
        )
        temp_db.unlink(missing_ok=True)
        src = _connect_read_only(source_db)
        try:
            dst = sqlite3.connect(temp_db)
            try:
                src.backup(dst)
            finally:
                dst.close()
        finally:
            src.close()
        if target_db.exists():
            backup = target_db.with_name(LEGACY_DB_NAME + ".pre-migration")
            os.replace(target_db, backup)
        os.replace(temp_db, target_db)
    except (OSError, sqlite3.Error) as exc:
        try:
            temp_db.unlink(missing_ok=True)
        except OSError:
            pass
        return f"Legacy data migration from {source_dir} failed; will retry next launch: {exc}"

    _mark_migration_done(sessions_dir, f"migrated from {source_dir}")
    return f"Migrated saved data from {source_dir} to {sessions_dir}"



LEGACY_MIGRATION_MESSAGE = None if SQLITE_CREDENTIAL_STORAGE else migrate_legacy_data()

_secure_data_permissions()



def remove_persistent_browser_cookies(sessions_dir: Path = SESSIONS_DIR) -> None:
    """Remove Chromium cookie stores left by older persistent-cookie builds."""
    for cookie_path in sessions_dir.rglob("Cookies*"):
        try:
            if cookie_path.is_dir():
                shutil.rmtree(cookie_path)
            else:
                cookie_path.unlink()
            logging.info("Removed legacy persistent cookie store %s", cookie_path)
        except OSError as exc:
            logging.warning("Could not remove legacy cookie store %s: %s", cookie_path, exc)
