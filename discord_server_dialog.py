from imports import *
from constants import *
from directories import *

# -----------------------
# Discord Menu
# -----------------------

class DiscordServerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Community Discord Servers")
        self.setMinimumSize(400, 300)
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, invite_link FROM discord_servers")
            servers = cursor.fetchall()

        for name, link in servers:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, url=link: webbrowser.open(url))
            layout.addWidget(btn)
