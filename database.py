from imports import *
from constants import *
from directories import *

def initialize_database():
    """
    Initialize and verify the consolidated database for all data storage.
    Ensures all necessary tables are created if they are missing, and checks each table's columns to verify schema.
    """
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Define the schema for each table
    required_tables = {
        "characters": {
            "sql": '''
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    password TEXT
                )
            ''',
            "columns": {
                "id": "INTEGER",
                "name": "TEXT",
                "password": "TEXT"
            }
        },
        "last_active_character": {
            "sql": '''
                CREATE TABLE IF NOT EXISTS last_active_character (
                    character_id INTEGER,
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
                )
            ''',
            "columns": {
                "character_id": "INTEGER"
            }
        },
        "settings": {
            "sql": '''
                CREATE TABLE IF NOT EXISTS settings (
                    setting_name TEXT PRIMARY KEY,
                    setting_value BLOB
                )
            ''',
            "columns": {
                "setting_name": "TEXT",
                "setting_value": "BLOB"
            }
        },
        "coins": {
            "sql": '''
                CREATE TABLE IF NOT EXISTS coins (
                    character_id INTEGER,
                    pocket INTEGER DEFAULT 0,
                    bank INTEGER DEFAULT 0,
                    FOREIGN KEY (character_id) REFERENCES characters (id) ON DELETE CASCADE
                )
            ''',
            "columns": {
                "character_id": "INTEGER",
                "pocket": "INTEGER",
                "bank": "INTEGER"
            }
        },
        "cookies": {
            "sql": '''
                CREATE TABLE IF NOT EXISTS cookies (
                    name TEXT,
                    domain TEXT,
                    path TEXT,
                    value TEXT,
                    expiration INTEGER,
                    UNIQUE(name, domain, path)
                )
            ''',
            "columns": {
                "name": "TEXT",
                "domain": "TEXT",
                "path": "TEXT",
                "value": "TEXT",
                "expiration": "INTEGER"
            }
        },
        "color_mappings": {
            "sql": '''
                CREATE TABLE IF NOT EXISTS color_mappings (
                    Type TEXT PRIMARY KEY,
                    Color TEXT
                )
            ''',
            "columns": {
                "Type": "TEXT",
                "Color": "TEXT"
            }
        },
        "destinations": {
            "sql": '''
                CREATE TABLE IF NOT EXISTS destinations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER,
                    col INTEGER,
                    row INTEGER,
                    timestamp TEXT,
                    FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
                )
            ''',
            "columns": {
                "id": "INTEGER",
                "character_id": "INTEGER",
                "col": "INTEGER",
                "row": "INTEGER",
                "timestamp": "TEXT"
            }
        },
        "recent_destinations": {
            "sql": '''
                CREATE TABLE IF NOT EXISTS recent_destinations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    character_id INTEGER,
                    col INTEGER,
                    row INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE
                )
            ''',
            "columns": {
                "id": "INTEGER",
                "character_id": "INTEGER",
                "col": "INTEGER",
                "row": "INTEGER",
                "timestamp": "DATETIME"
            }
        }
    }

    # Check and create each table if missing, and verify columns
    for table_name, table_info in required_tables.items():
        # Create table if it does not exist
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            cursor.execute(table_info["sql"])
            logging.info(f"Table '{table_name}' created.")
        else:
            logging.info(f"Table '{table_name}' already exists.")

        # Verify columns in the existing table
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = {col[1]: col[2] for col in cursor.fetchall()}
        for column_name, column_type in table_info["columns"].items():
            if column_name not in existing_columns:
                # Add missing column
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                logging.info(f"Added missing column '{column_name}' to table '{table_name}'")
            elif existing_columns[column_name].upper() != column_type.upper():
                logging.warning(f"Column '{column_name}' in '{table_name}' has type '{existing_columns[column_name]}', expected '{column_type}'")

    # Commit and close the connection
    connection.commit()
    connection.close()
    logging.info("Database verification and table creation with column check completed.")


