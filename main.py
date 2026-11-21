from imports import *
from constants import *
from directories import *
from rbc_community_map import *

# -----------------------
# Main Entry Point
# -----------------------

def main() -> None:
    app = QApplication(sys.argv)

    images_dir = APP_DIR / "images"

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
