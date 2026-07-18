from imports import *
from constants import *

from splash import SplashScreen
from rbc_community_map import RBCCommunityMap


def main() -> None:
    app = QApplication(sys.argv)

    # Resolve base paths safely (works in dev and packaged builds)
    base_dir = Path(__file__).resolve().parent
    images_dir = base_dir / "images"

    app_icon = PySide6.QtGui.QIcon(str(images_dir / "favicon.ico"))
    app.setWindowIcon(app_icon)

    splash = SplashScreen(str(images_dir / "loading.png"))
    splash.show()
    splash.show_message("Starting up...")

    try:
        main_window = RBCCommunityMap(splash=splash)
        main_window.show()
        splash.finish(main_window)
    except Exception as exc:
        logging.critical("Fatal startup error", exc_info=exc)
        splash.close()
        QMessageBox.critical(
            None,
            "Startup Error",
            "The application failed to start.\n\n"
            "Please check the log files for details.",
        )
        sys.exit(1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
