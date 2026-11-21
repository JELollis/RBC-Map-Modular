from imports import *
from constants import *
from directories import *
from rbc_community_map import *

# -----------------------
# Main Entry Point
# -----------------------

def main() -> None:
    """Run the RBC City Map Application."""
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('../testing/images/favicon.ico'))
    window = RBCCommunityMap()
    window.show()  # Explicitly show the window
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
