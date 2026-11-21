from imports import *
from constants import *
from directories import *

# -----------------------
# Character Dialog
# -----------------------

class CharacterDialog(QDialog):
    """
    Dialog for adding or modifying a character.
    """

    def __init__(self, parent=None, character=None):
        """
        Initialize the CharacterDialog.

        Args:
            parent (QWidget): Parent widget.
            character (dict, optional): Character data to populate the fields. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle('Character')
        self.setFixedSize(300, 150)

        layout = QFormLayout(self)

        self.name_edit = QLineEdit(self)
        self.password_edit = QLineEdit(self)
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow('Name:', self.name_edit)
        layout.addRow('Password:', self.password_edit)

        if character:
            self.name_edit.setText(character['name'])
            self.password_edit.setText(character['password'])

        buttons_layout = QHBoxLayout()

        ok_button = QPushButton('OK', self)
        ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_button)

        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addRow(buttons_layout)
