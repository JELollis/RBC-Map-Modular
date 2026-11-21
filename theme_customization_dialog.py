from imports import *
from constants import *
from directories import *

# -----------------------
# Theme Customization Dialog
# -----------------------

class ThemeCustomizationDialog(QDialog):
    """
    Dialog for customizing the application's theme colors.
    """

    def __init__(self, parent=None, color_mappings=None):
        """
        Initialize the theme customization dialog.

        Args:
            parent (QWidget): The parent widget.
            color_mappings (dict): A dictionary of color mappings.
        """
        super().__init__(parent)
        self.setWindowTitle('Theme Customization')
        self.setMinimumSize(400, 300)
        self.color_mappings = color_mappings if color_mappings else {}

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        self.ui_tab = QWidget()
        self.minimap_tab = QWidget()
        self.tabs.addTab(self.ui_tab, "UI, Buttons, and Text")
        self.tabs.addTab(self.minimap_tab, "Minimap Content")

        self.setup_ui_tab()
        self.setup_minimap_tab()

        button_layout = QHBoxLayout()
        save_button = QPushButton('Save', self)
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def setup_ui_tab(self):
        """
        Set up the UI tab in the theme customization dialog.
        """
        layout = QGridLayout(self.ui_tab)

        ui_elements = ['background', 'text_color', 'button_color']
        for index, element in enumerate(ui_elements):
            color_square = QLabel()
            color_square.setFixedSize(20, 20)
            pixmap = QPixmap(20, 20)
            pixmap.fill(self.color_mappings.get(element, QColor('white')))
            color_square.setPixmap(pixmap)

            color_button = QPushButton('Change Color')
            color_button.clicked.connect(lambda _, el=element, sq=color_square: self.change_color(el, sq))

            layout.addWidget(QLabel(f"{element.replace('_', ' ').capitalize()}:"), index, 0)
            layout.addWidget(color_square, index, 1)
            layout.addWidget(color_button, index, 2)

    def setup_minimap_tab(self):
        """
        Set up the Minimap Content tab in the theme customization dialog.
        """
        layout = QGridLayout(self.minimap_tab)

        minimap_elements = ['bank', 'tavern', 'transit', 'user_building', 'shop', 'guild', 'placesofinterest']
        for index, element in enumerate(minimap_elements):
            color_square = QLabel()
            color_square.setFixedSize(20, 20)
            pixmap = QPixmap(20, 20)
            pixmap.fill(self.color_mappings.get(element, QColor('white')))
            color_square.setPixmap(pixmap)

            color_button = QPushButton('Change Color')
            color_button.clicked.connect(lambda _, el=element, sq=color_square: self.change_color(el, sq))

            layout.addWidget(QLabel(f"{element.capitalize()}:"), index, 0)
            layout.addWidget(color_square, index, 1)
            layout.addWidget(color_button, index, 2)

    def change_color(self, element_name, color_square):
        """
        Open a color dialog to change the color of the specified element.

        Args:
            element_name (str): The name of the element.
            color_square (QLabel): The QLabel that shows the current color.
        """
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_mappings[element_name] = color
            pixmap = QPixmap(20, 20)
            pixmap.fill(color)
            color_square.setPixmap(pixmap)

    def apply_theme(self):
        """
        Apply the theme settings to the application.
        """
        # Apply background color
        background_color = self.color_mappings.get('background', QColor('white'))
        self.setStyleSheet(f"background-color: {background_color.name()};")

        # Apply text and button colors
        text_color = self.color_mappings.get('text_color', QColor('black')).name()
        button_color = self.color_mappings.get('button_color', QColor('lightgrey')).name()
        self.setStyleSheet(
            f"QWidget {{ background-color: {background_color.name()}; }}"
            f"QPushButton {{ background-color: {button_color}; color: {text_color}; }}"
            f"QLabel {{ color: {text_color}; }}"
        )
