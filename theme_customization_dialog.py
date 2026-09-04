from imports import *
from constants import *


class ThemeCustomizationDialog(QDialog):
    """
    Dialog for customizing application theme colors for UI and minimap elements.
    """

    def __init__(self, parent=None, color_mappings: dict | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Theme Customization')
        self.setWindowIcon(APP_ICON)
        self.setMinimumSize(400, 300)

        self.color_mappings = color_mappings.copy() if color_mappings else {}
        # Track which elements the user actually changes, so change_theme can
        # record only those as overrides (highest precedence over CSS/defaults).
        self.changed_minimap_elements: set[str] = set()

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
        cancel_button = QPushButton('Cancel', self)
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        apply_theme_to_widget(self, self.color_mappings)
        logging.debug("Theme customization dialog initialized")

    def setup_ui_tab(self) -> None:
        layout = QGridLayout(self.ui_tab)
        ui_elements = [
            'background',
            'text_color',
            'button_color',
            'button_hover_color',
            'button_pressed_color',
            'button_border_color'
        ]

        for idx, elem in enumerate(ui_elements):
            color_square = QLabel(self.ui_tab)
            color_square.setFixedSize(20, 20)
            color = self.color_mappings.get(elem, PySide6.QtGui.QColor('white'))
            pixmap = PySide6.QtGui.QPixmap(20, 20)
            pixmap.fill(color)
            color_square.setPixmap(pixmap)

            color_button = QPushButton('Change Color', self.ui_tab)
            color_button.clicked.connect(lambda _, e=elem, sq=color_square: self.change_color(e, sq))

            layout.addWidget(QLabel(f"{elem.replace('_', ' ').capitalize()}:", self.ui_tab), idx, 0)
            layout.addWidget(color_square, idx, 1)
            layout.addWidget(color_button, idx, 2)

    def setup_minimap_tab(self) -> None:
        layout = QGridLayout(self.minimap_tab)
        minimap_elements = ['bank', 'tavern', 'transit', 'user_building', 'shop', 'guild', 'placesofinterest']

        for idx, elem in enumerate(minimap_elements):
            color_square = QLabel(self.minimap_tab)
            color_square.setFixedSize(20, 20)
            color = self.color_mappings.get(elem, PySide6.QtGui.QColor('white'))
            pixmap = PySide6.QtGui.QPixmap(20, 20)
            pixmap.fill(color)
            color_square.setPixmap(pixmap)

            color_button = QPushButton('Change Color', self.minimap_tab)
            color_button.clicked.connect(lambda _, e=elem, sq=color_square: self.change_color(e, sq))

            layout.addWidget(QLabel(f"{elem.capitalize()}:", self.minimap_tab), idx, 0)
            layout.addWidget(color_square, idx, 1)
            layout.addWidget(color_button, idx, 2)

    def change_color(self, element_name: str, color_square: QLabel) -> None:
        color = QColorDialog.getColor(self.color_mappings.get(element_name, PySide6.QtGui.QColor('white')), self)
        if color.isValid():
            self.color_mappings[element_name] = color
            self.changed_minimap_elements.add(element_name)
            pixmap = PySide6.QtGui.QPixmap(20, 20)
            pixmap.fill(color)
            color_square.setPixmap(pixmap)
            logging.debug(f"Changed color for '{element_name}' to {color.name()}")
