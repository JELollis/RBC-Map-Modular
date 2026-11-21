from imports import *
from constants import *

# -----------------------
# Directory Setup
# -----------------------
def ensure_directories_exist(directories: list[str] = None) -> bool:
    """
    Ensure that the required directories exist, creating them if necessary.
    """
    if directories is None:
        directories = REQUIRED_DIRECTORIES

    success = True
    for directory in directories:
        try:
            # Check existence first to avoid unnecessary syscalls
            if not os.path.isdir(directory):
                os.makedirs(directory, exist_ok=True)
                logging.debug(f"Created directory: {directory}")
            else:
                logging.debug(f"Directory already exists: {directory}")
        except OSError as e:
            logging.error(f"Failed to create directory '{directory}': {e}")
            success = False
    return success


def migrate_schema(conn: sqlite3.Connection) -> None:
    """
    Migrate the database schema to the latest version.

    Handles sequential migrations:
    - v1 -> v2: Fixes custom_css, guilds, and shops tables.
    - v2 -> v3: Adds active_cookie column to characters table.
    """
    cursor = conn.cursor()
    cursor.execute("PRAGMA user_version")
    version = cursor.fetchone()[0]

    if version < 2:
        logging.info("Applying schema migration: v1 → v2 (fixing custom_css, guilds, and shops)")

        try:
            # --- Step 1: Fix custom_css table ---
            cursor.execute("PRAGMA table_info(custom_css)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'profile_name' not in columns:
                logging.info("custom_css missing profile_name column. Rebuilding custom_css table.")
                cursor.execute("ALTER TABLE custom_css RENAME TO custom_css_old")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS custom_css (
                        profile_name TEXT NOT NULL,
                        element TEXT NOT NULL,
                        value TEXT NOT NULL,
                        PRIMARY KEY (profile_name, element),
                        FOREIGN KEY (profile_name) REFERENCES css_profiles(profile_name) ON DELETE CASCADE
                    )
                """)
                try:
                    cursor.execute("""
                        INSERT INTO custom_css (element, value, profile_name)
                        SELECT element, value, 'Default' FROM custom_css_old
                    """)
                    logging.info("Migrated old custom_css data successfully.")
                except sqlite3.Error as e:
                    logging.warning(f"Failed to migrate custom_css data: {e}")
                cursor.execute("DROP TABLE IF EXISTS custom_css_old")

            # --- Step 2: Fix guilds table ---
            cursor.execute("PRAGMA index_list(guilds)")
            indexes = cursor.fetchall()
            unique_names = [index[1] for index in indexes if index[2]]  # index[2] == 1 means UNIQUE
            if not any('Name' in idx for idx in unique_names):
                logging.info("guilds table missing UNIQUE constraint on Name. Rebuilding guilds table.")
                cursor.execute("ALTER TABLE guilds RENAME TO guilds_old")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS guilds (
                        ID INTEGER PRIMARY KEY,
                        Name TEXT NOT NULL UNIQUE,
                        Column TEXT NOT NULL,
                        Row TEXT NOT NULL,
                        next_update TIMESTAMP DEFAULT NULL
                    )
                """)
                try:
                    cursor.execute("""
                        INSERT INTO guilds (ID, Name, Column, Row, next_update)
                        SELECT ID, Name, Column, Row, next_update FROM guilds_old
                    """)
                    logging.info("Migrated old guilds data successfully.")
                except sqlite3.Error as e:
                    logging.warning(f"Failed to migrate guilds data: {e}")
                cursor.execute("DROP TABLE IF EXISTS guilds_old")

            # --- Step 3: Fix shops table ---
            cursor.execute("PRAGMA index_list(shops)")
            shops_indexes = cursor.fetchall()
            shops_has_unique_name = any('Name' in idx for idx in shops_indexes if idx[2])

            if not shops_has_unique_name:
                logging.info("shops table missing UNIQUE constraint on Name. Rebuilding shops table.")
                cursor.execute("ALTER TABLE shops RENAME TO shops_old")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS shops (
                        ID INTEGER PRIMARY KEY,
                        Name TEXT NOT NULL UNIQUE,
                        Column TEXT NOT NULL,
                        Row TEXT NOT NULL,
                        next_update TIMESTAMP DEFAULT NULL
                    )
                """)
                try:
                    cursor.execute("""
                        INSERT INTO shops (ID, Name, Column, Row, next_update)
                        SELECT ID, Name, Column, Row, next_update FROM shops_old
                    """)
                    logging.info("Migrated old shops data successfully.")
                except sqlite3.Error as e:
                    logging.warning(f"Failed to migrate shops data: {e}")
                cursor.execute("DROP TABLE IF EXISTS shops_old")

            # --- Finish migration ---
            conn.execute("PRAGMA user_version = 2")
            conn.commit()
            logging.info("Migration to v2 complete.")

        except sqlite3.Error as e:
            logging.error(f"Migration failed: {e}")
            conn.rollback()
            raise
