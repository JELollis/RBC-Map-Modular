from imports import *
from constants import *
from directories import *
from rbc_community_map import *

def main():
    """
    Main function to run the RBC City Map Application.
    """
    app = QApplication(sys.argv)
    window = CityMapApp()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()
