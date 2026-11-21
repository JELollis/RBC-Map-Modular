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
        """
        Initialize the set destination dialog.

        Args:
            parent (QWidget): Parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Set Destination")
        self.resize(200, 200)

        # Store the parent reference to access its methods
        self.parent = parent

        # Set up the main layout for the dialog
        main_layout = QVBoxLayout(self)

        # Comboboxes to select destinations
        dropdown_layout = QFormLayout()
        self.tavern_dropdown = QComboBox()
        self.bank_dropdown = QComboBox()
        self.transit_dropdown = QComboBox()
        self.shop_dropdown = QComboBox()
        self.guild_dropdown = QComboBox()
        self.poi_dropdown = QComboBox()
        self.user_building_dropdown = QComboBox()

        # Populate dropdowns with values from the database
        self.populate_dropdown(self.tavern_dropdown, self.parent.taverns_coordinates.keys())
        self.populate_dropdown(self.bank_dropdown, [f"{col} & {row}" for (col, row, _, _) in self.parent.banks_coordinates])
        self.populate_dropdown(self.transit_dropdown, self.parent.transits_coordinates.keys())
        self.populate_dropdown(self.shop_dropdown, self.parent.shops_coordinates.keys())
        self.populate_dropdown(self.guild_dropdown, self.parent.guilds_coordinates.keys())
        self.populate_dropdown(self.poi_dropdown, self.parent.places_of_interest_coordinates.keys())
        self.populate_dropdown(self.user_building_dropdown, self.parent.user_buildings_coordinates.keys())

        dropdown_layout.addRow("Tavern:", self.tavern_dropdown)
        dropdown_layout.addRow("Bank:", self.bank_dropdown)
        dropdown_layout.addRow("Transit:", self.transit_dropdown)
        dropdown_layout.addRow("Shop:", self.shop_dropdown)
        dropdown_layout.addRow("Guild:", self.guild_dropdown)
        dropdown_layout.addRow("Place of Interest:", self.poi_dropdown)
        dropdown_layout.addRow("User Building:", self.user_building_dropdown)

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

        # Add control buttons
        button_layout = QGridLayout()  # Change to QGridLayout to accommodate (widget, row, column) syntax

        set_button = QPushButton("Set Destination")
        set_button.clicked.connect(self.set_destination)
        clear_button = QPushButton("Clear Destination")
        clear_button.clicked.connect(self.clear_destination)
        update_button = QPushButton("Update Data")
        update_button.clicked.connect(self.update_comboboxes)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        # Add buttons to the layout using the correct syntax for QGridLayout
        button_layout.addWidget(set_button, 0, 0)
        button_layout.addWidget(clear_button, 0, 1)
        button_layout.addWidget(update_button, 1, 0)
        button_layout.addWidget(cancel_button, 1, 1)

        main_layout.addLayout(button_layout)

    def populate_dropdown(self, dropdown, items):
        dropdown.clear()
        dropdown.addItem("Select a destination")
        dropdown.addItems(items)

    def update_comboboxes(self):
        self.parent.columns, self.parent.rows, self.parent.banks_coordinates, self.parent.taverns_coordinates, self.parent.transits_coordinates, self.parent.user_buildings_coordinates, self.parent.color_mappings, self.parent.shops_coordinates, self.parent.guilds_coordinates, self.parent.places_of_interest_coordinates = load_data()

        self.populate_dropdown(self.tavern_dropdown, self.parent.taverns_coordinates.keys())
        self.populate_dropdown(self.bank_dropdown, [f"{col} & {row}" for (col, row, _, _) in self.parent.banks_coordinates])
        self.populate_dropdown(self.transit_dropdown, self.parent.transits_coordinates.keys())
        self.populate_dropdown(self.shop_dropdown, self.parent.shops_coordinates.keys())
        self.populate_dropdown(self.guild_dropdown, self.parent.guilds_coordinates.keys())
        self.populate_dropdown(self.poi_dropdown, self.parent.places_of_interest_coordinates.keys())
        self.populate_dropdown(self.user_building_dropdown, self.parent.user_buildings_coordinates.keys())
        self.populate_dropdown(self.columns_dropdown, self.parent.columns.keys())
        self.populate_dropdown(self.rows_dropdown, self.parent.rows.keys())

    def clear_destination(self):
        """
        Clear the currently set destination and update the minimap.
        """
        # Clear the destination in the parent application
        self.parent.destination = None

        # Save the cleared destination to the file to ensure persistence
        with open('../Testing/sessions/destination.pkl', 'wb') as f:
            pickle.dump(self.parent.destination, f)
            pickle.dump(datetime.now(), f)
        self.parent.update_minimap()
        self.accept()

    def set_destination(self):
        selected_tavern = self.tavern_dropdown.currentText()
        selected_bank = self.bank_dropdown.currentText()
        selected_transit = self.transit_dropdown.currentText()
        selected_shop = self.shop_dropdown.currentText()
        selected_guild = self.guild_dropdown.currentText()
        selected_poi = self.poi_dropdown.currentText()
        selected_user_building = self.user_building_dropdown.currentText()

        col, row = None, None  # Initialize col and row to None
        direction = None  # Initialize direction to None

        if selected_tavern != "Select a destination":
            col, row = self.parent.taverns_coordinates[selected_tavern]
        elif selected_bank != "Select a destination":
            col_name, row_name = selected_bank.split(" & ")
            col, row = self.parent.columns[col_name], self.parent.rows[row_name]
            col += 1  # Adjust bank coordinates by +1
            row += 1
        elif selected_transit != "Select a destination":
            col, row = self.parent.transits_coordinates[selected_transit]
        elif selected_shop != "Select a destination":
            col, row = self.parent.shops_coordinates[selected_shop]
        elif selected_guild != "Select a destination":
            col, row = self.parent.guilds_coordinates[selected_guild]
        elif selected_poi != "Select a destination":
            col, row = self.parent.places_of_interest_coordinates[selected_poi]
        elif selected_user_building != "Select a destination":
            col, row = self.parent.user_buildings_coordinates[selected_user_building]
        else:
            col_name = self.columns_dropdown.currentText()
            row_name = self.rows_dropdown.currentText()
            direction = self.directional_dropdown.currentText()

            if col_name and row_name:
                col = self.parent.columns.get(col_name)
                row = self.parent.rows.get(row_name)

                if col is not None and row is not None:
                    # Apply direction
                    if direction == "East":
                        col += 1  # Only move to the East
                    elif direction == "South":
                        row += 1  # Only move to the South
                    elif direction == "South East":
                        col += 1  # Move to the East
                        row += 1  # Move to the South

        # If col and row are set, update the destination
        if col is not None and row is not None:
            self.parent.destination = (col, row)
            self.parent.save_destination()
            self.parent.update_minimap()
            self.accept()
            logging.debug(f"Setting destination to col={col}, row={row} for direction={direction}")
        else:
            logging.warning("No valid destination selected or incorrect coordinates provided.")
