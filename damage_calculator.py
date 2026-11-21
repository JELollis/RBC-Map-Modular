from imports import *
from constants import *
from directories import *

# -----------------------
# Damage Calculator Tool
# -----------------------
class DamageCalculator(QDialog):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.charisma_level = 0  # Default charisma level
        self.setWindowTitle("Damage Calculator")
        self.setMinimumWidth(400)

        # Main layout for the dialog
        main_layout = QVBoxLayout()

        # Target BP input
        bp_layout = QHBoxLayout()
        bp_label = QLabel("Target BP:")
        self.bp_input = QLineEdit()
        self.bp_input.setValidator(QIntValidator(0, 100000000))  # Allow only integer input
        bp_layout.addWidget(bp_label)
        bp_layout.addWidget(self.bp_input)
        main_layout.addLayout(bp_layout)

        # Charisma level selection
        charisma_layout = QHBoxLayout()
        charisma_label = QLabel("Charisma Level:")
        self.charisma_dropdown = QComboBox()
        self.charisma_dropdown.addItems(["No Charisma", "Charisma 1", "Charisma 2", "Charisma 3"])
        self.charisma_dropdown.currentIndexChanged.connect(self.update_charisma_level)
        charisma_layout.addWidget(charisma_label)
        charisma_layout.addWidget(self.charisma_dropdown)
        main_layout.addLayout(charisma_layout)

        # Weapons needed display
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setPlaceholderText("Weapons needed will be displayed here.")
        main_layout.addWidget(self.result_display)

        # Total cost display
        self.total_cost_label = QLabel("Total Cost: 0 Coins")
        main_layout.addWidget(self.total_cost_label)

        # Calculate button
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate_damage)
        main_layout.addWidget(self.calculate_button)

        # Set the layout for the dialog
        self.setLayout(main_layout)

        # Static prices for Discount Magic at different charisma levels
        self.discount_magic_prices = {
            "Vial of Holy Water": [1400, 1357, 1302, 1260],
            "Garlic Spray": [700, 678, 651, 630],
            "Wooden Stake": [2800, 2715, 2604, 2520],
        }

    def update_charisma_level(self):
        # Update charisma level from dropdown selection
        self.charisma_level = self.charisma_dropdown.currentIndex()

    def calculate_damage(self):
        # Clear previous results
        self.result_display.clear()

        try:
            # Get target BP from input
            target_bp = int(self.bp_input.text())
        except ValueError:
            self.result_display.setText("Please enter a valid BP value.")
            return

        if target_bp <= 0:
            self.result_display.setText("BP must be greater than 0.")
            return

        results = []
        total_cost = 0
        remaining_bp = target_bp
        total_hits = 0

        # Load prices for weapons based on charisma level
        vial_cost = self.discount_magic_prices["Vial of Holy Water"][self.charisma_level]
        spray_cost = self.discount_magic_prices["Garlic Spray"][self.charisma_level]
        stake_cost = self.discount_magic_prices["Wooden Stake"][self.charisma_level]

        # Step 1: Calculate the number of Vial of Holy Water hits needed to reduce BP to <= 1350
        vial_hits = 0
        while remaining_bp > 1350:
            damage = math.floor(remaining_bp * 0.6)  # Vial of Holy Water does BP * 0.6 damage
            remaining_bp -= damage
            vial_hits += 1
            total_cost += vial_cost
            total_hits += 1

        if vial_hits > 0:
            results.append(
                f"Discount Magic - Vial of Holy Water - Qty: {vial_hits} - Total Cost: {vial_hits * vial_cost:,} coins")

        # Step 2: Calculate the number of Garlic Spray hits needed to reduce BP to <= 200
        spray_hits = 0
        while remaining_bp > 200:
            remaining_bp -= 75  # Garlic Spray does a fixed average of 75 damage
            spray_hits += 1
            total_cost += spray_cost
            total_hits += 1

        if spray_hits > 0:
            results.append(
                f"Discount Magic - Garlic Spray - Qty: {spray_hits} - Total Cost: {spray_hits * spray_cost:,} coins")

        # Step 3: Use one Wooden Stake if BP <= 200
        if remaining_bp <= 200 and remaining_bp > 0:
            remaining_bp = 0  # Wooden Stake brings BP to 0
            total_cost += stake_cost
            total_hits += 1
            results.append(f"Discount Magic - Wooden Stake - Qty: 1 - Total Cost: {stake_cost:,} coins")

        # Final output for total cost and total hits
        results.append(f"Totals: Hits: {total_hits} Coins: {total_cost:,}")
        self.result_display.setText("\n".join(results))
        self.total_cost_label.setText(f"Total Cost: {total_cost:,} Coins")
