from imports import *
from constants import *

class ShoppingListTool(QDialog):
    """Tool for managing a character’s shopping list with SQLite-backed shop data."""

    def __init__(self, character_name: str, db_path: str, parent=None, color_mappings: dict | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Shopping List Tool")
        self.setGeometry(100, 100, 700, 500)
        self.character_name = character_name
        self.DB_PATH = db_path
        self.color_mappings = color_mappings or {}
        self.list_total = 0
        self.next_shop_update = None

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

        self.load_shop_move_time()
        self.shop_timer = QTimer(self)
        self.shop_timer.timeout.connect(self.update_shop_countdown)
        self.shop_timer.start(1000)

        logging.debug(f"ShoppingListTool initialized for {character_name}")

    def setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        # Top row
        filter_row = QHBoxLayout()
        self.shop_combobox = QComboBox()
        self.charisma_combobox = QComboBox()
        self.charisma_combobox.addItems(["No Charisma", "Charisma 1", "Charisma 2", "Charisma 3"])
        filter_row.addWidget(QLabel("Select Shop:"))
        filter_row.addWidget(self.shop_combobox)
        filter_row.addSpacing(20)
        filter_row.addWidget(QLabel("Charisma Level:"))
        filter_row.addWidget(self.charisma_combobox)
        main_layout.addLayout(filter_row)

        # Middle row
        list_row = QHBoxLayout()

        # Available Items
        available_layout = QVBoxLayout()
        available_layout.addWidget(QLabel("Available Items:"))
        self.available_items_list = QListWidget()
        available_layout.addWidget(self.available_items_list)
        self.add_item_button = QPushButton("Add →")
        available_layout.addWidget(self.add_item_button)
        list_row.addLayout(available_layout)

        # Shopping List
        shopping_layout = QVBoxLayout()
        shopping_layout.addWidget(QLabel("Shopping List:"))
        self.shopping_list = QListWidget()
        shopping_layout.addWidget(self.shopping_list)
        self.remove_item_button = QPushButton("← Remove")
        shopping_layout.addWidget(self.remove_item_button)
        list_row.addLayout(shopping_layout)

        main_layout.addLayout(list_row)

        # Bottom
        self.total_label = QLabel()
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.shop_countdown_label = QLabel()
        self.shop_countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.total_label)
        main_layout.addWidget(self.shop_countdown_label)

        self.setLayout(main_layout)

        # Connect signals
        self.add_item_button.clicked.connect(self.add_item)
        self.remove_item_button.clicked.connect(self.remove_item)
        self.shop_combobox.currentIndexChanged.connect(self.load_items)
        self.charisma_combobox.currentIndexChanged.connect(self._update_all)

        # Apply theme
        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

        self.update_total()

    def populate_shop_dropdown(self) -> None:
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
        self.load_items()
        self.update_shopping_list_prices()

    def update_shopping_list_prices(self) -> None:
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
        except sqlite3.Error as e:
            logging.error(f"Failed to update shopping list prices: {e}")

    def update_total(self) -> None:
        self.list_total = sum(
            int(item.text().split(" - ")[1].split(" Coins")[0]) * int(item.text().split(" - ")[2].split("x")[0])
            for item in [self.shopping_list.item(i) for i in range(self.shopping_list.count())]
        )
        self.total_label.setText(
            f"<b>List total:</b> {self.list_total} Coins | <b>Coins in Pocket:</b> {self.coins_in_pocket()} | <b>Bank:</b> {self.coins_in_bank()}"
        )

    def coins_in_pocket(self) -> int:
        if not self.sqlite_cursor:
            return 0
        try:
            self.sqlite_cursor.execute("SELECT pocket FROM coins WHERE character_id = (SELECT id FROM characters WHERE name = ?)",
                                       (self.character_name,))
            result = self.sqlite_cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logging.error(f"Failed to fetch pocket coins: {e}")
            return 0

    def coins_in_bank(self) -> int:
        if not self.sqlite_cursor:
            return 0
        try:
            self.sqlite_cursor.execute("SELECT bank FROM coins WHERE character_id = (SELECT id FROM characters WHERE name = ?)",
                                       (self.character_name,))
            result = self.sqlite_cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            logging.error(f"Failed to fetch bank coins: {e}")
            return 0

    def load_shop_move_time(self):
        try:
            with sqlite3.connect(self.DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT next_update FROM shops WHERE next_update IS NOT NULL ORDER BY next_update ASC LIMIT 1"
                )
                result = cursor.fetchone()
                if result:
                    self.next_shop_update = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except Exception as e:
            logging.error(f"Failed to load shop move time: {e}")
            self.next_shop_update = None

    def update_shop_countdown(self):
        now = datetime.now(timezone.utc)
        if self.next_shop_update:
            remaining = max(timedelta(0), self.next_shop_update - now)
            days = remaining.days
            hours, rem = divmod(remaining.seconds, 3600)
            minutes, seconds = divmod(rem, 60)
            text = (
                f"Shops move at {self.next_shop_update.strftime('%Y-%m-%d %H:%M:%S UTC')} "
                f"or in {days}d {hours}h {minutes}m {seconds}s"
            )
        else:
            text = "Shops move time unknown."
        self.shop_countdown_label.setText(text)

    def closeEvent(self, event) -> None:
        if self.sqlite_connection:
            try:
                self.sqlite_connection.close()
                logging.debug("SQLite connection closed")
            except sqlite3.Error as e:
                logging.error(f"Failed to close connection: {e}")
        event.accept()