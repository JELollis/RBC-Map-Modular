from imports import *
from constants import *

class DatabaseViewer(QDialog):
    """
    Graphical interface for viewing SQLite database tables in a tabbed layout.
    """

    def __init__(self, db_connection, parent=None, color_mappings: dict | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle('SQLite Database Viewer')
        self.setWindowIcon(APP_ICON)
        self.setGeometry(100, 100, 800, 600)

        self.db_connection = db_connection
        self.cursor = db_connection.cursor()
        self.color_mappings = color_mappings or {}

        layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in self.cursor.fetchall()]
            for table_name in tables:
                column_names, data = self.get_table_data(table_name)
                self.add_table_tab(table_name, column_names, data)
            logging.debug(f"Loaded {len(tables)} tables into viewer")
        except sqlite3.Error as e:
            logging.error(f"Failed to load tables: {e}")
            QMessageBox.critical(self, "Error", "Failed to load database tables.")

    def get_table_data(self, table_name: str) -> tuple[list[str], list[tuple]]:
        try:
            self.cursor.execute(f"PRAGMA table_info(`{table_name}`)")
            column_names = [col[1] for col in self.cursor.fetchall()]
            self.cursor.execute(f"SELECT * FROM `{table_name}`")
            data = self.cursor.fetchall()
            return column_names, data
        except sqlite3.Error as e:
            logging.error(f"Failed to fetch data for table '{table_name}': {e}")
            return [], []

    def add_table_tab(self, table_name: str, column_names: list[str], data: list[tuple]) -> None:
        table_widget = QTableWidget()
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(column_names))
        table_widget.setHorizontalHeaderLabels(column_names)

        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(value or "")))

        table_widget.resizeColumnsToContents()
        self.tab_widget.addTab(table_widget, table_name)
        logging.debug(f"Added tab for table '{table_name}' with {len(data)} rows")

    def closeEvent(self, event) -> None:
        try:
            self.cursor.close()
            self.db_connection.close()
            logging.debug("Database connection closed")
        except sqlite3.Error as e:
            logging.error(f"Failed to close database connection: {e}")
        event.accept()