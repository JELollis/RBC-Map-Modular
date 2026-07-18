from imports import *
from constants import *


class CSSCustomizationDialog(QDialog):
    """
    Two-mode CSS customization dialog.

    - Simple Mode: GUI controls for non-CSS users
    - Advanced Mode: Full raw CSS editor

    CSS text is the single source of truth.
    Database writes occur ONLY on Apply.
    """

    SIMPLE = 0
    ADVANCED = 1

    def __init__(
            self,
            parent: QWidget | None = None,
            current_profile: str | None = None,
            color_mappings: dict | None = None,
    ) -> None:
        super().__init__(parent)

        self.parent = parent
        self.color_mappings = color_mappings or {}
        self.current_profile = current_profile or self._load_current_profile()

        self.setWindowTitle("CSS Customization")
        self.setWindowIcon(APP_ICON)
        self.resize(900, 600)

        # ---- CSS state ----
        self._original_css = self._load_css_from_db(self.current_profile)
        self._working_css = self._original_css

        self._build_ui()

        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

        logging.debug(
            "CSSCustomizationDialog initialized (profile=%s)",
            self.current_profile,
        )

    # =====================================================
    # UI
    # =====================================================

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # ---- Profile + Mode Bar ----
        top_bar = QHBoxLayout()

        top_bar.addWidget(QLabel("Profile:"))

        self.profile_dropdown = QComboBox()
        self._load_profiles()
        self.profile_dropdown.setCurrentText(self.current_profile)
        self.profile_dropdown.currentTextChanged.connect(self._on_profile_changed)
        top_bar.addWidget(self.profile_dropdown)

        new_btn = QPushButton("New")
        new_btn.clicked.connect(self._create_profile)
        top_bar.addWidget(new_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_profile)
        top_bar.addWidget(delete_btn)

        top_bar.addStretch()

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["Simple", "Advanced"])
        self.mode_selector.currentIndexChanged.connect(self._switch_mode)
        top_bar.addWidget(QLabel("Mode:"))
        top_bar.addWidget(self.mode_selector)

        layout.addLayout(top_bar)

        # ---- Editor Stack ----
        self.editor_stack = QStackedWidget()

        self.simple_editor = QWidget()
        self.advanced_editor = QTextEdit()

        self._build_simple_editor()
        self._build_advanced_editor()

        self.editor_stack.addWidget(self.simple_editor)
        self.editor_stack.addWidget(self.advanced_editor)

        layout.addWidget(self.editor_stack)

        # ---- Buttons ----
        button_bar = QHBoxLayout()

        load_btn = QPushButton("Load .css")
        load_btn.clicked.connect(self._load_css_file)
        button_bar.addWidget(load_btn)

        save_btn = QPushButton("Save .css")
        save_btn.clicked.connect(self._save_css_file)
        button_bar.addWidget(save_btn)

        button_bar.addStretch()

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_changes)
        button_bar.addWidget(apply_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_bar.addWidget(cancel_btn)

        layout.addLayout(button_bar)

        # Start in Simple Mode
        self._switch_mode(self.SIMPLE)

    # =====================================================
    # Simple Mode (GUI)
    # =====================================================

    def _build_simple_editor(self) -> None:
        layout = QFormLayout(self.simple_editor)

        bg_btn = QPushButton("Change Background Color")
        bg_btn.clicked.connect(
            lambda: self._pick_color("BODY", "background-color")
        )

        text_btn = QPushButton("Change Text Color")
        text_btn.clicked.connect(
            lambda: self._pick_color("BODY", "color")
        )

        link_btn = QPushButton("Change Link Color")
        link_btn.clicked.connect(
            lambda: self._pick_color("A", "color")
        )

        layout.addRow("Page Background:", bg_btn)
        layout.addRow("Text Color:", text_btn)
        layout.addRow("Link Color:", link_btn)

        note = QLabel(
            "Simple Mode modifies common visual elements safely.\n"
            "Switch to Advanced Mode for full control."
        )
        note.setWordWrap(True)
        layout.addRow(note)

    def _pick_color(self, selector: str, prop: str) -> None:
        color = QColorDialog.getColor(self)
        if not color.isValid():
            return

        self._set_css_property(selector, prop, color.name())
        self._sync_advanced_editor()

    # =====================================================
    # Advanced Mode (Raw CSS)
    # =====================================================

    def _build_advanced_editor(self) -> None:
        self.advanced_editor.setFontFamily("Courier")
        self.advanced_editor.setFontPointSize(10)
        self.advanced_editor.setPlainText(self._working_css)
        self.advanced_editor.textChanged.connect(self._on_advanced_changed)

    def _on_advanced_changed(self) -> None:
        self._working_css = self.advanced_editor.toPlainText()

    def _sync_advanced_editor(self) -> None:
        self.advanced_editor.blockSignals(True)
        self.advanced_editor.setPlainText(self._working_css)
        self.advanced_editor.blockSignals(False)

    # =====================================================
    # Mode Switching
    # =====================================================

    def _switch_mode(self, index: int) -> None:
        self.editor_stack.setCurrentIndex(index)
        if index == self.ADVANCED:
            self._sync_advanced_editor()

    # =====================================================
    # CSS Manipulation (Core Helper)
    # =====================================================

    def _set_css_property(
            self,
            selector: str,
            property_name: str,
            value: str,
    ) -> None:
        """
        Insert or update a single CSS property in a selector block
        without disturbing other rules.
        """
        css = self._working_css

        block_re = re.compile(
            rf"({re.escape(selector)}\s*\{{)([^}}]*)(\}})",
            re.IGNORECASE | re.MULTILINE,
            )

        match = block_re.search(css)

        if match:
            before, body, after = match.groups()

            prop_re = re.compile(
                rf"{re.escape(property_name)}\s*:\s*[^;]+;",
                re.IGNORECASE,
            )

            if prop_re.search(body):
                body = prop_re.sub(
                    f"{property_name}: {value};",
                    body,
                )
            else:
                body = body.rstrip() + f"\n  {property_name}: {value};"

            css = css[: match.start()] + before + body + after + css[match.end():]

        else:
            css += f"\n{selector} {{\n  {property_name}: {value};\n}}\n"

        self._working_css = css

    # =====================================================
    # Apply / Cancel
    # =====================================================

    def _apply_changes(self) -> None:
        css = self._working_css.strip()

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()

                # Clear existing rules
                cur.execute(
                    "DELETE FROM custom_css WHERE profile_name = ?",
                    (self.current_profile,),
                )

                rules = re.findall(
                    r"([^{]+){([^}]+)}",
                    css,
                    re.DOTALL,
                )

                cur.executemany(
                    """
                    INSERT INTO custom_css (profile_name, element, value)
                    VALUES (?, ?, ?)
                    """,
                    [
                        (self.current_profile, sel.strip(), body.strip())
                        for sel, body in rules
                    ],
                )

                cur.execute(
                    """
                    INSERT OR REPLACE INTO settings (setting_name, setting_value)
                    VALUES ('css_profile', ?)
                    """,
                    (self.current_profile,),
                )

                conn.commit()

            if self.parent:
                parent = cast("MainWindowType", self.parent)
                parent.current_css_profile = self.current_profile
                parent.apply_custom_css(css)
                parent.website_frame.reload()

            self.accept()
            logging.info("CSS applied successfully")

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    # =====================================================
    # File I/O
    # =====================================================

    def _load_css_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load CSS", "", "CSS Files (*.css)"
        )
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self._working_css = f.read()
                    self._sync_advanced_editor()
            except IOError as e:
                QMessageBox.critical(self, "Error", str(e))

    def _save_css_file(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSS", "", "CSS Files (*.css)"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self._working_css)
            except IOError as e:
                QMessageBox.critical(self, "Error", str(e))

    # =====================================================
    # Profile Handling
    # =====================================================

    def _load_current_profile(self) -> str:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT setting_value FROM settings WHERE setting_name = 'css_profile'"
                )
                row = cur.fetchone()
                return row[0] if row else "Default"
        except sqlite3.Error:
            return "Default"

    def _load_profiles(self) -> None:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("SELECT profile_name FROM css_profiles")
                profiles = [r[0] for r in cur.fetchall()]
            self.profile_dropdown.clear()
            self.profile_dropdown.addItems(profiles)
        except sqlite3.Error as e:
            logging.error("Failed to load CSS profiles: %s", e)

    def _create_profile(self) -> None:
        name, ok = QInputDialog.getText(self, "New Profile", "Profile name:")
        if ok and name:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT OR IGNORE INTO css_profiles (profile_name) VALUES (?)",
                        (name,),
                    )
                    conn.commit()
                self._load_profiles()
                self.profile_dropdown.setCurrentText(name)
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", str(e))

    def _delete_profile(self) -> None:
        profile = self.profile_dropdown.currentText()
        if profile == "Default":
            QMessageBox.warning(self, "Warning", "Default profile cannot be deleted.")
            return

        if QMessageBox.question(
                self,
                "Confirm",
                f"Delete profile '{profile}'?",
        ) != QMessageBox.StandardButton.Yes:
            return

        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM css_profiles WHERE profile_name = ?",
                    (profile,),
                )
                cur.execute(
                    "DELETE FROM custom_css WHERE profile_name = ?",
                    (profile,),
                )
                conn.commit()
            self._load_profiles()
            self.profile_dropdown.setCurrentText("Default")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    def _on_profile_changed(self, profile: str) -> None:
        self.current_profile = profile
        self._original_css = self._load_css_from_db(profile)
        self._working_css = self._original_css
        self._sync_advanced_editor()

    def _load_css_from_db(self, profile: str) -> str:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT element, value FROM custom_css WHERE profile_name = ?",
                    (profile,),
                )
                return "\n".join(
                    f"{sel} {{ {val} }}"
                    for sel, val in cur.fetchall()
                )
        except sqlite3.Error:
            return ""
