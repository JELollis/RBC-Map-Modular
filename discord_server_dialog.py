from imports import *
from constants import *

class DiscordServerDialog(QDialog):
    def __init__(self, parent=None, color_mappings: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Community Discord Servers")
        self.setMinimumSize(400, 300)
        self.color_mappings = color_mappings or {}

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, invite_link FROM discord_servers")
                servers = cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Failed to load Discord servers: {e}")
            QMessageBox.critical(self, "Database Error", "Unable to load server list.")
            servers = []

        for name, link in servers:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, url=link: webbrowser.open(url))
            layout.addWidget(btn)

        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)