"""
OS credential-store (keyring) helpers and secret migration.

Split out of the monolithic ``main_1.0.4.py``; character passwords and
cookie values live in the OS credential store, with an SQLite fallback
profile (``RBC_MAP_CREDENTIAL_STORAGE=sqlite``).
"""

from imports import *
from constants import *



# -----------------------
# Credential storage
# -----------------------

SERVICE_NAME = "RBC Community Map"

KEYRING_TIMEOUT = 3

_linux_keyring_lock = Lock()

_linux_keyring_disabled = False



class CredentialStoreError(RuntimeError):
    """Raised when the configured operating-system keyring cannot be used."""



def _username(namespace: str, identifier: str) -> str:
    """Return a stable, non-sensitive keyring account name."""
    digest = hashlib.sha256(f"{namespace}\0{identifier}".encode("utf-8")).hexdigest()
    return f"{namespace}:{digest}"



def _probe_secret_service_backend(backend) -> None:
    """Check one Secret Service collection without creating or unlocking it."""
    import secretstorage

    with secretstorage.dbus_init() as bus:
        collection = secretstorage.Collection(
            bus,
            getattr(backend, "preferred_collection", "/org/freedesktop/secrets/aliases/default"),
        )
        if collection.is_locked():
            raise CredentialStoreError("Unlock the Secret Service collection before using saved credentials.")



def _require_unlocked_secret_service(operation_name=None, service=None, account=None) -> None:
    """Check Secret Service before a chained read can fall through to it."""
    backend = keyring.get_keyring()
    if type(backend).__module__ == "keyring.backends.SecretService":
        _probe_secret_service_backend(backend)
        return
    if type(backend).__module__ != "keyring.backends.chainer":
        return
    for candidate in getattr(backend, "backends", ()):
        if type(candidate).__module__ == "keyring.backends.SecretService":
            _probe_secret_service_backend(candidate)
            return
        get_password = getattr(candidate, "get_password", None)
        if get_password is not None and get_password(service, account) is not None:
            return



def _run_keyring(operation, on_timeout=None, preflight=None):
    """Bound Linux keyring calls and quarantine a backend that hangs."""
    global _linux_keyring_disabled
    if not sys.platform.startswith("linux"):
        return operation()

    with _linux_keyring_lock:
        if _linux_keyring_disabled:
            raise CredentialStoreError("OS credential store timed out earlier. Restart the app to retry.")
        result = Future()

        def run():
            try:
                if preflight is None:
                    _require_unlocked_secret_service()
                else:
                    _require_unlocked_secret_service(*preflight)
                result.set_result(operation())
            except Exception as exc:
                result.set_exception(exc)

        Thread(target=run, daemon=True).start()
        try:
            return result.result(timeout=KEYRING_TIMEOUT)
        except TimeoutError as exc:
            if on_timeout is not None and on_timeout():
                return result.result()
            _linux_keyring_disabled = True
            raise CredentialStoreError(
                "OS credential store did not respond. Check Secret Service and restart the app."
            ) from exc



def set_secret(namespace: str, identifier: str, value: str) -> None:
    """Store a secret and verify that the keyring can read it back."""
    if not isinstance(value, str) or not value:
        raise CredentialStoreError("refusing to store an empty or non-text secret")
    account = _username(namespace, identifier)
    abandoned = Event()
    state_lock = RLock()
    committed = False

    def compensate(previous):
        if previous is None:
            keyring.delete_password(SERVICE_NAME, account)
        else:
            keyring.set_password(SERVICE_NAME, account, previous)

    def handle_timeout():
        nonlocal committed
        with state_lock:
            if committed:
                return True
            abandoned.set()
            return False

    def write_and_verify():
        nonlocal committed
        previous = keyring.get_password(SERVICE_NAME, account)
        if abandoned.is_set():
            return
        write_completed = False
        try:
            keyring.set_password(SERVICE_NAME, account, value)
            write_completed = True
            if abandoned.is_set():
                with state_lock:
                    must_compensate = not committed
                if must_compensate:
                    compensate(previous)
                return
            if keyring.get_password(SERVICE_NAME, account) != value:
                raise CredentialStoreError("keyring write verification failed")
            with state_lock:
                if abandoned.is_set():
                    must_compensate = True
                else:
                    committed = True
                    must_compensate = False
            if must_compensate:
                compensate(previous)
        except Exception:
            if write_completed:
                with state_lock:
                    must_compensate = not committed
                    if must_compensate:
                        abandoned.set()
                if must_compensate:
                    compensate(previous)
            raise

    try:
        _run_keyring(
            write_and_verify,
            on_timeout=handle_timeout,
            preflight=("set", SERVICE_NAME, account),
        )
    except CredentialStoreError:
        raise
    except Exception as exc:  # keyring backends expose different exception types
        raise CredentialStoreError(f"OS credential store unavailable: {exc}") from exc



