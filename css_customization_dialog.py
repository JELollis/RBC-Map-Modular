from imports import *
from constants import *
from directories import *

class CSSCustomizationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSS Customization")
        self.setMinimumSize(600, 400)

        self.parent = parent  # Reference to the main window for calling refresh_page

        # Tab widget for organizing sections
        self.tab_widget = QTabWidget()
        self.tabs = {}  # To store individual tab widgets by category

        # Add tabs for each CSS category
        self.add_tab("General", ["BODY", "H1", "P", "DIV", "A", "UL", "FORM"])
        self.add_tab("Tables", ["TD.cityblock", "TD.intersect", "TD.street"])
        self.add_tab("Text", ["SPAN.intersect", "SPAN.transit", "SPAN.arena", "SPAN.pub", "SPAN.bank",
                              "SPAN.shop", "SPAN.grave", "SPAN.pk", "SPAN.lair", "SPAN.alchemy"])
        self.add_tab("Miscellaneous", ["SPAN.vhuman", "SPAN.phuman", "SPAN.whuman", "SPAN.object", "#mo"])

        # Control buttons
        self.save_button = QPushButton("Save and Apply")
        self.save_button.clicked.connect(self.save_and_apply_changes)
        self.upload_button = QPushButton("Upload CSS File")
        self.upload_button.clicked.connect(self.upload_css_file)
        self.clear_button = QPushButton("Clear All Customizations")
        self.clear_button.clicked.connect(self.clear_all_customizations)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.clear_button)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def add_tab(self, title, css_items):
        """
        Add a new tab for a specific category of CSS customizations.

        Args:
            title (str): The title of the tab.
            css_items (list): A list of CSS elements to customize in this tab.
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)

        for item in css_items:
            item_layout = QHBoxLayout()

            label = QLabel(item)
            label.setFixedWidth(150)

            color_button = QPushButton("Pick Color")
            color_button.clicked.connect(lambda _, i=item: self.pick_color(i))

            image_button = None
            if "TD" in item:  # Add image picker for applicable elements
                image_button = QPushButton("Pick Image")
                image_button.clicked.connect(lambda _, i=item: self.pick_image(i))
                item_layout.addWidget(image_button)

            item_layout.addWidget(label)
            item_layout.addWidget(color_button)

            layout.addLayout(item_layout)

        layout.addStretch()
        tab.setLayout(layout)
        self.tab_widget.addTab(tab, title)
        self.tabs[title] = tab

    def pick_color(self, css_item):
        """
        Open a color picker dialog for a specific CSS item.

        Args:
            css_item (str): The CSS item to customize.
        """
        color = QColorDialog.getColor()
        if color.isValid():
            logging.info(f"Selected color {color.name()} for {css_item}")
            self.save_css_item(css_item, color.name())

    def pick_image(self, css_item):
        """
        Open a file dialog to select an image for a specific CSS item.

        Args:
            css_item (str): The CSS item to apply a background image to.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image File", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            logging.info(f"Selected image {file_path} for {css_item}")
            self.save_css_item(css_item, f"url('{file_path}')")

    def save_css_item(self, css_item, value):
        """
        Save the customization for a specific CSS item to the database.

        Args:
            css_item (str): The CSS item being customized.
            value (str): The CSS value (e.g., color or background image).
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Create the table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_css (
                    element TEXT PRIMARY KEY, 
                    value TEXT
                )
            """)

            # Insert or replace the CSS customization
            cursor.execute(
                "INSERT OR REPLACE INTO custom_css (element, value) VALUES (?, ?)",
                (css_item, value)
            )

            connection.commit()
            logging.info(f"Saved CSS item '{css_item}' with value '{value}' to the database.")
        except sqlite3.Error as e:
            logging.error(f"Error saving CSS item: {e}")
        finally:
            connection.close()

    def save_and_apply_changes(self):
        """
        Save all changes to the database and apply the CSS to the webpage.
        """
        logging.info("Saving and applying CSS customizations...")

        # Generate the custom CSS string
        custom_css = self.generate_custom_css()

        # Apply the CSS and refresh the page
        self.apply_custom_css(custom_css)
        if self.parent:
            self.parent.refresh_page()

        logging.info("CSS customizations applied and page refreshed.")

    def apply_custom_css(self, css):
        """
        Inject the custom CSS into the webview.

        Args:
            css (str): The CSS string to inject.
        """
        if self.parent and hasattr(self.parent, 'website_frame'):
            logging.info("Injecting the following CSS into the webpage:")
            logging.info(css)  # Log the CSS being applied for debugging

            self.parent.website_frame.page().runJavaScript(f"""
                let styleTag = document.getElementById('custom-css');
                if (!styleTag) {{
                    styleTag = document.createElement('style');
                    styleTag.id = 'custom-css';
                    document.head.appendChild(styleTag);
                }}
                styleTag.innerHTML = `{css}`;
            """)
            logging.info("Custom CSS successfully injected into the webpage.")
        else:
            logging.error("Website frame not found. Cannot apply custom CSS.")

    def generate_custom_css(self):
        """
        Generate a complete CSS string from the saved customizations.

        Returns:
            str: The complete CSS string.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()

            # Fetch saved customizations
            cursor.execute("SELECT element, value FROM custom_css")
            customizations = cursor.fetchall()
            logging.info("Fetched customizations from database:")
            for element, value in customizations:
                logging.info(f"{element}: {value}")

            css_string = "\n".join([f"{element} {{ {value} }}" for element, value in customizations])
            logging.info("Generated CSS string:")
            logging.info(css_string)

            return css_string
        except sqlite3.Error as e:
            logging.error(f"Error generating custom CSS: {e}")
            return ""
        finally:
            connection.close()

    def upload_css_file(self):
        """
        Allow the user to upload an external CSS file and apply it.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSS File", "", "CSS Files (*.css)")
        if file_path:
            with open(file_path, "r") as file:
                css_content = file.read()

            # Save the uploaded CSS to the database
            self.save_css_item("uploaded_css", css_content)

            # Apply the CSS
            self.apply_custom_css(css_content)
            if self.parent:
                self.parent.refresh_page()

            logging.info("Uploaded CSS applied and page refreshed.")

    def clear_all_customizations(self):
        """
        Clear all saved CSS customizations.
        """
        try:
            connection = sqlite3.connect(DB_PATH)
            cursor = connection.cursor()
            cursor.execute("DELETE FROM custom_css")
            connection.commit()
            logging.info("All CSS customizations cleared.")
        except sqlite3.Error as e:
            logging.error(f"Error clearing customizations: {e}")
        finally:
            connection.close()

        if self.parent:
            self.parent.refresh_page()
