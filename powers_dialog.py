from imports import *
from constants import *

class PowersDialog(QDialog):
    """Dialog displaying power information with destination-setting functionality."""

    def __init__(self, parent: QWidget, character_x: int, character_y: int, db_path: str, color_mappings: dict | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Powers Information")
        self.setWindowIcon(APP_ICON)
        self.setMinimumSize(600, 400)
        self.parent = parent
        self.character_x = character_x
        self.character_y = character_y
        self.DB_PATH = db_path
        self.color_mappings = color_mappings or {}

        try:
            self.db_connection = sqlite3.connect(db_path)
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to database: {e}")
            self.db_connection = None

        # Main layout
        main_layout = QHBoxLayout(self)

        # Powers List
        self.powers_list = QListWidget()
        self.powers_list.itemClicked.connect(self.load_power_info)
        main_layout.addWidget(self.powers_list)

        # Details Panel
        self.details_panel = QVBoxLayout()

        # --- Centered Guild Move Timer ---
        self.guild_countdown_label = QLabel("Guilds move time unknown.")
        self.guild_countdown_label.setStyleSheet("font-size: 9pt; color: gray; margin-bottom: 4px;")
        self.guild_countdown_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.details_panel.addWidget(self.guild_countdown_label)

        # --- Power Info Fields ---
        self.power_name_label: QLabel = self._create_labeled_field("Power")
        self.guild_label: QLabel = self._create_labeled_field("Guild")
        self.cost_label: QLabel = self._create_labeled_field("Cost")
        self.quest_info_text: QTextEdit = self._create_labeled_field("Quest Info", QTextEdit)
        self.skill_info_text: QTextEdit = self._create_labeled_field("Skill Info", QTextEdit)

        # --- Destination Button ---
        self.set_destination_button = QPushButton("Set Destination")
        self.set_destination_button.setEnabled(False)
        self.set_destination_button.clicked.connect(self.set_destination)
        self.details_panel.addWidget(self.set_destination_button)

        main_layout.addLayout(self.details_panel)
        self.setLayout(main_layout)

        # Apply theme
        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

        # Load powers and initialize timer
        if self.db_connection:
            self.load_powers()
        self.load_guild_move_time()
        self.guild_timer = QTimer(self)
        self.guild_timer.timeout.connect(self.update_guild_countdown)
        self.guild_timer.start(1000)
        logging.debug(f"PowersDialog initialized at ({character_x}, {character_y})")

    T = TypeVar("T", QLabel, QTextEdit)

    def _create_labeled_field(self, label_text: str, widget_type: Type[T] = QLabel) -> T:
        """Create a labeled field with a widget."""
        label = QLabel(f"<b>{label_text}:</b>", self)
        widget = widget_type(self)
        if isinstance(widget, QTextEdit):
            widget.setReadOnly(True)
        self.details_panel.addWidget(label)
        self.details_panel.addWidget(widget)
        return widget

    def load_powers(self) -> None:
        """Load powers from the database into the list."""
        try:
            with self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT name FROM powers ORDER BY name ASC")
                for name, in cursor.fetchall():
                    self.powers_list.addItem(name)
            logging.debug(f"Loaded {self.powers_list.count()} powers")
        except sqlite3.Error as e:
            logging.error(f"Failed to load powers: {e}")
            QMessageBox.critical(self, "Database Error", "Failed to load powers")

    def load_power_info(self, item: QListWidgetItem) -> None:
        """Display details for the selected power."""
        power_name = item.text()
        try:
            with self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute(
                    "SELECT name, guild, cost, quest_info, skill_info FROM powers WHERE name = ?",
                    (power_name,)
                )
                details = cursor.fetchone()
                if not details:
                    raise ValueError(f"No details for {power_name}")

                name, guild, cost, quest_info, skill_info = details
                self.power_name_label.setText(f"<b>Power:</b> {name}")
                self.guild_label.setText(f"<b>Guild:</b> {guild or 'Unknown'}")
                self.cost_label.setText(f"<b>Cost:</b> {cost or 'Unknown'} coins")
                self.quest_info_text.setPlainText(quest_info or "None")
                self.skill_info_text.setPlainText(skill_info or "None")

                if power_name == "Battle Cloak":
                    self._enable_nearest_peacekeeper_mission()
                elif guild:
                    cursor.execute("""
                        SELECT c.Coordinate, r.Coordinate
                        FROM guilds g
                        JOIN columns c ON g.Column = c.Name
                        JOIN rows r ON g.Row = r.Name
                        WHERE g.Name = ?
                    """, (guild,))
                    if loc := cursor.fetchone():
                        self._configure_destination_button(guild, loc[0], loc[1])
                    else:
                        self.set_destination_button.setEnabled(False)
                else:
                    self.set_destination_button.setEnabled(False)
            logging.debug(f"Loaded info for {power_name}")
        except (sqlite3.Error, ValueError) as e:
            logging.error(f"Failed to load power info for {power_name}: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load details for '{power_name}'")

    def _enable_nearest_peacekeeper_mission(self) -> None:
        """Enable destination button with the nearest Peacekeeper's Mission."""
        try:
            with self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute(
                    "SELECT c.`Coordinate`, r.`Coordinate` FROM `columns` c JOIN `rows` r "
                    "WHERE (c.`Name` = 'Emerald' AND r.`Name` IN ('67th', '33rd')) "
                    "OR (c.`Name` = 'Unicorn' AND r.`Name` = '33rd')"
                )
                missions = cursor.fetchall()
            if missions:
                closest = min(missions, key=lambda m: max(abs(m[0] - self.character_x), abs(m[1] - self.character_y)))
                self._configure_destination_button("Peacekeeper's Mission", closest[0], closest[1])
            else:
                self.set_destination_button.setEnabled(False)
                logging.debug("No Peacekeeper's Missions found")
        except sqlite3.Error as e:
            logging.error(f"Failed to find Peacekeeper's Mission: {e}")

    def _configure_destination_button(self, guild: str, col: str | int | None, row: str | int | None) -> None:
        """Configure the destination button with guild location."""
        try:
            col_val = int(col) if col not in ("NA", None) else None
            row_val = int(row) if row not in ("NA", None) else None
        except (ValueError, TypeError):
            logging.warning(f"Invalid col/row for destination: col={col}, row={row}")
            self.set_destination_button.setEnabled(False)
            return

        enabled = col_val is not None and row_val is not None
        self.set_destination_button.setEnabled(enabled)
        if enabled:
            self.set_destination_button.setProperty("guild", guild)
            self.set_destination_button.setProperty("Column", col_val)
            self.set_destination_button.setProperty("Row", row_val)
        logging.debug(f"Destination button {'enabled' if enabled else 'disabled'} for {guild} at ({col}, {row})")

    def set_destination(self) -> None:
        """Set the destination in the database and update the minimap."""
        guild = self.set_destination_button.property("guild")
        col = self.set_destination_button.property("Column")
        row = self.set_destination_button.property("Row")

        if not self.parent:
            logging.warning("No parent window set; cannot update destination.")
            return

        parent = cast("MainWindowType", self.parent)

        if not guild or not parent.selected_character:
            logging.warning("Missing guild or character for destination")
            QMessageBox.warning(self, "Error", "No character selected or invalid guild")
            return

        character_id = parent.selected_character['id']
        try:
            with sqlite3.connect(self.DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO destinations (character_id, col, row, timestamp) "
                    "VALUES (?, ?, ?, datetime('now'))",
                    (character_id, col, row)
                )
                conn.commit()
            parent.destination = (col, row)
            parent.update_minimap()
            logging.info(f"Destination set for {character_id} to {guild} at ({col}, {row})")
            # noinspection PyUnresolvedReferences
            QMessageBox.information(self, "Success", f"Destination set to {guild} at ({col}, {row})", QMessageBox.Ok)
        except sqlite3.Error as e:
            logging.error(f"Failed to set destination: {e}")
            QMessageBox.critical(self, "Database Error", "Failed to set destination")

    def closeEvent(self, event) -> None:
        """Close the database connection on dialog close."""
        if self.db_connection:
            try:
                self.db_connection.close()
                logging.debug("Database connection closed")
            except sqlite3.Error as e:
                logging.error(f"Failed to close database: {e}")
        event.accept()

    def load_guild_move_time(self):
        try:
            with sqlite3.connect(self.DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT next_update FROM guilds WHERE next_update IS NOT NULL ORDER BY next_update ASC LIMIT 1"
                )
                result = cursor.fetchone()
                if result:
                    self.next_guild_update = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                else:
                    self.next_guild_update = None
        except Exception as e:
            logging.error(f"Failed to load guild move time: {e}")
            self.next_guild_update = None

    def update_guild_countdown(self):
        now = datetime.now(timezone.utc)
        if self.next_guild_update:
            remaining = max(timedelta(0), self.next_guild_update - now)
            days = remaining.days
            hours, rem = divmod(remaining.seconds, 3600)
            minutes, seconds = divmod(rem, 60)
            text = (
                f"Guilds move at {self.next_guild_update.strftime('%Y-%m-%d %H:%M:%S UTC')} "
                f"or in {days}d {hours}h {minutes}m {seconds}s"
            )
        else:
            text = "Guilds move time unknown."
        self.guild_countdown_label.setText(text)