def get_secret(namespace: str, identifier: str) -> str | None:
    """Load a secret, or return ``None`` when no entry exists."""
    try:
        account = _username(namespace, identifier)
        return _run_keyring(
            lambda: keyring.get_password(SERVICE_NAME, account),
            preflight=("get", SERVICE_NAME, account),
        )
    except Exception as exc:
        raise CredentialStoreError(f"OS credential store unavailable: {exc}") from exc



def delete_secret(namespace: str, identifier: str) -> None:
    """Delete a secret when the backend supports deletion of an existing entry."""
    account = _username(namespace, identifier)

    def delete_if_present():
        if keyring.get_password(SERVICE_NAME, account) is not None:
            keyring.delete_password(SERVICE_NAME, account)

    try:
        _run_keyring(
            delete_if_present,
            preflight=("delete", SERVICE_NAME, account),
        )
    except Exception as exc:
        raise CredentialStoreError(f"OS credential store unavailable: {exc}") from exc



CHARACTER_SECRET_NAMESPACE = "character-password"

COOKIE_SECRET_NAMESPACE = "cookie-value"

CREDENTIAL_NAMESPACE_SETTING = "credential_namespace"

CREDENTIAL_NAMESPACE = None

SECRETS_MIGRATED = False


# Match both known sign-in forms without matching account password changes.
LOGIN_FORM_FIELDS = (("iam", "passwd"), ("username", "password"))

LOGIN_FORM_FINDER_JS = f"""
(() => {{
    if (location.origin !== 'https://quiz.ravenblack.net') return null;
    const fieldPairs = {json.dumps(LOGIN_FORM_FIELDS)};
    for (const form of document.querySelectorAll('form')) {{
        for (const [userName, passName] of fieldPairs) {{
            const user = form.querySelector(`input[name="${{userName}}"]`);
            const pass = form.querySelector(`input[name="${{passName}}"]`);
            if (user && pass) return {{form, user, pass}};
        }}
    }}
    return null;
}})()
"""



def ensure_credential_namespace(connection: sqlite3.Connection) -> str:
    """Load or create the persistent namespace owned by this database."""
    global CREDENTIAL_NAMESPACE
    row = connection.execute(
        "SELECT setting_value FROM settings WHERE setting_name = ?",
        (CREDENTIAL_NAMESPACE_SETTING,),
    ).fetchone()
    if row and row[0]:
        CREDENTIAL_NAMESPACE = str(row[0])
        return CREDENTIAL_NAMESPACE

    CREDENTIAL_NAMESPACE = uuid.uuid4().hex
    connection.execute(
        "INSERT INTO settings (setting_name, setting_value) VALUES (?, ?)",
        (CREDENTIAL_NAMESPACE_SETTING, CREDENTIAL_NAMESPACE),
    )
    return CREDENTIAL_NAMESPACE



def _credential_namespace(credential_namespace: str | None = None) -> str:
    """Return the active database namespace, requiring initialization first."""
    namespace = credential_namespace or CREDENTIAL_NAMESPACE
    if not namespace:
        raise CredentialStoreError("credential namespace has not been initialized")
    return namespace



def character_secret_id(character_id: int, credential_namespace: str | None = None) -> str:
    return f"{_credential_namespace(credential_namespace)}:{character_id}"



def cookie_secret_id(cookie_id: int, credential_namespace: str | None = None) -> str:
    return f"{_credential_namespace(credential_namespace)}:{cookie_id}"



def _migrate_legacy_secret(
    secret_namespace: str,
    namespaced_identifier: str,
    legacy_identifier: str,
) -> str | None:
    """Move a pre-namespaced keyring entry after the new key is verified."""
    legacy_value = get_secret(secret_namespace, legacy_identifier)
    if legacy_value is None:
        return None
    set_secret(secret_namespace, namespaced_identifier, legacy_value)
    if get_secret(secret_namespace, namespaced_identifier) != legacy_value:
        raise CredentialStoreError("credential namespace migration verification failed")
    try:
        delete_secret(secret_namespace, legacy_identifier)
    except CredentialStoreError:
        logging.warning("Could not remove legacy credential entry for %s", legacy_identifier)
    return legacy_value



