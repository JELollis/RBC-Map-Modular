from imports import *
from constants import *
# -----------------------
# Webview Cookie Database
# -----------------------

def save_cookie_to_db(cookie: QNetworkCookie) -> bool:
    """
    Save or update a single cookie in the SQLite database, overwriting if it exists.

    Args:
        cookie (QNetworkCookie): The cookie to save or update.

    Returns:
        bool: True if the cookie was saved/updated successfully, False otherwise.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            name = cookie.name().data().decode('utf-8', errors='replace')
            domain = cookie.domain()
            path = cookie.path()
            value = cookie.value().data().decode('utf-8', errors='replace')
            # noinspection PyUnresolvedReferences
            expiration = cookie.expirationDate().toString(Qt.ISODate) if not cookie.isSessionCookie() else None
            secure = int(cookie.isSecure())
            httponly = int(cookie.isHttpOnly())

            # Use UPSERT (INSERT OR REPLACE) to overwrite existing cookies based on name, domain, and path
            cursor.execute('''
                INSERT OR REPLACE INTO cookies (name, value, domain, path, expiration, secure, httponly)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, value, domain, path, expiration, secure, httponly))

            conn.commit()
            logging.debug(f"Saved/updated cookie: {name} for domain {domain}")
            return True
    except sqlite3.Error as e:
        logging.error(f"Failed to save/update cookie {cookie.name().data()}: {e}")
        return False

def load_cookies_from_db() -> List[QNetworkCookie]:
    """
    Load all cookies from the SQLite database.

    Returns:
        list[QNetworkCookie]: List of QNetworkCookie objects from the database.
    """
    cookies = []
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name, value, domain, path, expiration, secure, httponly FROM cookies')
            for name, value, domain, path, expiration, secure, httponly in cursor.fetchall():
                cookie = QNetworkCookie(
                    name.encode('utf-8'),
                    value.encode('utf-8')
                )
                cookie.setDomain(domain)
                cookie.setPath(path)
                if expiration:
                    # noinspection PyUnresolvedReferences
                    cookie.setExpirationDate(QDateTime.fromString(expiration, Qt.ISODate))
                cookie.setSecure(bool(secure))
                cookie.setHttpOnly(bool(httponly))
                cookies.append(cookie)
            logging.debug(f"Loaded {len(cookies)} cookies from database")
    except sqlite3.Error as e:
        logging.error(f"Failed to load cookies: {e}")
    return cookies

def clear_cookie_db() -> bool:
    """
    Clear all cookies from the SQLite database.

    Returns:
        bool: True if cookies were cleared successfully, False otherwise.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM cookies')
            conn.commit()
            logging.info("Cleared all cookies from database")
            return True
    except sqlite3.Error as e:
        logging.error(f"Failed to clear cookies: {e}")
        return False

