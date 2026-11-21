from imports import *
from constants import *
from directories import *

# -----------------------
# Webview Cookie Database
# -----------------------

def save_cookie_to_db(cookie):
    """
    Save a single cookie to the SQLite database.

    Args:
        cookie (QNetworkCookie): The QNetworkCookie object representing the cookie to save.

    This function inserts the cookie's details into the 'cookies' table in the SQLite database.
    """
    connection = sqlite3.connect(DB_PATH)
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
        list: A list of QNetworkCookie objects representing the cookies stored in the database.

    This function retrieves all cookies from the 'cookies' table in the SQLite database
    and converts them into QNetworkCookie objects.
    """
    connection = sqlite3.connect(DB_PATH)
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

    This function deletes all records from the 'cookies' table, effectively clearing all stored cookies.
    """
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('DELETE FROM cookies')
    connection.commit()
    connection.close()
