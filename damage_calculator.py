from imports import *
from constants import *


REQUIRED_WEAPONS = {
    "Vial of Holy Water",
    "Garlic Spray",
    "Wooden Stake",
}
# NOTE:
# Scrolls of Turning are intentionally excluded:
# - probabilistic damage
# - minor impact
# - not guaranteed → unsuitable for deterministic planning


@dataclass
class Weapon:
    name: str
    prices: list[int]  # indexed by charisma level


class DamageCalculator(QDialog):
    """Dialog for calculating weapons needed to reduce a target BP."""

    def __init__(
            self,
            db_connection: sqlite3.Connection,
            parent=None,
            color_mappings: dict | None = None,
    ) -> None:
        super().__init__(parent)

        self.db_connection = db_connection
        self.color_mappings = color_mappings or {}
        self.charisma_level = 0

        self.setWindowTitle("Damage Calculator")
        self.setWindowIcon(APP_ICON)
        self.setMinimumWidth(450)

        self._build_ui()
        self._load_valid_shops()

        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

        logging.debug("DamageCalculator initialized")

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # ---- Shop selector ----
        shop_layout = QHBoxLayout()
        shop_layout.addWidget(QLabel("Shop:"))
        self.shop_dropdown = QComboBox()
        shop_layout.addWidget(self.shop_dropdown)
        layout.addLayout(shop_layout)

        # ---- Target BP ----
        bp_layout = QHBoxLayout()
        bp_layout.addWidget(QLabel("Target BP:"))
        self.bp_input = QLineEdit()
        self.bp_input.setValidator(
            PySide6.QtGui.QIntValidator(0, 100_000_000)
        )
        bp_layout.addWidget(self.bp_input)
        layout.addLayout(bp_layout)

        # ---- Charisma ----
        charisma_layout = QHBoxLayout()
        charisma_layout.addWidget(QLabel("Charisma Level:"))
        self.charisma_dropdown = QComboBox()
        self.charisma_dropdown.addItems(
            ["No Charisma", "Charisma 1", "Charisma 2", "Charisma 3"]
        )
        self.charisma_dropdown.currentIndexChanged.connect(
            self._update_charisma_level
        )
        charisma_layout.addWidget(self.charisma_dropdown)
        layout.addLayout(charisma_layout)

        # ---- Results ----
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setPlaceholderText(
            "Weapons needed will be displayed here."
        )
        layout.addWidget(self.result_display)

        self.total_cost_label = QLabel("Total Cost: 0 Coins")
        layout.addWidget(self.total_cost_label)

        # ---- Controls ----
        self.calc_button = QPushButton("Calculate")
        self.calc_button.clicked.connect(self.calculate_damage)
        layout.addWidget(self.calc_button)

        self.setLayout(layout)

    # =====================================================
    # Shop / Inventory
    # =====================================================

    def _load_valid_shops(self) -> None:
        """
        Populate shop dropdown with only shops that sell
        all required weapons.
        """
        self.shops: dict[str, dict[str, Weapon]] = {}

        try:
            cursor = self.db_connection.cursor()

            cursor.execute("SELECT DISTINCT Name FROM shops")
            shop_names = [row[0] for row in cursor.fetchall()]

            for shop in shop_names:
                inventory = self._load_shop_inventory(cursor, shop)
                if self._inventory_is_valid(inventory):
                    self.shops[shop] = inventory

            self.shop_dropdown.addItems(sorted(self.shops.keys()))

            # Default to Discount Magic if present
            if "Discount Magic" in self.shops:
                self.shop_dropdown.setCurrentText("Discount Magic")

            if not self.shops:
                self.calc_button.setEnabled(False)
                self.result_display.setText(
                    "No shops found that sell all required weapons."
                )

            logging.debug(
                "Loaded %d valid shops for DamageCalculator",
                len(self.shops),
            )

        except sqlite3.Error as e:
            logging.error("Failed to load shop data: %s", e)
            self.calc_button.setEnabled(False)

    def _load_shop_inventory(
            self,
            cursor: sqlite3.Cursor,
            shop_name: str,
    ) -> dict[str, Weapon]:
        """
        Load weapon prices for a shop into a Weapon map.
        """
        cursor.execute(
            """
            SELECT item_name,
                   base_price,
                   charisma_level_1,
                   charisma_level_2,
                   charisma_level_3
            FROM shop_items
            WHERE shop_name = ?
            """,
            (shop_name,),
        )

        inventory: dict[str, Weapon] = {}
        for name, p0, p1, p2, p3 in cursor.fetchall():
            if name in REQUIRED_WEAPONS:
                inventory[name] = Weapon(
                    name=name,
                    prices=[p0, p1, p2, p3],
                )
        return inventory

    @staticmethod
    def _inventory_is_valid(inventory: dict[str, Weapon]) -> bool:
        return REQUIRED_WEAPONS.issubset(inventory.keys())

    # =====================================================
    # State
    # =====================================================

    def _update_charisma_level(self) -> None:
        self.charisma_level = self.charisma_dropdown.currentIndex()

    # =====================================================
    # Core Calculation (absolute, deterministic)
    # =====================================================

    def calculate_damage(self) -> None:
        self.result_display.clear()

        try:
            target_bp = int(self.bp_input.text())
            if target_bp <= 0:
                raise ValueError
        except ValueError:
            self.result_display.setText(
                "Please enter a valid positive BP value."
            )
            return

        shop_name = self.shop_dropdown.currentText()
        shop_inventory = self.shops.get(shop_name)

        if not shop_inventory:
            self.result_display.setText(
                "Selected shop does not sell all required weapons."
            )
            return

        vial = shop_inventory["Vial of Holy Water"]
        spray = shop_inventory["Garlic Spray"]
        stake = shop_inventory["Wooden Stake"]

        vial_cost = vial.prices[self.charisma_level]
        spray_cost = spray.prices[self.charisma_level]
        stake_cost = stake.prices[self.charisma_level]

        remaining_bp = target_bp
        total_cost = 0
        total_hits = 0
        output = []

        # ---- Vials (BP > 1350) ----
        vial_hits = 0
        while remaining_bp > 1350:
            damage = math.floor(remaining_bp * 0.6)
            remaining_bp -= damage
            vial_hits += 1
            total_cost += vial_cost
            total_hits += 1

        if vial_hits:
            output.append(
                f"{shop_name} - Vial of Holy Water - Qty: {vial_hits} - "
                f"Total Cost: {vial_hits * vial_cost:,} coins"
            )

        # ---- Sprays (BP > 200) ----
        spray_hits = 0
        while remaining_bp > 200:
            remaining_bp -= 75
            spray_hits += 1
            total_cost += spray_cost
            total_hits += 1

        if spray_hits:
            output.append(
                f"{shop_name} - Garlic Spray - Qty: {spray_hits} - "
                f"Total Cost: {spray_hits * spray_cost:,} coins"
            )

        # ---- Stake (BP ≤ 200) ----
        if 0 < remaining_bp <= 200:
            total_cost += stake_cost
            total_hits += 1
            output.append(
                f"{shop_name} - Wooden Stake - Qty: 1 - "
                f"Total Cost: {stake_cost:,} coins"
            )

        output.append(
            f"Totals: Hits: {total_hits} Coins: {total_cost:,}"
        )

        self.result_display.setText("\n".join(output))
        self.total_cost_label.setText(
            f"Total Cost: {total_cost:,} Coins"
        )

        logging.debug(
            "Damage calc: BP=%d shop=%s hits=%d cost=%d",
            target_bp,
            shop_name,
            total_hits,
            total_cost,
        )
