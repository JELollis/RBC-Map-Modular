from imports import *
from constants import *
from directories import *

class CSSCustomizationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSS Customization")
        self.setMinimumSize(600, 400)
        self.parent = parent

        # Initialize database table
        self.initialize_css_table()

        # Tab widget for organizing sections
        self.tab_widget = QTabWidget()
        self.tabs = {}

        # Add tabs with all CSS elements from the website
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
        self.add_tab("Miscellaneous", [
            "#mo"
        ])

        # Control buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save and Apply")
        self.save_button.clicked.connect(self.save_and_apply_changes)
        self.upload_button = QPushButton("Upload CSS File")
        self.upload_button.clicked.connect(self.upload_css_file)
        self.clear_button = QPushButton("Clear All Customizations")
        self.clear_button.clicked.connect(self.clear_all_customizations)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.clear_button)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # Load existing customizations
        self.load_existing_customizations()

    def initialize_css_table(self):
        """Initialize the custom_css table in the database."""
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
                logging.info("Custom CSS table initialized or verified.")
        except sqlite3.Error as e:
            logging.error(f"Error initializing custom_css table: {e}")

    def add_tab(self, title, css_items):
        """Add a new tab for a specific category of CSS customizations with properly aligned headers."""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)

        # Grid Layout for Headers and Rows
        grid_layout = QGridLayout()

        # Define column headers and explicit widths
        headers = ["Element", "Pick Image", "Pick Color", "Font", "Size", "Border", "Radius", "Box Shadow",
                   "Custom CSS", "Reset"]
        column_widths = [150, 100, 100, 120, 50, 60, 60, 100, 180, 80]

        # Add headers to the grid (Row 0)
        for col, (header, width) in enumerate(zip(headers, column_widths)):
            label = QLabel(header)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-weight: bold; padding: 5px; border-bottom: 2px solid gray;")
            label.setFixedWidth(width)
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            grid_layout.addWidget(label, 0, col)
            grid_layout.setColumnMinimumWidth(col, width)
            grid_layout.setColumnStretch(col, 0)

        # Add CSS items (Starting from Row 1)
        for row, item in enumerate(css_items, start=1):
            label = QLabel(item)
            label.setFixedWidth(column_widths[0])

            # Add a preview label to display selected color/image
            preview_label = QLabel()
            preview_label.setFixedSize(50, 20)
            preview_label.setStyleSheet("border: 1px solid black;")

            image_button = QPushButton("Pick Image")
            image_button.clicked.connect(lambda _, i=item, p=preview_label: self.pick_image(i, p))

            color_button = QPushButton("Pick Color")
            color_button.clicked.connect(lambda _, i=item, p=preview_label: self.pick_color(i, p))

            font_family_input = QFontComboBox()
            font_family_input.currentFontChanged.connect(
                lambda font, i=item: self.save_css_item(i, f'font-family: {font.family()};'))

            font_size_input = QSpinBox()
            font_size_input.setRange(8, 32)
            font_size_input.setValue(14)
            font_size_input.valueChanged.connect(lambda size, i=item: self.save_css_item(i, f'font-size: {size}px;'))

            border_width_input = QSpinBox()
            border_width_input.setRange(0, 10)
            border_width_input.setValue(1)
            border_width_input.valueChanged.connect(
                lambda width, i=item: self.save_css_item(i, f'border-width: {width}px;'))

            border_radius_input = QSpinBox()
            border_radius_input.setRange(0, 50)
            border_radius_input.setValue(0)
            border_radius_input.valueChanged.connect(
                lambda radius, i=item: self.save_css_item(i, f'border-radius: {radius}px;'))

            shadow_button = QPushButton("Box Shadow")
            shadow_button.clicked.connect(lambda _, i=item: self.pick_box_shadow(i))

            css_input = QLineEdit()
            css_input.setPlaceholderText("Enter custom CSS...")
            css_input.textChanged.connect(lambda text, i=item: self.save_css_item(i, text))

            reset_button = QPushButton("Reset")
            reset_button.clicked.connect(lambda _, i=item, p=preview_label: self.reset_css_item(i, p))

            # Add widgets to the grid, ensuring alignment
            grid_layout.addWidget(label, row, 0)
            grid_layout.addWidget(image_button, row, 1)
            grid_layout.addWidget(color_button, row, 2)
            grid_layout.addWidget(preview_label, row, 3)  # Display the preview box
            grid_layout.addWidget(font_family_input, row, 4)
            grid_layout.addWidget(font_size_input, row, 5)
            grid_layout.addWidget(border_width_input, row, 6)
            grid_layout.addWidget(border_radius_input, row, 7)
            grid_layout.addWidget(shadow_button, row, 8)
            grid_layout.addWidget(css_input, row, 9)
            grid_layout.addWidget(reset_button, row, 10)

        # Apply final layout adjustments
        grid_widget = QWidget()
        grid_widget.setLayout(grid_layout)

        main_layout.addWidget(grid_widget)
        tab.setLayout(main_layout)
        self.tab_widget.addTab(tab, title)
        self.tabs[title] = tab

    def pick_box_shadow(self, css_item):
        """Opens a dialog to set box-shadow values."""
        shadow_dialog = QDialog(self)
        shadow_dialog.setWindowTitle("Box Shadow Settings")
        shadow_layout = QVBoxLayout()

        h_offset = QSpinBox()
        h_offset.setRange(-20, 20)
        h_offset.setValue(0)

        v_offset = QSpinBox()
        v_offset.setRange(-20, 20)
        v_offset.setValue(0)

        blur_radius = QSpinBox()
        blur_radius.setRange(0, 30)
        blur_radius.setValue(5)

        spread_radius = QSpinBox()
        spread_radius.setRange(0, 30)
        spread_radius.setValue(0)

        color_picker = QPushButton("Pick Shadow Color")
        color = QColorDialog.getColor()
        color_picker.clicked.connect(lambda: color_picker.setStyleSheet(f"background-color: {color.name()}"))

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(lambda: self.save_css_item(
            css_item,
            f'box-shadow: {h_offset.value()}px {v_offset.value()}px {blur_radius.value()}px {spread_radius.value()}px {color.name()};'
        ))

        shadow_layout.addWidget(QLabel("Horizontal Offset"))
        shadow_layout.addWidget(h_offset)
        shadow_layout.addWidget(QLabel("Vertical Offset"))
        shadow_layout.addWidget(v_offset)
        shadow_layout.addWidget(QLabel("Blur Radius"))
        shadow_layout.addWidget(blur_radius)
        shadow_layout.addWidget(QLabel("Spread Radius"))
        shadow_layout.addWidget(spread_radius)
        shadow_layout.addWidget(color_picker)
        shadow_layout.addWidget(apply_button)

        shadow_dialog.setLayout(shadow_layout)
        shadow_dialog.exec_()

    def pick_color(self, css_item, preview_label):
        """Open a color picker dialog for a specific CSS item."""
        color = QColorDialog.getColor()
        if color.isValid():
            value = f"background-color: {color.name()};"
            self.save_css_item(css_item, value)
            preview_label.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
            logging.info(f"Selected color {color.name()} for {css_item}")

    def pick_image(self, css_item, preview_label):
        """Open a file dialog to select an image for a specific CSS item."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image File", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            value = f"background-image: url('file:///{file_path}'); background-size: cover;"
            self.save_css_item(css_item, value)
            preview_label.setStyleSheet(value)
            logging.info(f"Selected image {file_path} for {css_item}")

    def save_css_item(self, css_item, value):
        """Save the customization for a specific CSS item to the database."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO custom_css (element, value)
                    VALUES (?, ?)
                """, (css_item, value))
                conn.commit()
                logging.info(f"Saved CSS item '{css_item}' with value '{value}' to database.")
        except sqlite3.Error as e:
            logging.error(f"Error saving CSS item: {e}")

    def load_existing_customizations(self):
        """Load existing CSS customizations and update UI preview labels."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT element, value FROM custom_css")
                customizations = cursor.fetchall()

            for element, value in customizations:
                for tab_title, tab_widget in self.tabs.items():
                    layout = tab_widget.layout()
                    for i in range(layout.count()):
                        item_layout = layout.itemAt(i)
                        if item_layout and item_layout.layout() is not None:  # Check if it's a layout
                            sub_layout = item_layout.layout()
                            label = sub_layout.itemAt(0).widget()
                            preview = sub_layout.itemAt(1).widget()
                            if label.text() == element:
                                preview.setStyleSheet(value)
                                break
            logging.info(f"Loaded {len(customizations)} existing CSS customizations.")
        except sqlite3.Error as e:
            logging.error(f"Error loading customizations: {e}")

    def save_and_apply_changes(self):
        """Save changes and apply CSS to the webview."""
        logging.info("Saving and applying CSS customizations...")
        self.generate_custom_css()  # Ensure CSS is saved to the database
        self.apply_custom_css()  # Call the updated method without passing custom_css
        if self.parent:
            self.parent.website_frame.reload()
        self.accept()
        logging.info("CSS customizations saved and applied.")

    def apply_custom_css(self, css=None):
        """Inject the custom CSS into the webview via the parent."""
        if self.parent:
            self.parent.apply_custom_css()  # Call parent's method
        else:
            logging.error("Parent not available. Cannot apply CSS.")

    def generate_custom_css(self):
        """Generate a complete CSS string from saved customizations."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT element, value FROM custom_css")
                customizations = cursor.fetchall()
                css_string = "\n".join([f"{element} {{ {value} }}" for element, value in customizations])
                return css_string
        except sqlite3.Error as e:
            logging.error(f"Error generating custom CSS: {e}")
            return ""

    def upload_css_file(self):
        """Upload an external CSS file and apply it."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSS File", "", "CSS Files (*.css)")
        if file_path:
            try:
                with open(file_path, "r") as file:
                    css_content = file.read()

                # Parse CSS into individual rules
                rules = re.findall(r'([^{]+){([^}]+)}', css_content, re.DOTALL)
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    for selector, properties in rules:
                        selector = selector.strip()
                        value = properties.strip()
                        cursor.execute("""
                            INSERT OR REPLACE INTO custom_css (element, value)
                            VALUES (?, ?)
                        """, (selector, value))
                    conn.commit()

                self.load_existing_customizations()
                self.apply_custom_css(css_content)
                if self.parent:
                    self.parent.website_frame.reload()
                logging.info(f"Uploaded and applied CSS file: {file_path}")
            except Exception as e:
                logging.error(f"Error uploading CSS file: {e}")
                QMessageBox.critical(self, "Error", f"Failed to upload CSS file: {e}")

    def reset_css_item(self, css_item: str, preview_label: QLabel):
        """Resets a specific CSS element to its default state."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_css WHERE element = ?", (css_item,))
                conn.commit()
            preview_label.setStyleSheet("")
            logging.info(f"Reset CSS for {css_item}")
        except sqlite3.Error as e:
            logging.error(f"Error resetting CSS for {css_item}: {e}")

    def clear_all_customizations(self):
        """Clear all saved CSS customizations."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_css")
                conn.commit()
            self.load_existing_customizations()
            self.apply_custom_css("")
            if self.parent:
                self.parent.website_frame.reload()
            logging.info("All CSS customizations cleared.")
        except sqlite3.Error as e:
            logging.error(f"Error clearing customizations: {e}")
            QMessageBox.critical(self, "Error", f"Failed to clear customizations: {e}")
