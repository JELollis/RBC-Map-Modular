from imports import *
from constants import *
from directories import *

def initialize_cookie_db():
    """
    Initialize the SQLite database for storing cookies.
    """
    connection = sqlite3.connect(COOKIE_DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cookies (
            name TEXT,
            value TEXT,
            domain TEXT,
            path TEXT,
            expiry TEXT,
            secure INTEGER,
            httponly INTEGER
        )
    ''')
    connection.commit()
    connection.close()


def save_cookie_to_db(cookie):
    """
    Save a single cookie to the SQLite database.

    Args:
        cookie (QNetworkCookie): The cookie to save.
    """
    connection = sqlite3.connect(COOKIE_DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO cookies (name, value, domain, path, expiry, secure, httponly)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        cookie.name().data().decode('utf-8'),
        cookie.value().data().decode('utf-8'),
        cookie.domain(),
        cookie.path(),
        cookie.expirationDate().toString() if not cookie.isSessionCookie() else None,
        int(cookie.isSecure()),
        int(cookie.isHttpOnly())
    ))
    connection.commit()
    connection.close()


def load_cookies_from_db():
    """
    Load all cookies from the SQLite database.

    Returns:
        list: A list of QNetworkCookie objects.
    """
    connection = sqlite3.connect(COOKIE_DB_PATH)
    cursor = connection.cursor()
    cursor.execute('SELECT name, value, domain, path, expiry, secure, httponly FROM cookies')
    rows = cursor.fetchall()
    cookies = []
    for row in rows:
        cookie = QNetworkCookie(
            name=row[0].encode('utf-8'),
            value=row[1].encode('utf-8')
        )
        cookie.setDomain(row[2])
        cookie.setPath(row[3])

        if row[4]:
            cookie.setExpirationDate(QDateTime.fromString(row[4]))
        cookie.setSecure(bool(row[5]))
        cookie.setHttpOnly(bool(row[6]))
        cookies.append(cookie)
    connection.close()
    return cookies


def clear_cookie_db():
    """
    Clear all cookies from the SQLite database.
    """
    connection = sqlite3.connect(COOKIE_DB_PATH)
    cursor = connection.cursor()
    cursor.execute('DELETE FROM cookies')
    connection.commit()
    connection.close()
