from imports import *
from constants import *
from directories import *
from database import *

# -----------------------
# Theme Customization Dialog
# -----------------------

class ThemeCustomizationDialog(QDialog):
    """
    Dialog for customizing application theme colors for UI and minimap elements.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Theme Customization')
        self.setMinimumSize(400, 300)
        self.parent = parent

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        # Tabs
        self.ui_tab = QWidget()
        self.minimap_tab = QWidget()
        self.tabs.addTab(self.ui_tab, "UI, Buttons, and Text")
        self.tabs.addTab(self.minimap_tab, "Minimap Content")

        self.setup_ui_tab()
        self.setup_minimap_tab()

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton('Save', self)
        save_button.clicked.connect(self.save_and_accept)
        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        logging.debug("Theme customization dialog initialized")

    def setup_ui_tab(self) -> None:
        global color_mappings
        """Set up the UI tab for background, text, and button color customization."""
        layout = QGridLayout(self.ui_tab)
        ui_elements = ['background', 'text_color', 'button_color']

        for idx, elem in enumerate(ui_elements):
            color_square = QLabel(self.ui_tab)
            color_square.setFixedSize(20, 20)
            color = QColor(color_mappings.get(elem, '#ffffff'))
            pixmap = QPixmap(20, 20)
            pixmap.fill(color)
            color_square.setPixmap(pixmap)

            color_button = QPushButton('Change Color', self.ui_tab)
            color_button.clicked.connect(lambda _, e=elem, sq=color_square: self.change_color(e, sq))

            layout.addWidget(QLabel(f"{elem.replace('_', ' ').capitalize()}:", self.ui_tab), idx, 0)
            layout.addWidget(color_square, idx, 1)
            layout.addWidget(color_button, idx, 2)

    def setup_minimap_tab(self) -> None:
        global color_mappings
        """Set up the Minimap tab for customizing minimap element colors."""
        layout = QGridLayout(self.minimap_tab)
        minimap_elements = [
            'bank', 'tavern', 'transit', 'user_building', 'shop', 'guild',
            'placesofinterest', 'street', 'alley'
        ]

        for idx, elem in enumerate(minimap_elements):
            color_square = QLabel(self.minimap_tab)
            color_square.setFixedSize(20, 20)
            color = QColor(color_mappings.get(elem, '#ffffff'))
            pixmap = QPixmap(20, 20)
            pixmap.fill(color)
            color_square.setPixmap(pixmap)

            color_button = QPushButton('Change Color', self.minimap_tab)
            color_button.clicked.connect(lambda _, e=elem, sq=color_square: self.change_color(e, sq))

            layout.addWidget(QLabel(f"{elem.capitalize()}:", self.minimap_tab), idx, 0)
            layout.addWidget(color_square, idx, 1)
            layout.addWidget(color_button, idx, 2)

    def change_color(self, element_name: str, color_square: QLabel) -> None:
        global color_mappings
        current_color = QColor(color_mappings.get(element_name, '#ffffff'))
        color = QColorDialog.getColor(current_color, self)
        """
        Open a color picker to update an element’s color.

        Args:
            element_name: Key in color_mappings to update.
            color_square: QLabel displaying the current color.
        """
        if color.isValid():
            hex_color = color.name()  # Always store as hex string
            color_mappings[element_name] = hex_color
            pixmap = QPixmap(20, 20)
            pixmap.fill(QColor(hex_color))
            color_square.setPixmap(pixmap)
            logging.debug(f"Changed color for '{element_name}' to {hex_color}")

    def save_and_accept(self) -> None:
        """Save changes to database and apply them before closing."""
        global color_mappings, theme_settings, settings, keybind_config, current_css_profile
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()

                # Save all color mappings as hex strings
                for type_, color in color_mappings.items():
                    hex_color = QColor(color).name() if isinstance(color, QColor) else color
                    cursor.execute(
                        "INSERT OR REPLACE INTO color_mappings (type, color) VALUES (?, ?)",
                        (type_, hex_color)
                    )

                conn.commit()
                logging.debug(f"Saved {len(color_mappings)} color mappings to database")

        except sqlite3.Error as e:
            logging.error(f"Failed to save color mappings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save theme: {e}")
            return

        # Reload global values from the database
        try:
            (
                _, _, _, _, _, _, color_mappings,
                _, _, _, settings, theme_settings,
                keybind_config, current_css_profile
            ) = load_data(DB_PATH)
            logging.debug("Theme settings reloaded after save.")
        except Exception as e:
            logging.error(f"Failed to reload theme settings: {e}")

        # Reapply theme + update minimap
        if self.parent:
            self.parent.apply_theme()
            self.parent.update_minimap()

        self.accept()
