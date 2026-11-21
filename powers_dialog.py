from imports import *
from constants import *
from directories import *

# -----------------------
# Powers Reference Tool
# -----------------------
class PowersDialog(QDialog):
    def __init__(self, parent, character_x, character_y, DB_PATH):
        """Initialize the PowersDialog with character coordinates and SQLite connection."""
        super().__init__(parent)
        self.setWindowTitle("Powers Information")
        self.setMinimumSize(600, 400)
        self.parent = parent  # Reference to RBCCommunityMap
        self.character_x = character_x
        self.character_y = character_y
        self.DB_PATH = DB_PATH

        logging.debug("Initializing PowersDialog with coordinates: (%d, %d)", character_x, character_y)

        # SQLite connection
        self.db_connection = sqlite3.connect(DB_PATH)

        # Main layout
        main_layout = QHBoxLayout(self)

        # Left panel: Powers list
        self.powers_list = QListWidget()
        self.powers_list.itemClicked.connect(self.load_power_info)
        main_layout.addWidget(self.powers_list)

        # Right panel: Details
        self.details_panel = QVBoxLayout()
        self.power_name_label = self.create_labeled_field("Power")
        self.guild_label = self.create_labeled_field("Guild")
        self.cost_label = self.create_labeled_field("Cost")
        self.quest_info_text = self.create_labeled_field("Quest Info", QTextEdit)
        self.skill_info_text = self.create_labeled_field("Skill Info", QTextEdit)

        self.set_destination_button = QPushButton("Set Destination")
        self.set_destination_button.setEnabled(False)
        self.set_destination_button.clicked.connect(self.set_destination)
        self.details_panel.addWidget(self.set_destination_button)

        main_layout.addLayout(self.details_panel)
        self.load_powers()

    def create_labeled_field(self, label_text, widget_type=QLabel):
        """Helper to create a labeled field with a widget."""
        layout = self.details_panel
        label = QLabel(f"<b>{label_text}:</b>")
        widget = widget_type()
        if isinstance(widget, QTextEdit):
            widget.setReadOnly(True)
        layout.addWidget(label)
        layout.addWidget(widget)
        return widget

    def load_powers(self):
        """Load all powers from the database into the list widget."""
        try:
            with self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT power_id, name FROM powers ORDER BY name ASC")
                powers = cursor.fetchall()
            logging.debug("Loaded %d powers from database.", len(powers))
            for power_id, name in powers:
                self.powers_list.addItem(name)
        except sqlite3.Error as e:
            logging.error("Failed to load powers: %s", e)
            QMessageBox.critical(self, "Database Error", f"Failed to load powers:\n{e}")

    def load_power_info(self, item):
        """Load and display detailed information for the selected power."""
        power_name = item.text()
        logging.debug("Loading info for power: %s", power_name)
        try:
            with self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute(
                    "SELECT name, guild, cost, quest_info, skill_info FROM powers WHERE name = ?",
                    (power_name,)
                )
                power_details = cursor.fetchone()

                guild_location = None
                if power_details and power_details[1]:
                    name, guild, cost, quest_info, skill_info = power_details
                    if power_name == "Battle Cloak":
                        self.enable_nearest_peacekeeper_mission()
                    else:
                        cursor.execute("SELECT `Column`, `Row` FROM guilds WHERE Name = ?", (guild,))
                        guild_location = cursor.fetchone()

            if power_details:
                name, guild, cost, quest_info, skill_info = power_details
                logging.debug("Power details: %s, Guild: %s, Cost: %s", name, guild, cost)
                self.power_name_label.setText(f"<b>Power:</b> {name}")
                self.guild_label.setText(f"<b>Guild:</b> {guild}")
                self.cost_label.setText(f"<b>Cost:</b> {cost} coins" if cost else "<b>Cost:</b> Unknown")
                self.quest_info_text.setPlainText(quest_info or "None")
                self.skill_info_text.setPlainText(skill_info or "None")

                if guild_location and guild_location[0] != "NA" and guild_location[1] != "NA":
                    logging.debug("Guild location: %s at (%s, %s)", guild, *guild_location)
                    self.configure_destination_button(guild, *guild_location)
                elif power_name != "Battle Cloak":
                    logging.debug("Guild location not found or unknown.")
                    self.set_destination_button.setEnabled(False)
            else:
                logging.warning("No details for power: %s", power_name)
                QMessageBox.warning(self, "Not Found", f"No details found for '{power_name}'.")
        except sqlite3.Error as e:
            logging.error("Failed to load power details: %s", e)
            QMessageBox.critical(self, "Database Error", f"Failed to load power details:\n{e}")

    def enable_nearest_peacekeeper_mission(self):
        """Enable the Set Destination button with the nearest Peacekeeper's Mission."""
        try:
            with self.db_connection:
                cursor = self.db_connection.cursor()
                cursor.execute(
                    "SELECT c.`Coordinate`, r.`Coordinate` FROM `columns` c JOIN `rows` r "
                    "WHERE (c.`Name` = 'Emerald' AND r.`Name` IN ('67th', '33rd')) "
                    "OR (c.`Name` = 'Unicorn' AND r.`Name` = '33rd')"
                )
                missions = cursor.fetchall()
            if not missions:
                logging.warning("No Peacekeeper's Mission locations found.")
                return

            closest_mission = min(missions, key=lambda m: max(abs(m[0] - self.character_x), abs(m[1] - self.character_y)))
            logging.debug("Nearest Peacekeeper's Mission at (%d, %d)", *closest_mission)
            self.configure_destination_button("Peacekeeper's Mission", *closest_mission)
        except sqlite3.Error as e:
            logging.error("Database error in enable_nearest_peacekeeper_mission: %s", e)

    def configure_destination_button(self, guild, col, row):
        """Configure the Set Destination button with guild location properties."""
        self.set_destination_button.setEnabled(col != "NA" and row != "NA")
        self.set_destination_button.setProperty("guild", guild)
        self.set_destination_button.setProperty("Column", col)
        self.set_destination_button.setProperty("Row", row)

    def set_destination(self):
        """Set the destination directly in the database and refresh the minimap."""
        guild = self.set_destination_button.property("guild")
        col = self.set_destination_button.property("Column")
        row = self.set_destination_button.property("Row")

        logging.debug("Directly setting destination: %s at (%s, %s)", guild, col, row)

        if not guild or col == "NA" or row == "NA":
            logging.warning("Cannot set destination: Unknown location.")
            QMessageBox.warning(self, "Error", "This guild's location is unknown.")
            return

        if not self.parent.selected_character:
            logging.warning("No character selected. Cannot set destination.")
            return

        character_id = self.parent.selected_character['id']
        connection = sqlite3.connect(self.DB_PATH)
        cursor = connection.cursor()

        try:
            # Check if the destination already exists
            cursor.execute("SELECT id FROM destinations WHERE character_id = ?", (character_id,))
            existing_destination = cursor.fetchone()

            if existing_destination:
                cursor.execute('''
                    UPDATE destinations
                    SET col = ?, row = ?, timestamp = datetime('now')
                    WHERE character_id = ?
                ''', (col, row, character_id))
            else:
                cursor.execute('''
                    INSERT INTO destinations (character_id, col, row, timestamp)
                    VALUES (?, ?, ?, datetime('now'))
                ''', (character_id, col, row))

            connection.commit()
            logging.info("Database updated: Destination set for character %d at (%d, %d)", character_id, col, row)

            # Immediately update the minimap
            self.parent.destination = (col, row)
            self.parent.update_minimap()

            QMessageBox.information(self, "Destination Set", f"Minimap destination set to {guild} at ({col}, {row})")

        except sqlite3.Error as e:
            logging.error("Failed to set destination in database: %s", e)
            QMessageBox.critical(self, "Database Error", f"Failed to set destination:\n{e}")
        finally:
            connection.close()

    def closeEvent(self, event):
        """Close the SQLite database connection when the dialog closes."""
        if self.db_connection:
            self.db_connection.close()
        event.accept()
