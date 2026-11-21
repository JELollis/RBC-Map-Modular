from imports import *
from constants import *
from directories import *
from database import *

# -----------------------
# Shopping list Tools
# -----------------------
class ShoppingListTool(QMainWindow):
    def __init__(self, character_name, coins_db_path):
        super().__init__()
        self.setWindowTitle("Shopping List Tool")
        self.setGeometry(100, 100, 600, 400)
        self.character_name = character_name
        self.coins_db_path = coins_db_path  # Use the passed coins DB path
        self.mysql_connection = connect_to_database()  # Use MySQL connection for shop items

        if not self.mysql_connection:
            print("Failed to connect to the MySQL database.")
            sys.exit(1)

        # Initialize the MySQL cursor
        self.cursor = self.mysql_connection.cursor()

        # Initialize shopping list total
        self.list_total = 0

        # Setting up UI
        self.setup_ui()

        # Load data from MySQL
        self.populate_shop_dropdown()

        # Load coin information from SQLite
        self.load_coin_info()

    def setup_ui(self):
        # Initialize UI elements
        self.shop_combobox = QComboBox(self)
        self.charisma_combobox = QComboBox(self)
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
            f"List total: 0 Coins | Coins in Pocket: {self.coins_in_pocket()} | Bank: {self.coins_in_bank()}")
        layout.addWidget(self.total_label)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.add_item_button.clicked.connect(self.add_item)
        self.remove_item_button.clicked.connect(self.remove_item)

        # Load items when shop or charisma level changes
        self.shop_combobox.currentIndexChanged.connect(self.load_items)
        self.charisma_combobox.currentIndexChanged.connect(self.load_items)

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
            quantity = 1  # Default quantity is 1

            # Check if the item is already in the shopping list
            for i in range(self.shopping_list.count()):
                existing_item_text = self.shopping_list.item(i).text()
                existing_item_name = existing_item_text.split(" - ")[0]
                if existing_item_name == item_name:
                    # Update the quantity if the item is already present
                    existing_quantity = int(existing_item_text.split(" - ")[2].split("x")[0])
                    self.shopping_list.item(i).setText(f"{item_name} - {item_price} Coins - {existing_quantity + 1}x")
                    self.update_total()
                    return

            # If the item is not in the list, add it with quantity 1
            self.shopping_list.addItem(f"{item_name} - {item_price} Coins - {quantity}x")
            self.update_total()

    def remove_item(self):
        """
        Remove the selected item from the shopping list or decrease its quantity.
        """
        selected_item = self.shopping_list.currentItem()
        if selected_item:
            item_text = selected_item.text()
            item_name, item_price, item_quantity = item_text.split(" - ")
            item_quantity = int(item_quantity.split("x")[0])

            if item_quantity > 1:
                # Decrease the quantity if more than 1
                self.shopping_list.currentItem().setText(f"{item_name} - {item_price} Coins - {item_quantity - 1}x")
            else:
                # Remove the item from the list if quantity is 1
                self.shopping_list.takeItem(self.shopping_list.row(selected_item))

            self.update_total()

    def add_from_damage_calculator(self, hw_count, gs_count):
        """
        Add Holy Water and Garlic Spray to the shopping list based on the damage calculator results.

        Args:
            hw_count (int): The number of Holy Water items to add.
            gs_count (int): The number of Garlic Spray items to add.
        """
        shop_name = "Discount Potions"

        try:
            # Fetch the price for Vial of Holy Water
            query_hw = """
            SELECT charisma_level_1 FROM shop_items
            WHERE shop_name = %s AND item_name = 'Vial of Holy Water'
            """
            self.cursor.execute(query_hw, (shop_name,))
            hw_price = self.cursor.fetchone()

            if hw_price:
                hw_price = hw_price[0]
            else:
                print("Vial of Holy Water not found.")
                return

            # Fetch the price for Garlic Spray
            query_gs = """
            SELECT charisma_level_1 FROM shop_items
            WHERE shop_name = %s AND item_name = 'Garlic Spray'
            """
            self.cursor.execute(query_gs, (shop_name,))
            gs_price = self.cursor.fetchone()

            if gs_price:
                gs_price = gs_price[0]
            else:
                print("Garlic Spray not found.")
                return

            # Add Vial of Holy Water to the shopping list if hw_count > 0
            if hw_count > 0:
                self.shopping_list.addItem(f"Vial of Holy Water - {hw_price} Coins - {hw_count}x")

            # Add Garlic Spray to the shopping list if gs_count > 0
            if gs_count > 0:
                self.shopping_list.addItem(f"Garlic Spray - {gs_price} Coins - {gs_count}x")

            # Update the total price after adding the items
            self.update_total()

            # Ensure the shopping list window stays visible
            self.show()

        except pymysql.MySQLError as err:
            print(f"Error fetching prices from Discount Potions: {err}")

    def populate_shop_dropdown(self):
        """
        Populate the shop dropdown with available shops from the MySQL database.
        """
        try:
            self.cursor.execute("SELECT DISTINCT shop_name FROM shop_items")
            shops = self.cursor.fetchall()
            for shop in shops:
                self.shop_combobox.addItem(shop[0])
        except pymysql.MySQLError as err:
            print(f"Error fetching shop names: {err}")

    def load_items(self):
        """
        Load items from the selected shop and charisma level into the available items list.
        Update the shopping list prices based on the selected charisma level.
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

        # Load items for the selected shop and charisma level
        query = f"""
        SELECT item_name, {price_column}
        FROM shop_items
        WHERE shop_name = %s
        """
        self.cursor.execute(query, (shop_name,))
        items = self.cursor.fetchall()

        for item in items:
            item_name = item[0]
            price = item[1]
            self.available_items_list.addItem(f"{item_name} - {price} Coins")

        # Now update the prices of items in the shopping list based on the charisma level
        for index in range(self.shopping_list.count()):
            item_text = self.shopping_list.item(index).text()
            item_name = item_text.split(" - ")[0]
            quantity = int(item_text.split(" - ")[2].split("x")[0])

            # Query for the updated price
            query = f"""
            SELECT {price_column}
            FROM shop_items
            WHERE item_name = %s
            """
            self.cursor.execute(query, (item_name,))
            price = self.cursor.fetchone()[0]

            # Update the shopping list item with the new price
            self.shopping_list.item(index).setText(f"{item_name} - {price} Coins - {quantity}x")

        # Update the total cost after all prices are updated
        self.update_total()

    def update_total(self):
        """
        Calculate the total cost of items in the shopping list based on the quantity and item prices.
        Update the total label with the new total.
        """
        total = 0
        for index in range(self.shopping_list.count()):
            item_text = self.shopping_list.item(index).text()
            price = int(item_text.split(" - ")[1].split(" ")[0])  # Extract the price
            quantity = int(item_text.split(" - ")[2].split("x")[0])  # Extract the quantity
            total += price * quantity

        self.list_total = total
        self.total_label.setText(
            f"List Total: {self.list_total} Coins | Coins in Pocket: {self.coins_in_pocket()} | Bank: {self.coins_in_bank()}")

    def load_coin_info(self):
        """
        Load coin information (pocket and bank) from the SQLite database.
        """
        pocket_coins = self.coins_in_pocket()
        bank_coins = self.coins_in_bank()

        print(f"Coins in pocket: {pocket_coins}")
        print(f"Coins in bank: {bank_coins}")

        # Update the combined total label with pocket and bank information
        self.total_label.setText(
            f"List total: {self.list_total} Coins | Coins in Pocket: {pocket_coins} | Bank: {bank_coins}")

    def coins_in_pocket(self):
        """
        Retrieve the number of coins in the pocket for the given character from the SQLite DB.
        """
        connection = sqlite3.connect(self.coins_db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT pocket FROM coins WHERE character = ?", (self.character_name,))
        result = cursor.fetchone()

        connection.close()

        return result[0] if result else 0

    def coins_in_bank(self):
        """
        Retrieve the number of coins in the bank for the given character from the SQLite DB.
        """
        connection = sqlite3.connect(self.coins_db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT bank FROM coins WHERE character = ?", (self.character_name,))
        result = cursor.fetchone()

        connection.close()

        return result[0] if result else 0
