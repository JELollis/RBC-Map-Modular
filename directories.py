from imports import *
from constants import *

# -----------------------
# Directory Setup
# -----------------------

# Constants defined at the top of the file (or in a constants section)
def ensure_directories_exist(directories: list[str] = REQUIRED_DIRECTORIES) -> bool:
    """
    Ensure that the required directories exist, creating them if necessary.

    This function verifies the presence of essential directories for the application's operation.
    If any are missing, they are created in the current working directory. The default directories are:
    - logs: Stores application log files.
    - sessions: Stores session-related data (e.g., user sessions, cookies).
    - images: Stores image files (e.g., icons, UI assets).

    Args:
        directories (list[str], optional): List of directory names to ensure. Defaults to REQUIRED_DIRECTORIES.

    Returns:
        bool: True if all directories exist or were created successfully, False if an error occurred.

    Raises:
        OSError: If a directory cannot be created due to permissions or other system issues (logged and handled).
    """
    success = True
    for directory in directories:
        try:
            # Check existence first to avoid unnecessary syscalls
            if not os.path.isdir(directory):
                os.makedirs(directory, exist_ok=True)
                logging.debug(f"Created directory: {directory}")
            else:
                logging.debug(f"Directory already exists: {directory}")
        except OSError as e:
            logging.error(f"Failed to create directory '{directory}': {e}")
            success = False
    return success
