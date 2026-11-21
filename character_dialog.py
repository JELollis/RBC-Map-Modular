from imports import *
from constants import *
from directories import *

# -----------------------
# Character Dialog Class
# -----------------------
class CharacterDialog(QDialog):
    """
    A dialog for adding or modifying a character.

    This dialog provides a simple interface for entering or editing the name and password
    of a character. It can be used to add a new character or modify an existing one.
    """

    def __init__(self, parent=None, character=None):
        """
        Initialize the character dialog.

        Args:
            parent (QWidget): The parent widget for this dialog.
            character (dict, optional): A dictionary containing the character's information.
                                        If provided, the dialog will be pre-filled with this data.
                                        Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Character")

        # Create input fields for the character's name and password
        self.name_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)  # Hide the password text

        # If a character is provided, pre-fill the fields with its data
        if character:
            self.name_edit.setText(character['name'])
            self.password_edit.setText(character['password'])

        # Set up the form layout with labels and input fields
        layout = QFormLayout()
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Password:", self.password_edit)

        # Create OK and Cancel buttons
        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)

        # Add the buttons to the layout
        layout.addRow(button_box)
        self.setLayout(layout)

        # Connect the buttons to the dialog's accept and reject methods
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
