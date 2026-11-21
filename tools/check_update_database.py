"""Regression checks for update-database validation and error propagation."""

import ast
import gc
import logging
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace


from _app import load_app_tree, load_app_source
ROOT = Path(__file__).resolve().parent.parent
MAIN = Path("modular_app")
BUILDING_TABLES = ("banks", "taverns", "transits", "userbuildings", "placesofinterest")


_QT_PROVISION_MARKER = Path("/tmp/.rbc-map-qt-native-provisioned")


def _provision_qt_native_libs() -> bool:
    """Install Qt native libraries on CI runners, at most once per runner."""
    if _QT_PROVISION_MARKER.exists():
        return True
    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(
            ["sudo", "apt-get", "install", "-y",
             "libegl1", "libgl1", "libxkbcommon0", "libfontconfig1"],
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Qt native library provisioning failed: {exc}")
        return False
    _QT_PROVISION_MARKER.touch()
    return True


def _bind_qt_widgets():
    try:
        from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QTabWidget
    except (ImportError, OSError) as exc:
        print(f"Qt import failed: {exc}")
        return None
    return QApplication, QTableWidget, QTableWidgetItem, QTabWidget


_QT_PROBE = (
    "import os; os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen');"
    "from PySide6.QtCore import Qt;"
    "from PySide6.QtWidgets import QApplication;"
    "app = QApplication.instance() or QApplication([])"
)


def _probe_qt() -> bool:
    """Verify Qt imports and the offscreen plugin loads, in a subprocess so
    a platform-plugin abort cannot kill this checker before provisioning."""
    result = subprocess.run(
        [sys.executable, "-c", _QT_PROBE],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Qt offscreen probe failed (exit {result.returncode}): {result.stderr.strip()[-400:]}")
        return False
    return True


def _qt_widgets():
    """Return the Qt widget classes when Qt works; provision and re-verify on CI."""
    widgets = _bind_qt_widgets() if _probe_qt() else None
    if widgets is not None:
        return widgets
    if not os.environ.get("CI") or not _provision_qt_native_libs():
        return None
    widgets = _bind_qt_widgets() if _probe_qt() else None
    return widgets


class FakeRequests:
    class RequestException(Exception):
        pass


class FakeRequestExceptions:
    RequestException = FakeRequests.RequestException


FakeRequests.exceptions = FakeRequestExceptions


class FakeMessageBox:
    critical_calls = []

    @classmethod
    def critical(cls, *args):
        cls.critical_calls.append(args)


def load_update_method():
    tree = load_app_tree()
    methods = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and node.name == "update_database_with_json"
    ]
    assert len(methods) == 1, "expected one update_database_with_json method"
    map_assignments = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "BUILDING_CLASS_MAP"
            for target in node.targets
        )
    ]
    assert len(map_assignments) == 1, "expected one BUILDING_CLASS_MAP assignment"
    building_map = ast.literal_eval(map_assignments[0].value)
    namespace = {
        "sqlite3": sqlite3,
        "datetime": datetime,
        "timezone": timezone,
        "logging": logging,
        "requests": FakeRequests,
        "QMessageBox": FakeMessageBox,
        "DB_PATH": None,
        "BUILDING_CLASS_MAP": building_map,
    }
    exec(compile(ast.Module(body=[methods[0]], type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace["update_database_with_json"], namespace


def load_function(function_name: str):
    tree = load_app_tree()
    methods = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    ]
    assert len(methods) == 1, f"expected one {function_name} method"
    node = methods[0]
    node.decorator_list = []
    namespace = {
        "logging": logging,
        "requests": FakeRequests,
        "QMessageBox": FakeMessageBox,
        "fetch_location_update": lambda **kwargs: {},
        "DB_PATH": None,
        "BUILDING_CLASS_MAP": {},
        "QTabWidget": object,
    }
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace[function_name], namespace


def load_startup_run():
    tree = load_app_tree()
    classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "StartupUpdateWorker"
    ]
    assert len(classes) == 1, "expected one StartupUpdateWorker class"
    methods = [node for node in classes[0].body if isinstance(node, ast.FunctionDef) and node.name == "run"]
    assert len(methods) == 1, "expected one StartupUpdateWorker.run method"
    node = methods[0]
    node.decorator_list = []
    namespace = {
        "logging": logging,
        "requests": FakeRequests,
        "fetch_location_update": lambda **kwargs: {"guilds": {}, "shops": {}},
    }
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace["run"], namespace


def load_transit_helpers():
    tree = load_app_tree()
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RBCCommunityMap")
    wanted = {"_building_display_name", "normalize_building_name", "_upsert_building"}
    methods = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    assert {node.name for node in methods} == wanted
    building_map = next(
        ast.literal_eval(node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "BUILDING_CLASS_MAP" for target in node.targets)
    )
    namespace = {
        "re": __import__("re"),
        "logging": logging,
        "sqlite3": sqlite3,
        "BUILDING_CLASS_MAP": building_map,
    }
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(MAIN), "exec"), namespace)
    return namespace


