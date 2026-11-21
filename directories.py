from imports import *
from constants import *

# -----------------------
# Directory setup
# -----------------------

def ensure_directories_exist():
    """
    Ensure that the required directories exist. If they don't, create them.
    """
    required_dirs = ['logs', 'sessions', 'settings']
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
