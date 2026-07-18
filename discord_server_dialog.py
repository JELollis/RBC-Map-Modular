from imports import *
from constants import *


class DiscordServerDialog(QDialog):
    """
    Read-only dialog listing community Discord servers.

    Each entry opens the server invite link in the default browser.
    """

    def __init__(
            self,
            parent: QWidget | None = None,
            db_path: str = DB_PATH,
            color_mappings: dict | None = None,
    ):
        super().__init__(parent)

        self.db_path = db_path
        self.color_mappings = color_mappings or {}

        self.setWindowTitle("Community Discord Servers")
        self.setMinimumSize(400, 300)
        self.setWindowIcon(APP_ICON)

        self._build_ui()
        self._load_servers()

        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(self) -> None:
        self.layout = QVBoxLayout(self)

        self.info_label = QLabel(
            "Click a server name to open its Discord invite link."
        )
        self.layout.addWidget(self.info_label)

        self.button_container = QVBoxLayout()
        self.layout.addLayout(self.button_container)

        self.layout.addStretch(1)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        self.layout.addWidget(close_btn)

    # =====================================================
    # Data Loading
    # =====================================================

    def _load_servers(self) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name, invite_link FROM discord_servers ORDER BY name ASC"
                )
                servers = cursor.fetchall()

        except sqlite3.Error as exc:
            logging.error(
                "Failed to load Discord servers: %s",
                exc,
            )
            QMessageBox.critical(
                self,
                "Database Error",
                "Unable to load Discord server list.",
            )
            servers = []

        if not servers:
            self._show_empty_state()
            return

        for name, link in servers:
            self._add_server_button(name, link)

    # =====================================================
    # Helpers
    # =====================================================

    def _add_server_button(self, name: str, invite_link: str) -> None:
        btn = QPushButton(name)
        btn.setToolTip(invite_link)
        btn.clicked.connect(
            lambda _, url=invite_link: self._open_link(url)
        )
        self.button_container.addWidget(btn)

    @staticmethod
    def _open_link(url: str) -> None:
        try:
            webbrowser.open(url)
        except Exception as exc:
            logging.error("Failed to open URL %s: %s", url, exc)

    def _show_empty_state(self) -> None:
        label = QLabel(
            "No Discord servers are currently configured."
        )
        label.setAlignment(Qt.AlignHCenter)
        label.setStyleSheet("color: gray;")
        self.button_container.addWidget(label)
