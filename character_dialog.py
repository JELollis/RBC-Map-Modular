from imports import *
from constants import *


class CharacterDialog(QDialog):
    """
    Dialog for adding or editing a character.

    This dialog is UI-only and does not write to the database.
    The caller is responsible for persisting changes.
    """

    def __init__(
            self,
            parent=None,
            character: dict | None = None,
            color_mappings: dict | None = None,
    ):
        super().__init__(parent)

        self._is_edit = character is not None
        self._original_name = character["name"] if character else None

        self.setWindowTitle(
            "Edit Character" if self._is_edit else "Add Character"
        )
        self.setWindowIcon(APP_ICON)

        self.color_mappings = color_mappings or {}

        # -----------------------
        # Input Fields
        # -----------------------

        self.name_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        if self._is_edit:
            self.name_edit.setText(character["name"])
            self.name_edit.setEnabled(False)  # Prevent accidental renames
            self.password_edit.setPlaceholderText(
                "Enter new password (leave blank to keep existing)"
            )
        else:
            self.password_edit.setPlaceholderText("Enter password")

        # -----------------------
        # Layout
        # -----------------------

        form_layout = QFormLayout()
        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Password:", self.password_edit)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Save" if self._is_edit else "Add")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        form_layout.addRow(button_layout)
        self.setLayout(form_layout)

        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

        # -----------------------
        # Signals
        # -----------------------

        self.ok_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)

    # -----------------------
    # Public API
    # -----------------------

    def get_result(self) -> dict:
        """
        Return the dialog result data.

        Returns:
            dict with keys: name, password (password may be None)
        """
        password = self.password_edit.text().strip()
        return {
            "name": self.name_edit.text().strip(),
            "password": password if password else None,
        }

    # -----------------------
    # Validation
    # -----------------------

    def validate_and_accept(self) -> None:
        name = self.name_edit.text().strip()
        password = self.password_edit.text().strip()

        if not name:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Character name cannot be empty.",
            )
            return

        if not self._is_edit and not password:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Password cannot be empty when creating a character.",
            )
            return

        self.accept()
