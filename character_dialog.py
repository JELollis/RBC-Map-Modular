from imports import *
from constants import *
from directories import *

# -----------------------
# Character Dialog Class
# -----------------------

class CharacterDialog(QDialog):
    """
    Dialog for adding or editing a character’s name and password.
    """

    def __init__(self, parent=None, character: dict | None = None) -> None:
        """
        Initialize the character dialog.

        Args:
            parent: Parent widget (optional).
            character: Dict with 'name' and 'password' keys to pre-fill fields (optional).
        """
        super().__init__(parent)
        self.setWindowTitle("Character")

        # Input fields
        self.name_edit = QLineEdit(self)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        # Pre-fill if character data is provided
        if character:
            self.name_edit.setText(character.get('name', ''))
            self.password_edit.setText(character.get('password', ''))

        # Form layout
        layout = QFormLayout()
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Password:", self.password_edit)

        # Buttons
        button_box = QHBoxLayout()
        ok_button = QPushButton("OK", self)
        cancel_button = QPushButton("Cancel", self)
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addRow(button_box)

        self.setLayout(layout)

        # Connect signals
        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button.clicked.connect(self.reject)
        logging.debug(f"Character dialog initialized{' with existing data' if character else ''}")

    def validate_and_accept(self) -> None:
        """
        Validate input fields before accepting the dialog.
        """
        name = self.name_edit.text().strip()
        password = self.password_edit.text()

        if not name:
            QMessageBox.warning(self, "Input Error", "Name cannot be empty.")
            return
        if not password:
            QMessageBox.warning(self, "Input Error", "Password cannot be empty.")
            return

        self.accept()