def load_character_secret(connection: sqlite3.Connection, character_id: int, stored_value: str | None) -> str | None:
    """Load a character password and migrate legacy plaintext when possible."""
    global SECRETS_MIGRATED
    if SQLITE_CREDENTIAL_STORAGE:
        return stored_value
    if stored_value:
        try:
            set_secret(CHARACTER_SECRET_NAMESPACE, character_secret_id(character_id), stored_value)
            connection.execute("PRAGMA secure_delete = ON")
            connection.execute("UPDATE characters SET password = NULL WHERE id = ?", (character_id,))
            connection.commit()
            connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            SECRETS_MIGRATED = True
            logging.info("Migrated character %s password to the OS credential store", character_id)
        except CredentialStoreError as exc:
            logging.error("Could not migrate character %s password: %s", character_id, exc)
            return None
        return stored_value

    try:
        identifier = character_secret_id(character_id)
        secret = get_secret(CHARACTER_SECRET_NAMESPACE, identifier)
        if secret is None:
            secret = _migrate_legacy_secret(
                CHARACTER_SECRET_NAMESPACE,
                identifier,
                str(character_id),
            )
        return secret
    except CredentialStoreError as exc:
        logging.error("Could not load character %s password: %s", character_id, exc)
        return None



def store_character_secret(character_id: int, password: str) -> str | None:
    """Return the value to persist in the selected profile's password column."""
    if not password:
        raise CredentialStoreError("refusing to store an empty password")
    if SQLITE_CREDENTIAL_STORAGE:
        return password
    set_secret(CHARACTER_SECRET_NAMESPACE, character_secret_id(character_id), password)
    return None



def load_cookie_secret(
    connection: sqlite3.Connection,
    cookie_id: int,
    name: str,
    domain: str,
    path: str,
    stored_value: str | None,
) -> str | None:
    """Load a cookie value and migrate legacy plaintext when possible."""
    global SECRETS_MIGRATED
    if SQLITE_CREDENTIAL_STORAGE:
        return stored_value
    identifier = cookie_secret_id(cookie_id)
    if stored_value:
        try:
            set_secret(COOKIE_SECRET_NAMESPACE, identifier, stored_value)
            connection.execute("PRAGMA secure_delete = ON")
            connection.execute("UPDATE cookies SET value = NULL WHERE id = ?", (cookie_id,))
            connection.commit()
            connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            SECRETS_MIGRATED = True
            logging.info("Migrated cookie '%s' to the OS credential store", name)
        except CredentialStoreError as exc:
            logging.error("Could not migrate cookie '%s': %s", name, exc)
            return None
        return stored_value

    try:
        secret = get_secret(COOKIE_SECRET_NAMESPACE, identifier)
        if secret is None:
            secret = _migrate_legacy_secret(
                COOKIE_SECRET_NAMESPACE,
                identifier,
                str(cookie_id),
            )
        return secret
    except CredentialStoreError as exc:
        logging.error("Could not load cookie '%s': %s", name, exc)
        return None



def store_cookie_secret(connection: sqlite3.Connection, cookie_id: int, value: str) -> None:
    if not value:
        raise CredentialStoreError("refusing to store an empty cookie")
    if SQLITE_CREDENTIAL_STORAGE:
        connection.execute("UPDATE cookies SET value = ? WHERE id = ?", (value, cookie_id))
    else:
        set_secret(COOKIE_SECRET_NAMESPACE, cookie_secret_id(cookie_id), value)



def vacuum_migrated_secrets(connection: sqlite3.Connection) -> None:
    """Scrub old plaintext pages after a successful credential migration."""
    global SECRETS_MIGRATED
    if not SECRETS_MIGRATED:
        return
    try:
        connection.commit()
        connection.execute("PRAGMA secure_delete = ON")
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        connection.execute("VACUUM")
        SECRETS_MIGRATED = False
        logging.info("Scrubbed migrated credential data from the SQLite file")
    except sqlite3.Error as exc:
        logging.warning("Could not vacuum migrated credential data: %s", exc)
