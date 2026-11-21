from imports import *
from constants import *
from directories import *

# -----------------------
# CSS Customization Dialog
# -----------------------

class CSSCustomizationDialog(QDialog):
    """
    Dialog for customizing CSS settings for the UI.
    """

    def __init__(self, parent=None) -> None:
        """
        Initialize the CSS customization dialog.

        Args:
            parent: Parent widget (optional).
        """
        super().__init__(parent)
        self.setWindowTitle("CSS Customization")
        self.setMinimumSize(600, 400)
        self.parent = parent

        self.initialize_css_table()

        self.tab_widget = QTabWidget(self)
        self.tabs = {}
        self.add_tab("General", [
            "BODY", "H1", "DIV", "P", "A", "FORM", "UL", "DIV.spacey", ".head", "DIV.asubhead", "DIV.sb"
        ])
        self.add_tab("Tables", [
            "TD", "TD.cityblock", "TD.intersect", "TD.street", "TD.city", "TABLE.textad", "TABLE.hiscore",
            "TABLE.hiscore tr:first-child", "TABLE.hiscore tr:not(:first-child) td", "TD.headline", "TD.text",
            "TD.link", "TABLE.at", "TABLE.at TD", "TABLE.at TD.ahead", "TABLE.battle", "TABLE.battle TD",
            "TABLE.battle TD.n", "TABLE.battle TD.f", "TABLE.battle TD.e"
        ])
        self.add_tab("Text", [
            "SPAN.intersect", "SPAN.transit", "SPAN.arena", "SPAN.pub", "SPAN.bank", "SPAN.shop",
            "SPAN.grave", "SPAN.pk", "SPAN.lair", "SPAN.alchemy", "SPAN.sever", "SPAN.bind", "SPAN.human",
            "SPAN.vhuman", "SPAN.phuman", "SPAN.whuman", "SPAN.object", "P.ans", "UL.possessions",
            ".pansy", ".cloak", ".rich", ".mh"
        ])
        self.add_tab("Miscellaneous", ["#mo"])

        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save and Apply", self)
        self.save_button.clicked.connect(self.save_and_apply_changes)
        self.upload_button = QPushButton("Upload CSS File", self)
        self.upload_button.clicked.connect(self.upload_css_file)
        self.clear_button = QPushButton("Clear All Customizations", self)
        self.clear_button.clicked.connect(self.clear_all_customizations)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.clear_button)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.load_existing_customizations()
        logging.debug("CSS customization dialog initialized")

    def initialize_css_table(self) -> None:
        """Initialize or verify the custom_css table in the database."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS custom_css (
                        element TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)
                conn.commit()
            logging.debug("Custom CSS table verified")
        except sqlite3.Error as e:
            logging.error(f"Failed to initialize custom_css table: {e}")

    def add_tab(self, title: str, css_items: list[str]) -> None:
        """Add a tab for CSS customization with aligned headers and controls."""
        tab = QWidget(self)
        main_layout = QVBoxLayout(tab)
        grid_layout = QGridLayout()

        headers = ["Element", "Image", "Color", "Font", "Size", "Border", "Radius", "Shadow", "Custom CSS", "Reset"]
        column_widths = [150, 80, 80, 120, 50, 60, 60, 80, 180, 80]
        for col, (header, width) in enumerate(zip(headers, column_widths)):
            label = QLabel(header, tab)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-weight: bold; padding: 5px; border-bottom: 2px solid gray;")
            label.setFixedWidth(width)
            grid_layout.addWidget(label, 0, col)
            grid_layout.setColumnMinimumWidth(col, width)

        for row, item in enumerate(css_items, 1):
            label = QLabel(item, tab)
            label.setFixedWidth(column_widths[0])
            preview = QLabel(tab)
            preview.setFixedSize(50, 20)
            preview.setStyleSheet("border: 1px solid black;")

            image_btn = QPushButton("Pick", tab)
            image_btn.clicked.connect(lambda _, i=item, p=preview: self.pick_image(i, p))
            color_btn = QPushButton("Pick", tab)
            color_btn.clicked.connect(lambda _, i=item, p=preview: self.pick_color(i, p))
            font_combo = QFontComboBox(tab)
            font_combo.currentFontChanged.connect(lambda f, i=item: self.save_css_item(i, f'font-family: {f.family()};'))
            size_spin = QSpinBox(tab)
            size_spin.setRange(8, 32)
            size_spin.setValue(14)
            size_spin.valueChanged.connect(lambda s, i=item: self.save_css_item(i, f'font-size: {s}px;'))
            border_spin = QSpinBox(tab)
            border_spin.setRange(0, 10)
            border_spin.valueChanged.connect(lambda w, i=item: self.save_css_item(i, f'border-width: {w}px;'))
            radius_spin = QSpinBox(tab)
            radius_spin.setRange(0, 50)
            radius_spin.valueChanged.connect(lambda r, i=item: self.save_css_item(i, f'border-radius: {r}px;'))
            shadow_btn = QPushButton("Set", tab)
            shadow_btn.clicked.connect(lambda _, i=item: self.pick_box_shadow(i))
            css_input = QLineEdit(tab)
            css_input.setPlaceholderText("Custom CSS...")
            css_input.textChanged.connect(lambda t, i=item: self.save_css_item(i, t))
            reset_btn = QPushButton("Reset", tab)
            reset_btn.clicked.connect(lambda _, i=item, p=preview: self.reset_css_item(i, p))

            grid_layout.addWidget(label, row, 0)
            grid_layout.addWidget(image_btn, row, 1)
            grid_layout.addWidget(color_btn, row, 2)
            grid_layout.addWidget(font_combo, row, 3)
            grid_layout.addWidget(size_spin, row, 4)
            grid_layout.addWidget(border_spin, row, 5)
            grid_layout.addWidget(radius_spin, row, 6)
            grid_layout.addWidget(shadow_btn, row, 7)
            grid_layout.addWidget(css_input, row, 8)
            grid_layout.addWidget(reset_btn, row, 9)
            grid_layout.addWidget(preview, row, 10)  # Preview last for alignment

        main_layout.addWidget(QWidget(tab, layout=grid_layout))
        self.tab_widget.addTab(tab, title)
        self.tabs[title] = tab
        logging.debug(f"Added tab '{title}' with {len(css_items)} items")

    def pick_box_shadow(self, css_item: str) -> None:
        """Open a dialog to configure box-shadow for a CSS item."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Box Shadow Settings")
        layout = QVBoxLayout(dialog)

        h_offset = QSpinBox(dialog); h_offset.setRange(-20, 20)
        v_offset = QSpinBox(dialog); v_offset.setRange(-20, 20)
        blur = QSpinBox(dialog); blur.setRange(0, 30); blur.setValue(5)
        spread = QSpinBox(dialog); spread.setRange(0, 30)
        color_btn = QPushButton("Pick Color", dialog)
        color = QColor('gray')
        color_btn.clicked.connect(lambda: [setattr(color_btn, 'color', QColorDialog.getColor()),
                                          color_btn.setStyleSheet(f"background-color: {color_btn.color.name()}")])
        apply_btn = QPushButton("Apply", dialog)
        apply_btn.clicked.connect(lambda: [self.save_css_item(css_item,
            f'box-shadow: {h_offset.value()}px {v_offset.value()}px {blur.value()}px {spread.value()}px {color_btn.color.name()};'),
            dialog.accept()])

        layout.addWidget(QLabel("H Offset", dialog)); layout.addWidget(h_offset)
        layout.addWidget(QLabel("V Offset", dialog)); layout.addWidget(v_offset)
        layout.addWidget(QLabel("Blur", dialog)); layout.addWidget(blur)
        layout.addWidget(QLabel("Spread", dialog)); layout.addWidget(spread)
        layout.addWidget(color_btn); layout.addWidget(apply_btn)
        dialog.exec()

    def pick_color(self, css_item: str, preview: QLabel) -> None:
        """Pick a color and update the CSS item."""
        color = QColorDialog.getColor()
        if color.isValid():
            value = f"background-color: {color.name()};"
            self.save_css_item(css_item, value)
            preview.setStyleSheet(value)
            logging.debug(f"Set color {color.name()} for '{css_item}'")

    def pick_image(self, css_item: str, preview: QLabel) -> None:
        """Pick an image file and apply it as a background."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            value = f"background-image: url('file:///{file_path}'); background-size: cover;"
            self.save_css_item(css_item, value)
            preview.setStyleSheet(value)
            logging.debug(f"Set image {file_path} for '{css_item}'")

    def save_css_item(self, css_item: str, value: str) -> None:
        """Save a CSS customization to the database."""
        if not value.strip():
            return
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO custom_css (element, value) VALUES (?, ?)", (css_item, value))
                conn.commit()
            logging.debug(f"Saved CSS for '{css_item}': {value}")
        except sqlite3.Error as e:
            logging.error(f"Failed to save CSS for '{css_item}': {e}")

    def load_existing_customizations(self) -> None:
        """Load and apply existing CSS customizations to the UI."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT element, value FROM custom_css")
                customizations = dict(cursor.fetchall())

            for tab_title, tab in self.tabs.items():
                grid = tab.layout().itemAt(0).widget().layout()
                for row in range(1, grid.rowCount()):
                    label = grid.itemAtPosition(row, 0).widget()
                    preview = grid.itemAtPosition(row, 10).widget()
                    if label.text() in customizations:
                        preview.setStyleSheet(customizations[label.text()])
            logging.debug(f"Loaded {len(customizations)} CSS customizations")
        except sqlite3.Error as e:
            logging.error(f"Failed to load CSS customizations: {e}")

    def save_and_apply_changes(self) -> None:
        """Save changes and apply CSS to the parent webview."""
        css = self.parent.generate_custom_css()
        if css and self.parent:
            self.apply_custom_css(css)
            self.parent.website_frame.reload()
        self.accept()
        logging.info("CSS changes saved and applied")

    def apply_custom_css(self, css: str | None = None) -> None:
        """Apply CSS to the parent webview (proxy to parent method)."""
        if self.parent:
            self.parent.apply_custom_css(css or self.parent.generate_custom_css())
        else:
            logging.warning("No parent to apply CSS to")

    def generate_custom_css(self) -> str:
        """Generate CSS string from database customizations."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT element, value FROM custom_css")
                return "\n".join(f"{elem} {{ {val} }}" for elem, val in cursor.fetchall())
        except sqlite3.Error as e:
            logging.error(f"Failed to generate CSS: {e}")
            return ""

    def upload_css_file(self) -> None:
        """Upload and apply a CSS file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSS", "", "CSS Files (*.css)")
        if file_path:
            try:
                with open(file_path, "r") as f, sqlite3.connect(DB_PATH) as conn:
                    css = f.read()
                    rules = re.findall(r'([^{]+){([^}]+)}', css, re.DOTALL)
                    cursor = conn.cursor()
                    cursor.executemany("INSERT OR REPLACE INTO custom_css (element, value) VALUES (?, ?)",
                                      [(sel.strip(), prop.strip()) for sel, prop in rules])
                    conn.commit()
                self.load_existing_customizations()
                self.apply_custom_css(css)
                if self.parent:
                    self.parent.website_frame.reload()
                logging.info(f"Uploaded CSS file: {file_path}")
            except (IOError, sqlite3.Error) as e:
                logging.error(f"Failed to upload CSS file: {e}")
                QMessageBox.critical(self, "Error", f"Upload failed: {e}")

    def reset_css_item(self, css_item: str, preview: QLabel) -> None:
        """Reset a specific CSS item to default."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_css WHERE element = ?", (css_item,))
                conn.commit()
            preview.setStyleSheet("")
            logging.debug(f"Reset CSS for '{css_item}'")
        except sqlite3.Error as e:
            logging.error(f"Failed to reset CSS for '{css_item}': {e}")

    def clear_all_customizations(self) -> None:
        """Clear all CSS customizations."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_css")
                conn.commit()
            self.load_existing_customizations()
            self.apply_custom_css("")
            if self.parent:
                self.parent.website_frame.reload()
            logging.info("Cleared all CSS customizations")
        except sqlite3.Error as e:
            logging.error(f"Failed to clear CSS customizations: {e}")
            QMessageBox.critical(self, "Error", "Failed to clear customizations")
