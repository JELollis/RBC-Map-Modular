from imports import *
from constants import *
from directories import *

class CSSCustomizationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSS Customization")
        self.setMinimumSize(600, 400)
        self.parent = parent  # Reference to RBCCommunityMap

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
        """Add a new tab for a specific category of CSS customizations."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        for item in css_items:
            item_layout = QHBoxLayout()

            label = QLabel(item)
            label.setFixedWidth(200)  # Increased width to accommodate longer selectors

            # Preview square
            preview_label = QLabel()
            preview_label.setFixedSize(50, 20)
            preview_label.setStyleSheet("border: 1px solid black;")

            color_button = QPushButton("Pick Color")
            color_button.clicked.connect(lambda _, i=item, p=preview_label: self.pick_color(i, p))

            image_button = None
            if "TD" in item or "TABLE" in item or "DIV" in item:  # Add image picker for elements that typically use backgrounds
                image_button = QPushButton("Pick Image")
                image_button.clicked.connect(lambda _, i=item, p=preview_label: self.pick_image(i, p))
                item_layout.addWidget(image_button)

            item_layout.addWidget(label)
            item_layout.addWidget(preview_label)
            item_layout.addWidget(color_button)

            layout.addLayout(item_layout)

        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, title)
        self.tabs[title] = tab

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
