from imports import *
from constants import *
from directories import *
from splash import *
from rbc_community_map import *

# -----------------------
# Main Entry Point
# -----------------------

def main() -> None:
    """Run the RBC City Map Application."""
    global APP_ICON
    app = QApplication(sys.argv)
    APP_ICON = QIcon('./images/favicon.ico')
    app.setWindowIcon(APP_ICON)

    splash = SplashScreen("images/loading.png")
    splash.show()
    splash.show_message("Starting up...")

    # Delay decorating until instance is created
    main_window = RBCCommunityMap()

    init_methods = [
        '_init_scraper',
        '_init_window_properties',
        '_init_web_profile',
        '_init_ui_state',
        '_init_characters',
        '_init_ui_components',
        '_finalize_setup'
    ]

    for name in init_methods:
        method = getattr(main_window, name)
        setattr(main_window, name, splash_message(splash)(method))

    main_window.splash = splash
    main_window.show()
    splash.finish(main_window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