class FakeBuildingSpan:
    def __init__(self, text: str):
        self.text = text

    def get_text(self, *_args, **_kwargs):
        return self.text

    def get(self, name: str):
        return self.text if name == "title" else None


def transit_names_are_canonical_and_unique(root: Path) -> None:
    namespace = load_transit_helpers()
    display_name = namespace["_building_display_name"]
    normalize_name = namespace["normalize_building_name"]
    upsert = namespace["_upsert_building"]
    fake = SimpleNamespace(_BUILDING_NAME_OVERRIDES={})
    fake.normalize_building_name = normalize_name.__get__(fake)
    assert display_name(fake, "transit", FakeBuildingSpan("Calliope Station")) == "Calliope"
    assert display_name(fake, "transit", FakeBuildingSpan("Melpomene station")) == "Melpomene"

    db = root / "transits.db"
    connection = sqlite3.connect(db)
    try:
        connection.execute(
            'CREATE TABLE transits (ID INTEGER PRIMARY KEY, "Column" TEXT, Row TEXT, Name TEXT)'
        )
        connection.executemany(
            'INSERT INTO transits (ID, "Column", Row, Name) VALUES (?, ?, ?, ?)',
            [(1, "Mongoose", "25th", "Calliope Station"), (2, "Mongoose", "25th", "Calliope")],
        )
        cursor = connection.cursor()
        assert upsert(fake, cursor, "transit", "Calliope", "Mongoose", "25th") == "updated"
        rows = connection.execute(
            'SELECT Name FROM transits WHERE "Column"=? AND Row=?', ("Mongoose", "25th")
        ).fetchall()
        assert rows == [("Calliope",)]
        assert upsert(fake, cursor, "transit", "Clio", "Zelkova", "50th") == "inserted"
        assert connection.execute("SELECT COUNT(*) FROM transits").fetchone()[0] == 2

        for names in (("Calliope Station", "Calliope"), ("Calliope", "Calliope Station")):
            cursor.execute("DELETE FROM transits")
            for name in names:
                upsert(fake, cursor, "transit", name, "Mongoose", "25th")
                assert cursor.execute('SELECT Name, "Column", "Row" FROM transits').fetchall() == [
                    ("Calliope", "Mongoose", "25th")
                ], names
    finally:
        connection.close()


