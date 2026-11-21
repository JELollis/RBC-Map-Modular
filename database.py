from imports import *
from constants import *
from directories import *

def connect_to_database():
    """
    Attempt to connect to the MySQL database, starting with the remote server.

    The function tries to establish a connection to a remote MySQL database first.
    If the remote connection fails, it will then attempt to connect to a local MySQL database.

    Returns:
        pymysql.Connection: Database connection object if successful, None otherwise.
    """
    try:
        # Attempt to connect to the remote MySQL server
        connection = pymysql.connect(
            host=REMOTE_HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        logging.info("Connected to remote MySQL instance")
        return connection
    except pymysql.MySQLError as err:
        # Log the error if the remote connection fails
        logging.error("Connection to remote MySQL instance failed: %s", err)

        # Attempt to connect to the local MySQL server as a fallback
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
            # Log the error if the local connection also fails
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
