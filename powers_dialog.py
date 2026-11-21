from imports import *
from constants import *
from directories import *

# -----------------------
# Powers Reference Tool
# -----------------------

class PowersDialog(QDialog):
    """Dialog displaying power information with destination-setting functionality."""

    def __init__(self, parent: QWidget, character_x: int, character_y: int, db_path: str) -> None:
        """
        Initialize the PowersDialog.

        Args:
            parent: Reference to RBCCommunityMap.
            character_x: Character's X coordinate.
            character_y: Character's Y coordinate.
            db_path: Path to SQLite database.
        """
        super().__init__(parent)  # Ensure QDialog properties are inherited
        self.setWindowTitle("Powers Information")
        self.setMinimumSize(600, 400)
        self.parent = parent
        self.character_x = character_x
        self.character_y = character_y
        self.DB_PATH = db_path

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
        self.power_name_label = self._create_labeled_field("Power")
        self.guild_label = self._create_labeled_field("Guild")
        self.cost_label = self._create_labeled_field("Cost")
        self.quest_info_text = self._create_labeled_field("Quest Info", QTextEdit)
        self.skill_info_text = self._create_labeled_field("Skill Info", QTextEdit)

        self.set_destination_button = QPushButton("Set Destination")
        self.set_destination_button.setEnabled(False)
        self.set_destination_button.clicked.connect(self.set_destination)
        self.details_panel.addWidget(self.set_destination_button)

        main_layout.addLayout(self.details_panel)

        # Load powers if DB is available
        if self.db_connection:
            self.load_powers()

        self.setLayout(main_layout)  # Set QDialog layout
        logging.debug(f"PowersDialog initialized at ({character_x}, {character_y})")

    def _create_labeled_field(self, label_text: str, widget_type=QLabel) -> QWidget:
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
                    cursor.execute("SELECT `Column`, `Row` FROM guilds WHERE Name = ?", (guild,))
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

    def _configure_destination_button(self, guild: str, col: str | int, row: str | int) -> None:
        """Configure the destination button with guild location."""
        enabled = col != "NA" and row != "NA" and col is not None and row is not None
        self.set_destination_button.setEnabled(enabled)
        if enabled:
            self.set_destination_button.setProperty("guild", guild)
            self.set_destination_button.setProperty("Column", int(col))
            self.set_destination_button.setProperty("Row", int(row))
        logging.debug(f"Destination button {'enabled' if enabled else 'disabled'} for {guild} at ({col}, {row})")

    def set_destination(self) -> None:
        """Set the destination in the database and update the minimap."""
        guild = self.set_destination_button.property("guild")
        col = self.set_destination_button.property("Column")
        row = self.set_destination_button.property("Row")

        if not guild or not self.parent.selected_character:
            logging.warning("Missing guild or character for destination")
            QMessageBox.warning(self, "Error", "No character selected or invalid guild")
            return

        character_id = self.parent.selected_character['id']
        try:
            with sqlite3.connect(self.DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO destinations (character_id, col, row, timestamp) "
                    "VALUES (?, ?, ?, datetime('now'))",
                    (character_id, col, row)
                )
                conn.commit()
            self.parent.destination = (col, row)
            self.parent.update_minimap()
            logging.info(f"Destination set for {character_id} to {guild} at ({col}, {row})")
            QMessageBox.information(self, "Success", f"Destination set to {guild} at ({col}, {row})")
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
