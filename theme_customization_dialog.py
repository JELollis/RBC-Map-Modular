from imports import *
from constants import *
from directories import *

# -----------------------
# Theme Customization Dialog
# -----------------------

class ThemeCustomizationDialog(QDialog):
    """
    Dialog for customizing application theme colors for UI and minimap elements.
    """

    def __init__(self, parent=None, color_mappings: dict | None = None) -> None:
        """
        Initialize the theme customization dialog.

        Args:
            parent: Parent widget (optional).
            color_mappings: Current color mappings dict (optional).
        """
        super().__init__(parent)
        self.setWindowTitle('Theme Customization')
        self.setMinimumSize(400, 300)

        self.color_mappings = color_mappings.copy() if color_mappings else {}

        # Main layout
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
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        logging.debug("Theme customization dialog initialized")

    def setup_ui_tab(self) -> None:
        """Set up the UI tab for background, text, and button color customization."""
        layout = QGridLayout(self.ui_tab)
        ui_elements = ['background', 'text_color', 'button_color']

        for idx, elem in enumerate(ui_elements):
            color_square = QLabel(self.ui_tab)
            color_square.setFixedSize(20, 20)
            color = self.color_mappings.get(elem, QColor('white'))
            color_square.setPixmap(QPixmap(20, 20).fill(color))

            color_button = QPushButton('Change Color', self.ui_tab)
            color_button.clicked.connect(lambda _, e=elem, sq=color_square: self.change_color(e, sq))

            layout.addWidget(QLabel(f"{elem.replace('_', ' ').capitalize()}:", self.ui_tab), idx, 0)
            layout.addWidget(color_square, idx, 1)
            layout.addWidget(color_button, idx, 2)

    def setup_minimap_tab(self) -> None:
        """Set up the Minimap tab for customizing minimap element colors."""
        layout = QGridLayout(self.minimap_tab)
        minimap_elements = ['bank', 'tavern', 'transit', 'user_building', 'shop', 'guild', 'placesofinterest']

        for idx, elem in enumerate(minimap_elements):
            color_square = QLabel(self.minimap_tab)
            color_square.setFixedSize(20, 20)
            color = self.color_mappings.get(elem, QColor('white'))
            color_square.setPixmap(QPixmap(20, 20).fill(color))

            color_button = QPushButton('Change Color', self.minimap_tab)
            color_button.clicked.connect(lambda _, e=elem, sq=color_square: self.change_color(e, sq))

            layout.addWidget(QLabel(f"{elem.capitalize()}:", self.minimap_tab), idx, 0)
            layout.addWidget(color_square, idx, 1)
            layout.addWidget(color_button, idx, 2)

    def change_color(self, element_name: str, color_square: QLabel) -> None:
        """
        Open a color picker to update an element’s color.

        Args:
            element_name: Key in color_mappings to update.
            color_square: QLabel displaying the current color.
        """
        color = QColorDialog.getColor(self.color_mappings.get(element_name, QColor('white')), self)
        if color.isValid():
            self.color_mappings[element_name] = color
            color_square.setPixmap(QPixmap(20, 20).fill(color))
            logging.debug(f"Changed color for '{element_name}' to {color.name()}")

    def apply_theme(self) -> None:
        """Apply the selected theme colors to the dialog’s stylesheet."""
        try:
            bg_color = self.color_mappings.get('background', QColor('white')).name()
            text_color = self.color_mappings.get('text_color', QColor('black')).name()
            btn_color = self.color_mappings.get('button_color', QColor('lightgrey')).name()

            self.setStyleSheet(
                f"QWidget {{ background-color: {bg_color}; }}"
                f"QPushButton {{ background-color: {btn_color}; color: {text_color}; }}"
                f"QLabel {{ color: {text_color}; }}"
            )
            logging.debug("Theme applied to dialog")
        except Exception as e:
            logging.error(f"Failed to apply theme to dialog: {e}")
            self.setStyleSheet("")  # Reset on failure
