from imports import *


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
        logging.debug("Theme applied to %s", widget.__class__.__name__)
    except Exception as exc:
        logging.error(
            "Failed to apply theme to %s: %s",
            widget.__class__.__name__,
            exc,
        )
        widget.setStyleSheet("")


class SplashScreen(QSplashScreen):
    def __init__(self, image_path: str, max_height: int = 400):
        if not os.path.exists(image_path):
            logging.error("Image not found: %s", image_path)
            pixmap = PySide6.QtGui.QPixmap(300, 200)
            pixmap.fill(Qt.GlobalColor.black)
        else:
            pixmap = PySide6.QtGui.QPixmap(image_path)
            if pixmap.isNull():
                logging.error("Failed to load image: %s", image_path)
                pixmap = PySide6.QtGui.QPixmap(300, 200)
                pixmap.fill(Qt.GlobalColor.black)
            elif pixmap.height() > max_height:
                pixmap = pixmap.scaledToHeight(
                    max_height,
                    Qt.SmoothTransformation,
                )

        super().__init__(pixmap, Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def show_message(self, message: str) -> None:
        self.showMessage(
            f"Startup script: {message} loading...",
            Qt.AlignBottom | Qt.AlignHCenter,
            Qt.GlobalColor.white,
            )
        QApplication.processEvents()


def splash_message(
        splash_source: Callable[[Any], Any] | Any,
        message: str | None = None,
):
    """
    Decorator to display a startup splash message before executing a method.

    Args:
        splash_source:
            Either a callable (e.g. lambda self: self.splash)
            or a splash instance.
        message:
            Optional explicit message to display. If omitted, the
            function name is used.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                splash = (
                    splash_source(self)
                    if callable(splash_source)
                    else splash_source
                )

                if splash is not None:
                    # Defensive: ensure Qt object is still valid and visible
                    try:
                        if hasattr(splash, "isHidden") and not splash.isHidden():
                            splash.show_message(message or func.__name__)
                    except Exception:
                        # Splash issues must never block execution
                        pass

            except Exception:
                # Any splash-related failure must be silent
                pass

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
