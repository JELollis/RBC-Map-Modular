from imports import *
from constants import *

# -----------------------
# Theme Application
# -----------------------

def apply_theme_to_widget(widget: QWidget, color_mappings: dict) -> None:
    """Apply the selected theme colors to the given widget's stylesheet."""
    try:
        bg_color = color_mappings.get('background', PySide6.QtGui.QColor('white')).name()
        text_color = color_mappings.get('text_color', PySide6.QtGui.QColor('black')).name()
        btn_color = color_mappings.get('button_color', PySide6.QtGui.QColor('lightgrey')).name()
        btn_hover_color = color_mappings.get('button_hover_color', PySide6.QtGui.QColor('grey')).name()
        btn_pressed_color = color_mappings.get('button_pressed_color', PySide6.QtGui.QColor('darkgrey')).name()
        btn_border_color = color_mappings.get('button_border_color', PySide6.QtGui.QColor('black')).name()

        widget.setStyleSheet(
            f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QPushButton {{
                background-color: {btn_color};
                color: {text_color};
                border: 2px solid {btn_border_color};
                border-radius: 6px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {btn_hover_color};
            }}
            QPushButton:pressed {{
                background-color: {btn_pressed_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QComboBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {btn_border_color};
                border-radius: 4px;
                padding: 4px;
            }}
            QListWidget {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {btn_border_color};
            }}
            QLineEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {btn_border_color};
                padding: 3px;
            }}
            """
        )
        logging.debug(f"Theme applied to {widget.__class__.__name__}")
    except Exception as e:
        logging.error(f"Failed to apply theme to {widget.__class__.__name__}: {e}")
        widget.setStyleSheet("")

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
            pixmap = PySide6.QtGui.QPixmap(20, 20)
            pixmap.fill(color)
            color_square.setPixmap(pixmap)
            logging.debug(f"Changed color for '{element_name}' to {color.name()}")