def make_database(path: Path) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE guilds (Name TEXT PRIMARY KEY, "Column" TEXT, "Row" TEXT,
                                 next_update TEXT, last_scraped TEXT);
            CREATE TABLE shops (Name TEXT PRIMARY KEY, "Column" TEXT, "Row" TEXT,
                                next_update TEXT, last_scraped TEXT);
            CREATE TABLE shop_items (shop_name TEXT, item_name TEXT, base_price INTEGER,
                                     charisma_level_1 INTEGER, charisma_level_2 INTEGER, charisma_level_3 INTEGER);
            CREATE TABLE settings (setting_name TEXT PRIMARY KEY, setting_value TEXT);
            CREATE TABLE banks (Name TEXT, "Column" TEXT, "Row" TEXT);
            CREATE TABLE taverns (Name TEXT, "Column" TEXT, "Row" TEXT);
            CREATE TABLE transits (Name TEXT, "Column" TEXT, "Row" TEXT);
            CREATE TABLE userbuildings (Name TEXT, "Column" TEXT, "Row" TEXT);
            CREATE TABLE placesofinterest (Name TEXT, "Column" TEXT, "Row" TEXT);
            """
        )
        for table in BUILDING_TABLES:
            conn.execute(
                f'INSERT INTO {table} (Name, "Column", "Row") VALUES (?, ?, ?)',
                (f"Existing {table}", "A", "1st"),
            )
        conn.commit()
    finally:
        conn.close()


class FakeMap:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def update(self, data):
        method, namespace = load_update_method()
        namespace["DB_PATH"] = self.db_path
        method(self, data)

    def _upsert_building(self, cursor, kind, name, column, row):
        table = {
            "bank": "banks",
            "pub": "taverns",
            "transit": "transits",
            "arena": "placesofinterest",
            "grave": "placesofinterest",
            "lair": "userbuildings",
            "alchemy": "placesofinterest",
        }[kind]
        cursor.execute(
            f'INSERT INTO {table} (Name, "Column", "Row") VALUES (?, ?, ?)',
            (name, column, row),
        )


def shops_remain_available_without_coordinates(root: Path) -> None:
    db = root / "map.db"
    make_database(db)
    with sqlite3.connect(db) as conn:
        conn.executemany(
            "INSERT INTO shop_items VALUES (?, ?, 100, 95, 90, 85)",
            [
                ("Discount Magic", "Vial of Holy Water"),
                ("Discount Magic", "Garlic Spray"),
                ("Discount Magic", "Wooden Stake"),
                ("Known Shop", "Garlic Spray"),
                ("  ", "Garlic Spray"),
                (None, "Garlic Spray"),
            ],
        )
        conn.execute('INSERT INTO shops (Name, "Column", Row) VALUES (?, ?, ?)', ("Known Shop", "B", "2nd"))

    initialize, namespace = load_function("initialize_database")
    namespace.update(
        sqlite3=sqlite3,
        create_tables=lambda _conn: None,
        ensure_credential_namespace=lambda _conn: None,
        migrate_schema=lambda _conn: None,
        insert_initial_data=lambda _conn: None,
    )
    assert initialize(db)
    query = 'SELECT Name, "Column", Row FROM shops ORDER BY Name'
    with sqlite3.connect(db) as conn:
        assert conn.execute(query).fetchall() == [("Discount Magic", "NA", "NA"), ("Known Shop", "B", "2nd")]

    FakeMap(db).update({"shops": {}})
    with sqlite3.connect(db) as conn:
        assert conn.execute(query).fetchall() == [("Discount Magic", "NA", "NA"), ("Known Shop", "NA", "NA")]

        tree = load_app_tree()
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "DamageCalculator")
        method_names = {"_load_valid_shops", "_load_shop_inventory", "_inventory_is_valid"}
        methods = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in method_names]
        weapons = next(
            node for node in tree.body if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "REQUIRED_WEAPONS" for target in node.targets)
        )
        namespace = {"sqlite3": sqlite3, "logging": logging, "Weapon": SimpleNamespace}
        exec(compile(ast.Module(body=[weapons, *methods], type_ignores=[]), str(MAIN), "exec"), namespace)
        options = []
        calculator = SimpleNamespace(
            db_connection=conn,
            shop_dropdown=SimpleNamespace(addItems=options.extend, setCurrentText=lambda _name: None),
        )
        calculator._load_shop_inventory = namespace["_load_shop_inventory"].__get__(calculator)
        calculator._inventory_is_valid = namespace["_inventory_is_valid"].__func__
        namespace["_load_valid_shops"](calculator)
        assert options == ["Discount Magic"]

    FakeMap(db).update({"shops": {"Discount Magic": {"column": "C", "row": "3rd"}}})
    with sqlite3.connect(db) as conn:
        assert conn.execute(query).fetchall() == [("Discount Magic", "C", "3rd"), ("Known Shop", "NA", "NA")]


def shop_viewer_displays_unknown_coordinates_as_blank(_root: Path) -> None:
    widgets = _qt_widgets()
    if widgets is None:
        message = "shop_viewer_displays_unknown_coordinates_as_blank skipped: Qt unavailable"
        if os.environ.get("CI"):
            raise SystemExit(f"{message} (CI requires Qt; install native Qt libraries)")
        print(message)
        return
    QApplication, QTableWidget, QTableWidgetItem, QTabWidget = widgets

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    render, namespace = load_function("add_table_tab")
    namespace.update(QTableWidget=QTableWidget, QTableWidgetItem=QTableWidgetItem)
    tabs = QTabWidget()
    render(
        None, tabs, "shops", ["Name", "Column", "Row"],
        [("Discount Magic", "NA", "NA"), ("Known Shop", "B", "2nd")],
    )
    table = tabs.widget(0)
    assert [
        [table.item(row, col).text() for col in range(3)] for row in range(2)
    ] == [["Discount Magic", "", ""], ["Known Shop", "B", "2nd"]]
    tabs.close()
    app.processEvents()


def count_rows(db_path: Path, table: str) -> int:
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    finally:
        conn.close()


def malformed_payload_is_reported(root: Path) -> None:
    db = root / "map.db"
    make_database(db)
    try:
        FakeMap(db).update({"guilds": []})
    except AttributeError:
        return
    raise AssertionError("malformed guild payload was swallowed")


def manual_update_reports_database_failure(root: Path) -> None:
    method, namespace = load_function("update_data")
    FakeMessageBox.critical_calls.clear()
    namespace["fetch_location_update"] = lambda **kwargs: {"guilds": [], "shops": {}}

    class FailingApp:
        def update_database_with_json(self, data):
            raise sqlite3.DatabaseError("simulated database failure")

        def fetch_and_merge_community_buildings(self, **kwargs):
            raise AssertionError("community merge should not run after database failure")

        def refresh_map_data_from_db(self):
            raise AssertionError("map refresh should not run after database failure")

        def get_locations_last_updated(self):
            return None

    assert method(FailingApp()) is False
    assert FakeMessageBox.critical_calls, "manual failure should show an error"


def dialog_stops_before_success_path() -> None:
    source = load_app_source()
    guard = "if not self.parent.update_data():"
    assert guard in source
    guard_start = source.index(guard)
    step_two = source.index("# Step 2: Reload from DB", guard_start)
    assert "return" in source[guard_start:step_two]


def startup_worker_reports_database_failure(root: Path) -> None:
    method, namespace = load_startup_run()
    events = []

    class Signal:
        def emit(self, *args):
            events.append(args)

    class FailingApp:
        def get_locations_last_updated(self):
            return None

        def update_database_with_json(self, data):
            raise sqlite3.DatabaseError("simulated database failure")

        def fetch_and_merge_community_buildings(self, **kwargs):
            raise AssertionError("community merge should not run after database failure")

    worker = type("Worker", (), {})()
    worker.started = Signal()
    worker.finished = Signal()
    worker.app = FailingApp()
    worker.REQUEST_TIMEOUT = 10
    namespace["fetch_location_update"] = lambda **kwargs: {"guilds": {}, "shops": {}}
    method(worker)
    assert events[-1][0] is False
    assert "Startup update failed" in events[-1][1]


def missing_buildings_preserves_local_data(root: Path) -> None:
    db = root / "map.db"
    make_database(db)
    FakeMap(db).update({"guilds": {}, "shops": {}})
    assert count_rows(db, "banks") == 1


def empty_buildings_preserves_local_data(root: Path) -> None:
    db = root / "map.db"
    make_database(db)
    FakeMap(db).update({"buildings": {}})
    assert count_rows(db, "taverns") == 1


def shop_only_buildings_preserve_local_data(root: Path) -> None:
    db = root / "map.db"
    make_database(db)
    FakeMap(db).update(
        {"buildings": {"shop": {"kind": "shop", "name": "Shop", "column": "B", "row": "2nd"}}}
    )
    assert count_rows(db, "transits") == 1


def mixed_valid_and_malformed_preserves_local_data(root: Path) -> None:
    db = root / "map.db"
    make_database(db)
    FakeMap(db).update(
        {
            "buildings": {
                "valid": {"kind": "bank", "name": "New Bank", "column": "B", "row": "2nd"},
                "malformed": {"kind": "pub", "name": "Missing Row", "column": "C"},
            }
        }
    )
    assert_building_snapshot(db)


def assert_building_snapshot(db: Path, bank=("Existing banks", "A", "1st")) -> None:
    conn = sqlite3.connect(db)
    try:
        for table in BUILDING_TABLES:
            expected = [bank] if table == "banks" else (
                [(f"Existing {table}", "A", "1st")] if bank[0] == "Existing banks" else []
            )
            assert conn.execute(f'SELECT Name, "Column", "Row" FROM {table}').fetchall() == expected, table
    finally:
        conn.close()


def snapshot_handles_non_building_entries(root: Path) -> None:
    bank = {"kind": "bank", "name": "New Bank", "column": "B", "row": "2nd"}
    for label, entry, expected in (
        ("non-object", "invalid", ("Existing banks", "A", "1st")),
        ("unknown-kind", {"kind": "unknown"}, ("New Bank", "B", "2nd")),
        ("shop", {"kind": "shop", "name": "Shop", "column": "C", "row": "3rd"}, ("New Bank", "B", "2nd")),
    ):
        db = root / f"{label}.db"
        make_database(db)
        FakeMap(db).update({"buildings": {"bank": bank, "extra": entry}})
        assert_building_snapshot(db, expected)


def valid_buildings_replace_snapshot(root: Path) -> None:
    db = root / "map.db"
    make_database(db)
    FakeMap(db).update(
        {"buildings": {"new": {"kind": "bank", "name": "New Bank", "column": "B", "row": "2nd"}}}
    )
    assert count_rows(db, "banks") == 1
    conn = sqlite3.connect(db)
    try:
        assert conn.execute("SELECT Name FROM banks").fetchone()[0] == "New Bank"
    finally:
        conn.close()


def run_case(name, case) -> None:
    temp = tempfile.mkdtemp()
    try:
        case(Path(temp))
    finally:
        gc.collect()
        shutil.rmtree(temp, ignore_errors=True)
    print(f"ok   {name}")


for case in (
    shops_remain_available_without_coordinates,
    shop_viewer_displays_unknown_coordinates_as_blank,
    malformed_payload_is_reported,
    manual_update_reports_database_failure,
    startup_worker_reports_database_failure,
    missing_buildings_preserves_local_data,
    empty_buildings_preserves_local_data,
    shop_only_buildings_preserve_local_data,
    mixed_valid_and_malformed_preserves_local_data,
    snapshot_handles_non_building_entries,
    valid_buildings_replace_snapshot,
):
    run_case(case.__name__, case)

run_case("transit_names_are_canonical_and_unique", transit_names_are_canonical_and_unique)

dialog_stops_before_success_path()
print("ok   dialog_stops_before_success_path")

print("all update-database checks passed")
