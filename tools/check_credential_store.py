"""Dependency-light regression checks for the credential-store adapter."""

from __future__ import annotations

import ast
import gc
import hashlib
import logging
import shutil
import sqlite3
import sys
import tempfile
import time
import types
from concurrent.futures import Future, TimeoutError
from threading import Event, Lock, RLock, Thread
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _app import load_app_tree, load_app_source
def load_credential_store():
    tree = load_app_tree()
    names = {
        "SERVICE_NAME",
        "KEYRING_TIMEOUT",
        "_linux_keyring_lock",
        "_linux_keyring_disabled",
        "CredentialStoreError",
        "_username",
        "_probe_secret_service_backend",
        "_require_unlocked_secret_service",
        "_run_keyring",
        "set_secret",
        "get_secret",
        "delete_secret",
    }
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in names for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names:
            nodes.append(node)
    module = types.ModuleType("credential_store")
    module.__dict__.update({
        "hashlib": hashlib,
        "sys": sys,
        "Future": Future,
        "TimeoutError": TimeoutError,
        "Event": Event,
        "Lock": Lock,
        "RLock": RLock,
        "Thread": Thread,
        "keyring": None,
    })
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "modular_app", "exec"), module.__dict__)
    return module


credential_store = load_credential_store()
CredentialStoreError = credential_store.CredentialStoreError
delete_secret = credential_store.delete_secret
get_secret = credential_store.get_secret
set_secret = credential_store.set_secret


class FakeKeyring:
    values: dict[tuple[str, str], str] = {}
    available = True

    @classmethod
    def get_keyring(cls):
        return cls

    @classmethod
    def set_password(cls, service: str, account: str, value: str) -> None:
        if not cls.available:
            raise RuntimeError("simulated unavailable keyring")
        cls.values[(service, account)] = value

    @classmethod
    def get_password(cls, service: str, account: str) -> str | None:
        if not cls.available:
            raise RuntimeError("simulated unavailable keyring")
        return cls.values.get((service, account))

    @classmethod
    def delete_password(cls, service: str, account: str) -> None:
        if not cls.available:
            raise RuntimeError("simulated unavailable keyring")
        del cls.values[(service, account)]


class FakeByteValue:
    def __init__(self, value: str):
        self.value = value

    def data(self) -> bytes:
        return self.value.encode()


class FakeDate:
    def toString(self, *_args) -> str:
        return ""


class FakeCookie:
    def __init__(self, value: str):
        self._value = value

    def name(self) -> FakeByteValue:
        return FakeByteValue("ip")

    def value(self) -> FakeByteValue:
        return FakeByteValue(self._value)

    def domain(self) -> str:
        return "quiz.ravenblack.net"

    def path(self) -> str:
        return "/"

    def isSessionCookie(self) -> bool:
        return True

    def expirationDate(self) -> FakeDate:
        return FakeDate()

    def isSecure(self) -> bool:
        return False

    def isHttpOnly(self) -> bool:
        return False


def load_migration_helpers() -> dict[str, object]:
    tree = load_app_tree()
    names = {
        "CHARACTER_SECRET_NAMESPACE",
        "COOKIE_SECRET_NAMESPACE",
        "CREDENTIAL_NAMESPACE_SETTING",
        "CREDENTIAL_NAMESPACE",
        "SECRETS_MIGRATED",
        "SQLITE_CREDENTIAL_STORAGE",
        "store_character_secret",
        "store_cookie_secret",
        "ensure_credential_namespace",
        "_credential_namespace",
        "_migrate_legacy_secret",
        "character_secret_id",
        "cookie_secret_id",
        "load_character_secret",
        "load_cookie_secret",
        "vacuum_migrated_secrets",
    }
    nodes = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in names for target in node.targets
        ):
            nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in names:
            nodes.append(node)
    namespace = {
        "CredentialStoreError": CredentialStoreError,
        "delete_secret": delete_secret,
        "get_secret": get_secret,
        "set_secret": set_secret,
        "logging": logging,
        "os": __import__("os"),
        "Path": Path,
        "DB_PATH": ":memory:",
        "uuid": __import__("uuid"),
        "sqlite3": sqlite3,
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "modular_app", "exec"), namespace)
    # Keep migration checks in keyring mode even when the developer's shell
    # exports the opt-in SQLite profile setting. The SQLite-specific check
    # enables this explicitly after loading the helpers.
    namespace["SQLITE_CREDENTIAL_STORAGE"] = False
    return namespace


