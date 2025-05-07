from imports import *
from constants import *

class DamageCalculator(QDialog):
    """Dialog for calculating weapons needed to reduce a target BP."""

    def __init__(self, db_connection: sqlite3.Connection, parent=None, color_mappings: dict | None = None) -> None:
        """
        Initialize the Damage Calculator.

        Args:
            db_connection: SQLite database connection (unused currently).
            parent: Parent widget (default is None).
            color_mappings: Theme colors dictionary (optional).
        """
        super().__init__(parent)
        self.db_connection = db_connection
        self.charisma_level = 0
        self.color_mappings = color_mappings or {}

        self.setWindowTitle("Damage Calculator")
        self.setWindowIcon(APP_ICON)
        self.setMinimumWidth(400)

        main_layout = QVBoxLayout(self)

        # Target BP input
        bp_layout = QHBoxLayout()
        bp_layout.addWidget(QLabel("Target BP:"))
        self.bp_input = QLineEdit()
        self.bp_input.setValidator(PySide6.QtGui.QIntValidator(0, 100000000))
        bp_layout.addWidget(self.bp_input)
        main_layout.addLayout(bp_layout)

        # Charisma dropdown
        charisma_layout = QHBoxLayout()
        charisma_layout.addWidget(QLabel("Charisma Level:"))
        self.charisma_dropdown = QComboBox()
        self.charisma_dropdown.addItems(["No Charisma", "Charisma 1", "Charisma 2", "Charisma 3"])
        self.charisma_dropdown.currentIndexChanged.connect(self.update_charisma_level)
        charisma_layout.addWidget(self.charisma_dropdown)
        main_layout.addLayout(charisma_layout)

        # Output and controls
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setPlaceholderText("Weapons needed will be displayed here.")
        main_layout.addWidget(self.result_display)

        self.total_cost_label = QLabel("Total Cost: 0 Coins")
        main_layout.addWidget(self.total_cost_label)

        # Calculate button
        calc_button = QPushButton("Calculate")
        calc_button.clicked.connect(self.calculate_damage)
        main_layout.addWidget(calc_button)

        self.setLayout(main_layout)

        # Apply theme if available
        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

        # Static prices
        self.discount_magic_prices = {}
        self.load_item_prices_from_db()

        logging.debug("DamageCalculator initialized")

    def load_item_prices_from_db(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT name, charisma_0, charisma_1, charisma_2, charisma_3
                FROM shop_items
                WHERE shop_name = 'Discount Magic'
                  AND name IN ('Vial of Holy Water', 'Garlic Spray', 'Wooden Stake')
            """)
            rows = cursor.fetchall()
            prices = {}
            for name, *charisma_prices in rows:
                prices[name] = charisma_prices  # [c0, c1, c2, c3]
            self.discount_magic_prices = prices
            logging.debug("Loaded Discount Magic item prices: %s", prices)
        except Exception as e:
            logging.error("Failed to load item prices from Discount Magic: %s", e)
            QMessageBox.critical(self, "Error", "Could not load item prices from Discount Magic.")
            self.discount_magic_prices = {}

    def update_charisma_level(self) -> None:
        """Update charisma level based on dropdown selection."""
        self.charisma_level = self.charisma_dropdown.currentIndex()
        logging.debug(f"Charisma level set to {self.charisma_level}")

    def calculate_damage(self) -> None:
        """Calculate weapons needed to reduce target BP to 0."""
        self.result_display.clear()
        try:
            target_bp = int(self.bp_input.text())
            if target_bp <= 0:
                raise ValueError("BP must be positive")
        except ValueError:
            self.result_display.setText("Please enter a valid positive BP value")
            logging.warning("Invalid BP input")
            return

        vial_cost = self.discount_magic_prices["Vial of Holy Water"][self.charisma_level]
        spray_cost = self.discount_magic_prices["Garlic Spray"][self.charisma_level]
        stake_cost = self.discount_magic_prices["Wooden Stake"][self.charisma_level]

        remaining_bp = target_bp
        total_cost = 0
        total_hits = 0
        results = []

        # Vials until BP <= 1350
        vial_hits = 0
        while remaining_bp > 1350:
            damage = math.floor(remaining_bp * 0.6)
            remaining_bp -= damage
            vial_hits += 1
            total_cost += vial_cost
            total_hits += 1
        if vial_hits:
            results.append(f"Discount Magic - Vial of Holy Water - Qty: {vial_hits} - Total Cost: {vial_hits * vial_cost:,} coins")

        # Sprays until BP <= 200
        spray_hits = 0
        while remaining_bp > 200:
            remaining_bp -= 75
            spray_hits += 1
            total_cost += spray_cost
            total_hits += 1
        if spray_hits:
            results.append(f"Discount Magic - Garlic Spray - Qty: {spray_hits} - Total Cost: {spray_hits * spray_cost:,} coins")

        # Stake if BP <= 200
        if 0 < remaining_bp <= 200:
            total_cost += stake_cost
            total_hits += 1
            results.append(f"Discount Magic - Wooden Stake - Qty: 1 - Total Cost: {stake_cost:,} coins")
            remaining_bp = 0

        # Summary
        results.append(f"Totals: Hits: {total_hits} Coins: {total_cost:,}")
        self.result_display.setText("\n".join(results))
        self.total_cost_label.setText(f"Total Cost: {total_cost:,} Coins")
        logging.debug(f"Calculated for BP {target_bp}: {total_hits} hits, {total_cost} coins")