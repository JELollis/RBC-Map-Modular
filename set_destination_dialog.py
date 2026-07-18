from imports import *
from constants import *
from database import *


class SetDestinationDialog(QDialog):
    """
    Dialog for selecting and setting a destination on the map.

    UI-focused: persists destinations and triggers minimap refresh via parent.
    """

    RECENT_PLACEHOLDER = "Select a recent destination"
    DEST_PLACEHOLDER = "Select a destination"

    def __init__(
            self,
            parent: QWidget | None = None,
            color_mappings: dict | None = None,
    ) -> None:
        super().__init__(parent)

        self.parent = cast("MainWindowType", parent) if parent else None
        self.color_mappings = color_mappings or {}

        self.setWindowTitle("Set Destination")
        self.setWindowIcon(APP_ICON)
        self.resize(650, 300)

        logging.debug("SetDestinationDialog initialized")

        self._build_ui()
        self._setup_timers()
        self._populate_all_dropdowns()

        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

    # =====================================================
    # UI Construction
    # =====================================================

    def _build_ui(self) -> None:
        self.main_layout = QVBoxLayout(self)

        # ---- Last Updated Label ----
        self.last_updated_label = QLabel("🕒 Location data last updated: calculating...")
        self.main_layout.addWidget(self.last_updated_label)

        # ---- Dropdowns ----
        self._create_dropdowns()
        self._configure_dropdowns()

        dropdown_form = QFormLayout()
        dropdown_form.addRow("Recent:", self.recent_destinations_dropdown)
        dropdown_form.addRow("Tavern:", self.tavern_dropdown)
        dropdown_form.addRow("Bank:", self.bank_dropdown)
        dropdown_form.addRow("Transit:", self.transit_dropdown)
        dropdown_form.addRow("Shop:", self.shop_dropdown)
        dropdown_form.addRow("Guild:", self.guild_dropdown)
        dropdown_form.addRow("Place of Interest:", self.poi_dropdown)
        dropdown_form.addRow("User Building:", self.user_building_dropdown)
        self.main_layout.addLayout(dropdown_form)

        # ---- Custom Coordinates ----
        coord_layout = QHBoxLayout()
        coord_layout.addWidget(QLabel("ABC Street:"))
        coord_layout.addWidget(self.columns_dropdown, 1)
        coord_layout.addWidget(QLabel("123 Street:"))
        coord_layout.addWidget(self.rows_dropdown, 1)
        coord_layout.addWidget(QLabel("Direction:"))
        coord_layout.addWidget(self.directional_dropdown, 1)
        self.main_layout.addLayout(coord_layout)

        # ---- Buttons ----
        button_grid = QGridLayout()

        set_btn = QPushButton("Set")
        clear_btn = QPushButton("Clear")
        update_btn = QPushButton("Update Data")
        cancel_btn = QPushButton("Cancel")

        set_btn.clicked.connect(self.set_destination)
        clear_btn.clicked.connect(self.clear_destination)
        update_btn.clicked.connect(self.update_combo_boxes)
        cancel_btn.clicked.connect(self.reject)

        button_grid.addWidget(set_btn, 0, 0)
        button_grid.addWidget(clear_btn, 0, 1)
        button_grid.addWidget(update_btn, 1, 0)
        button_grid.addWidget(cancel_btn, 1, 1)

        self.main_layout.addLayout(button_grid)

        # ---- Countdown Labels ----
        self.guildCountdownLabel = QLabel("Guilds move at ...")
        self.shopCountdownLabel = QLabel("Shops move at ...")
        self.main_layout.addWidget(self.guildCountdownLabel)
        self.main_layout.addWidget(self.shopCountdownLabel)

    def _create_dropdowns(self) -> None:
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

    def _configure_dropdowns(self) -> None:
        dropdowns = [
            self.recent_destinations_dropdown,
            self.tavern_dropdown,
            self.bank_dropdown,
            self.transit_dropdown,
            self.shop_dropdown,
            self.guild_dropdown,
            self.poi_dropdown,
            self.user_building_dropdown,
            self.columns_dropdown,
            self.rows_dropdown,
            self.directional_dropdown,
        ]

        style = "QComboBox { border: 2px solid #5F6368; padding: 5px; border-radius: 4px; }"

        for dropdown in dropdowns:
            dropdown.setStyleSheet(style)
            dropdown.setEditable(True)
            dropdown.setInsertPolicy(QComboBox.NoInsert)
            completer = dropdown.completer()
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.setFilterMode(Qt.MatchContains)

    # =====================================================
    # Timers
    # =====================================================

    def _setup_timers(self) -> None:
        self.last_updated_timer = QTimer(self)
        self.last_updated_timer.timeout.connect(self.update_last_updated_label)
        self.last_updated_timer.start(1000)

        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown_labels)
        self.countdown_timer.start(1000)

        self.load_next_move_times()
        self.update_last_updated_label()

    def closeEvent(self, event):
        """
        Defensive close to avoid crashes when cursor/conn failed or were assigned incorrectly.
        """
        for attr in ("cursor", "conn", "connection"):
            obj = getattr(self, attr, None)
            if obj is None:
                continue
            try:
                close = getattr(obj, "close", None)
                if callable(close):
                    close()
            except Exception:
                pass
        event.accept()

    # =====================================================
    # Dropdown Population
    # =====================================================

    def _populate_all_dropdowns(self) -> None:
        self.populate_recent_destinations()

        if not self.parent:
            # still populate direction so dialog UI is usable in fallback
            self.populate_dropdown(self.directional_dropdown, ["On", "East", "South", "Southeast"], placeholder=self.DEST_PLACEHOLDER)
            self.populate_dropdown(self.columns_dropdown, [], placeholder=self.DEST_PLACEHOLDER)
            self.populate_dropdown(self.rows_dropdown, [], placeholder=self.DEST_PLACEHOLDER)
            return

        p = self.parent

        self.populate_dropdown(self.tavern_dropdown, p.taverns_coordinates.keys(), placeholder=self.DEST_PLACEHOLDER)
        self.populate_dropdown(self.transit_dropdown, p.transits_coordinates.keys(), placeholder=self.DEST_PLACEHOLDER)
        self.populate_dropdown(self.shop_dropdown, p.shops_coordinates.keys(), placeholder=self.DEST_PLACEHOLDER)
        self.populate_dropdown(self.guild_dropdown, p.guilds_coordinates.keys(), placeholder=self.DEST_PLACEHOLDER)
        self.populate_dropdown(self.poi_dropdown, p.places_of_interest_coordinates.keys(), placeholder=self.DEST_PLACEHOLDER)
        self.populate_dropdown(self.user_building_dropdown, p.user_buildings_coordinates.keys(), placeholder=self.DEST_PLACEHOLDER)

        # Banks: support both refactored and legacy shapes
        bank_items = self._get_bank_display_items(p)
        self.populate_dropdown(self.bank_dropdown, bank_items, placeholder=self.DEST_PLACEHOLDER)

        # Columns/Rows
        self.populate_dropdown(self.columns_dropdown, p.columns.keys(), placeholder=self.DEST_PLACEHOLDER)
        self.populate_dropdown(self.rows_dropdown, p.rows.keys(), placeholder=self.DEST_PLACEHOLDER)

        # Direction
        self.populate_dropdown(self.directional_dropdown, ["On", "East", "South", "Southeast"], placeholder=self.DEST_PLACEHOLDER)

    def _get_bank_display_items(self, p) -> list[str]:
        """
        Return bank items suitable for display in bank dropdown.

        Supports:
        - refactor: banks_coordinates is dict[str, tuple[str,str]] where keys are "Col & Row"
        - legacy: banks_coordinates might be dict/iterables containing col,row pairs
        """
        banks = getattr(p, "banks_coordinates", None)
        if not banks:
            return []

        # If dict-like, prefer keys when they look like intersections already.
        if hasattr(banks, "keys") and hasattr(banks, "values"):
            keys = list(banks.keys())
            # If keys already contain '&' then they are display labels.
            if any("&" in str(k) for k in keys):
                return [str(k) for k in keys]
            # Otherwise try to build from values (col,row,...)
            items = []
            try:
                for val in banks.values():
                    if isinstance(val, (tuple, list)) and len(val) >= 2:
                        items.append(f"{val[0]} & {val[1]}")
            except Exception:
                pass
            return items

        # Fallback: iterable of tuples
        items = []
        try:
            for val in banks:
                if isinstance(val, (tuple, list)) and len(val) >= 2:
                    items.append(f"{val[0]} & {val[1]}")
        except Exception:
            pass
        return items

    def populate_dropdown(self, dropdown: QComboBox, items, placeholder: str) -> None:
        dropdown.clear()
        dropdown.addItem(placeholder)
        dropdown.addItems(sorted([str(item) for item in items]))

    def populate_recent_destinations(self) -> None:
        """
        Populate recent destinations for the currently selected character.
        Attaches (col,row) as userData so currentData() works.
        """
        self.recent_destinations_dropdown.clear()
        self.recent_destinations_dropdown.addItem(self.RECENT_PLACEHOLDER)

        if not self.parent or not getattr(self.parent, "selected_character", None):
            return

        character_id = self.parent.selected_character.get("id")
        if not character_id:
            return

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT col, row
                    FROM recent_destinations
                    WHERE character_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 10
                    """,
                    (character_id,),
                )

                inv_cols = {v: k for k, v in self.parent.columns.items()}
                inv_rows = {v: k for k, v in self.parent.rows.items()}

                for col, row in cursor.fetchall():
                    even_col = col - (col % 2)
                    even_row = row - (row % 2)

                    col_name = inv_cols.get(even_col, f"Column {even_col}")
                    row_name = inv_rows.get(even_row, f"Row {even_row}")
                    building = self._get_building_name(cursor, col_name, row_name)

                    display = f"{col_name} & {row_name}"
                    if building:
                        display += f" - {building}"

                    # ✅ Attach coords as userData
                    self.recent_destinations_dropdown.addItem(display, (col, row))

        except sqlite3.Error as e:
            logging.error(f"Failed to load recent destinations: {e}")

    def _get_building_name(self, cursor: sqlite3.Cursor, col: str, row: str) -> str | None:
        tables = ["banks", "guilds", "placesofinterest", "shops", "taverns", "transits", "userbuildings"]
        for table in tables:
            try:
                cursor.execute(
                    f"SELECT Name FROM `{table}` WHERE `Column` = ? AND `Row` = ?",
                    (col, row),
                )
                if (res := cursor.fetchone()):
                    return res[0]
            except sqlite3.Error:
                continue
        return None

    # =====================================================
    # Actions
    # =====================================================

    def clear_destination(self) -> None:
        if not self.parent or not self.parent.selected_character:
            self.show_error_dialog("No Character", "Please select a character first.")
            return

        character_id = self.parent.selected_character["id"]
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
            self.show_error_dialog("Database Error", f"Failed to clear destination:\n{e}")

    def set_destination(self) -> None:
        if not self.parent or not self.parent.selected_character:
            self.show_error_dialog("No Character", "Please select a character first.")
            return

        self.parent.selected_route_label = None

        coords = self.get_selected_destination()
        if not coords:
            self.show_error_dialog("No Destination", "Please select a valid destination.")
            return

        character_id = self.parent.selected_character["id"]

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO destinations (character_id, col, row, timestamp)
                    VALUES (?, ?, ?, datetime('now'))
                    """,
                    (character_id, coords[0], coords[1]),
                )
                conn.commit()

            # Save to recent (parent implements)
            if hasattr(self.parent, "save_to_recent_destinations"):
                self.parent.save_to_recent_destinations(character_id, coords[0], coords[1])

            # Reload destination (parent implements)
            if hasattr(self.parent, "load_last_destination_for_character"):
                self.parent.load_last_destination_for_character(character_id)
            else:
                self.parent.destination = coords

            self.parent.update_minimap()
            logging.info(f"Set destination for character {character_id} to {coords}")
            self.accept()

        except sqlite3.Error as e:
            logging.error(f"Failed to set destination: {e}")
            self.show_error_dialog("Database Error", f"Failed to set destination:\n{e}")

    def get_selected_destination(self) -> tuple[int, int] | None:
        if not self.parent:
            return None

        p = self.parent

        # 1) Recent
        if self.recent_destinations_dropdown.currentText() != self.RECENT_PLACEHOLDER:
            data = self.recent_destinations_dropdown.currentData()
            if isinstance(data, tuple) and len(data) == 2:
                return data
            # fallback parse if data missing
            return None

        # 2) Named dropdowns (safe lookup)
        dropdowns = [
            (self.tavern_dropdown, p.taverns_coordinates),
            (self.transit_dropdown, p.transits_coordinates),
            (self.shop_dropdown, p.shops_coordinates),
            (self.guild_dropdown, p.guilds_coordinates),
            (self.poi_dropdown, p.places_of_interest_coordinates),
            (self.user_building_dropdown, p.user_buildings_coordinates),
        ]
        for dd, mapping in dropdowns:
            sel = dd.currentText()
            if sel != self.DEST_PLACEHOLDER:
                coords = mapping.get(sel)
                if coords:
                    return coords

        # 3) Bank dropdown (supports " & " and " &amp; ")
        bank = self.bank_dropdown.currentText()
        if bank != self.DEST_PLACEHOLDER:
            col_name, row_name = self._split_intersection(bank)
            if col_name and row_name:
                col = p.columns.get(col_name.strip())
                row = p.rows.get(row_name.strip())
                if col is not None and row is not None:
                    return (col + 1, row + 1)

        # 4) Custom XY + direction
        col = p.columns.get(self.columns_dropdown.currentText())
        row = p.rows.get(self.rows_dropdown.currentText())
        if col is None or row is None:
            return None

        direction = self.directional_dropdown.currentText()
        if direction == "On":
            return (col, row)
        if direction == "East":
            return (col + 1, row)
        if direction == "South":
            return (col, row + 1)
        if direction in ("Southeast", "South East"):
            return (col + 1, row + 1)

        return (col, row)

    @staticmethod
    def _split_intersection(text: str) -> tuple[str | None, str | None]:
        # Accept both " & " and " &amp; "
        if " &amp; " in text:
            parts = text.split(" &amp; ", 1)
        elif " & " in text:
            parts = text.split(" & ", 1)
        else:
            return None, None
        if len(parts) != 2:
            return None, None
        return parts[0], parts[1]

    # =====================================================
    # Update Data (kept, but guarded)
    # =====================================================

    def update_combo_boxes(self) -> None:
        logging.info("Updating combo boxes.")

        if not self.parent:
            self.show_error_dialog("No Parent", "No parent window found.")
            return

        # Prefer parent.update_data() if it exists; otherwise bail cleanly.
        if not hasattr(self.parent, "update_data") or not callable(getattr(self.parent, "update_data")):
            self.show_error_dialog(
                "Update Not Available",
                "Update service is not available in this build.\n"
                "Startup update runs automatically if enabled.",
            )
            return

        status_dialog = QDialog(self)
        status_dialog.setWindowTitle("Updating Location Data")
        status_dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(status_dialog)
        status_label = QLabel("Step 1: Triggering bot scrape...")
        layout.addWidget(status_label)
        status_dialog.setFixedSize(400, 100)
        status_dialog.show()
        QApplication.processEvents()

        try:
            # Step 1: Trigger update
            self.parent.update_data()

            # Step 2: Reload from DB
            status_label.setText("Step 2: Reloading updated location data...")
            QApplication.processEvents()

            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Name, Coordinate FROM columns")
                columns = {row[0]: row[1] for row in cursor.fetchall()}
                cursor.execute("SELECT Name, Coordinate FROM rows")
                rows = {row[0]: row[1] for row in cursor.fetchall()}

                def to_coords(col_name: str, row_name: str) -> tuple[int, int]:
                    return (columns.get(col_name, 0) + 1, rows.get(row_name, 0) + 1)

                cursor.execute("SELECT Name, Column, Row FROM shops")
                self.parent.shops_coordinates.clear()
                self.parent.shops_coordinates.update({
                    name: to_coords(col, row)
                    for name, col, row in cursor.fetchall()
                    if col != "NA" and row != "NA"
                })

                cursor.execute("SELECT Name, Column, Row FROM guilds")
                self.parent.guilds_coordinates.clear()
                self.parent.guilds_coordinates.update({
                    name: to_coords(col, row)
                    for name, col, row in cursor.fetchall()
                    if col != "NA" and row != "NA"
                })

            # Step 3: Populate UI dropdowns
            status_label.setText("Step 3: Populating dropdowns...")
            QApplication.processEvents()
            self._populate_all_dropdowns()

            self.parent.update_minimap()

            status_label.setText("✅ Update complete.")
            QApplication.processEvents()
            QTimer.singleShot(1500, status_dialog.accept)

        except Exception as e:
            logging.exception("Failed to update combo boxes:")
            status_label.setText("❌ Update failed.")
            QApplication.processEvents()
            QTimer.singleShot(2000, status_dialog.accept)
            self.show_error_dialog("Update Failed", str(e))

    # =====================================================
    # Countdown + "Last Updated" (unchanged, but stable)
    # =====================================================

    def load_next_move_times(self) -> None:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT next_update, last_scraped
                    FROM guilds
                    WHERE next_update IS NOT NULL AND last_scraped IS NOT NULL
                    ORDER BY next_update ASC
                    LIMIT 1
                    """
                )
                res = cursor.fetchone()
                self.next_guild_update = (
                    datetime.strptime(res[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    if res else None
                )

                cursor.execute(
                    """
                    SELECT next_update, last_scraped
                    FROM shops
                    WHERE next_update IS NOT NULL AND last_scraped IS NOT NULL
                    ORDER BY next_update ASC
                    LIMIT 1
                    """
                )
                res = cursor.fetchone()
                self.next_shop_update = (
                    datetime.strptime(res[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    if res else None
                )
        except Exception as e:
            logging.error(f"Failed to load next move times: {e}")
            self.next_guild_update = None
            self.next_shop_update = None

    def update_countdown_labels(self) -> None:
        now = datetime.now(timezone.utc)

        def format_countdown(next_time, label: QLabel, label_name: str):
            if next_time:
                remaining = max(timedelta(0), next_time - now)
                days = remaining.days
                hours, remainder = divmod(remaining.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                label.setText(
                    f"{label_name} move at {next_time.strftime('%Y-%m-%d %H:%M:%S UTC')} "
                    f"or in {days}d {hours}h {minutes}m {seconds}s"
                )
            else:
                label.setText(f"{label_name} move time unknown.")

        format_countdown(self.next_guild_update, self.guildCountdownLabel, "Guilds")
        format_countdown(self.next_shop_update, self.shopCountdownLabel, "Shops")

    def update_last_updated_label(self) -> None:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT MAX(last_scraped) FROM (
                        SELECT last_scraped FROM guilds WHERE last_scraped IS NOT NULL
                        UNION ALL
                        SELECT last_scraped FROM shops WHERE last_scraped IS NOT NULL
                    )
                    """
                )
                res = cursor.fetchone()
                if res and res[0]:
                    last = datetime.strptime(res[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                    delta = datetime.now(timezone.utc) - last
                    days = delta.days
                    hours, rem = divmod(delta.seconds, 3600)
                    minutes, seconds = divmod(rem, 60)
                    self.last_updated_label.setText(
                        f"🕒 Location data last updated {days}d {hours}h {minutes}m {seconds}s ago"
                    )
                else:
                    self.last_updated_label.setText("🕒 Location data last updated: unknown")
        except Exception as e:
            logging.warning(f"Failed to update last_updated_label: {e}")
            self.last_updated_label.setText("🕒 Location data last updated: error")

    # =====================================================
    # Misc
    # =====================================================

    def show_error_dialog(self, title: str, message: str) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(message, dialog))
        close_btn = QPushButton("Close", dialog)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.setFixedSize(360, 120)
        dialog.exec()

    def set_external_destination(self, col: int, row: int, guild_name: str) -> None:
        """
        Allow other dialogs (e.g., Powers) to seed a destination.
        """
        self.recent_destinations_dropdown.clear()
        self.recent_destinations_dropdown.addItem(f"{guild_name} - {col}, {row}", (col, row))
        self.recent_destinations_dropdown.setCurrentIndex(0)
        self.set_destination()