def load_cookie_callback() -> tuple[object, dict[str, object]]:
    tree = load_app_tree()
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RBCCommunityMap")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "on_cookie_added")
    namespace = {
        "sqlite3": sqlite3,
        "DB_PATH": ":memory:",
        "logging": logging,
        "CredentialStoreError": CredentialStoreError,
        "CHARACTER_SECRET_NAMESPACE": "character-password",
        "COOKIE_SECRET_NAMESPACE": "cookie-value",
        "store_cookie_secret": lambda _connection, cookie_id, value: set_secret(
            "cookie-value", namespace["cookie_secret_id"](cookie_id), value
        ),
        "Qt": type("Qt", (), {"DateFormat": type("DateFormat", (), {"ISODate": object()})}),
    }
    helpers = load_migration_helpers()
    helpers["CREDENTIAL_NAMESPACE"] = "test-cookie-namespace"
    namespace.update({"_credential_namespace": helpers["_credential_namespace"]})
    namespace["CREDENTIAL_NAMESPACE"] = helpers["CREDENTIAL_NAMESPACE"]
    namespace["cookie_secret_id"] = helpers["cookie_secret_id"]
    exec(compile(ast.Module(body=[method], type_ignores=[]), "modular_app", "exec"), namespace)
    return namespace["on_cookie_added"], namespace


def check_cookie_callback() -> None:
    callback, namespace = load_cookie_callback()
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = Path(handle.name)
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.executescript(
            """
            CREATE TABLE characters (id INTEGER PRIMARY KEY, name TEXT, active_cookie INTEGER);
            CREATE TABLE cookies (id INTEGER PRIMARY KEY, name TEXT, value TEXT,
                                  domain TEXT, path TEXT, expiration TEXT,
                                  secure INTEGER, httponly INTEGER);
            INSERT INTO characters VALUES (1, 'Alice', NULL);
            INSERT INTO characters VALUES (2, 'Bob', NULL);
            """
        )
        connection.commit()
        connection.close()

        namespace["DB_PATH"] = str(db_path)
        FakeKeyring.values.clear()
        FakeKeyring.available = True
        callback(object(), FakeCookie("Alice#pwA"))
        callback(object(), FakeCookie("Bob#pwB"))

        connection = sqlite3.connect(db_path)
        rows = connection.execute("SELECT id, name FROM cookies ORDER BY id").fetchall()
        assert len(rows) == 2
        linked = connection.execute("SELECT active_cookie FROM characters ORDER BY id").fetchall()
        assert linked == [(rows[0][0],), (rows[1][0],)]
        connection.close()

        callback(object(), FakeCookie("Carol#pwC"))
        callback(object(), FakeCookie("Alice#"))
        connection = sqlite3.connect(db_path)
        assert connection.execute("SELECT COUNT(*) FROM cookies").fetchone()[0] == 2
        assert get_secret("cookie-value", namespace["cookie_secret_id"](rows[0][0])) == "Alice#pwA"
        connection.close()
    finally:
        if connection is not None:
            connection.close()
        gc.collect()
        db_path.unlink(missing_ok=True)


