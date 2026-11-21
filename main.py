from imports import *
from constants import *
from directories import *
from rbc_community_map import *

# -----------------------
# Main Entry Point
# -----------------------

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    app = QApplication(sys.argv)
    window = CityMapApp()
    sys.exit(app.exec())
