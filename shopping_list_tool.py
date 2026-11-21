from imports import *
from constants import *
from directories import *

# -----------------------
# Shopping list Tools
# -----------------------
class ShoppingListTool(QMainWindow):
    def __init__(self, character_name, DB_PATH):
        """
        Initialize the Shopping List Tool with SQLite database support.

        Args:
            character_name (str): Name of the character using the tool.
            DB_PATH (str): Path to the SQLite database.
        """
        super().__init__()
        self.setWindowTitle("Shopping List Tool")
        self.setGeometry(100, 100, 600, 400)
        self.character_name = character_name
        self.DB_PATH = DB_PATH  # Central SQLite DB path

        # Initialize SQLite connection
        self.sqlite_connection = sqlite3.connect(self.DB_PATH)
        self.sqlite_cursor = self.sqlite_connection.cursor()

        # Initialize shopping list total
        self.list_total = 0

        # Setting up UI
        self.setup_ui()

        # Load data from SQLite (shop info)
        self.populate_shop_dropdown()

    def setup_ui(self):
        # Initialize UI elements
        self.shop_combobox = QComboBox(self)
        self.charisma_combobox = QComboBox(self)
        self.charisma_combobox.currentIndexChanged.connect(self.load_items)
        self.available_items_list = QListWidget(self)
        self.shopping_list = QListWidget(self)

        # Add options to charisma combobox
        self.charisma_combobox.addItems(["No Charisma", "Charisma 1", "Charisma 2", "Charisma 3"])

        # Buttons
        self.add_item_button = QPushButton("Add Item", self)
        self.remove_item_button = QPushButton("Remove Item", self)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Shop:"))
        layout.addWidget(self.shop_combobox)
        layout.addWidget(QLabel("Select Charisma Level:"))
        layout.addWidget(self.charisma_combobox)
        layout.addWidget(QLabel("Available Items:"))
        layout.addWidget(self.available_items_list)
        layout.addWidget(self.add_item_button)
        layout.addWidget(QLabel("Shopping List:"))
        layout.addWidget(self.shopping_list)
        layout.addWidget(self.remove_item_button)

        # Create a label to display the total of the shopping list, coins in pocket, and bank balance
        self.total_label = QLabel(
            f"List total: {self.list_total} Coins | Coins in Pocket: {self.coins_in_pocket()} | Bank: {self.coins_in_bank()}"
        )
        layout.addWidget(self.total_label)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.add_item_button.clicked.connect(self.add_item)
        self.remove_item_button.clicked.connect(self.remove_item)

        # Load items when shop or charisma level changes
        self.shop_combobox.currentIndexChanged.connect(self.load_items)
        self.charisma_combobox.currentIndexChanged.connect(self.update_shopping_list_prices)

        # Load items initially
        self.load_items()

    def add_item(self):
        """
        Add the selected item from the available items list to the shopping list.
        """
        selected_item = self.available_items_list.currentItem()
        if selected_item:
            item_text = selected_item.text()
            item_name, item_price = item_text.split(" - ")
            item_price = int(item_price.split(" Coins")[0])

            # Prompt user for the quantity
            quantity, ok = QInputDialog.getInt(self, "Enter Quantity", f"How many {item_name} to add?", 1, 1)
            if ok:
                # Check if the item is already in the shopping list
                for i in range(self.shopping_list.count()):
                    existing_item_text = self.shopping_list.item(i).text()
                    existing_item_name = existing_item_text.split(" - ")[0]
                    if existing_item_name == item_name:
                        # Update the quantity if the item is already present
                        existing_quantity = int(existing_item_text.split(" - ")[2].split("x")[0])
                        self.shopping_list.item(i).setText(
                            f"{item_name} - {item_price} Coins - {existing_quantity + quantity}x"
                        )
                        self.update_total()
                        return

                # If the item is not in the list, add it with the entered quantity
                self.shopping_list.addItem(f"{item_name} - {item_price} Coins - {quantity}x")
                self.update_total()

    def remove_item(self):
        """
        Prompt for quantity to remove from the selected item in the shopping list.
        """
        selected_item = self.shopping_list.currentItem()
        if selected_item:
            item_text = selected_item.text()
            item_name, item_price, item_quantity = item_text.split(" - ")
            item_price = int(item_price.split(" Coins")[0])
            item_quantity = int(item_quantity.split("x")[0])

            # Prompt the user for the quantity to remove
            quantity_to_remove, ok = QInputDialog.getInt(self, "Enter Quantity", f"How many {item_name} to remove?", 1, 1, item_quantity)
            if ok:
                new_quantity = item_quantity - quantity_to_remove
                if new_quantity > 0:
                    # Update the item's quantity in the list without re-adding "Coins"
                    self.shopping_list.currentItem().setText(f"{item_name} - {item_price} Coins - {new_quantity}x")
                else:
                    # Remove the item if the quantity reaches zero
                    self.shopping_list.takeItem(self.shopping_list.row(selected_item))

                self.update_total()

    def populate_shop_dropdown(self):
        """
        Populate the shop dropdown with available shops from the MySQL database.
        """
        try:
            self.sqlite_cursor.execute("SELECT DISTINCT shop_name FROM shop_items")
            shops = self.sqlite_cursor.fetchall()
            for shop in shops:
                self.shop_combobox.addItem(shop[0])
        except pymysql.MySQLError as err:
            print(f"Error fetching shop names: {err}")

    def load_items(self):
        """
        Load items from the selected shop and charisma level into the available items list.
        """
        self.available_items_list.clear()
        shop_name = self.shop_combobox.currentText()
        charisma_level = self.charisma_combobox.currentText()

        # Determine the price column based on charisma level
        price_column = {
            "No Charisma": "base_price",
            "Charisma 1": "charisma_level_1",
            "Charisma 2": "charisma_level_2",
            "Charisma 3": "charisma_level_3"
        }.get(charisma_level, "base_price")

        # Load items for the selected shop and charisma level from MySQL
        query = f"""
        SELECT item_name, {price_column}
        FROM shop_items
        WHERE shop_name = ?
        """
        self.sqlite_cursor.execute(query, (shop_name,))
        items = self.sqlite_cursor.fetchall()

        for item in items:
            item_name = item[0]
            price = item[1]
            self.available_items_list.addItem(f"{item_name} - {price} Coins")

    def update_shopping_list_prices(self):
        """
        Update the prices in the shopping list based on the selected charisma level.
        """
        shop_name = self.shop_combobox.currentText()
        charisma_level = self.charisma_combobox.currentText()

        # Determine the price column based on charisma level
        price_column = {
            "No Charisma": "base_price",
            "Charisma 1": "charisma_level_1",
            "Charisma 2": "charisma_level_2",
            "Charisma 3": "charisma_level_3"
        }.get(charisma_level, "base_price")

        # Update prices for each item in the shopping list
        for i in range(self.shopping_list.count()):
            item_text = self.shopping_list.item(i).text()
            item_name = item_text.split(" - ")[0]
            quantity = int(item_text.split(" - ")[2].split("x")[0])

            # Query for the updated price from MySQL
            query = f"""
            SELECT {price_column}
            FROM shop_items
            WHERE item_name = ? AND shop_name = ?
            """
            self.sqlite_cursor.execute(query, (item_name, shop_name))
            result = self.sqlite_cursor.fetchone()

            if result:
                updated_price = result[0]
                self.shopping_list.item(i).setText(f"{item_name} - {updated_price} Coins - {quantity}x")

        self.update_total()

    def update_total(self):
        """
        Update the total cost of the shopping list and display it.
        """
        self.list_total = 0
        for index in range(self.shopping_list.count()):
            item_text = self.shopping_list.item(index).text()
            item_price = int(item_text.split(" - ")[1].split(" Coins")[0])
            item_quantity = int(item_text.split(" - ")[2].split("x")[0])
            self.list_total += item_price * item_quantity

        # Update the label with the correct total, considering the coins in pocket and bank
        self.total_label.setText(
            f"List total: {self.list_total} Coins | Coins in Pocket: {self.coins_in_pocket()} | Bank: {self.coins_in_bank()}"
        )

    def coins_in_pocket(self):
        """
        Retrieve the number of coins in the pocket for the given character from the SQLite DB.
        """
        cursor = self.sqlite_connection.cursor()
        cursor.execute("SELECT id FROM characters WHERE name = ?", (self.character_name,))
        character_id = cursor.fetchone()

        if character_id:
            cursor.execute("SELECT pocket FROM coins WHERE character_id = ?", (character_id[0],))
            result = cursor.fetchone()
            return result[0] if result else 0
        return 0

    def coins_in_bank(self):
        """
        Retrieve the number of coins in the bank for the given character from the SQLite DB.
        """
        cursor = self.sqlite_connection.cursor()
        cursor.execute("SELECT id FROM characters WHERE name = ?", (self.character_name,))
        character_id = cursor.fetchone()

        if character_id:
            cursor.execute("SELECT bank FROM coins WHERE character_id = ?", (character_id[0],))
            result = cursor.fetchone()
            return result[0] if result else 0
        return 0
