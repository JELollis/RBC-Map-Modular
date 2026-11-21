"""Regression check for the pre-1.0.0 data migration in the modular package.

Extracts ``_count_characters`` and ``migrate_legacy_data`` from the main
script without importing it (importing would start the Qt app), then runs
them against temporary folders.

Usage: python tools/check_legacy_migration.py 
Exits non-zero on the first failure.
"""
import ast
import logging
import os
import shutil
import sqlite3
import stat
import sys
import tempfile
from pathlib import Path

from _app import load_app_tree, load_app_source
ROOT = Path(__file__).resolve().parent.parent
MAIN = Path("modular_app")
WANTED = {"_connect_read_only", "_count_characters", "_mark_migration_done",
          "_copy_if_absent", "migrate_legacy_data", "remove_persistent_browser_cookies",
          "_legacy_sessions_dirs", "_secure_data_permissions"}


def load_functions():
    tree = load_app_tree()
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in WANTED]
    assert {n.name for n in nodes} == WANTED, f"missing functions in {MAIN.name}"
    # Default arguments reference module globals; bind placeholders, tests pass real values.
    ns = {"Path": Path, "os": os, "shutil": shutil, "sqlite3": sqlite3, "logging": logging,
          "APP_DIR": Path("unused"), "DATA_DIR": Path("unused"), "SESSIONS_DIR": Path("unused"),
          "LEGACY_SESSIONS_DIRS": [],
          "LEGACY_DB_NAME": "rbc_map_data.db",
          "LEGACY_MIGRATION_MARKER": ".legacy-migration-done"}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(MAIN), "exec"), ns)
    return (ns["migrate_legacy_data"], ns["_count_characters"],
            ns["remove_persistent_browser_cookies"], ns["_legacy_sessions_dirs"],
            ns["_secure_data_permissions"])


