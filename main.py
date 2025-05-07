from imports import *
from constants import *

from splash import SplashScreen, splash_message
from rbc_community_map import RBCCommunityMap

def main() -> None:
    """Run the RBC City Map Application."""
    app = QApplication(sys.argv)
    
    app_icon = QIcon(APP_ICON_PATH)
    app.setWindowIcon(app_icon)

    # Now create splash after QApplication exists
    splash = SplashScreen("images/loading.png")

    splash.show()
    splash.show_message("Starting up...")

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