from imports import *
from constants import *
from directories import *
from database import *

# -----------------------
# Set Destination Dialog
# -----------------------
class set_destination_dialog(QDialog):
    """
    A dialog for setting a destination on the map.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Destination")
        self.resize(200, 250)
        self.parent = parent  # Access to parent methods and properties
        logging.info("Initialized set_destination_dialog")

        # Main layout setup
        main_layout = QVBoxLayout(self)

        # Define the style with a border for dropdowns
        dropdown_style = """
            QComboBox {
                border: 2px solid #5F6368;
                padding: 5px;
                border-radius: 4px;
            }
        """

        # Dropdown for recent destinations
        self.recent_destinations_dropdown = QComboBox()
        self.populate_recent_destinations()

        # Dropdowns for selecting destinations
        dropdown_layout = QFormLayout()
        self.tavern_dropdown = QComboBox()
        self.bank_dropdown = QComboBox()
        self.transit_dropdown = QComboBox()
        self.shop_dropdown = QComboBox()
        self.guild_dropdown = QComboBox()
        self.poi_dropdown = QComboBox()
        self.user_building_dropdown = QComboBox()

        # Populate dropdowns with values from the data sources
        self.populate_dropdown(self.tavern_dropdown, self.parent.taverns_coordinates.keys())
        self.populate_dropdown(self.bank_dropdown, [f"{col} & {row}" for (col, row, _, _) in self.parent.banks_coordinates])
        self.populate_dropdown(self.transit_dropdown, self.parent.transits_coordinates.keys())
        self.populate_dropdown(self.shop_dropdown, self.parent.shops_coordinates.keys())
        self.populate_dropdown(self.guild_dropdown, self.parent.guilds_coordinates.keys())
        self.populate_dropdown(self.poi_dropdown, self.parent.places_of_interest_coordinates.keys())
        self.populate_dropdown(self.user_building_dropdown, self.parent.user_buildings_coordinates.keys())

        logging.info("Populated destination dropdowns.")

        dropdown_layout.addRow("Recent Destinations:", self.recent_destinations_dropdown)
        dropdown_layout.addRow("Tavern:", self.tavern_dropdown)
        dropdown_layout.addRow("Bank:", self.bank_dropdown)
        dropdown_layout.addRow("Transit:", self.transit_dropdown)
        dropdown_layout.addRow("Shop:", self.shop_dropdown)
        dropdown_layout.addRow("Guild:", self.guild_dropdown)
        dropdown_layout.addRow("Place of Interest:", self.poi_dropdown)
        dropdown_layout.addRow("User Building:", self.user_building_dropdown)

        # Custom location entry
        custom_location_layout = QHBoxLayout()
        self.columns_dropdown = QComboBox()
        self.rows_dropdown = QComboBox()
        self.directional_dropdown = QComboBox()

        self.populate_dropdown(self.columns_dropdown, self.parent.columns.keys())
        self.populate_dropdown(self.rows_dropdown, self.parent.rows.keys())
        self.populate_dropdown(self.directional_dropdown, ["On", "East", "South", "South East"])

        custom_location_layout.addWidget(QLabel("ABC Street:"))
        custom_location_layout.addWidget(self.columns_dropdown)
        custom_location_layout.addWidget(QLabel("123 Street:"))
        custom_location_layout.addWidget(self.rows_dropdown)
        custom_location_layout.addWidget(QLabel("Direction:"))
        custom_location_layout.addWidget(self.directional_dropdown)

        main_layout.addLayout(dropdown_layout)
        main_layout.addLayout(custom_location_layout)

        # Control buttons
        button_layout = QGridLayout()
        set_button = QPushButton("Set Destination")
        set_button.clicked.connect(self.set_destination)
        clear_button = QPushButton("Clear Destination")
        clear_button.clicked.connect(self.clear_destination)
        update_button = QPushButton("Update Data")
        update_button.clicked.connect(self.update_comboboxes)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(set_button, 0, 0)
        button_layout.addWidget(clear_button, 0, 1)
        button_layout.addWidget(update_button, 1, 0)
        button_layout.addWidget(cancel_button, 1, 1)

        main_layout.addLayout(button_layout)

    def populate_recent_destinations(self):
        """
        Populate the recent destinations dropdown for the selected character.
        """
        logging.info("Populating recent destinations.")
        self.recent_destinations_dropdown.clear()
        self.recent_destinations_dropdown.addItem("Select a recent destination")

        character_id = self.parent.selected_character.get('id')

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        try:
            # Fetch recent destinations for the character
            cursor.execute(
                "SELECT col, row FROM recent_destinations WHERE character_id = ? ORDER BY timestamp DESC LIMIT 10",
                (character_id,)
            )
            recent_destinations = cursor.fetchall()
            logging.info(f"Fetched {len(recent_destinations)} recent destinations for character {character_id}.")

            # Process each recent destination
            for col, row in recent_destinations:
                try:
                    # Convert to integers if they aren't already
                    col = int(col)
                    row = int(row)
                except ValueError:
                    logging.error("Non-integer values for col/row: col=%s, row=%s", col, row)
                    continue

                # Round coordinates to the nearest odd number (unless boundary)
                rounded_col = col if col in (0, 200) else (col if col % 2 != 0 else col - 1)
                rounded_row = row if row in (0, 200) else (row if row % 2 != 0 else row - 1)
                logging.debug("Rounded col=%d to %d and row=%d to %d", col, rounded_col, row, rounded_row)

                # Fetch street names
                cursor.execute("SELECT Name FROM `columns` WHERE Coordinate = ?", (rounded_col,))
                col_name = cursor.fetchone()
                col_name = col_name[0] if col_name else f"Column {rounded_col}"

                cursor.execute("SELECT Name FROM `rows` WHERE Coordinate = ?", (rounded_row,))
                row_name = cursor.fetchone()
                row_name = row_name[0] if row_name else f"Row {rounded_row}"

                # Check for a named building at this location across all relevant tables
                building_name = None
                for table in ["banks", "guilds", "placesofinterest", "shops", "taverns", "transits", "userbuildings"]:
                    cursor.execute(
                        f"SELECT Name FROM `{table}` WHERE `Column` = ? AND `Row` = ?",
                        (col_name, row_name)
                    )
                    result = cursor.fetchone()
                    if result:
                        building_name = result[0]
                        break

                # Format display name
                display_name = f"{col_name} & {row_name}"
                if building_name:
                    display_name += f" - {building_name}"

                self.recent_destinations_dropdown.addItem(display_name, (col, row))
                logging.info(f"Added recent destination: {display_name}")
        except sqlite3.Error as e:
            logging.error(f"Error fetching recent destinations: {e}")
        finally:
            connection.close()

    def populate_dropdown(self, dropdown, items):
        logging.info("Populating dropdown with %d items.", len(items))
        dropdown.clear()
        dropdown.addItem("Select a destination")
        dropdown.addItems(items)

    def update_comboboxes(self):
        logging.info("Updating comboboxes.")
        self.show_notification("Updating Shop and Guild Data. Please wait...")

        # Run the scraper to update data if available
        if hasattr(self.parent, 'AVITD_scraper') and self.parent.AVITD_scraper:
            self.parent.AVITD_scraper.scrape_guilds_and_shops()

        # Reload data from the SQLite database
        try:
            updated_data = load_data(DB_PATH)
            self.parent.columns, self.parent.rows, self.parent.banks_coordinates, \
                self.parent.taverns_coordinates, self.parent.transits_coordinates, \
                self.parent.user_buildings_coordinates, self.parent.color_mappings, \
                self.parent.shops_coordinates, self.parent.guilds_coordinates, \
                self.parent.places_of_interest_coordinates = updated_data

            # Populate dropdowns with updated data
            self.populate_dropdown(self.tavern_dropdown, self.parent.taverns_coordinates.keys())
            self.populate_dropdown(self.bank_dropdown,
                                   [f"{col} & {row}" for (col, row, _, _) in self.parent.banks_coordinates])
            self.populate_dropdown(self.transit_dropdown, self.parent.transits_coordinates.keys())
            self.populate_dropdown(self.shop_dropdown, self.parent.shops_coordinates.keys())
            self.populate_dropdown(self.guild_dropdown, self.parent.guilds_coordinates.keys())
            self.populate_dropdown(self.poi_dropdown, self.parent.places_of_interest_coordinates.keys())
            self.populate_dropdown(self.user_building_dropdown, self.parent.user_buildings_coordinates.keys())

            # Call update_minimap to redraw the map with the new data
            if hasattr(self.parent, 'update_minimap') and callable(self.parent.update_minimap):
                logging.info("Updating minimap with new data.")
                self.parent.update_minimap()

            logging.info("Comboboxes updated successfully.")
        except Exception as e:
            logging.error(f"Failed to update comboboxes: {e}")

    def show_notification(self, message):
        logging.info("Displaying notification: %s", message)
        dialog = QDialog(self)
        dialog.setWindowTitle("Notification")
        dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout()
        message_label = QLabel(message)
        layout.addWidget(message_label)
        dialog.setLayout(layout)

        QTimer.singleShot(5000, dialog.accept)
        dialog.setFixedSize(300, 100)
        dialog.exec()

    def clear_destination(self):
        if not self.parent.selected_character:
            logging.warning("No character selected for clearing destination.")
            return

        character_id = self.parent.selected_character['id']
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        try:
            cursor.execute('DELETE FROM destinations WHERE character_id = ?', (character_id,))
            connection.commit()
            logging.info(f"Cleared destination for character {character_id}")

            self.parent.destination = None
            self.parent.update_minimap()
        except sqlite3.Error as e:
            logging.error(f"Failed to clear destination for character {character_id}: {e}")
        finally:
            connection.close()

        self.accept()

    def set_destination(self):
        logging.info("Attempting to set destination.")

        # Retrieve the selected destination coordinates
        destination_coords = self.get_selected_destination()

        if not destination_coords:
            logging.warning("No valid destination selected.")
            # Show a dialog to the user if no destination is selected
            self.show_error_dialog("No destination selected", "Please select a valid destination from the list.")
            return

        if self.parent.selected_character:
            character_id = self.parent.selected_character['id']
            logging.info(f"Setting destination for character {character_id} to {destination_coords}")

            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            try:
                # First, check if the destination already exists in recent destinations
                cursor.execute('''
                    SELECT 1 FROM recent_destinations WHERE character_id = ? AND col = ? AND row = ?
                ''', (character_id, destination_coords[0], destination_coords[1]))
                existing_destination = cursor.fetchone()

                if existing_destination:
                    logging.info("Destination already exists in recent destinations. Not adding again.")
                else:
                    # If not, add it to the recent destinations
                    cursor.execute('''
                        INSERT INTO recent_destinations (character_id, col, row, timestamp)
                        VALUES (?, ?, ?, datetime('now'))
                    ''', (character_id, destination_coords[0], destination_coords[1]))
                    connection.commit()
                    logging.info(f"Added destination to recent destinations: {destination_coords}")

                # Now, update or insert the destination as the current destination
                cursor.execute("SELECT id FROM destinations WHERE character_id = ?", (character_id,))
                existing_destination = cursor.fetchone()

                if existing_destination:
                    cursor.execute('''
                        UPDATE destinations
                        SET col = ?, row = ?, timestamp = datetime('now')
                        WHERE character_id = ?
                    ''', (destination_coords[0], destination_coords[1], character_id))
                else:
                    cursor.execute('''
                        INSERT INTO destinations (character_id, col, row, timestamp)
                        VALUES (?, ?, ?, datetime('now'))
                    ''', (character_id, destination_coords[0], destination_coords[1]))

                connection.commit()
                logging.info(f"Destination set successfully for character {character_id} at {destination_coords}.")

                self.parent.destination = destination_coords
                self.parent.update_minimap()
            except sqlite3.Error as e:
                logging.error(f"Failed to set destination for character {character_id}: {e}")
            finally:
                connection.close()

            self.accept()
        else:
            logging.warning("No character selected. Destination not set.")
            self.show_error_dialog("No character selected", "Please select a character to set the destination.")

    def get_selected_destination(self):
        logging.info("Retrieving selected destination.")

        # Check recent destinations dropdown first
        recent_selection = self.recent_destinations_dropdown.currentText()
        if recent_selection and recent_selection != "Select a recent destination":
            # Fetch the coordinates stored with the dropdown item
            coords = self.recent_destinations_dropdown.currentData()
            logging.info(f"Selected recent destination: {recent_selection} with coordinates {coords}")
            return coords

        # Dropdowns with predefined coordinates
        selected_dropdowns = [
            (self.tavern_dropdown, self.parent.taverns_coordinates),
            (self.transit_dropdown, self.parent.transits_coordinates),
            (self.shop_dropdown, self.parent.shops_coordinates),
            (self.guild_dropdown, self.parent.guilds_coordinates),
            (self.poi_dropdown, self.parent.places_of_interest_coordinates),
            (self.user_building_dropdown, self.parent.user_buildings_coordinates)
        ]

        # Check each dropdown for a valid selection
        for dropdown, data in selected_dropdowns:
            selection = dropdown.currentText()
            if selection and selection != "Select a destination":
                coords = data.get(selection)
                logging.info(f"Selected destination: {selection} with coordinates {coords}")
                return coords

        # Special handling for banks
        bank_selection = self.bank_dropdown.currentText()
        if bank_selection and bank_selection != "Select a destination":
            # Parse the bank's "ABC Street & 123 Street" format
            col_name, row_name = bank_selection.split(" & ")

            # Look up column and row coordinates using parent data (columns and rows tables)
            col_coord = self.parent.columns.get(col_name.strip())
            row_coord = self.parent.rows.get(row_name.strip())

            if col_coord is not None and row_coord is not None:
                # Apply +1 offset for cell directly SE of intersection
                logging.info("Selected bank destination: %s with coordinates (%d, %d)", bank_selection, col_coord + 1,
                             row_coord + 1)
                return col_coord + 1, row_coord + 1

        # Custom location entry
        col = self.parent.columns.get(self.columns_dropdown.currentText())
        row = self.parent.rows.get(self.rows_dropdown.currentText())
        if col is not None and row is not None:
            logging.info("Custom destination selected: Column %s, Row %s", col, row)
            return col, row

        logging.warning("No valid destination selected.")
        return None

    def set_external_destination(self, col, row, guild_name):
        """Set a destination externally and update the UI accordingly."""
        logging.info("External destination set: %s at (%s, %s)", guild_name, col, row)

        # Store the destination internally
        self.external_destination = (col, row, guild_name)

        # Ensure the destination is recognized properly
        self.recent_destinations_dropdown.clear()
        self.recent_destinations_dropdown.addItem(f"{guild_name} - {col}, {row}", (col, row))

        # Ensure it gets selected
        self.recent_destinations_dropdown.setCurrentIndex(1)

        # Enable the Set Destination button
        self.set_destination()

    def show_error_dialog(self, title, message):
        # Create a dialog box to display the error message
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle(title)
        error_dialog.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        layout = QVBoxLayout()
        message_label = QLabel(message)
        layout.addWidget(message_label)

        # Adding a button to close the dialog
        close_button = QPushButton("Close")
        close_button.clicked.connect(error_dialog.accept)
        layout.addWidget(close_button)

        error_dialog.setLayout(layout)
        error_dialog.setFixedSize(300, 100)  # Set a fixed size for the dialog
        error_dialog.exec()