def make_db(path: Path, characters: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE characters (id INTEGER PRIMARY KEY, name TEXT, password TEXT)")
    conn.executemany("INSERT INTO characters (name, password) VALUES (?, '')",
                     [(c,) for c in characters])
    conn.commit()
    conn.close()


def names(path: Path):
    conn = sqlite3.connect(path)
    try:
        return sorted(r[0] for r in conn.execute("SELECT name FROM characters"))
    finally:
        conn.close()


def run(name, fn):
    with tempfile.TemporaryDirectory() as tmp:
        fn(Path(tmp))
    print(f"ok   {name}")


migrate, count, remove_cookie_store, legacy_dirs_fn, secure_perms = load_functions()


def fresh_install_no_legacy(t: Path):
    assert migrate(t / "new", [t / "app/sessions"]) is None
    assert not (t / "new").exists()


def migrates_root_sessions(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    (t / "app/sessions/profile").mkdir()
    (t / "app/sessions/profile/Cookies").write_text("c")
    msg = migrate(t / "new", [t / "app/sessions", t / "app/testing/sessions"])
    assert msg and "Migrated" in msg, msg
    assert names(t / "new/rbc_map_data.db") == ["Alice"]
    assert not (t / "new/profile/Cookies").exists(), "legacy Chromium cookies must not be copied"
    assert names(t / "app/sessions/rbc_map_data.db") == ["Alice"], "original changed"
    assert not (t / "new/rbc_map_data.db.migrating").exists()


def prefers_newest_legacy(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Old"])
    make_db(t / "app/testing/sessions/rbc_map_data.db", ["Newer"])
    os.utime(t / "app/sessions/rbc_map_data.db", (1, 1))
    migrate(t / "new", [t / "app/sessions", t / "app/testing/sessions"])
    assert names(t / "new/rbc_map_data.db") == ["Newer"]


def replaces_empty_new_db_with_backup(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    make_db(t / "new/rbc_map_data.db", [])  # created by an earlier 1.0.0 launch
    msg = migrate(t / "new", [t / "app/sessions"])
    assert msg and "Migrated" in msg, msg
    assert names(t / "new/rbc_map_data.db") == ["Alice"]
    assert (t / "new/rbc_map_data.db.pre-migration").is_file()


def keeps_existing_profile_files(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    (t / "app/sessions/profile").mkdir()
    (t / "app/sessions/profile/Cookies").write_text("legacy")
    (t / "app/sessions/profile/Preferences").write_text("legacy-prefs")
    make_db(t / "new/rbc_map_data.db", [])  # earlier 1.0.0 launch
    (t / "new/profile").mkdir()
    (t / "new/profile/Cookies").write_text("current")
    msg = migrate(t / "new", [t / "app/sessions"])
    assert msg and "Migrated" in msg, msg
    assert (t / "new/profile/Cookies").read_text() == "current", "existing profile file overwritten"
    assert (t / "new/profile/Preferences").read_text() == "legacy-prefs", "missing file not copied"
    assert names(t / "new/rbc_map_data.db") == ["Alice"]


def keeps_populated_new_db(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    make_db(t / "new/rbc_map_data.db", ["Bob"])
    assert migrate(t / "new", [t / "app/sessions"]) is None
    assert names(t / "new/rbc_map_data.db") == ["Bob"]


def second_run_is_noop(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    migrate(t / "new", [t / "app/sessions"])
    assert migrate(t / "new", [t / "app/sessions"]) is None


def same_dir_is_ignored(t: Path):
    make_db(t / "s/rbc_map_data.db", ["Alice"])
    assert migrate(t / "s", [t / "s"]) is None


def corrupt_legacy_db_is_skipped(t: Path):
    # A legacy database that is not readable SQLite has no characters to
    # migrate, so it is skipped without copying or settling the marker.
    legacy = t / "app/sessions"
    legacy.mkdir(parents=True)
    (legacy / "rbc_map_data.db").write_bytes(b"not a database" * 100)
    assert migrate(t / "new", [legacy]) is None
    assert not (t / "new").exists()
    assert not (t / "new/.legacy-migration-done").exists()


def failure_leaves_no_partial_db(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    real_copytree = shutil.copytree

    def failing_copytree(*args, **kwargs):
        raise OSError("simulated copy failure")

    shutil.copytree = failing_copytree
    try:
        msg = migrate(t / "new", [t / "app/sessions"])
    finally:
        shutil.copytree = real_copytree
    assert msg and "failed" in msg, msg
    assert not (t / "new/rbc_map_data.db").exists()
    assert not (t / "new/rbc_map_data.db.migrating").exists()
    assert not (t / "new/.legacy-migration-done").exists()


def delete_characters(path: Path):
    conn = sqlite3.connect(path)
    conn.execute("DELETE FROM characters")
    conn.commit()
    conn.close()


def deleted_characters_stay_deleted(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    migrate(t / "new", [t / "app/sessions"])
    delete_characters(t / "new/rbc_map_data.db")
    assert migrate(t / "new", [t / "app/sessions"]) is None
    assert names(t / "new/rbc_map_data.db") == [], "deleted characters came back"


def populated_target_settles_migration(t: Path):
    # Characters created in 1.0.0 before this fix, later all deleted.
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    make_db(t / "new/rbc_map_data.db", ["Bob"])
    assert migrate(t / "new", [t / "app/sessions"]) is None
    assert (t / "new/.legacy-migration-done").is_file()
    delete_characters(t / "new/rbc_map_data.db")
    assert migrate(t / "new", [t / "app/sessions"]) is None
    assert names(t / "new/rbc_map_data.db") == []


def unreadable_target_is_kept(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    (t / "new").mkdir()
    (t / "new/rbc_map_data.db").write_bytes(b"not a database" * 100)
    assert migrate(t / "new", [t / "app/sessions"]) is None
    assert (t / "new/rbc_map_data.db").read_bytes().startswith(b"not a database")


def reserved_characters_in_paths(t: Path):
    legacy = t / "app #1 %20/sessions"
    make_db(legacy / "rbc_map_data.db", ["Alice"])
    msg = migrate(t / "new #2 %3F", [legacy])
    assert msg and "Migrated" in msg, msg
    assert names(t / "new #2 %3F/rbc_map_data.db") == ["Alice"]
    assert not (t / "app").exists(), "URI fragment created a stray file"
    # A populated target under a reserved name must be read correctly and kept.
    make_db(t / "tgt #3/rbc_map_data.db", ["Bob"])
    assert migrate(t / "tgt #3", [legacy]) is None
    assert names(t / "tgt #3/rbc_map_data.db") == ["Bob"]


def empty_legacy_does_not_replace_new_db(t: Path):
    make_db(t / "app/sessions/rbc_map_data.db", [])
    make_db(t / "new/rbc_map_data.db", [])
    assert migrate(t / "new", [t / "app/sessions"]) is None


def newest_empty_legacy_loses_to_older_populated(t: Path):
    # A newer but empty legacy DB must not beat an older populated one,
    # even when the target exists but holds no characters.
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    make_db(t / "app/testing/sessions/rbc_map_data.db", [])
    os.utime(t / "app/sessions/rbc_map_data.db", (1, 1))  # older mtime
    make_db(t / "new/rbc_map_data.db", [])
    msg = migrate(t / "new", [t / "app/sessions", t / "app/testing/sessions"])
    assert msg and "Migrated" in msg, msg
    assert names(t / "new/rbc_map_data.db") == ["Alice"]


def empty_legacy_is_not_migrated(t: Path):
    # With no populated legacy DB there is nothing to copy or settle.
    make_db(t / "app/sessions/rbc_map_data.db", [])
    assert migrate(t / "new", [t / "app/sessions"]) is None
    assert not (t / "new/rbc_map_data.db").exists()
    assert not (t / "new/.legacy-migration-done").exists()


def interrupted_profile_copy_is_repaired(t: Path):
    # A leftover .migrating file from a killed copy is replaced cleanly.
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    (t / "app/sessions/profile").mkdir()
    (t / "app/sessions/profile/Preferences").write_text("x" * 1000)
    (t / "new/profile").mkdir(parents=True)
    (t / "new/profile/Preferences.migrating").write_text("partial")
    msg = migrate(t / "new", [t / "app/sessions"])
    assert msg and "Migrated" in msg, msg
    assert (t / "new/profile/Preferences").read_text() == "x" * 1000
    assert not (t / "new/profile/Preferences.migrating").exists()


def schema_less_target_is_migrated(t: Path):
    # A 0-byte or table-less target is empty, not unreadable.
    make_db(t / "app/sessions/rbc_map_data.db", ["Alice"])
    (t / "new1").mkdir(parents=True)
    (t / "new1/rbc_map_data.db").write_bytes(b"")
    assert "Migrated" in (migrate(t / "new1", [t / "app/sessions"]) or "")
    assert names(t / "new1/rbc_map_data.db") == ["Alice"]
    assert (t / "new1/rbc_map_data.db.pre-migration").stat().st_size == 0
    # Same for a valid SQLite file that simply lacks the characters table.
    other = t / "app2/sessions"
    make_db(other / "rbc_map_data.db", ["Bob"])
    (t / "new2").mkdir(parents=True)
    conn = sqlite3.connect(t / "new2/rbc_map_data.db")
    conn.execute("CREATE TABLE something_else (x)")
    conn.commit()
    conn.close()
    assert "Migrated" in (migrate(t / "new2", [other]) or "")
    assert names(t / "new2/rbc_map_data.db") == ["Bob"]


def windows_install_dirs_are_scanned(t: Path):
    """W1: pre-1.0 Windows installs under LOCALAPPDATA/Program Files are found."""
    src = t / "Program Files" / "RBC-Map" / "sessions"
    local = t / "Local"
    make_db(src / "rbc_map_data.db", ["Carol"])
    saved = {k: os.environ.get(k) for k in ("LOCALAPPDATA", "ProgramFiles", "ProgramFiles(x86)")}
    try:
        os.environ["LOCALAPPDATA"] = str(t / "Local")
        os.environ["ProgramFiles"] = str(t / "Program Files")
        os.environ["ProgramFiles(x86)"] = str(t / "Program Files (x86)")
        # Real detection on Windows; forced nt branch elsewhere.
        dirs = legacy_dirs_fn() if os.name == "nt" else legacy_dirs_fn(is_windows=True)
        # Startup's actual call: the default must include Windows paths only on nt.
        native = legacy_dirs_fn()
        virtual = local / "VirtualStore"
        windows_paths = {
            local / "RBC Community Map" / "sessions",
            local / "RBCCommunityMap" / "sessions",
            t / "Program Files" / "RBC-Map" / "sessions",
            t / "Program Files" / "RBC Community Map" / "sessions",
            t / "Program Files (x86)" / "RBC-Map" / "sessions",
            t / "Program Files (x86)" / "RBC Community Map" / "sessions",
            virtual / "Program Files" / "RBC Community Map" / "sessions",
            virtual / "Program Files" / "RBC-Map" / "sessions",
            virtual / "Program Files (x86)" / "RBC Community Map" / "sessions",
            virtual / "Program Files (x86)" / "RBC-Map" / "sessions",
        }
        assert bool(windows_paths & set(native)) == (os.name == "nt"), native
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    virtual = local / "VirtualStore"
    expected = [
        local / "RBC Community Map" / "sessions",
        local / "RBCCommunityMap" / "sessions",
        t / "Program Files" / "RBC-Map" / "sessions",
        t / "Program Files" / "RBC Community Map" / "sessions",
        t / "Program Files (x86)" / "RBC-Map" / "sessions",
        t / "Program Files (x86)" / "RBC Community Map" / "sessions",
        virtual / "Program Files" / "RBC Community Map" / "sessions",
        virtual / "Program Files" / "RBC-Map" / "sessions",
        virtual / "Program Files (x86)" / "RBC Community Map" / "sessions",
        virtual / "Program Files (x86)" / "RBC-Map" / "sessions",
    ]
    for path in expected:
        assert path in dirs, f"{path} missing from {dirs}"
    msg = migrate(t / "new", dirs)
    assert msg and "Migrated" in msg, msg
    assert names(t / "new/rbc_map_data.db") == ["Carol"]

    # Realistic 0.12-0.13 case: DB under Program Files (x86)\RBC Community Map.
    # migrate() picks the newest populated legacy DB, so give it a later mtime.
    legacy_x86 = t / "Program Files (x86)" / "RBC Community Map" / "sessions"
    make_db(legacy_x86 / "rbc_map_data.db", ["Dave"])
    future = os.stat(src / "rbc_map_data.db").st_mtime + 60
    os.utime(legacy_x86 / "rbc_map_data.db", (future, future))
    msg = migrate(t / "new2", dirs)
    assert msg and "Migrated" in msg, msg
    assert names(t / "new2/rbc_map_data.db") == ["Dave"]
    # Legacy sources are read-only: both source databases stay unchanged.
    assert names(src / "rbc_map_data.db") == ["Carol"], "Program Files source modified"
    assert names(legacy_x86 / "rbc_map_data.db") == ["Dave"], "Program Files (x86) source modified"

    # UAC-virtualized install: VirtualStore competies with the Program Files
    # databases; the newest populated DB wins, as at real startup.
    vsrc = virtual / "Program Files (x86)" / "RBC Community Map" / "sessions"
    make_db(vsrc / "rbc_map_data.db", ["Eve"])
    newest = os.stat(legacy_x86 / "rbc_map_data.db").st_mtime + 60
    os.utime(vsrc / "rbc_map_data.db", (newest, newest))
    assert vsrc in dirs
    msg = migrate(t / "new3", dirs)
    assert msg and "Migrated" in msg, msg
    assert names(t / "new3/rbc_map_data.db") == ["Eve"]
    assert names(vsrc / "rbc_map_data.db") == ["Eve"], "VirtualStore source modified"


def posix_data_permissions_are_private(t: Path):
    """W2: data/sessions dirs are 0700 and DB-family files 0600 on POSIX."""
    if os.name != "posix":
        return
    data_dir = t / "data"
    sessions = data_dir / "sessions"
    sessions.mkdir(parents=True)
    for path in (data_dir, sessions):
        os.chmod(path, 0o755)
    db = sessions / "rbc_map_data.db"
    sqlite3.connect(db).close()
    for suffix in ("-wal", "-shm", ".migrating", ".pre-migration"):
        (sessions / f"rbc_map_data.db{suffix}").write_text("x")
    other = sessions / "cookies.txt"
    other.write_text("x")
    for path in sessions.iterdir():
        os.chmod(path, 0o644)
    secure_perms(data_dir, sessions)
    for path in (data_dir, sessions):
        assert stat.S_IMODE(path.stat().st_mode) == 0o700, oct(stat.S_IMODE(path.stat().st_mode))
    for path in sessions.iterdir():
        if path.name.startswith("rbc_map_data.db"):
            assert stat.S_IMODE(path.stat().st_mode) == 0o600, f"{path.name}: {oct(stat.S_IMODE(path.stat().st_mode))}"
    assert stat.S_IMODE(other.stat().st_mode) == 0o644, "unrelated files untouched"


def removes_old_cookie_store(t: Path):
    sessions = t / "new"
    sessions.mkdir(parents=True)
    for suffix in ("", "-journal", "-wal", "-shm"):
        (sessions / f"Cookies{suffix}").write_text("legacy")
        (sessions / "Network").mkdir(exist_ok=True)
        (sessions / "Network" / f"Cookies{suffix}").write_text("nested legacy")
    remove_cookie_store(sessions)
    assert not list(sessions.glob("Cookies*"))
    assert not list((sessions / "Network").glob("Cookies*"))


for case in [fresh_install_no_legacy, migrates_root_sessions, prefers_newest_legacy,
             replaces_empty_new_db_with_backup, keeps_existing_profile_files,
             keeps_populated_new_db, second_run_is_noop,
             same_dir_is_ignored, corrupt_legacy_db_is_skipped,
             failure_leaves_no_partial_db,
             deleted_characters_stay_deleted, populated_target_settles_migration,
             unreadable_target_is_kept, reserved_characters_in_paths,
             empty_legacy_does_not_replace_new_db,
             newest_empty_legacy_loses_to_older_populated,
             empty_legacy_is_not_migrated,
             interrupted_profile_copy_is_repaired,
             schema_less_target_is_migrated,
             windows_install_dirs_are_scanned,
             posix_data_permissions_are_private,
             removes_old_cookie_store]:
    run(case.__name__, case)
print("all legacy-migration checks passed")
