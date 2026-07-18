from imports import *
from constants import *


class PowersDialog(QDialog):
    """
    Dialog displaying power information with destination-setting functionality.
    """

    def __init__(
            self,
            parent: QWidget,
            character_x: int,
            character_y: int,
            db_path: str,
            color_mappings: dict | None = None,
    ) -> None:
        super().__init__(parent)

        self.parent = cast("MainWindowType", parent)
        self.character_x = character_x
        self.character_y = character_y
        self.db_path = db_path
        self.color_mappings = color_mappings or {}

        self.setWindowTitle("Powers Information")
        self.setWindowIcon(APP_ICON)
        self.setMinimumSize(600, 400)

        self._open_db()
        self._build_ui()

        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

        self.load_powers()
        self._load_guild_move_time()
        self._start_timer()

        logging.debug(
            "PowersDialog initialized at (%d, %d)",
            character_x,
            character_y,
        )

    # =====================================================
    # Database
    # =====================================================

    def _open_db(self) -> None:
        try:
            self.db_connection = sqlite3.connect(self.db_path)
        except sqlite3.Error as exc:
            logging.error("Failed to connect to database: %s", exc)
            self.db_connection = None

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(self) -> None:
        main_layout = QHBoxLayout(self)

        # ---- Power list ----
        self.powers_list = QListWidget()
        self.powers_list.itemClicked.connect(self.load_power_info)
        main_layout.addWidget(self.powers_list)

        # ---- Details panel ----
        self.details_panel = QVBoxLayout()

        self.guild_countdown_label = QLabel("Guilds move time unknown.")
        self.guild_countdown_label.setAlignment(Qt.AlignHCenter)
        self.guild_countdown_label.setStyleSheet(
            "font-size: 9pt; color: gray; margin-bottom: 4px;"
        )
        self.details_panel.addWidget(self.guild_countdown_label)

        self.power_name_label = self._create_labeled_field("Power")
        self.guild_label = self._create_labeled_field("Guild")
        self.cost_label = self._create_labeled_field("Cost")
        self.quest_info_text = self._create_labeled_field(
            "Quest Info", QTextEdit
        )
        self.skill_info_text = self._create_labeled_field(
            "Skill Info", QTextEdit
        )

        self.set_destination_button = QPushButton("Set Destination")
        self.set_destination_button.setEnabled(False)
        self.set_destination_button.clicked.connect(self.set_destination)
        self.details_panel.addWidget(self.set_destination_button)

        main_layout.addLayout(self.details_panel)
        self.setLayout(main_layout)

    T = TypeVar("T", QLabel, QTextEdit)

    def _create_labeled_field(
            self,
            label_text: str,
            widget_type: Type[T] = QLabel,
    ) -> T:
        label = QLabel(f"<b>{label_text}:</b>", self)
        widget = widget_type(self)
        if isinstance(widget, QTextEdit):
            widget.setReadOnly(True)
        self.details_panel.addWidget(label)
        self.details_panel.addWidget(widget)
        return widget

    # =====================================================
    # Power Loading
    # =====================================================

    def load_powers(self) -> None:
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                "SELECT name FROM powers ORDER BY name ASC"
            )
            for (name,) in cursor.fetchall():
                self.powers_list.addItem(name)
            logging.debug(
                "Loaded %d powers",
                self.powers_list.count(),
            )
        except sqlite3.Error as exc:
            logging.error("Failed to load powers: %s", exc)
            QMessageBox.critical(
                self,
                "Database Error",
                "Failed to load powers",
            )

    def load_power_info(self, item: QListWidgetItem) -> None:
        power_name = item.text()

        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                SELECT name, guild, cost, quest_info, skill_info
                FROM powers
                WHERE name = ?
                """,
                (power_name,),
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("No power details")

            name, guild, cost, quest, skill = row

            self.power_name_label.setText(f"<b>Power:</b> {name}")
            self.guild_label.setText(
                f"<b>Guild:</b> {guild or 'Unknown'}"
            )
            self.cost_label.setText(
                f"<b>Cost:</b> {cost or 'Unknown'} coins"
            )
            self.quest_info_text.setPlainText(quest or "None")
            self.skill_info_text.setPlainText(skill or "None")

            self._resolve_destination_for_power(name, guild)

        except (sqlite3.Error, ValueError) as exc:
            logging.error(
                "Failed to load power info for %s: %s",
                power_name,
                exc,
            )
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to load details for '{power_name}'",
            )

    # =====================================================
    # Destination Resolution
    # =====================================================

    def _resolve_destination_for_power(
            self,
            power_name: str,
            guild: str | None,
    ) -> None:
        if power_name == "Battle Cloak":
            self._enable_nearest_peacekeeper_mission()
            return

        if not guild:
            self.set_destination_button.setEnabled(False)
            return

        cursor = self.db_connection.cursor()
        cursor.execute(
            """
            SELECT c.Coordinate, r.Coordinate
            FROM guilds g
            JOIN columns c ON g.Column = c.Name
            JOIN rows r ON g.Row = r.Name
            WHERE g.Name = ?
            """,
            (guild,),
        )

        if row := cursor.fetchone():
            self._configure_destination_button(guild, row[0], row[1])
        else:
            self.set_destination_button.setEnabled(False)

    def _enable_nearest_peacekeeper_mission(self) -> None:
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(
                """
                SELECT c.Coordinate, r.Coordinate
                FROM columns c
                JOIN rows r
                WHERE (c.Name = 'Emerald' AND r.Name IN ('67th', '33rd'))
                   OR (c.Name = 'Unicorn' AND r.Name = '33rd')
                """
            )
            missions = cursor.fetchall()

            if missions:
                closest = min(
                    missions,
                    key=lambda m: max(
                        abs(m[0] - self.character_x),
                        abs(m[1] - self.character_y),
                    ),
                )
                self._configure_destination_button(
                    "Peacekeeper's Mission",
                    closest[0],
                    closest[1],
                )
            else:
                self.set_destination_button.setEnabled(False)

        except sqlite3.Error as exc:
            logging.error(
                "Failed to find Peacekeeper's Mission: %s",
                exc,
            )
            self.set_destination_button.setEnabled(False)

    def _configure_destination_button(
            self,
            guild: str,
            col: int | str | None,
            row: int | str | None,
    ) -> None:
        try:
            col_val = int(col)
            row_val = int(row)
        except (TypeError, ValueError):
            self.set_destination_button.setEnabled(False)
            return

        self.set_destination_button.setEnabled(True)
        self.set_destination_button.setProperty("guild", guild)
        self.set_destination_button.setProperty("Column", col_val)
        self.set_destination_button.setProperty("Row", row_val)

    # =====================================================
    # Destination Action
    # =====================================================

    def set_destination(self) -> None:
        guild = self.set_destination_button.property("guild")
        col = self.set_destination_button.property("Column")
        row = self.set_destination_button.property("Row")

        if not guild or not self.parent.selected_character:
            QMessageBox.warning(
                self,
                "Error",
                "No character selected or invalid destination",
            )
            return

        character_id = self.parent.selected_character["id"]

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO destinations
                    (character_id, col, row, timestamp)
                    VALUES (?, ?, ?, datetime('now'))
                    """,
                    (character_id, col, row),
                )
                conn.commit()

            self.parent.destination = (col, row)
            self.parent.update_minimap()

            QMessageBox.information(
                self,
                "Success",
                f"Destination set to {guild} at ({col}, {row})",
            )

        except sqlite3.Error as exc:
            logging.error("Failed to set destination: %s", exc)
            QMessageBox.critical(
                self,
                "Database Error",
                "Failed to set destination",
            )

    # =====================================================
    # Guild Timer
    # =====================================================

    def _start_timer(self) -> None:
        self.guild_timer = QTimer(self)
        self.guild_timer.timeout.connect(self.update_guild_countdown)
        self.guild_timer.start(1000)

    def _load_guild_move_time(self) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT next_update
                    FROM guilds
                    WHERE next_update IS NOT NULL
                    ORDER BY next_update ASC
                    LIMIT 1
                    """
                )
                row = cursor.fetchone()
                if row:
                    self.next_guild_update = datetime.strptime(
                        row[0], "%Y-%m-%d %H:%M:%S"
                    ).replace(tzinfo=timezone.utc)
                else:
                    self.next_guild_update = None
        except Exception:
            self.next_guild_update = None

    def update_guild_countdown(self) -> None:
        now = datetime.now(timezone.utc)
        if self.next_guild_update:
            remaining = max(
                timedelta(0), self.next_guild_update - now
            )
            days = remaining.days
            hours, rem = divmod(remaining.seconds, 3600)
            minutes, seconds = divmod(rem, 60)
            text = (
                f"Guilds move at "
                f"{self.next_guild_update.strftime('%Y-%m-%d %H:%M:%S UTC')} "
                f"or in {days}d {hours}h {minutes}m {seconds}s"
            )
        else:
            text = "Guilds move time unknown."

        self.guild_countdown_label.setText(text)

    # =====================================================
    # Cleanup
    # =====================================================

    def closeEvent(self, event):
        """
        Defensive close to avoid crashes when cursor/conn failed or were assigned incorrectly.
        """
        for attr in ("cursor", "conn", "connection"):
            obj = getattr(self, attr, None)
            if obj is None:
                continue
            try:
                close = getattr(obj, "close", None)
                if callable(close):
                    close()
            except Exception:
                pass
        event.accept()
