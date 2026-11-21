from imports import *
from constants import *
from directories import *

# -----------------------
# Startup Splash
# -----------------------

class SplashScreen(QSplashScreen):
    def __init__(self, image_path, max_height=400):
        if not os.path.exists(image_path):
            logging.error(f"Image not found: {image_path}")
            pixmap = QPixmap(300, 200)
            pixmap.fill(Qt.black)
        else:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                logging.error(f"Failed to load image: {image_path}")
                pixmap = QPixmap(300, 200)
                pixmap.fill(Qt.black)
            else:
                # Scale pixmap to max_height, preserving aspect ratio
                if pixmap.height() > max_height:
                    pixmap = pixmap.scaledToHeight(max_height, Qt.SmoothTransformation)
        super().__init__(pixmap, Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def show_message(self, message):
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
