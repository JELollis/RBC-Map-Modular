from imports import *
from constants import *

class CharacterDialog(QDialog):
    """
    A dialog for adding or modifying a character, with validation.
    """

    def __init__(self, parent=None, character=None, color_mappings: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Character")
        self.setWindowIcon(APP_ICON)
        self.color_mappings = color_mappings or {}

        # Input fields
        self.name_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        if character:
            self.name_edit.setText(character['name'])
            self.password_edit.setText(character['password'])

        # Form layout
        layout = QFormLayout()
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Password:", self.password_edit)

        # OK and Cancel buttons
        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addRow(button_box)
        self.setLayout(layout)

        # Apply theme if available
        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

        # Connect buttons
        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button.clicked.connect(self.reject)

    def validate_and_accept(self):
        """Check if inputs are valid before accepting."""
        name = self.name_edit.text().strip()
        password = self.password_edit.text().strip()

        if not name or not password:
            QMessageBox.warning(self, "Validation Error", "Character name and password cannot be empty.")
            return  # 🚨 Do NOT call accept(), keep dialog open

        self.accept()  # ✅ Only accept if valid
