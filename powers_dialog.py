from imports import *
from constants import *
from directories import *

# -----------------------
# Powers Reference Tool
# -----------------------
class PowersDialog(QDialog):
    def __init__(self):
        """
        Initialize the PowersDialog with an SQLite connection using the global DB_PATH.
        """
        super().__init__()
        self.setWindowTitle("Powers Information")
        self.setMinimumSize(600, 400)

        # Establish SQLite connection using the global DB_PATH
        self.db_connection = sqlite3.connect(DB_PATH)

        # Layout setup
        main_layout = QHBoxLayout(self)

        # Left panel: List of powers
        self.powers_list = QListWidget()
        self.powers_list.itemClicked.connect(self.load_power_info)
        main_layout.addWidget(self.powers_list)

        # Right panel: Power details
        self.details_panel = QVBoxLayout()

        # Power name
        self.power_name_label = QLabel("<b>Power:</b>")
        self.details_panel.addWidget(self.power_name_label)

        # Guild
        self.guild_label = QLabel("<b>Guild:</b>")
        self.details_panel.addWidget(self.guild_label)

        # Cost
        self.cost_label = QLabel("<b>Cost:</b>")
        self.details_panel.addWidget(self.cost_label)

        # Quest information
        self.quest_info_text = QTextEdit()
        self.quest_info_text.setReadOnly(True)
        self.details_panel.addWidget(QLabel("<b>Quest Info:</b>"))
        self.details_panel.addWidget(self.quest_info_text)

        # Skill information
        self.skill_info_text = QTextEdit()
        self.skill_info_text.setReadOnly(True)
        self.details_panel.addWidget(QLabel("<b>Skill Info:</b>"))
        self.details_panel.addWidget(self.skill_info_text)

        main_layout.addLayout(self.details_panel)

        # Load all powers into the list
        self.load_powers()

    def load_powers(self):
        """
        Load all powers from the SQLite database and populate the list widget.
        """
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT power_id, name FROM powers ORDER BY name ASC")
            powers = cursor.fetchall()
            cursor.close()

            # Populate the powers list
            for power_id, name in powers:
                self.powers_list.addItem(name)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load powers from the database:\n{e}")

    def load_power_info(self, item):
        """
        Load detailed information for the selected power and display it.

        Args:
            item: The selected QListWidgetItem containing the power's name.
        """
        try:
            power_name = item.text()
            cursor = self.db_connection.cursor()

            # Query for the power's details
            cursor.execute(
                """
                SELECT name, guild, cost, quest_info, skill_info
                FROM powers
                WHERE name = ?
                """, (power_name,)
            )
            power_details = cursor.fetchone()
            cursor.close()

            # Update the UI with the fetched details
            if power_details:
                name, guild, cost, quest_info, skill_info = power_details
                self.power_name_label.setText(f"<b>Power:</b> {name}")
                self.guild_label.setText(f"<b>Guild:</b> {guild}")
                self.cost_label.setText(f"<b>Cost:</b> {cost} coins" if cost else "<b>Cost:</b> Unknown")
                self.quest_info_text.setPlainText(quest_info if quest_info else "None")
                self.skill_info_text.setPlainText(skill_info if skill_info else "None")
            else:
                QMessageBox.warning(self, "Not Found", f"No details found for '{power_name}'.")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load power details:\n{e}")

    def closeEvent(self, event):
        """
        Ensure the SQLite database connection is closed when the dialog is closed.
        """
        if self.db_connection:
            self.db_connection.close()
        event.accept()
