from imports import *
from constants import *

class CSSCustomizationDialog(QDialog):
    def __init__(self, parent: QWidget = None, current_profile: str = None, color_mappings: dict | None = None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.color_mappings = color_mappings or {}
        self.current_profile = current_profile or self.get_current_profile()

        self.setWindowTitle("CSS Customization")
        self.setWindowIcon(APP_ICON)
        self.resize(600, 400)
        self.tabs = {}
        self.setup_ui()
        self.load_existing_customizations()

        if self.color_mappings:
            apply_theme_to_widget(self, self.color_mappings)

        logging.debug(f"CSSCustomizationDialog initialized with profile '{self.current_profile}'")

    def get_current_profile(self) -> str:
        """Retrieve the current CSS profile from settings."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'css_profile'")
                result = cursor.fetchone()
                return result[0] if result else "Default"
        except sqlite3.Error as e:
            logging.error(f"Failed to retrieve current profile: {e}")
            return "Default"

    def update_current_profile(self, profile: str) -> None:
        """Update the css_profile setting in the database."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (setting_name, setting_value) VALUES (?, ?)",
                    ("css_profile", profile)
                )
                conn.commit()
            self.current_profile = profile
            logging.debug(f"Updated css_profile to: {profile}")
        except sqlite3.Error as e:
            logging.error(f"Failed to update css_profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update profile: {e}")

    def setup_ui(self) -> None:
        """Set up the UI for CSS customization."""
        main_layout = QVBoxLayout(self)

        # Profile selection
        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Profile:"))
        self.profile_dropdown = QComboBox()
        self.load_profiles()
        self.profile_dropdown.setCurrentText(self.current_profile)
        self.profile_dropdown.currentTextChanged.connect(self.on_profile_change)
        profile_layout.addWidget(self.profile_dropdown)

        new_profile_btn = QPushButton("New Profile")
        new_profile_btn.clicked.connect(self.create_new_profile)
        profile_layout.addWidget(new_profile_btn)

        delete_profile_btn = QPushButton("Delete Profile")
        delete_profile_btn.clicked.connect(self.delete_profile)
        profile_layout.addWidget(delete_profile_btn)

        main_layout.addLayout(profile_layout)

        # Tabs for CSS categories
        self.tab_widget = QTabWidget()
        self.add_tab("Background", ["BODY"])
        self.add_tab("Text", ["H1", "P", "A", "TD", "DIV"])
        self.add_tab("City Elements", ["TD.cityblock", "TD.intersect", "TD.street", "TD.city"])
        self.add_tab("Special Elements", [
            "SPAN.intersect", "SPAN.transit", "SPAN.pub", "SPAN.bank", "SPAN.shop",
            "SPAN.grave", "SPAN.pk", "SPAN.lair", "SPAN.alchemy"
        ])
        main_layout.addWidget(self.tab_widget)

        # Buttons
        button_layout = QHBoxLayout()
        upload_btn = QPushButton("Upload CSS File")
        upload_btn.clicked.connect(self.upload_css_file)
        button_layout.addWidget(upload_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all_customizations)
        button_layout.addWidget(clear_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.save_and_apply_changes)
        button_layout.addWidget(apply_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # Ensure preview updates even if currentTextChanged isn't triggered
        self.on_profile_change(self.current_profile)

    def on_profile_change(self, profile: str) -> None:
        """Handle profile change: update DB, load styles, apply CSS."""
        if profile != self.current_profile:
            self.update_current_profile(profile)

        self.current_profile = profile
        self.load_existing_customizations()
        css = self.generate_custom_css()

        if css and self.parent:
            parent = cast("MainWindowType", self.parent)
            parent.apply_custom_css(css)
            parent.website_frame.reload()

        logging.info(f"Switched to profile: {profile} and applied CSS")

    def load_profiles(self) -> None:
        """Load available CSS profiles from the database."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT profile_name FROM css_profiles")
                profiles = [row[0] for row in cursor.fetchall()]
            self.profile_dropdown.clear()
            self.profile_dropdown.addItems(profiles)
            logging.debug(f"Loaded {len(profiles)} profiles")
        except sqlite3.Error as e:
            logging.error(f"Failed to load profiles: {e}")
            QMessageBox.critical(self, "Error", "Failed to load profiles")

    def create_new_profile(self) -> None:
        """Create a new CSS profile."""
        profile_name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
        if ok and profile_name:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT OR IGNORE INTO css_profiles (profile_name) VALUES (?)", (profile_name,))
                    conn.commit()
                self.load_profiles()
                self.profile_dropdown.setCurrentText(profile_name)
                self.on_profile_change(profile_name)
                logging.info(f"Created new profile: {profile_name}")
            except sqlite3.Error as e:
                logging.error(f"Failed to create profile: {e}")
                QMessageBox.critical(self, "Error", "Failed to create profile")

    def delete_profile(self) -> None:
        """Delete the selected CSS profile."""
        profile = self.profile_dropdown.currentText()
        if profile == "Default":
            QMessageBox.warning(self, "Warning", "Cannot delete the Default profile")
            return
        # noinspection PyUnresolvedReferences
        reply = QMessageBox.question(self, "Confirm Delete", f"Delete profile '{profile}'?", QMessageBox.Yes | QMessageBox.No)
        # noinspection PyUnresolvedReferences
        if reply == QMessageBox.Yes:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM css_profiles WHERE profile_name = ?", (profile,))
                    conn.commit()
                self.load_profiles()
                self.profile_dropdown.setCurrentText("Default")
                self.on_profile_change("Default")
                logging.info(f"Deleted profile: {profile}")
            except sqlite3.Error as e:
                logging.error(f"Failed to delete profile: {e}")
                QMessageBox.critical(self, "Error", "Failed to delete profile")

    def add_tab(self, tab_title: str, elements: list[str]) -> None:
        """Add a tab for a category of CSS elements."""
        tab = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        grid = QGridLayout(container)

        grid.addWidget(QLabel("Element"), 0, 0)
        grid.addWidget(QLabel("Preview"), 0, 1)
        grid.addWidget(QLabel("Color"), 0, 2)
        grid.addWidget(QLabel("Image"), 0, 3)
        grid.addWidget(QLabel("Shadow"), 0, 4)
        grid.addWidget(QLabel("Reset"), 0, 5)

        for i, element in enumerate(elements, 1):
            label = QLabel(element)
            preview = QLabel("Preview")
            preview.setFixedSize(100, 30)
            preview.setStyleSheet("border: 1px solid black;")
            color_btn = QPushButton("Pick Color")
            color_btn.clicked.connect(lambda _, e=element, p=preview: self.pick_color(e, p))
            image_btn = QPushButton("Pick Image")
            image_btn.clicked.connect(lambda _, e=element, p=preview: self.pick_image(e, p))
            shadow_btn = QPushButton("Add Shadow")
            shadow_btn.clicked.connect(lambda _, e=element: self.add_shadow(e))
            reset_btn = QPushButton("Reset")
            reset_btn.clicked.connect(lambda _, e=element, p=preview: self.reset_css_item(e, p))
            grid.addWidget(label, i, 0)
            grid.addWidget(preview, i, 1)
            grid.addWidget(color_btn, i, 2)
            grid.addWidget(image_btn, i, 3)
            grid.addWidget(shadow_btn, i, 4)
            grid.addWidget(reset_btn, i, 5)

        scroll.setWidget(container)
        tab.setLayout(QVBoxLayout())
        tab.layout().addWidget(scroll)
        self.tab_widget.addTab(tab, tab_title)
        self.tabs[tab_title] = tab
        tab.grid = grid

    def pick_color(self, css_item: str, preview: QLabel) -> None:
        """Open a color picker and apply the selected color."""
        color = QColorDialog.getColor()
        if color.isValid():
            style = f"background-color: {color.name()};"
            preview.setStyleSheet(style)
            self.save_css_item(css_item, style)
            logging.debug(f"Set color for '{css_item}': {color.name()}")

    def pick_image(self, css_item: str, preview: QLabel) -> None:
        """Open a file dialog to select an image and apply it as a background."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            style = f"background-image: url({file_path}); background-size: cover;"
            preview.setStyleSheet(style)
            self.save_css_item(css_item, style)
            logging.debug(f"Set image for '{css_item}': {file_path}")

    def add_shadow(self, css_item: str) -> None:
        """Add a default shadow effect to the element."""
        style = "box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5);"
        self.save_css_item(css_item, style)
        self.load_existing_customizations()
        logging.debug(f"Added shadow to '{css_item}'")

    def save_css_item(self, css_item: str, value: str) -> None:
        """Save a CSS customization to the database under the current profile."""
        if not value.strip():
            return
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO custom_css (profile_name, element, value) VALUES (?, ?, ?)",
                    (self.current_profile, css_item, value)
                )
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Failed to save CSS for '{css_item}': {e}")
            QMessageBox.critical(self, "Error", f"Failed to save CSS: {e}")

    def load_existing_customizations(self) -> None:
        """Load and apply existing CSS customizations for the current profile."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT element, value FROM custom_css WHERE profile_name = ?",
                    (self.current_profile,)
                )
                customizations = dict(cursor.fetchall())

            for tab in self.tabs.values():
                grid = tab.grid
                for row in range(1, grid.rowCount()):
                    label = grid.itemAtPosition(row, 0).widget()
                    preview = grid.itemAtPosition(row, 1).widget()
                    preview.setStyleSheet(customizations.get(label.text(), ""))
        except sqlite3.Error as e:
            logging.error(f"Failed to load CSS customizations: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load customizations: {e}")

    def save_and_apply_changes(self) -> None:
        selected_profile = self.profile_dropdown.currentText()
        self.update_current_profile(selected_profile)
        self.current_profile = selected_profile
        css = self.generate_custom_css()
        if css and self.parent:
            parent = cast("MainWindowType", self.parent)
            parent.current_css_profile = self.current_profile
            parent.apply_custom_css(css)
            parent.website_frame.reload()
        self.accept()
        logging.info("CSS changes saved and applied")

    def generate_custom_css(self) -> str:
        """Generate CSS string from database customizations for the current profile."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT element, value FROM custom_css WHERE profile_name = ?",
                    (self.current_profile,)
                )
                return "\n".join(f"{elem} {{ {val} }}" for elem, val in cursor.fetchall())
        except sqlite3.Error as e:
            logging.error(f"Failed to generate CSS: {e}")
            return ""

    def upload_css_file(self) -> None:
        """Upload and apply a CSS file to the current profile."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSS", "", "CSS Files (*.css)")
        if file_path:
            try:
                with open(file_path, "r") as f, sqlite3.connect(DB_PATH) as conn:
                    css = f.read()
                    rules = re.findall(r'([^{]+){([^}]+)}', css, re.DOTALL)
                    cursor = conn.cursor()
                    cursor.executemany(
                        "INSERT OR REPLACE INTO custom_css (profile_name, element, value) VALUES (?, ?, ?)",
                        [(self.current_profile, sel.strip(), prop.strip()) for sel, prop in rules]
                    )
                    conn.commit()
                self.load_existing_customizations()
                if self.parent:
                    parent = cast("MainWindowType", self.parent)
                    parent.apply_custom_css(css)
                    parent.website_frame.reload()
                logging.info(f"Uploaded CSS file: {file_path} to profile '{self.current_profile}'")
            except (IOError, sqlite3.Error) as e:
                logging.error(f"Failed to upload CSS file: {e}")
                QMessageBox.critical(self, "Error", f"Upload failed: {e}")

    def reset_css_item(self, css_item: str, preview: QLabel) -> None:
        """Reset a specific CSS item to default for the current profile."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM custom_css WHERE profile_name = ? AND element = ?",
                    (self.current_profile, css_item)
                )
                conn.commit()
            preview.setStyleSheet("")
            logging.debug(f"Reset CSS for '{css_item}' in profile '{self.current_profile}'")
        except sqlite3.Error as e:
            logging.error(f"Failed to reset CSS for '{css_item}': {e}")
            QMessageBox.critical(self, "Error", f"Failed to reset CSS: {e}")

    def clear_all_customizations(self) -> None:
        """Clear all CSS customizations for the current profile."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_css WHERE profile_name = ?", (self.current_profile,))
                conn.commit()
            self.load_existing_customizations()
            if self.parent:
                parent = cast("MainWindowType", self.parent)
                parent.apply_custom_css("")
                parent.website_frame.reload()
            logging.info(f"Cleared all CSS customizations for profile '{self.current_profile}'")
        except sqlite3.Error as e:
            logging.error(f"Failed to clear CSS customizations: {e}")
            QMessageBox.critical(self, "Error", "Failed to clear customizations")