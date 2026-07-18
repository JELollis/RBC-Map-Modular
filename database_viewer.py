from imports import *
from constants import *


class DatabaseViewer(QDialog):
    """
    Graphical interface for viewing SQLite database tables in grouped tabbed layout.
    """

    TAB_GROUPS = {
        "App Info": [
            "rows", "columns", "settings", "last_active_character",
            "cookies", "css_profiles", "custom_css", "color_mappings",
            "discord_servers", "powers", "shop_items"
        ],
        "Character Info": [
            "characters", "coins", "destinations"
        ],
        "Building Info": [
            "banks", "placesofinterest", "taverns", "transits",
            "userbuildings", "shops", "guilds"
        ]
    }

    def __init__(self, db_connection, parent=None, color_mappings: dict | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("SQLite Database Viewer")
        self.setWindowIcon(APP_ICON)
        self.setGeometry(100, 100, 800, 600)

        self.db_connection = db_connection
        self.cursor = db_connection.cursor()
        self.color_mappings = color_mappings or {}

        main_layout = QVBoxLayout(self)
        self.parent_tab_widget = QTabWidget()
        main_layout.addWidget(self.parent_tab_widget)

        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = [row[0] for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Failed to load tables: {e}")
            QMessageBox.critical(self, "Error", "Failed to load database tables.")
            return

        # Track added tables
        added_tables = set()

        for group_name, table_list in self.TAB_GROUPS.items():
            child_tab_widget = QTabWidget()
            for table in table_list:
                if table in all_tables:
                    column_names, data = self.get_table_data(table)
                    self.add_table_tab(child_tab_widget, table, column_names, data)
                    added_tables.add(table)
            self.parent_tab_widget.addTab(child_tab_widget, group_name)

        # Add remaining tables to 'Other' tab
        other_tab_widget = QTabWidget()
        remaining_tables = sorted(set(all_tables) - added_tables)
        for table in remaining_tables:
            column_names, data = self.get_table_data(table)
            self.add_table_tab(other_tab_widget, table, column_names, data)
        if remaining_tables:
            self.parent_tab_widget.addTab(other_tab_widget, "Other")

        logging.debug(f"Loaded {len(all_tables)} tables into grouped viewer")

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

    def add_table_tab(self, tab_widget: QTabWidget, table_name: str,
                      column_names: list[str], data: list[tuple]) -> None:
        table_widget = QTableWidget()
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(column_names))
        table_widget.setHorizontalHeaderLabels(column_names)

        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(value or "")))

        table_widget.resizeColumnsToContents()
        tab_widget.addTab(table_widget, table_name)
        logging.debug(f"Added tab for table '{table_name}' with {len(data)} rows")

    def closeEvent(self, event) -> None:
        try:
            self.cursor.close()
            self.db_connection.close()
            logging.debug("Database connection closed")
        except sqlite3.Error as e:
            logging.error(f"Failed to close database connection: {e}")
        event.accept()
