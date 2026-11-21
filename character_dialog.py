from imports import *
from constants import *
from directories import *

# -----------------------
# Character Dialog Class
# -----------------------

class CharacterDialog(QDialog):
    """
    A dialog for adding or modifying a character.
    """

    def __init__(self, parent=None, character=None):
        """
        Initialize the character dialog.

        Args:
            parent (QWidget): Parent widget.
            character (dict, optional): Character dictionary to modify. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Character")

        self.name_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        if character:
            self.name_edit.setText(character['name'])
            self.password_edit.setText(character['password'])

        layout = QFormLayout()
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Password:", self.password_edit)

        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)

        layout.addRow(button_box)
        self.setLayout(layout)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
