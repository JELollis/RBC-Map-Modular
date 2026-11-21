from imports import *
from constants import *
from directories import *
from database import *

# -----------------------
# Set Destination Dialog
# -----------------------

class SetDestinationDialog(QDialog):
    """Dialog for setting a destination on the map."""

    def __init__(self, parent: QWidget = None) -> None:
        """
        Initialize the Set Destination dialog.

        Args:
            parent: Reference to RBCCommunityMap.
        """
        super().__init__(parent)
        self.setWindowTitle("Set Destination")
        self.setWindowIcon(APP_ICON)
        self.resize(650, 300)
        self.parent = parent
        logging.debug("SetDestinationDialog initialized")

        main_layout = QVBoxLayout(self)
        dropdown_style = "QComboBox { border: 2px solid #5F6368; padding: 5px; border-radius: 4px; }"

        # Create all dropdowns
        self.recent_destinations_dropdown = QComboBox()
        self.tavern_dropdown = QComboBox()
        self.bank_dropdown = QComboBox()
        self.transit_dropdown = QComboBox()
        self.shop_dropdown = QComboBox()
        self.guild_dropdown = QComboBox()
        self.poi_dropdown = QComboBox()
        self.user_building_dropdown = QComboBox()
        self.columns_dropdown = QComboBox()
        self.rows_dropdown = QComboBox()
        self.directional_dropdown = QComboBox()

        # Apply style and search to all dropdowns
        all_dropdowns = [
            self.recent_destinations_dropdown,
            self.tavern_dropdown, self.bank_dropdown, self.transit_dropdown,
            self.shop_dropdown, self.guild_dropdown, self.poi_dropdown,
            self.user_building_dropdown,
            self.columns_dropdown, self.rows_dropdown, self.directional_dropdown,
        ]

        for dropdown in all_dropdowns:
            dropdown.setStyleSheet(dropdown_style)
            dropdown.setEditable(True)
            dropdown.setInsertPolicy(QComboBox.NoInsert)
            completer = dropdown.completer()
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.setFilterMode(Qt.MatchContains)

        # Populate dropdowns
        self.populate_recent_destinations()
        self._populate_initial_dropdowns()
        self.populate_dropdown(self.columns_dropdown, self.parent.columns.keys() if self.parent else [])
        self.populate_dropdown(self.rows_dropdown, self.parent.rows.keys() if self.parent else [])
        self.populate_dropdown(self.directional_dropdown, ["On", "East", "South", "South East"])

        # Layout: Predefined dropdowns
        dropdown_layout = QFormLayout()
        dropdown_layout.addRow("Recent:", self.recent_destinations_dropdown)
        dropdown_layout.addRow("Tavern:", self.tavern_dropdown)
        dropdown_layout.addRow("Bank:", self.bank_dropdown)
        dropdown_layout.addRow("Transit:", self.transit_dropdown)
        dropdown_layout.addRow("Shop:", self.shop_dropdown)
        dropdown_layout.addRow("Guild:", self.guild_dropdown)
        dropdown_layout.addRow("Place of Interest:", self.poi_dropdown)
        dropdown_layout.addRow("User Building:", self.user_building_dropdown)

        # Layout: Custom XY + direction
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("ABC Street:"))
        custom_layout.addWidget(self.columns_dropdown, 1)
        custom_layout.addWidget(QLabel("123 Street:"))
        custom_layout.addWidget(self.rows_dropdown, 1)
        custom_layout.addWidget(QLabel("Direction:"))
        custom_layout.addWidget(self.directional_dropdown, 1)

        self.columns_dropdown.setMinimumWidth(120)
        self.rows_dropdown.setMinimumWidth(120)
        self.directional_dropdown.setMinimumWidth(120)

        # Layout: Buttons
        button_layout = QGridLayout()
        set_btn = QPushButton("Set")
        set_btn.clicked.connect(self.set_destination)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_destination)
        update_btn = QPushButton("Update Data")
        update_btn.clicked.connect(self.update_comboboxes)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(set_btn, 0, 0)
        button_layout.addWidget(clear_btn, 0, 1)
        button_layout.addWidget(update_btn, 1, 0)
        button_layout.addWidget(cancel_btn, 1, 1)

        # Final layout
        main_layout.addLayout(dropdown_layout)
        main_layout.addLayout(custom_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def _populate_initial_dropdowns(self) -> None:
        """Populate predefined destination dropdowns with initial data."""
        if not self.parent:
            logging.warning("No parent; skipping dropdown population")
            return
        self.populate_dropdown(self.tavern_dropdown, self.parent.taverns_coordinates.keys())
        self.populate_dropdown(self.bank_dropdown,[f"{col} & {row}" for col, row, *_ in self.parent.banks_coordinates.values()])
        self.populate_dropdown(self.transit_dropdown, self.parent.transits_coordinates.keys())
        self.populate_dropdown(self.shop_dropdown, self.parent.shops_coordinates.keys())
        self.populate_dropdown(self.guild_dropdown, self.parent.guilds_coordinates.keys())
        self.populate_dropdown(self.poi_dropdown, self.parent.places_of_interest_coordinates.keys())
        self.populate_dropdown(self.user_building_dropdown, self.parent.user_buildings_coordinates.keys())
        logging.debug("Initial dropdowns populated")

    def populate_recent_destinations(self) -> None:
        """Populate recent destinations dropdown for the selected character."""
        self.recent_destinations_dropdown.clear()
        self.recent_destinations_dropdown.addItem("Select a recent destination")
        if not self.parent or not self.parent.selected_character:
            logging.debug("No parent or character selected; skipping recent destinations")
            return

        character_id = self.parent.selected_character.get('id')
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT col, row FROM recent_destinations WHERE character_id = ? ORDER BY timestamp DESC LIMIT 10",
                    (character_id,)
                )
                for col, row in cursor.fetchall():
                    col_name = next((k for k, v in self.parent.columns.items() if v == col), f"Column {col}")
                    row_name = next((k for k, v in self.parent.rows.items() if v == row), f"Row {row}")
                    building_name = self._get_building_name(cursor, col_name, row_name)
                    display = f"{col_name} & {row_name}" + (f" - {building_name}" if building_name else "")
                    self.recent_destinations_dropdown.addItem(display, (col, row))
                logging.debug(f"Loaded {self.recent_destinations_dropdown.count() - 1} recent destinations")
        except sqlite3.Error as e:
            logging.error(f"Failed to load recent destinations: {e}")

    def _get_building_name(self, cursor: sqlite3.Cursor, col: str, row: str) -> str | None:
        """Get building name at given coordinates."""
        tables = ["banks", "guilds", "placesofinterest", "shops", "taverns", "transits", "userbuildings"]
        for table in tables:
            cursor.execute(f"SELECT Name FROM `{table}` WHERE `Column` = ? AND `Row` = ?", (col, row))
            if result := cursor.fetchone():
                return result[0]
        return None

    def populate_dropdown(self, dropdown: QComboBox, items: list | KeysView) -> None:
        """Populate a dropdown with items."""
        dropdown.clear()
        dropdown.addItem("Select a destination")
        dropdown.addItems([str(item) for item in items])
        logging.debug(f"Populated dropdown with {len(items)} items")

    def update_comboboxes(self) -> None:
        """Update dropdowns with fresh data from scraper and database."""
        self.show_notification("Updating data... Please wait")
        if self.parent and hasattr(self.parent, 'AVITD_scraper'):
            self.parent.AVITD_scraper.scrape_guilds_and_shops()
        try:
            updated_data = load_data(DB_PATH)
            self.parent.columns, self.parent.rows, self.parent.banks_coordinates, \
            self.parent.taverns_coordinates, self.parent.transits_coordinates, \
            self.parent.user_buildings_coordinates, self.parent.color_mappings, \
            self.parent.shops_coordinates, self.parent.guilds_coordinates, \
            self.parent.places_of_interest_coordinates, _ = updated_data[:10]  # Ignore keybind_config
            self._populate_initial_dropdowns()
            self.parent.update_minimap()
            logging.info("Dropdowns updated successfully")
        except Exception as e:
            logging.error(f"Failed to update dropdowns: {e}")
            self.show_error_dialog("Update Failed", str(e))

    def show_notification(self, message: str) -> None:
        """Show a temporary notification."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Notification")
        dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(message, dialog))
        dialog.setFixedSize(300, 100)
        QTimer.singleShot(5000, dialog.accept)
        dialog.exec()
        logging.debug(f"Notification shown: {message}")

    def clear_destination(self) -> None:
        """Clear the current destination for the selected character."""
        if not self.parent or not self.parent.selected_character:
            logging.warning("No character selected to clear destination")
            return
        character_id = self.parent.selected_character['id']
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM destinations WHERE character_id = ?", (character_id,))
                conn.commit()
            self.parent.destination = None
            self.parent.update_minimap()
            logging.info(f"Cleared destination for character {character_id}")
            self.accept()
        except sqlite3.Error as e:
            logging.error(f"Failed to clear destination: {e}")

    def set_destination(self) -> None:
        """Set the selected destination for the current character."""
        if not self.parent or not self.parent.selected_character:
            self.show_error_dialog("No Character", "Please select a character first")
            return
        coords = self.get_selected_destination()
        if not coords:
            self.show_error_dialog("No Destination", "Please select a valid destination")
            return

        character_id = self.parent.selected_character['id']
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO destinations (character_id, col, row, timestamp) VALUES (?, ?, ?, datetime('now'))",
                              (character_id, coords[0], coords[1]))
                if not cursor.execute("SELECT 1 FROM recent_destinations WHERE character_id = ? AND col = ? AND row = ?",
                                     (character_id, coords[0], coords[1])).fetchone():
                    cursor.execute("INSERT INTO recent_destinations (character_id, col, row, timestamp) VALUES (?, ?, ?, datetime('now'))",
                                  (character_id, coords[0], coords[1]))
                conn.commit()
            self.parent.destination = coords
            self.parent.update_minimap()
            logging.info(f"Set destination for character {character_id} to {coords}")
            self.accept()
        except sqlite3.Error as e:
            logging.error(f"Failed to set destination: {e}")

    def get_selected_destination(self) -> tuple[int, int] | None:
        """Retrieve coordinates of the selected destination."""
        if (recent := self.recent_destinations_dropdown.currentText()) != "Select a recent destination":
            return self.recent_destinations_dropdown.currentData()

        dropdowns = [
            (self.tavern_dropdown, self.parent.taverns_coordinates),
            (self.transit_dropdown, self.parent.transits_coordinates),
            (self.shop_dropdown, self.parent.shops_coordinates),
            (self.guild_dropdown, self.parent.guilds_coordinates),
            (self.poi_dropdown, self.parent.places_of_interest_coordinates),
            (self.user_building_dropdown, self.parent.user_buildings_coordinates),
        ]
        for dropdown, data in dropdowns:
            if (sel := dropdown.currentText()) != "Select a destination":
                return data[sel]

        if (bank := self.bank_dropdown.currentText()) != "Select a destination":
            col_name, row_name = bank.split(" & ")
            col = self.parent.columns.get(col_name.strip())
            row = self.parent.rows.get(row_name.strip())
            if col is not None and row is not None:
                return col + 1, row + 1

        col = self.parent.columns.get(self.columns_dropdown.currentText())
        row = self.parent.rows.get(self.rows_dropdown.currentText())
        if col is not None and row is not None:
            return col, row

        logging.debug("No valid destination selected")
        return None

    def set_external_destination(self, col: int, row: int, guild_name: str) -> None:
        """Set a destination externally."""
        self.recent_destinations_dropdown.clear()
        self.recent_destinations_dropdown.addItem(f"{guild_name} - {col}, {row}", (col, row))
        self.recent_destinations_dropdown.setCurrentIndex(0)  # Select the added item
        self.set_destination()
        logging.info(f"External destination set: {guild_name} at ({col}, {row})")

    def show_error_dialog(self, title: str, message: str) -> None:
        """Show an error dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(message, dialog))
        close_btn = QPushButton("Close", dialog)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.setFixedSize(300, 100)
        dialog.exec()
        logging.debug(f"Error dialog shown: {title} - {message}")
