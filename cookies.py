from imports import *
from constants import *


def save_cookie_to_db(cookie: QNetworkCookie) -> bool:
    """
    Save or update a single cookie in the SQLite database.

    Cookies are uniquely identified by (name, domain, path).
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            name = cookie.name().data().decode("utf-8", errors="replace")
            value = cookie.value().data().decode("utf-8", errors="replace")
            domain = cookie.domain()
            path = cookie.path()

            expiration = (
                cookie.expirationDate().toString(Qt.DateFormat.ISODate)
                if not cookie.isSessionCookie()
                else None
            )

            secure = int(cookie.isSecure())
            httponly = int(cookie.isHttpOnly())

            cursor.execute(
                """
                INSERT OR REPLACE INTO cookies
                    (name, value, domain, path, expiration, secure, httponly)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, value, domain, path, expiration, secure, httponly),
            )

            conn.commit()

            logging.debug(
                "Saved/updated cookie '%s' for domain '%s'",
                name,
                domain,
            )
            return True

    except sqlite3.Error as exc:
        logging.error(
            "Failed to save/update cookie '%s': %s",
            cookie.name().data().decode("utf-8", errors="replace"),
            exc,
        )
        return False

def load_cookies_from_db() -> list[QNetworkCookie]:
    """
    Load all stored cookies from the SQLite database.
    """
    cookies: list[QNetworkCookie] = []

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT name, value, domain, path, expiration, secure, httponly
                FROM cookies
                """
            )

            for name, value, domain, path, expiration, secure, httponly in cursor.fetchall():
                cookie = QNetworkCookie(
                    name.encode("utf-8"),
                    value.encode("utf-8"),
                )
                cookie.setDomain(domain)
                cookie.setPath(path)

                if expiration:
                    cookie.setExpirationDate(
                        QDateTime.fromString(
                            expiration,
                            Qt.DateFormat.ISODate,
                        )
                    )

                cookie.setSecure(bool(secure))
                cookie.setHttpOnly(bool(httponly))
                cookies.append(cookie)

        logging.debug(
            "Loaded %d cookies from database",
            len(cookies),
        )

    except sqlite3.Error as exc:
        logging.error("Failed to load cookies: %s", exc)

    return cookies

def clear_cookie_db() -> bool:
    """
    Remove all cookies from the SQLite database.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cookies")
            conn.commit()

        logging.info("Cleared all cookies from database")
        return True

    except sqlite3.Error as exc:
        logging.error("Failed to clear cookies: %s", exc)
        return False