def connect_to_database():
    """
    Attempt to connect to the MySQL database, starting with the remote server.
    """
    try:
        connection = pymysql.connect(
            host=REMOTE_HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        logging.info("Connected to remote MySQL instance")
        return connection
    except pymysql.MySQLError as err:
        logging.error("Connection to remote MySQL instance failed: %s", err)
        try:
            connection = pymysql.connect(
                host=LOCAL_HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE
            )
            logging.info("Connected to local MySQL instance")
            return connection
        except pymysql.MySQLError as err:
            logging.error("Connection to local MySQL instance failed: %s", err)
            return None


# -----------------------
# Load Data from Database
# -----------------------

def load_data():
    """
    Load various map-related data from the MySQL database.

    This function establishes a database connection and retrieves data for columns, rows,
    banks, taverns, transits, user buildings, color mappings, shops, guilds, and places of interest.
    The data is stored in dictionaries or lists and returned for use in the application.

    Returns:
        tuple: Contains the following data:
            - columns (dict): Mapping of column names to their coordinates.
            - rows (dict): Mapping of row names to their coordinates.
            - banks_coordinates (list): List of tuples containing column and row coordinates for banks.
            - taverns_coordinates (dict): Mapping of tavern names to their coordinates.
            - transits_coordinates (dict): Mapping of transit names to their coordinates.
            - user_buildings_coordinates (dict): Mapping of user building names to their coordinates.
            - color_mappings (dict): Mapping of element types to their QColor values.
            - shops_coordinates (dict): Mapping of shop names to their coordinates.
            - guilds_coordinates (dict): Mapping of guild names to their coordinates.
            - places_of_interest_coordinates (dict): Mapping of place of interest names to their coordinates.
    """
    connection = connect_to_database()
    if not connection:
        sys.exit("Failed to connect to the database.")

    cursor = connection.cursor()

    # Fetch column names and their coordinates
    cursor.execute("SELECT `Name`, `Coordinate` FROM `columns`")
    columns_data = cursor.fetchall()
    columns = {name: int(coordinate) for name, coordinate in columns_data}

    # Fetch row names and their coordinates
    cursor.execute("SELECT `Name`, `Coordinate` FROM `rows`")
    rows_data = cursor.fetchall()
    rows = {name: int(coordinate) for name, coordinate in rows_data}

    # Fetch coordinates from the banks table
    cursor.execute("SELECT `Column`, `Row` FROM banks")
    banks_data = cursor.fetchall()
    banks_coordinates = [
        (col, row, None, None)
        for col, row in banks_data
    ]

    # Fetch taverns and their coordinates
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM taverns")
    taverns_data = cursor.fetchall()
    taverns_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in taverns_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch transits and their coordinates
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM transits")
    transits_data = cursor.fetchall()
    transits_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in transits_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch user buildings and their coordinates
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM userbuildings")
    user_buildings_data = cursor.fetchall()
    user_buildings_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in user_buildings_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch color mappings
    cursor.execute("SELECT `Type`, `Color` FROM color_mappings")
    color_mappings_data = cursor.fetchall()
    color_mappings = {type_: QColor(color) for type_, color in color_mappings_data}

    # Fetch shops and their coordinates
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM shops")
    shops_data = cursor.fetchall()
    shops_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in shops_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch guilds and their coordinates
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM guilds")
    guilds_data = cursor.fetchall()
    guilds_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in guilds_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Fetch places of interest and their coordinates
    cursor.execute("SELECT `Name`, `Column`, `Row` FROM placesofinterest")
    places_of_interest_data = cursor.fetchall()
    places_of_interest_coordinates = {
        name: (columns.get(col) + 1, rows.get(row) + 1)
        for name, col, row in places_of_interest_data
        if columns.get(col) is not None and rows.get(row) is not None
    }

    # Close the database connection after fetching all data
    connection.close()

    return columns, rows, banks_coordinates, taverns_coordinates, transits_coordinates, user_buildings_coordinates, color_mappings, shops_coordinates, guilds_coordinates, places_of_interest_coordinates


# -----------------------
# Tools
# -----------------------
class DatabaseViewer(QMainWindow):
    """
    Main application class for viewing database tables.

    This class provides a graphical interface to display the contents of multiple database tables
    in a tabbed layout, allowing users to easily browse and inspect the data.
    """

    def __init__(self, db_connection):
        """
        Initialize the DatabaseViewer with the provided table data.

        Args:
            db_connection: The established database connection.
        """
        super().__init__()
        self.setWindowTitle('MySQL Database Viewer')
        self.setGeometry(100, 100, 800, 600)

        # Create a QTabWidget to hold the table views
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.db_connection = db_connection
        self.cursor = self.db_connection.cursor()

        # Query to get all table names
        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()

        for (table_name,) in tables:
            column_names, data = self.get_table_data(table_name)
            self.add_table_tab(table_name, column_names, data)

    def get_table_data(self, table_name):
        """
        Fetch the column names and data for a given table.

        Args:
            table_name: The name of the table to fetch data from.

        Returns:
            A tuple containing a list of column names and the data.
        """
        # Use backticks to handle reserved keywords or special characters in table names
        self.cursor.execute(f"SELECT * FROM `{table_name}`")
        data = self.cursor.fetchall()

        column_names = [i[0] for i in self.cursor.description]
        return column_names, data

    def add_table_tab(self, table_name, column_names, data):
        """
        Add a new tab for a table.

        Args:
            table_name: The name of the table.
            column_names: List of column names for the table.
            data: The data to display in the table.
        """
        # Create a QTableWidget to display the table data
        table_widget = QTableWidget()
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(column_names))
        table_widget.setHorizontalHeaderLabels(column_names)

        # Populate the table with data
        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

        # Add the table widget as a new tab
        self.tab_widget.addTab(table_widget, table_name)

    def closeEvent(self, event):
        """
        Ensure the database connection is closed when the application is closed.
        """
        self.cursor.close()
        self.db_connection.close()
        event.accept()
