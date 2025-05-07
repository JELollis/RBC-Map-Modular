from constants import *
from imports import *

def ensure_directories_exist(directories: list[str] = None) -> bool:
    """
    Ensure that the required directories exist, creating them if necessary.
    """
    if directories is None:
        directories = REQUIRED_DIRECTORIES

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

# Example usage at startup (optional, depending on your flow)
if not ensure_directories_exist():
    logging.warning("Some directories could not be created. Application may encounter issues.")
