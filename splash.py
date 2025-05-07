from imports import *

# -----------------------
# Define Type Checking
# -----------------------

if TYPE_CHECKING:
    class AVITDScraper:
        def scrape_guilds_and_shops(self) -> None: ...
        def close_connection(self) -> None: ...


    class MainWindowType(QWidget):
        current_css_profile: str
        selected_character: dict | None
        destination: tuple[int, int] | None
        website_frame: QWebEngineView
        AVITD_scraper: AVITDScraper
        def apply_custom_css(self, css: str) -> None: ...
        def update_minimap(self) -> None: ...

        columns: dict[str, int]
        rows: dict[str, int]
        taverns_coordinates: dict[str, tuple[int, int]]
        banks_coordinates: dict[str, tuple[str, str, str, str]]
        transits_coordinates: dict[str, tuple[int, int]]
        shops_coordinates: dict[str, tuple[int, int]]
        guilds_coordinates: dict[str, tuple[int, int]]
        places_of_interest_coordinates: dict[str, tuple[int, int]]
        user_buildings_coordinates: dict[str, tuple[int, int]]

# -----------------------
# Define App Icon
# -----------------------

APP_ICON = PySide6.QtGui.QIcon()

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

# -----------------------
# Startup Splash
# -----------------------

class SplashScreen(QSplashScreen):
    def __init__(self, image_path, max_height=400):
        if not os.path.exists(image_path):
            logging.error(f"Image not found: {image_path}")
            pixmap = PySide6.QtGui.QPixmap(300, 200)
            # noinspection PyUnresolvedReferences
            pixmap.fill(Qt.black)
        else:
            pixmap = PySide6.QtGui.QPixmap(image_path)
            if pixmap.isNull():
                logging.error(f"Failed to load image: {image_path}")
                pixmap = PySide6.QtGui.QPixmap(300, 200)
                # noinspection PyUnresolvedReferences
                pixmap.fill(Qt.black)
            else:
                # Scale pixmap to max_height, preserving aspect ratio
                if pixmap.height() > max_height:
                    # noinspection PyUnresolvedReferences

                    pixmap = pixmap.scaledToHeight(max_height, Qt.SmoothTransformation)
        # noinspection PyUnresolvedReferences
        super().__init__(pixmap, Qt.WindowStaysOnTopHint)
        # noinspection PyUnresolvedReferences
        self.setAttribute(Qt.WA_DeleteOnClose)

    def show_message(self, message):
        # noinspection PyUnresolvedReferences
        self.showMessage(f"Startup script: {message} loading...", Qt.AlignBottom | Qt.AlignHCenter, Qt.white)
        QApplication.processEvents()

# -----------------------
# Splash Messages Decorator
# -----------------------

def splash_message(splash):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if splash and not splash.isHidden():
                splash.show_message(func.__name__)  # Show the original method name
            return func(self, *args, **kwargs)
        wrapper.__name__ = func.__name__  # Preserve the original method name
        return wrapper
    return decorator