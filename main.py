from imports import *
from constants import *
from directories import *
from rbc_community_map import *

# -----------------------
# Main Entry Point
# -----------------------

# Main Entry Point

def main() -> None:
    global APP_ICON
    app = QApplication(sys.argv)
    APP_ICON = PySide6.QtGui.QIcon('./images/favicon.ico')
    app.setWindowIcon(APP_ICON)

    splash = SplashScreen("images/loading.png")
    splash.show()
    splash.show_message("Starting up...")

    # Pass splash into the constructor
    main_window = RBCCommunityMap(splash=splash)

    main_window.show()
    splash.finish(main_window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
