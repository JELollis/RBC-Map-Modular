from imports import *
from constants import *
from directories import *

# -----------------------
# Shops/Guilds Dialog
# -----------------------

class ShopsGuildsDialog(QDialog):
    """
    Dialog for selecting a shop or guild as the destination.
    """

    def __init__(self, parent=None):
        """
        Initialize the Shops/Guilds dialog.

        Args:
            parent (QWidget): The parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle('Select Shops or Guilds')
        self.setFixedSize(300, 400)

        layout = QVBoxLayout(self)

        self.is_shop = True
        self.selected_name = None

        self.shop_guild_combo = QComboBox(self)
        self.shop_guild_combo.addItems(['Shops', 'Guilds'])
        self.shop_guild_combo.currentIndexChanged.connect(self.update_list)
        layout.addWidget(self.shop_guild_combo)

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        buttons_layout = QHBoxLayout()

        select_button = QPushButton('Select', self)
        select_button.clicked.connect(self.accept)
        buttons_layout.addWidget(select_button)

        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

        self.update_list()

    def update_list(self):
        """
        Update the list of shops or guilds based on the selected category.
        """
        self.list_widget.clear()
        self.is_shop = self.shop_guild_combo.currentText() == 'Shops'
        items = shops_coordinates if self.is_shop else guilds_coordinates
        for name in items.keys():
            self.list_widget.addItem(QListWidgetItem(name))

    def accept(self):
        """
        Accept the dialog and set the selected shop or guild.
        """
        current_item = self.list_widget.currentItem()
        if current_item:
            self.selected_name = current_item.text()
        super().accept()
