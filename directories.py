from imports import *
from constants import *


def ensure_directories_exist(
        directories: list[os.PathLike | str] | None = None,
) -> bool:
    """
    Ensure that the required directories exist, creating them if necessary.
    """
    if directories is None:
        directories = REQUIRED_DIRECTORIES

    success = True
    for directory in directories:
        try:
            if not os.path.isdir(directory):
                os.makedirs(directory, exist_ok=True)
                logging.debug("Created directory: %s", directory)
            else:
                logging.debug("Directory already exists: %s", directory)
        except OSError as exc:
            logging.error(
                "Failed to create directory '%s': %s",
                directory,
                exc,
            )
            success = False

    return success


# Validate directories at startup
if not ensure_directories_exist():
    logging.warning(
        "Some directories could not be created. "
        "Application may encounter issues."
    )
