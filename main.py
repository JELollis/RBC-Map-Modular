from imports import *
from constants import *
from splash import *
from directories import *
from rbc_community_map import *

# -----------------------
# Main Entry Point
# -----------------------

def main() -> None:
    """Run the RBC City Map Application."""

if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash = SplashScreen("images/loading.png")
    splash.show()
    splash.show_message("Starting up...")

    init_methods = [
        '_init_scraper', '_init_window_properties', '_init_web_profile',
        '_init_ui_state', '_init_characters', '_init_ui_components', '_finalize_setup'
    ]
    for name in init_methods:
        method = getattr(RBCCommunityMap, name)
        setattr(RBCCommunityMap, name, splash_message(splash)(method))

    main_window = RBCCommunityMap()
    main_window.splash = splash

    sys.exit(app.exec())
