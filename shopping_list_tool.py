from imports import *
from constants import *


class ShoppingListTool(QDialog):
    """Tool for managing a character’s shopping list with SQLite-backed shop data."""

    def __init__(
            self,
            character_name: str,
            db_path: str,
            parent=None,
            color_mappings: dict | None = None,
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle("Shopping List Tool")
        self.setGeometry(100, 100, 700, 500)

        self.character_name = character_name
        self.db_path = db_path
        self.color_mappings = color_mappings or {}

        # Internal data model (authoritative)
        self.shopping_items: dict[str, dict[str, int]] = {}

        self.list_total = 0
        self.next_shop_update = None

        self._open_db()
        self._build_ui()

        if self.sqlite_cursor:
            self.populate_shop_dropdown()

        self.load_shop_move_time()
        self._start_timer()

        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

        logging.debug("ShoppingListTool initialized for %s", character_name)

    # =====================================================
    # Database
    # =====================================================

    def _open_db(self) -> None:
        try:
            self.sqlite_connection = sqlite3.connect(self.db_path)
            self.sqlite_cursor = self.sqlite_connection.cursor()
        except sqlite3.Error as exc:
            logging.error("Failed to connect to database: %s", exc)
            self.sqlite_connection = None
            self.sqlite_cursor = None

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        # ---- Filters ----
        filter_row = QHBoxLayout()

        self.shop_combobox = QComboBox()
        self.charisma_combobox = QComboBox()
        self.charisma_combobox.addItems(
            ["No Charisma", "Charisma 1", "Charisma 2", "Charisma 3"]
        )

        filter_row.addWidget(QLabel("Select Shop:"))
        filter_row.addWidget(self.shop_combobox)
        filter_row.addSpacing(20)
        filter_row.addWidget(QLabel("Charisma Level:"))
        filter_row.addWidget(self.charisma_combobox)

        main_layout.addLayout(filter_row)

        # ---- Lists ----
        list_row = QHBoxLayout()

        self.available_items_list = QListWidget()
        self.shopping_list = QListWidget()

        left = QVBoxLayout()
        left.addWidget(QLabel("Available Items:"))
        left.addWidget(self.available_items_list)
        self.add_item_button = QPushButton("Add →")
        left.addWidget(self.add_item_button)

        right = QVBoxLayout()
        right.addWidget(QLabel("Shopping List:"))
        right.addWidget(self.shopping_list)
        self.remove_item_button = QPushButton("← Remove")
        right.addWidget(self.remove_item_button)

        list_row.addLayout(left)
        list_row.addLayout(right)
        main_layout.addLayout(list_row)

        # ---- Totals & Countdown ----
        self.total_label = QLabel()
        self.shop_countdown_label = QLabel()
        main_layout.addSpacing(10)
        main_layout.addWidget(self.total_label)
        main_layout.addWidget(self.shop_countdown_label)

        # ---- Signals ----
        self.add_item_button.clicked.connect(self.add_item)
        self.remove_item_button.clicked.connect(self.remove_item)
        self.shop_combobox.currentIndexChanged.connect(self.load_items)
        self.charisma_combobox.currentIndexChanged.connect(self._refresh_prices)

        self.update_total()

    # =====================================================
    # Shop / Item Loading
    # =====================================================

    def populate_shop_dropdown(self) -> None:
        if not self.sqlite_cursor:
            return
        try:
            self.sqlite_cursor.execute(
                "SELECT DISTINCT shop_name FROM shop_items"
            )
            shops = [row[0] for row in self.sqlite_cursor.fetchall()]
            self.shop_combobox.addItems(shops)
        except sqlite3.Error as exc:
            logging.error("Failed to populate shop dropdown: %s", exc)

    def load_items(self) -> None:
        self.available_items_list.clear()

        if not self.sqlite_cursor:
            return

        shop = self.shop_combobox.currentText()
        if not shop:
            return

        price_column = self._price_column()

        try:
            self.sqlite_cursor.execute(
                f"""
                SELECT item_name, {price_column}
                FROM shop_items
                WHERE shop_name = ?
                """,
                (shop,),
            )

            for name, price in self.sqlite_cursor.fetchall():
                self.available_items_list.addItem(
                    f"{name} - {price} Coins"
                )
        except sqlite3.Error as exc:
            logging.error("Failed to load items: %s", exc)

    def _price_column(self) -> str:
        return {
            "No Charisma": "base_price",
            "Charisma 1": "charisma_level_1",
            "Charisma 2": "charisma_level_2",
            "Charisma 3": "charisma_level_3",
        }.get(self.charisma_combobox.currentText(), "base_price")

    # =====================================================
    # Shopping List Logic (Model-driven)
    # =====================================================

    def add_item(self) -> None:
        item = self.available_items_list.currentItem()
        if not item:
            return

        name, price_part = item.text().split(" - ")
        price = int(price_part.split()[0])

        qty, ok = QInputDialog.getInt(
            self, "Quantity", f"How many {name}?", 1, 1
        )
        if not ok:
            return

        entry = self.shopping_items.setdefault(
            name, {"price": price, "quantity": 0}
        )
        entry["price"] = price
        entry["quantity"] += qty

        self._refresh_shopping_list()

    def remove_item(self) -> None:
        item = self.shopping_list.currentItem()
        if not item:
            return

        name = item.text().split(" - ")[0]
        entry = self.shopping_items.get(name)
        if not entry:
            return

        qty, ok = QInputDialog.getInt(
            self,
            "Remove",
            f"How many {name}?",
            1,
            1,
            entry["quantity"],
        )
        if not ok:
            return

        entry["quantity"] -= qty
        if entry["quantity"] <= 0:
            del self.shopping_items[name]

        self._refresh_shopping_list()

    def _refresh_prices(self) -> None:
        if not self.sqlite_cursor:
            return

        shop = self.shop_combobox.currentText()
        if not shop or not self.shopping_items:
            return

        price_column = self._price_column()
        names = list(self.shopping_items.keys())

        try:
            self.sqlite_cursor.execute(
                f"""
                SELECT item_name, {price_column}
                FROM shop_items
                WHERE shop_name = ?
                  AND item_name IN ({",".join("?" * len(names))})
                """,
                (shop, *names),
            )

            for name, price in self.sqlite_cursor.fetchall():
                self.shopping_items[name]["price"] = price

        except sqlite3.Error as exc:
            logging.error("Failed to refresh prices: %s", exc)

        self._refresh_shopping_list()

    def _refresh_shopping_list(self) -> None:
        self.shopping_list.clear()

        for name, data in self.shopping_items.items():
            self.shopping_list.addItem(
                f"{name} - {data['price']} Coins - {data['quantity']}x"
            )

        self.update_total()

    # =====================================================
    # Totals & Coins
    # =====================================================

    def update_total(self) -> None:
        self.list_total = sum(
            item["price"] * item["quantity"]
            for item in self.shopping_items.values()
        )

        self.total_label.setText(
            f"<b>List total:</b> {self.list_total} Coins | "
            f"<b>Coins in Pocket:</b> {self.coins_in_pocket()} | "
            f"<b>Bank:</b> {self.coins_in_bank()}"
        )

    def coins_in_pocket(self) -> int:
        if not self.sqlite_cursor:
            return 0
        try:
            self.sqlite_cursor.execute(
                """
                SELECT pocket FROM coins
                WHERE character_id = (
                    SELECT id FROM characters WHERE name = ?
                )
                """,
                (self.character_name,),
            )
            row = self.sqlite_cursor.fetchone()
            return row[0] if row else 0
        except sqlite3.Error:
            return 0

    def coins_in_bank(self) -> int:
        if not self.sqlite_cursor:
            return 0
        try:
            self.sqlite_cursor.execute(
                """
                SELECT bank FROM coins
                WHERE character_id = (
                    SELECT id FROM characters WHERE name = ?
                )
                """,
                (self.character_name,),
            )
            row = self.sqlite_cursor.fetchone()
            return row[0] if row else 0
        except sqlite3.Error:
            return 0

    # =====================================================
    # Countdown
    # =====================================================

    def _start_timer(self) -> None:
        self.shop_timer = QTimer(self)
        self.shop_timer.timeout.connect(self.update_shop_countdown)
        self.shop_timer.start(1000)

    def load_shop_move_time(self) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT next_update
                    FROM shops
                    WHERE next_update IS NOT NULL
                    ORDER BY next_update ASC
                    LIMIT 1
                    """
                )
                row = cursor.fetchone()
                if row:
                    self.next_shop_update = datetime.strptime(
                        row[0], "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=timezone.utc)
        except Exception:
            self.next_shop_update = None

    def update_shop_countdown(self) -> None:
        now = datetime.now(timezone.utc)
        if self.next_shop_update:
            remaining = max(
                timedelta(0), self.next_shop_update - now
            )
            days = remaining.days
            hours, rem = divmod(remaining.seconds, 3600)
            minutes, seconds = divmod(rem, 60)
            text = (
                f"Shops move at "
                f"{self.next_shop_update.strftime('%Y-%m-%d %H:%M:%S UTC')} "
                f"or in {days}d {hours}h {minutes}m {seconds}s"
            )
        else:
            text = "Shops move time unknown."

        self.shop_countdown_label.setText(text)

    # =====================================================
    # Cleanup
    # =====================================================

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