def check_migrations() -> None:
    namespace = load_migration_helpers()
    load_character_secret = namespace["load_character_secret"]
    load_cookie_secret = namespace["load_cookie_secret"]
    vacuum_migrated_secrets = namespace["vacuum_migrated_secrets"]

    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE settings (setting_name TEXT PRIMARY KEY, setting_value BLOB);
        CREATE TABLE characters (id INTEGER PRIMARY KEY, name TEXT, password TEXT);
        CREATE TABLE cookies (id INTEGER PRIMARY KEY, name TEXT, value TEXT,
                              domain TEXT, path TEXT, expiration TEXT,
                              secure INTEGER, httponly INTEGER);
        INSERT INTO characters VALUES (1, 'Alice', 'pwA');
        INSERT INTO cookies VALUES (10, 'ip', 'Alice#pwA', 'quiz.ravenblack.net', '/', NULL, 0, 0);
        INSERT INTO cookies VALUES (11, 'ip', 'Bob#pwB', 'quiz.ravenblack.net', '/', NULL, 0, 0);
        """
    )
    namespace["CREDENTIAL_NAMESPACE"] = namespace["ensure_credential_namespace"](connection)

    FakeKeyring.available = True
    FakeKeyring.values.clear()
    assert load_character_secret(connection, 1, "pwA") == "pwA"
    assert connection.execute("SELECT password FROM characters WHERE id = 1").fetchone()[0] is None

    rows = connection.execute("SELECT id, name, value, domain, path FROM cookies ORDER BY id").fetchall()
    for cookie_id, name, value, domain, path in rows:
        assert load_cookie_secret(connection, cookie_id, name, domain, path, value) == value
    assert get_secret("cookie-value", namespace["cookie_secret_id"](10)) == "Alice#pwA"
    assert get_secret("cookie-value", namespace["cookie_secret_id"](11)) == "Bob#pwB"
    assert connection.execute("SELECT value FROM cookies ORDER BY id").fetchall() == [(None,), (None,)]
    vacuum_migrated_secrets(connection)
    assert namespace["SECRETS_MIGRATED"] is False

    connection.execute("INSERT INTO characters VALUES (2, 'Bob', 'pwB')")
    FakeKeyring.available = False
    assert load_character_secret(connection, 2, "pwB") is None
    assert connection.execute("SELECT password FROM characters WHERE id = 2").fetchone()[0] == "pwB"
    connection.close()


def check_database_secret_namespaces() -> None:
    namespace = load_migration_helpers()
    ensure_namespace = namespace["ensure_credential_namespace"]
    character_id = namespace["character_secret_id"]
    cookie_id = namespace["cookie_secret_id"]
    first = sqlite3.connect(":memory:")
    first.execute("CREATE TABLE settings (setting_name TEXT PRIMARY KEY, setting_value BLOB)")
    first_namespace = ensure_namespace(first)
    first.commit()
    second = sqlite3.connect(":memory:")
    second.execute("CREATE TABLE settings (setting_name TEXT PRIMARY KEY, setting_value BLOB)")
    second_namespace = ensure_namespace(second)
    assert first_namespace != second_namespace
    assert character_id(1, first_namespace) != character_id(1, second_namespace)
    assert cookie_id(1, first_namespace) != cookie_id(1, second_namespace)

    with tempfile.TemporaryDirectory() as temp_dir:
        original = Path(temp_dir) / "original.db"
        copied = Path(temp_dir) / "copied.db"
        connection = sqlite3.connect(original)
        connection.execute("CREATE TABLE settings (setting_name TEXT PRIMARY KEY, setting_value BLOB)")
        original_namespace = ensure_namespace(connection)
        connection.commit()
        connection.close()
        shutil.copy2(original, copied)
        copied_connection = sqlite3.connect(copied)
        assert ensure_namespace(copied_connection) == original_namespace
        copied_connection.close()

    namespace["CREDENTIAL_NAMESPACE"] = "legacy-test"
    legacy_connection = sqlite3.connect(":memory:")
    legacy_connection.execute("CREATE TABLE settings (setting_name TEXT PRIMARY KEY, setting_value BLOB)")
    set_secret("character-password", "7", "legacy-password")
    real_set_secret = namespace["set_secret"]

    def failing_namespaced_write(secret_namespace, identifier, value):
        if identifier != "7":
            raise CredentialStoreError("simulated namespaced write failure")
        return real_set_secret(secret_namespace, identifier, value)

    namespace["set_secret"] = failing_namespaced_write
    assert namespace["load_character_secret"](legacy_connection, 7, None) is None
    assert get_secret("character-password", "7") == "legacy-password"
    namespace["set_secret"] = real_set_secret
    assert namespace["load_character_secret"](legacy_connection, 7, None) == "legacy-password"
    assert get_secret("character-password", character_id(7)) == "legacy-password"
    assert get_secret("character-password", "7") is None

    namespace["CREDENTIAL_NAMESPACE"] = None
    assert namespace["load_character_secret"](legacy_connection, 8, None) is None
    first.close()
    second.close()
    legacy_connection.close()


class FakeTextField:
    def __init__(self, value: str):
        self.value = value

    def text(self) -> str:
        return self.value


class FakeCharacterDialog:
    def __init__(self, name: str, password: str):
        self.name_edit = FakeTextField(name)
        self.password_edit = FakeTextField(password)

    def exec(self) -> bool:
        return True


class FakeMessageBox:
    @staticmethod
    def critical(*_args) -> None:
        return None

    @staticmethod
    def warning(*_args) -> None:
        return None


def load_character_mutation_methods() -> dict[str, object]:
    tree = load_app_tree()
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "RBCCommunityMap")
    wanted = {"firstrun_character_creation", "add_new_character", "modify_character"}
    methods = [node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    namespace = {
        "sqlite3": sqlite3,
        "DB_PATH": ":memory:",
        "logging": logging,
        "CredentialStoreError": CredentialStoreError,
        "CHARACTER_SECRET_NAMESPACE": "character-password",
        "COOKIE_SECRET_NAMESPACE": "cookie-value",
        "QMessageBox": FakeMessageBox,
        "sys": sys,
        "get_secret": get_secret,
        "set_secret": set_secret,
        "delete_secret": delete_secret,
        "SQLITE_CREDENTIAL_STORAGE": False,
        "store_character_secret": lambda _character_id, _password: (_ for _ in ()).throw(
            CredentialStoreError("simulated unavailable keyring")
        ),
        "CharacterDialog": lambda *_args: namespace["dialog"],
        "QTimer": type("QTimer", (), {"singleShot": staticmethod(lambda *_args: None)}),
        "QListWidgetItem": lambda *_args: object(),
        "QUrl": lambda value: value,
    }
    helpers = load_migration_helpers()
    helpers["CREDENTIAL_NAMESPACE"] = "character-test"
    namespace.update({
        "CREDENTIAL_NAMESPACE": helpers["CREDENTIAL_NAMESPACE"],
        "_credential_namespace": helpers["_credential_namespace"],
        "character_secret_id": helpers["character_secret_id"],
        "cookie_secret_id": helpers["cookie_secret_id"],
    })
    exec(compile(ast.Module(body=methods, type_ignores=[]), "modular_app", "exec"), namespace)
    return namespace


def check_failed_character_creates_roll_back() -> None:
    namespace = load_character_mutation_methods()
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = Path(handle.name)
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.executescript(
            """
            CREATE TABLE characters (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, password TEXT);
            CREATE TABLE coins (character_id INTEGER, pocket INTEGER, bank INTEGER);
            """
        )
        connection.commit()
        connection.close()
        namespace["DB_PATH"] = str(db_path)
        namespace["dialog"] = FakeCharacterDialog("Alice", "pwA")
        fake_self = type("FakeWindow", (), {})()
        fake_self.characters = []
        fake_self.character_list = type("FakeList", (), {"addItem": lambda *_args: None})()
        namespace["firstrun_character_creation"](fake_self)
        namespace["dialog"] = FakeCharacterDialog("Bob", "pwB")
        namespace["add_new_character"](fake_self)

        connection = sqlite3.connect(db_path)
        assert connection.execute("SELECT COUNT(*) FROM characters").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM coins").fetchone()[0] == 0
        connection.close()
        connection = None
    finally:
        if connection is not None:
            connection.close()
        gc.collect()
        db_path.unlink(missing_ok=True)


def check_modify_character_atomicity() -> None:
    namespace = load_character_mutation_methods()
    store_calls = []

    def working_store(character_id, password):
        store_calls.append((character_id, password))
        set_secret("character-password", namespace["character_secret_id"](character_id), password)

    namespace["store_character_secret"] = working_store
    real_connect = sqlite3.connect

    def fast_connect(*args, **kwargs):
        kwargs["timeout"] = 0.1
        return real_connect(*args, **kwargs)

    namespace["sqlite3"] = type(
        "SQLiteProxy",
        (),
        {"connect": staticmethod(fast_connect), "Error": sqlite3.Error},
    )
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = Path(handle.name)
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.execute(
            "CREATE TABLE characters (id INTEGER PRIMARY KEY, name TEXT, password TEXT, active_cookie INTEGER)"
        )
        connection.execute("INSERT INTO characters VALUES (1, 'Alice', NULL, NULL)")
        connection.commit()
        connection.close()
        connection = None
        namespace["DB_PATH"] = str(db_path)
        namespace["CREDENTIAL_NAMESPACE"] = "modify-test"
        set_secret("character-password", namespace["character_secret_id"](1), "old-password")

        character = {"id": 1, "name": "Alice", "password": "old-password"}
        item = type("FakeItem", (), {"text": lambda _self: "Alice", "setText": lambda *_args: None})()
        character_list = type("FakeList", (), {"currentItem": lambda _self: item})()
        fake_self = type("FakeWindow", (), {})()
        fake_self.characters = [character]
        fake_self.character_list = character_list

        holder = sqlite3.connect(db_path)
        holder.execute("BEGIN IMMEDIATE")
        namespace["dialog"] = FakeCharacterDialog("Alice-renamed", "new-password")
        namespace["modify_character"](fake_self)
        assert store_calls == []
        assert get_secret("character-password", namespace["character_secret_id"](1)) == "old-password"
        holder.rollback()
        holder.close()

        connection = sqlite3.connect(db_path)
        connection.execute(
            "CREATE TRIGGER reject_character_update BEFORE UPDATE ON characters "
            "BEGIN SELECT RAISE(ABORT, 'simulated update failure'); END"
        )
        connection.commit()
        connection.close()
        namespace["dialog"] = FakeCharacterDialog("Alice-renamed", "new-password")
        namespace["modify_character"](fake_self)
        assert store_calls == [(1, "new-password")]
        assert get_secret("character-password", namespace["character_secret_id"](1)) == "old-password"
        connection = sqlite3.connect(db_path)
        assert connection.execute("SELECT name FROM characters WHERE id = 1").fetchone()[0] == "Alice"
        connection.close()
        connection = None
    finally:
        if connection is not None:
            connection.close()
        gc.collect()
        db_path.unlink(missing_ok=True)


def check_password_change_clears_active_cookie() -> None:
    namespace = load_character_mutation_methods()

    def working_store(character_id, password):
        set_secret("character-password", namespace["character_secret_id"](character_id), password)

    namespace["store_character_secret"] = working_store
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as handle:
        db_path = Path(handle.name)
    connection = None
    try:
        connection = sqlite3.connect(db_path)
        connection.execute(
            "CREATE TABLE characters (id INTEGER PRIMARY KEY, name TEXT, password TEXT, active_cookie INTEGER)"
        )
        connection.execute("INSERT INTO characters VALUES (1, 'Alice', NULL, 7)")
        connection.commit()
        connection.close()
        connection = None

        namespace["DB_PATH"] = str(db_path)
        namespace["CREDENTIAL_NAMESPACE"] = "cookie-clear-test"
        set_secret("character-password", namespace["character_secret_id"](1), "old-password")
        set_secret("cookie-value", namespace["cookie_secret_id"](7), "old-cookie")

        character = {"id": 1, "name": "Alice", "password": "old-password"}
        item = type("FakeItem", (), {"text": lambda _self: "Alice", "setText": lambda *_args: None})()
        character_list = type("FakeList", (), {"currentItem": lambda _self: item})()
        fake_self = type("FakeWindow", (), {})()
        fake_self.characters = [character]
        fake_self.character_list = character_list
        namespace["dialog"] = FakeCharacterDialog("Alice", "new-password")

        namespace["modify_character"](fake_self)
        connection = sqlite3.connect(db_path)
        assert connection.execute("SELECT active_cookie FROM characters WHERE id = 1").fetchone() == (None,)
        assert get_secret("cookie-value", namespace["cookie_secret_id"](7)) is None
        connection.close()
        connection = None
    finally:
        if connection is not None:
            connection.close()
        gc.collect()
        db_path.unlink(missing_ok=True)


def check_sqlite_profile_secrets() -> None:
    helpers = load_migration_helpers()
    helpers["SQLITE_CREDENTIAL_STORAGE"] = True

    def unexpected_keyring_call(*_args):
        raise AssertionError("the SQLite profile must not call the keyring")

    helpers.update(get_secret=unexpected_keyring_call, set_secret=unexpected_keyring_call)
    with sqlite3.connect(":memory:") as db:
        db.executescript(
            "CREATE TABLE characters (id INTEGER PRIMARY KEY, password TEXT);"
            "CREATE TABLE cookies (id INTEGER PRIMARY KEY, value TEXT);"
            "INSERT INTO characters VALUES (1, NULL);"
            "INSERT INTO cookies VALUES (1, NULL);"
        )
        password = helpers["store_character_secret"](1, "saved-password")
        db.execute("UPDATE characters SET password = ? WHERE id = 1", (password,))
        helpers["store_cookie_secret"](db, 1, "saved-cookie")
        assert helpers["load_character_secret"](db, 1, password) == "saved-password"
        value = db.execute("SELECT value FROM cookies WHERE id = 1").fetchone()[0]
        assert helpers["load_cookie_secret"](db, 1, "ip", "", "/", value) == "saved-cookie"


def check_hung_keyring_stops_blocking() -> None:
    release = Event()
    finished = Event()
    calls = []

    def hang(*_args):
        calls.append("get")
        try:
            assert release.wait(5)
        finally:
            finished.set()

    with (
        patch.object(credential_store.sys, "platform", "linux"),
        patch.object(credential_store, "KEYRING_TIMEOUT", 0.2),
        patch.object(credential_store, "_linux_keyring_disabled", False),
        patch.object(credential_store.keyring, "get_password", side_effect=hang),
    ):
        try:
            for expected in ("did not respond", "timed out earlier"):
                try:
                    get_secret("test", "timeout")
                except CredentialStoreError as exc:
                    assert expected in str(exc)
                else:
                    raise AssertionError("a hung backend must fail")
            assert calls == ["get"], "a timed-out backend must not be called again"
        finally:
            release.set()
            assert finished.wait(2)


def check_timed_out_write_is_reverted() -> None:
    release = Event()
    finished = Event()
    account = credential_store._username("test", "late-write")
    original_set_password = FakeKeyring.set_password

    def delayed_set_password(service: str, key: str, value: str) -> None:
        if value == "new-secret":
            assert release.wait(2)
        original_set_password(service, key, value)
        if value == "old-secret":
            finished.set()

    FakeKeyring.values[(credential_store.SERVICE_NAME, account)] = "old-secret"
    with (
        patch.object(credential_store.sys, "platform", "linux"),
        patch.object(credential_store, "KEYRING_TIMEOUT", 0.2),
        patch.object(credential_store, "_linux_keyring_disabled", False),
        patch.object(FakeKeyring, "set_password", side_effect=delayed_set_password),
    ):
        try:
            set_secret("test", "late-write", "new-secret")
        except CredentialStoreError as exc:
            assert "did not respond" in str(exc)
        else:
            raise AssertionError("a delayed write must time out")

        release.set()
        assert finished.wait(2)
        assert FakeKeyring.values[(credential_store.SERVICE_NAME, account)] == "old-secret"


def check_verify_timeout_is_reverted() -> None:
    release = Event()
    verify_started = Event()
    restored = Event()
    account = credential_store._username("test", "verify-timeout")
    original_set_password = FakeKeyring.set_password
    calls = 0

    def blocking_verify(service: str, key: str) -> str | None:
        nonlocal calls
        calls += 1
        if calls == 2:
            verify_started.set()
            assert release.wait(2)
        return FakeKeyring.values.get((service, key))

    def tracking_set_password(service: str, key: str, value: str) -> None:
        original_set_password(service, key, value)
        if value == "old-secret":
            restored.set()

    FakeKeyring.values[(credential_store.SERVICE_NAME, account)] = "old-secret"
    with (
        patch.object(credential_store.sys, "platform", "linux"),
        patch.object(credential_store, "KEYRING_TIMEOUT", 0.2),
        patch.object(credential_store, "_linux_keyring_disabled", False),
        patch.object(FakeKeyring, "get_password", side_effect=blocking_verify),
        patch.object(FakeKeyring, "set_password", side_effect=tracking_set_password),
    ):
        try:
            set_secret("test", "verify-timeout", "new-secret")
        except CredentialStoreError as exc:
            assert "did not respond" in str(exc)
        else:
            raise AssertionError("a blocked verification read must time out")

        assert verify_started.is_set()
        release.set()
        assert restored.wait(2)
        assert FakeKeyring.values[(credential_store.SERVICE_NAME, account)] == "old-secret"


def check_timed_out_new_secret_is_deleted() -> None:
    release = Event()
    deleted = Event()
    account = credential_store._username("test", "new-secret")
    original_set_password = FakeKeyring.set_password
    original_delete_password = FakeKeyring.delete_password

    def delayed_set_password(service: str, key: str, value: str) -> None:
        if value == "new-secret":
            assert release.wait(2)
        original_set_password(service, key, value)

    def tracking_delete_password(service: str, key: str) -> None:
        original_delete_password(service, key)
        deleted.set()

    FakeKeyring.values.pop((credential_store.SERVICE_NAME, account), None)
    with (
        patch.object(credential_store.sys, "platform", "linux"),
        patch.object(credential_store, "KEYRING_TIMEOUT", 0.2),
        patch.object(credential_store, "_linux_keyring_disabled", False),
        patch.object(FakeKeyring, "set_password", side_effect=delayed_set_password),
        patch.object(FakeKeyring, "delete_password", side_effect=tracking_delete_password),
    ):
        try:
            set_secret("test", "new-secret", "new-secret")
        except CredentialStoreError as exc:
            assert "did not respond" in str(exc)
        else:
            raise AssertionError("a delayed new secret must time out")

        release.set()
        assert deleted.wait(2)
        assert (credential_store.SERVICE_NAME, account) not in FakeKeyring.values


def check_chained_secret_service_probe() -> None:
    locked = True
    operation_calls = []

    SecretServiceBackend = type("SecretServiceBackend", (), {"preferred_collection": "/default"})
    SecretServiceBackend.__module__ = "keyring.backends.SecretService"
    ChainerBackend = type("ChainerBackend", (), {})
    ChainerBackend.__module__ = "keyring.backends.chainer"
    chainer = ChainerBackend()
    chainer.backends = [SecretServiceBackend()]

    class BusContext:
        def __enter__(self):
            return object()

        def __exit__(self, *_args):
            return False

    class Collection:
        def __init__(self, _bus, _path):
            pass

        def is_locked(self):
            return locked

    secretstorage = types.ModuleType("secretstorage")
    secretstorage.dbus_init = lambda: BusContext()
    secretstorage.Collection = Collection

    with (
        patch.object(credential_store.sys, "platform", "linux"),
        patch.object(credential_store, "KEYRING_TIMEOUT", 0.2),
        patch.object(credential_store, "_linux_keyring_disabled", False),
        patch.object(credential_store.keyring, "get_keyring", return_value=chainer),
        patch.dict(sys.modules, {"secretstorage": secretstorage}),
    ):
        try:
            credential_store._run_keyring(
                lambda: operation_calls.append("called"),
                preflight=("get", credential_store.SERVICE_NAME, "account"),
            )
        except CredentialStoreError as exc:
            assert "Unlock the Secret Service collection" in str(exc)
        else:
            raise AssertionError("a locked chained Secret Service must fail early")
        assert operation_calls == []

        chainer.backends = [object()]
        assert credential_store._run_keyring(
            lambda: "ok",
            preflight=("get", credential_store.SERVICE_NAME, "account"),
        ) == "ok"

        KWalletBackend = type(
            "KWalletBackend",
            (),
            {
                "get_password": lambda _self, _service, _account: "existing",
                "set_password": lambda _self, _service, _account, _value: None,
            },
        )
        KWalletBackend.__module__ = "keyring.backends.kwallet"
        chainer.backends = [KWalletBackend(), SecretServiceBackend()]
        operation_calls.clear()
        assert credential_store._run_keyring(
            lambda: operation_calls.append("primary-read"),
            preflight=("get", credential_store.SERVICE_NAME, "account"),
        ) is None
        assert operation_calls == ["primary-read"]
        operation_calls.clear()
        assert credential_store._run_keyring(
            lambda: operation_calls.append("primary-write"),
            preflight=("set", credential_store.SERVICE_NAME, "account"),
        ) is None
        assert operation_calls == ["primary-write"]

        KWalletBackend.get_password = lambda _self, _service, _account: None
        operation_calls.clear()
        try:
            credential_store._run_keyring(
                lambda: operation_calls.append(
                    credential_store.keyring.get_password(
                        credential_store.SERVICE_NAME, "account"
                    )
                ),
                preflight=("get", credential_store.SERVICE_NAME, "account"),
            )
        except CredentialStoreError as exc:
            assert "Unlock the Secret Service collection" in str(exc)
        else:
            raise AssertionError("a locked fallback Secret Service must fail early")
        assert operation_calls == []


def check_compensation_does_not_extend_timeout() -> None:
    release = Event()
    account = credential_store._username("test", "blocked-restore")
    original_set_password = FakeKeyring.set_password
    calls = 0

    def failing_verify(service: str, key: str) -> str | None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("simulated verify failure")
        return FakeKeyring.values.get((service, key))

    def blocked_restore(service: str, key: str, value: str) -> None:
        if value == "old-secret":
            assert release.wait(2)
        original_set_password(service, key, value)

    FakeKeyring.values[(credential_store.SERVICE_NAME, account)] = "old-secret"
    with (
        patch.object(credential_store.sys, "platform", "linux"),
        patch.object(credential_store, "KEYRING_TIMEOUT", 0.2),
        patch.object(credential_store, "_linux_keyring_disabled", False),
        patch.object(FakeKeyring, "get_password", side_effect=failing_verify),
        patch.object(FakeKeyring, "set_password", side_effect=blocked_restore),
    ):
        started = time.monotonic()
        try:
            set_secret("test", "blocked-restore", "new-secret")
        except CredentialStoreError:
            elapsed = time.monotonic() - started
        else:
            raise AssertionError("a failed verification must raise")
        assert elapsed < 1, "a blocked compensation must not extend the caller timeout"
        release.set()


def check_committed_write_is_reported_successfully() -> None:
    release = Event()
    verify_started = Event()
    commit_ready = Event()
    account = credential_store._username("test", "committed")
    original_rlock = RLock
    calls = 0

    class TrackingLock:
        def __init__(self):
            self._lock = original_rlock()

        def __enter__(self):
            self._lock.acquire()
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self._lock.release()
            commit_ready.set()
            return False

    def delayed_verify(service: str, key: str) -> str | None:
        nonlocal calls
        calls += 1
        if calls == 2:
            verify_started.set()
            assert release.wait(2)
        return FakeKeyring.values.get((service, key))

    FakeKeyring.values[(credential_store.SERVICE_NAME, account)] = "old-secret"
    real_run_keyring = credential_store._run_keyring

    def gate_timeout(operation, on_timeout=None, preflight=None):
        def delayed_timeout():
            assert commit_ready.wait(2)
            return on_timeout() if on_timeout is not None else False

        return real_run_keyring(operation, on_timeout=delayed_timeout, preflight=preflight)

    with (
        patch.object(credential_store.sys, "platform", "linux"),
        patch.object(credential_store, "KEYRING_TIMEOUT", 0.2),
        patch.object(credential_store, "_linux_keyring_disabled", False),
        patch.object(credential_store, "RLock", TrackingLock),
        patch.object(credential_store, "_run_keyring", side_effect=gate_timeout),
        patch.object(FakeKeyring, "get_password", side_effect=delayed_verify),
    ):
        result = []
        error = []

        def call_set_secret():
            try:
                set_secret("test", "committed", "new-secret")
                result.append("success")
            except Exception as exc:
                error.append(exc)

        caller = Thread(target=call_set_secret)
        caller.start()
        assert verify_started.wait(2)
        time.sleep(0.3)
        release.set()
        caller.join(2)
        assert not caller.is_alive()
        assert result == ["success"]
        assert error == []
        assert credential_store._linux_keyring_disabled is False


def check_verify_mismatch_restores_previous() -> None:
    account = credential_store._username("test", "mismatch")
    FakeKeyring.values[(credential_store.SERVICE_NAME, account)] = "old-secret"
    with (
        patch.object(credential_store.sys, "platform", "linux"),
        patch.object(credential_store, "KEYRING_TIMEOUT", 0.2),
        patch.object(credential_store, "_linux_keyring_disabled", False),
        patch.object(FakeKeyring, "get_password", side_effect=["old-secret", "wrong-secret"]),
    ):
        try:
            set_secret("test", "mismatch", "new-secret")
        except CredentialStoreError as exc:
            assert "verification failed" in str(exc)
        else:
            raise AssertionError("a mismatched verification must raise")
        assert FakeKeyring.values[(credential_store.SERVICE_NAME, account)] == "old-secret"


def main() -> int:
    original_keyring = credential_store.keyring
    credential_store.keyring = FakeKeyring
    try:
        set_secret("test", "account", "secret")
        assert get_secret("test", "account") == "secret"
        delete_secret("test", "account")
        assert get_secret("test", "account") is None
        try:
            set_secret("test", "account", "")
        except CredentialStoreError:
            pass
        else:
            raise AssertionError("empty secrets must be rejected")
        check_migrations()
        check_cookie_callback()
        check_database_secret_namespaces()
        check_failed_character_creates_roll_back()
        check_modify_character_atomicity()
        check_password_change_clears_active_cookie()
        check_sqlite_profile_secrets()
        check_timed_out_write_is_reverted()
        check_verify_timeout_is_reverted()
        check_timed_out_new_secret_is_deleted()
        check_chained_secret_service_probe()
        check_compensation_does_not_extend_timeout()
        check_committed_write_is_reported_successfully()
        check_verify_mismatch_restores_previous()
        check_hung_keyring_stops_blocking()
    finally:
        FakeKeyring.available = True
        credential_store.keyring = original_keyring
    print("credential-store checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
