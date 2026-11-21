from imports import *
from constants import *
from directories import *

# -----------------------
# Shopping List Tools
# -----------------------

class ShoppingListTool(QDialog):
    """Tool for managing a character’s shopping list with SQLite-backed shop data."""

    def __init__(self, character_name: str, db_path: str, parent=None) -> None:
        """
        Initialize the Shopping List Tool.

        Args:
            character_name: Name of the character using the tool.
            db_path: Path to the SQLite database.
            parent: Parent widget (default is None).
        """
        super().__init__(parent)  # Ensure it gets QDialog properties
        self.setWindowTitle("Shopping List Tool")
        self.setGeometry(100, 100, 600, 400)
        self.character_name = character_name
        self.DB_PATH = db_path
        self.list_total = 0

        try:
            self.sqlite_connection = sqlite3.connect(self.DB_PATH)
            self.sqlite_cursor = self.sqlite_connection.cursor()
        except sqlite3.Error as e:
            logging.error(f"Failed to connect to database: {e}")
            self.sqlite_connection = None
            self.sqlite_cursor = None

        self.setup_ui()
        if self.sqlite_connection:
            self.populate_shop_dropdown()
        logging.debug(f"ShoppingListTool initialized for {character_name}")

    def setup_ui(self) -> None:
        """Set up the UI elements and layout."""
        layout = QVBoxLayout(self)  # Use QVBoxLayout for QDialog

        self.shop_combobox = QComboBox()
        self.charisma_combobox = QComboBox()
        self.charisma_combobox.addItems(["No Charisma", "Charisma 1", "Charisma 2", "Charisma 3"])
        self.available_items_list = QListWidget()
        self.shopping_list = QListWidget()
        self.add_item_button = QPushButton("Add Item")
        self.remove_item_button = QPushButton("Remove Item")
        self.total_label = QLabel(f"List total: 0 Coins | Coins in Pocket: {self.coins_in_pocket()} | Bank: {self.coins_in_bank()}")

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
        layout.addWidget(self.total_label)

        self.setLayout(layout)  # Set the layout for QDialog

        # Signal connections
        self.add_item_button.clicked.connect(self.add_item)
        self.remove_item_button.clicked.connect(self.remove_item)
        self.shop_combobox.currentIndexChanged.connect(self.load_items)
        self.charisma_combobox.currentIndexChanged.connect(self._update_all)

    def populate_shop_dropdown(self) -> None:
        """Populate the shop dropdown with data from SQLite."""
        if not self.sqlite_cursor:
            return
        try:
            self.sqlite_cursor.execute("SELECT DISTINCT shop_name FROM shop_items")
            shops = [row[0] for row in self.sqlite_cursor.fetchall()]
            self.shop_combobox.addItems(shops)
            logging.debug(f"Populated shop dropdown with {len(shops)} shops")
        except sqlite3.Error as e:
            logging.error(f"Failed to populate shop dropdown: {e}")

    def load_items(self) -> None:
        """Load available items based on selected shop and charisma level."""
        if not self.sqlite_cursor or not self.shop_combobox.currentText():
            self.available_items_list.clear()
            return

        self.available_items_list.clear()
        shop_name = self.shop_combobox.currentText()
        price_column = {
            "No Charisma": "base_price",
            "Charisma 1": "charisma_level_1",
            "Charisma 2": "charisma_level_2",
            "Charisma 3": "charisma_level_3"
        }.get(self.charisma_combobox.currentText(), "base_price")

        try:
            self.sqlite_cursor.execute(
                f"SELECT item_name, {price_column} FROM shop_items WHERE shop_name = ?",
                (shop_name,)
            )
            for name, price in self.sqlite_cursor.fetchall():
                self.available_items_list.addItem(f"{name} - {price} Coins")
            logging.debug(f"Loaded {self.available_items_list.count()} items for {shop_name}")
        except sqlite3.Error as e:
            logging.error(f"Failed to load items: {e}")

    def add_item(self) -> None:
        """Add an item from available items to the shopping list."""
        if not (item := self.available_items_list.currentItem()):
            return

        name, price_str = item.text().split(" - ")
        price = int(price_str.split(" Coins")[0])
        quantity, ok = QInputDialog.getInt(self, "Quantity", f"How many {name}?", 1, 1)
        if not ok:
            return

        for i in range(self.shopping_list.count()):
            if (existing := self.shopping_list.item(i).text()).startswith(f"{name} - "):
                curr_qty = int(existing.split(" - ")[2].split("x")[0])
                self.shopping_list.item(i).setText(f"{name} - {price} Coins - {curr_qty + quantity}x")
                self.update_total()
                return

        self.shopping_list.addItem(f"{name} - {price} Coins - {quantity}x")
        self.update_total()
        logging.debug(f"Added {name} x{quantity} to shopping list")

    def remove_item(self) -> None:
        """Remove or reduce quantity of an item from the shopping list."""
        if not (item := self.shopping_list.currentItem()):
            return

        name, price_str, qty_str = item.text().split(" - ")
        price = int(price_str.split(" Coins")[0])
        curr_qty = int(qty_str.split("x")[0])
        qty_to_remove, ok = QInputDialog.getInt(self, "Remove", f"How many {name}?", 1, 1, curr_qty)
        if not ok:
            return

        new_qty = curr_qty - qty_to_remove
        if new_qty > 0:
            item.setText(f"{name} - {price} Coins - {new_qty}x")
        else:
            self.shopping_list.takeItem(self.shopping_list.row(item))
        self.update_total()
        logging.debug(f"Removed {qty_to_remove}x {name} from shopping list")

    def _update_all(self) -> None:
        """Update both available items and shopping list prices."""
        self.load_items()
        self.update_shopping_list_prices()

    def update_shopping_list_prices(self) -> None:
        """Update prices in the shopping list based on charisma level."""
        if not self.sqlite_cursor or not self.shop_combobox.currentText():
            return

        shop_name = self.shop_combobox.currentText()
        price_column = {
            "No Charisma": "base_price",
            "Charisma 1": "charisma_level_1",
            "Charisma 2": "charisma_level_2",
            "Charisma 3": "charisma_level_3"
        }.get(self.charisma_combobox.currentText(), "base_price")

        try:
            items = {self.shopping_list.item(i).text().split(" - ")[0]: i for i in range(self.shopping_list.count())}
            if items:
                self.sqlite_cursor.execute(
                    f"SELECT item_name, {price_column} FROM shop_items WHERE shop_name = ? AND item_name IN ({','.join('?' * len(items))})",
                    (shop_name, *items.keys())
                )
                for name, price in self.sqlite_cursor.fetchall():
                    i = items[name]
                    qty = int(self.shopping_list.item(i).text().split(" - ")[2].split("x")[0])
                    self.shopping_list.item(i).setText(f"{name} - {price} Coins - {qty}x")
            self.update_total()
            logging.debug(f"Updated prices for {len(items)} shopping list items")
        except sqlite3.Error as e:
            logging.error(f"Failed to update shopping list prices: {e}")

    def update_total(self) -> None:
        """Update and display the total cost of the shopping list."""
        self.list_total = sum(
            int(item.text().split(" - ")[1].split(" Coins")[0]) * int(item.text().split(" - ")[2].split("x")[0])
            for item in [self.shopping_list.item(i) for i in range(self.shopping_list.count())]
        )
        self.total_label.setText(
            f"List total: {self.list_total} Coins | Coins in Pocket: {self.coins_in_pocket()} | Bank: {self.coins_in_bank()}"
        )

    def coins_in_pocket(self) -> int:
        """Retrieve coins in pocket for the character."""
        if not self.sqlite_cursor:
            return 0
        try:
            self.sqlite_cursor.execute(
                "SELECT pocket FROM coins WHERE character_id = (SELECT id FROM characters WHERE name = ?)",
                (self.character_name,))
            result = self.sqlite_cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logging.error(f"Failed to fetch pocket coins: {e}")
            return 0

    def coins_in_bank(self) -> int:
        """Retrieve coins in bank for the character."""
        if not self.sqlite_cursor:
            return 0
        try:
            self.sqlite_cursor.execute(
                "SELECT bank FROM coins WHERE character_id = (SELECT id FROM characters WHERE name = ?)",
                (self.character_name,))
            result = self.sqlite_cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logging.error(f"Failed to fetch bank coins: {e}")
            return 0

    def closeEvent(self, event) -> None:
        """Close the SQLite connection when the window closes."""
        if self.sqlite_connection:
            try:
                self.sqlite_connection.close()
                logging.debug("SQLite connection closed")
            except sqlite3.Error as e:
                logging.error(f"Failed to close connection: {e}")
        event.accept()
