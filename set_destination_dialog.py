from imports import *
from constants import *

class SetDestinationDialog(QDialog):
    """Dialog for setting a destination on the map."""

    def __init__(self, parent: QWidget = None, color_mappings: dict | None = None) -> None:
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
        self.color_mappings = color_mappings or {}

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
            self.user_building_dropdown, self.columns_dropdown, self.rows_dropdown,
            self.directional_dropdown,
        ]

        for dropdown in all_dropdowns:
            dropdown.setStyleSheet(dropdown_style)
            dropdown.setEditable(True)
            # noinspection PyUnresolvedReferences
            dropdown.setInsertPolicy(QComboBox.NoInsert)
            completer = dropdown.completer()
            # noinspection PyUnresolvedReferences
            completer.setCompletionMode(QCompleter.PopupCompletion)
            # noinspection PyUnresolvedReferences
            completer.setFilterMode(Qt.MatchContains)

        # Populate dropdowns
        self.populate_recent_destinations()
        self._populate_initial_dropdowns()

        if self.parent:
            parent = cast("MainWindowType", self.parent)
            self.populate_dropdown(self.columns_dropdown, list(parent.columns.keys()))
            self.populate_dropdown(self.rows_dropdown, list(parent.rows.keys()))
        else:
            self.populate_dropdown(self.columns_dropdown, [])
            self.populate_dropdown(self.rows_dropdown, [])

        self.populate_dropdown(self.directional_dropdown, ["On", "East", "South", "South East"])

        # Layout: Dropdowns
        dropdown_layout = QFormLayout()
        dropdown_layout.addRow("Recent:", self.recent_destinations_dropdown)
        dropdown_layout.addRow("Tavern:", self.tavern_dropdown)
        dropdown_layout.addRow("Bank:", self.bank_dropdown)
        dropdown_layout.addRow("Transit:", self.transit_dropdown)
        dropdown_layout.addRow("Shop:", self.shop_dropdown)
        dropdown_layout.addRow("Guild:", self.guild_dropdown)
        dropdown_layout.addRow("Place of Interest:", self.poi_dropdown)
        dropdown_layout.addRow("User Building:", self.user_building_dropdown)

        # Layout: XY + Direction
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
        clear_btn = QPushButton("Clear")
        update_btn = QPushButton("Update Data")
        cancel_btn = QPushButton("Cancel")
        button_layout.addWidget(set_btn, 0, 0)
        button_layout.addWidget(clear_btn, 0, 1)
        button_layout.addWidget(update_btn, 1, 0)
        button_layout.addWidget(cancel_btn, 1, 1)

        set_btn.clicked.connect(lambda: self.set_destination())
        clear_btn.clicked.connect(self.clear_destination)
        update_btn.clicked.connect(self.update_combo_boxes)
        cancel_btn.clicked.connect(self.reject)

        # Countdown labels
        self.guildCountdownLabel = QLabel("Guilds move at ...")
        self.shopCountdownLabel = QLabel("Shops move at ...")

        # Final layout
        main_layout.addLayout(dropdown_layout)
        main_layout.addLayout(custom_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.guildCountdownLabel)
        main_layout.addWidget(self.shopCountdownLabel)
        self.setLayout(main_layout)

        # Apply theme
        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

        # Countdown logic
        self.load_next_move_times()
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown_labels)
        self.countdown_timer.start(1000)

    def _populate_initial_dropdowns(self) -> None:
        """Populate predefined destination dropdowns with initial data."""
        if not self.parent:
            logging.warning("No parent; skipping dropdown population")
            return

        parent = cast("MainWindowType", self.parent)

        self.populate_dropdown(self.tavern_dropdown, list(parent.taverns_coordinates.keys()))
        self.populate_dropdown(self.bank_dropdown, [f"{col} & {row}" for col, row, *_ in parent.banks_coordinates.values()])
        self.populate_dropdown(self.transit_dropdown, list(parent.transits_coordinates.keys()))
        self.populate_dropdown(self.shop_dropdown, list(parent.shops_coordinates.keys()))
        self.populate_dropdown(self.guild_dropdown, list(parent.guilds_coordinates.keys()))
        self.populate_dropdown(self.poi_dropdown, list(parent.places_of_interest_coordinates.keys()))
        self.populate_dropdown(self.user_building_dropdown, list(parent.user_buildings_coordinates.keys()))

        logging.debug("Initial dropdowns populated")

    def populate_recent_destinations(self) -> None:
        """Populate recent destinations dropdown for the selected character."""
        self.recent_destinations_dropdown.clear()
        self.recent_destinations_dropdown.addItem("Select a recent destination")

        if not self.parent:
            logging.debug("No parent; skipping recent destinations")
            return

        parent = cast("MainWindowType", self.parent)

        if not parent.selected_character:
            logging.debug("No character selected; skipping recent destinations")
            return

        character_id = parent.selected_character.get('id')

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT col, row FROM recent_destinations WHERE character_id = ? ORDER BY timestamp DESC LIMIT 10",
                    (character_id,)
                )

                # Create inverse mappings (coord → name)
                inverse_columns = {v: k for k, v in parent.columns.items()}
                inverse_rows = {v: k for k, v in parent.rows.items()}

                for col, row in cursor.fetchall():
                    # Round down to nearest even coordinate for label mapping
                    even_col = col - (col % 2)
                    even_row = row - (row % 2)

                    col_name = inverse_columns.get(even_col, f"Column {even_col}")
                    row_name = inverse_rows.get(even_row, f"Row {even_row}")
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

    def update_combo_boxes(self):
        logging.info("Updating combo boxes.")
        self.show_notification("Updating Shop and Guild Data. Please wait...")

        try:
            if not self.parent:
                logging.warning("No parent found; cannot update combo boxes.")
                return

            parent = cast("MainWindowType", self.parent)

            # Run scraper to update shops and guilds
            parent.AVITD_scraper.scrape_guilds_and_shops()

            # Update only shops and guilds coordinates from database
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                # Fetch columns and rows for coordinate conversion
                cursor.execute("SELECT `Name`, `Coordinate` FROM `columns`")
                columns = {row[0]: row[1] for row in cursor.fetchall()}
                cursor.execute("SELECT `Name`, `Coordinate` FROM `rows`")
                rows = {row[0]: row[1] for row in cursor.fetchall()}

                def to_coords(col_name: str, row_name: str) -> tuple[int, int]:
                    return (columns.get(col_name, 0) + 1, rows.get(row_name, 0) + 1)

                # Update shops_coordinates
                cursor.execute("SELECT Name, `Column`, `Row` FROM shops")
                parent.shops_coordinates = {
                    name: to_coords(col, row)
                    for name, col, row in cursor.fetchall()
                    if col != "NA" and row != "NA"
                }

                # Update guilds_coordinates
                cursor.execute("SELECT Name, `Column`, `Row` FROM guilds")
                parent.guilds_coordinates = {
                    name: to_coords(col, row)
                    for name, col, row in cursor.fetchall()
                    if col != "NA" and row != "NA"
                }

            # Populate dropdowns
            self.populate_dropdown(self.tavern_dropdown, parent.taverns_coordinates.keys())
            self.populate_dropdown(self.bank_dropdown, parent.banks_coordinates.keys())
            self.populate_dropdown(self.transit_dropdown, parent.transits_coordinates.keys())
            self.populate_dropdown(self.shop_dropdown, parent.shops_coordinates.keys())
            self.populate_dropdown(self.guild_dropdown, parent.guilds_coordinates.keys())
            self.populate_dropdown(self.poi_dropdown, parent.places_of_interest_coordinates.keys())
            self.populate_dropdown(self.user_building_dropdown, parent.user_buildings_coordinates.keys())

            parent.update_minimap()
            logging.info("Combo boxes updated successfully.")

        except Exception as e:
            logging.error(f"Failed to update Combo boxes: {e}")
            self.show_error_dialog("Update Failed", str(e))

    def show_notification(self, message: str) -> None:
        """Show a temporary notification."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Notification")
        # noinspection PyUnresolvedReferences
        dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(message, dialog))
        dialog.setFixedSize(300, 100)
        QTimer.singleShot(5000, dialog.accept)
        dialog.exec()
        logging.debug(f"Notification shown: {message}")

    def clear_destination(self) -> None:
        """Clear the current destination for the selected character."""
        if not self.parent:
            logging.warning("No parent found; cannot clear destination.")
            return

        parent = cast("MainWindowType", self.parent)

        if not parent.selected_character:
            logging.warning("No character selected to clear destination")
            return

        character_id = parent.selected_character['id']

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM destinations WHERE character_id = ?", (character_id,))
                conn.commit()

            parent.destination = None
            parent.update_minimap()
            logging.info(f"Cleared destination for character {character_id}")
            self.accept()

        except sqlite3.Error as e:
            logging.error(f"Failed to clear destination: {e}")

    def set_destination(self) -> None:
        """Set the selected destination for the current character."""
        if not self.parent:
            self.show_error_dialog("No Character", "Please select a character first")
            return

        parent = cast("MainWindowType", self.parent)
        parent.selected_route_label = None

        if not parent.selected_character:
            self.show_error_dialog("No Character", "Please select a character first")
            return

        coords = self.get_selected_destination()
        if not coords:
            self.show_error_dialog("No Destination", "Please select a valid destination")
            return

        character_id = parent.selected_character['id']

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO destinations (character_id, col, row, timestamp)
                    VALUES (?, ?, ?, datetime('now'))
                """, (character_id, coords[0], coords[1]))

                conn.commit()

            # ✅ Save to recent using centralized logic
            parent.save_to_recent_destinations(character_id, coords[0], coords[1])

            # ✅ Reload destination from DB to sync to current character context
            parent.load_last_destination_for_character(character_id)
            parent.update_minimap()
            logging.info(f"Set destination for character {character_id} to {coords}")
            self.accept()

        except sqlite3.Error as e:
            logging.error(f"Failed to set destination: {e}")

    def get_selected_destination(self) -> tuple[int, int] | None:
        """Retrieve coordinates of the selected destination."""
        if not self.parent:
            return None

        parent = cast("MainWindowType", self.parent)

        if (recent := self.recent_destinations_dropdown.currentText()) != "Select a recent destination":
            return self.recent_destinations_dropdown.currentData()

        dropdowns = [
            (self.tavern_dropdown, parent.taverns_coordinates),
            (self.transit_dropdown, parent.transits_coordinates),
            (self.shop_dropdown, parent.shops_coordinates),
            (self.guild_dropdown, parent.guilds_coordinates),
            (self.poi_dropdown, parent.places_of_interest_coordinates),
            (self.user_building_dropdown, parent.user_buildings_coordinates),
        ]
        for dropdown, data in dropdowns:
            if (sel := dropdown.currentText()) != "Select a destination":
                return data[sel]

        # Bank dropdown (custom formatted)
        if (bank := self.bank_dropdown.currentText()) != "Select a destination":
            try:
                col_name, row_name = bank.split(" & ")
                col = parent.columns.get(col_name.strip())
                row = parent.rows.get(row_name.strip())
                if col is not None and row is not None:
                    return col + 1, row + 1
            except ValueError:
                logging.warning(f"Invalid bank format: {bank}")
                return None

        # Custom XY + direction
        col = parent.columns.get(self.columns_dropdown.currentText())
        row = parent.rows.get(self.rows_dropdown.currentText())
        direction = self.directional_dropdown.currentText()

        if col is not None and row is not None:
            original_coords = (col, row)
            if direction == "On":
                return original_coords
            elif direction == "East":
                return (col + 1, row)
            elif direction == "South":
                return (col, row + 1)
            elif direction == "South East":
                return (col + 1, row + 1)
            else:
                logging.warning(f"Unrecognized direction: {direction}")
                return original_coords

        logging.debug("No valid destination selected")
        return None

    def set_external_destination(self, col: int, row: int, guild_name: str) -> None:
        """Set a destination externally."""
        self.parent().selected_route_label = None
        self.recent_destinations_dropdown.clear()
        self.recent_destinations_dropdown.addItem(f"{guild_name} - {col}, {row}", (col, row))
        self.recent_destinations_dropdown.setCurrentIndex(0)  # Select the added item
        self.set_destination()
        logging.info(f"External destination set: {guild_name} at ({col}, {row})")

    def show_error_dialog(self, title: str, message: str) -> None:
        """Show an error dialog."""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        # noinspection PyUnresolvedReferences
        dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(message, dialog))
        close_btn = QPushButton("Close", dialog)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.setFixedSize(300, 100)
        dialog.exec()
        logging.debug(f"Error dialog shown: {title} - {message}")

    def load_next_move_times(self):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT next_update, last_scraped FROM guilds WHERE next_update IS NOT NULL AND last_scraped IS NOT NULL ORDER BY next_update ASC LIMIT 1")
                result = cursor.fetchone()
                self.next_guild_update = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=timezone.utc) if result else None
                self.guild_scraped_at = datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=timezone.utc) if result else None

                cursor.execute(
                    "SELECT next_update, last_scraped FROM shops WHERE next_update IS NOT NULL AND last_scraped IS NOT NULL ORDER BY next_update ASC LIMIT 1")
                result = cursor.fetchone()
                self.next_shop_update = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=timezone.utc) if result else None
                self.shop_scraped_at = datetime.strptime(result[1], "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=timezone.utc) if result else None
        except Exception as e:
            logging.error(f"Failed to load next move times: {e}")
            self.next_guild_update = self.guild_scraped_at = None
            self.next_shop_update = self.shop_scraped_at = None

    def update_countdown_labels(self):
        now = datetime.now(timezone.utc)

        def format_countdown(next_time, label: QLabel, label_name: str):
            if next_time:
                remaining = max(timedelta(0), next_time - now)  # simple, correct
                days = remaining.days
                hours, remainder = divmod(remaining.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                label.setText(
                    f"{label_name} move at {next_time.strftime('%Y-%m-%d %H:%M:%S UTC')} or in {days}d {hours}h {minutes}m {seconds}s"
                )
            else:
                label.setText(f"{label_name} move time unknown.")

        format_countdown(self.next_guild_update, self.guildCountdownLabel, "Guilds")
        format_countdown(self.next_shop_update, self.shopCountdownLabel, "Shops")