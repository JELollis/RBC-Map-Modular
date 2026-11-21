from imports import *
from constants import *

# -----------------------
# Directory Setup
# -----------------------

def ensure_directories_exist():
    """
    Ensure that the required directories exist. If they don't, create them.

    This function checks for the presence of directories that are essential for
    the application's operation. If any of these directories are missing, they
    are created automatically to prevent issues during runtime. The directories
    managed by this function include:
    - logs: Stores application log files.
    - sessions: Stores session-related data, such as user sessions or cookies.
    - settings: Stores application settings and configuration files.
    - images: Stores image files used by the application, such as icons.

    If any of these directories do not exist, they are created in the current working directory.
    """
    required_dirs = ['logs', 'sessions', 'images']
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
