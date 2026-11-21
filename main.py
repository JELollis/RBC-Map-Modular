from imports import *
from constants import *
from directories import *
from rbc_community_map import *

def main():
    """
    Main function to run the RBC City Map Application.
    """
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('../testing/images/favicon.ico'))  # Set the global favicon
    window = RBCCommunityMap()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
