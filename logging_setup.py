from imports import *
from constants import *
from directories import *

# -----------------------
# Logging Setup
# -----------------------
def setup_logging(log_dir: str = LOG_DIR, log_level: int = LOG_LEVEL, log_format: str = LOG_FORMAT) -> bool:
    """
    Set up logging configuration to save logs in the specified directory with daily rotation.

    Configures the root logger to write logs to a file named 'rbc_YYYY-MM-DD.log' in the given directory.
    Logs are appended to the file for the current day, effectively rotating daily by filename.

    Args:
        log_dir (str, optional): Directory to store log files. Defaults to LOG_DIR ('logs').
        log_level (int, optional): Logging level (e.g., logging.DEBUG). Defaults to LOG_LEVEL.
        log_format (str, optional): Log message format. Defaults to LOG_FORMAT.

    Returns:
        bool: True if logging was set up successfully, False if an error occurred.

    Raises:
        OSError: If the log file cannot be created or written to (logged to stderr if possible).
    """
    try:
        # Ensure log directory exists (assuming ensure_directories_exist is called earlier)
        log_filename = datetime.now().strftime(f'{log_dir}/rbc_%Y-%m-%d.log')

        # Clear any existing handlers to avoid duplication if called multiple times
        logger = logging.getLogger()
        if logger.handlers:
            logger.handlers.clear()

        # Set up file handler
        handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
        handler.setFormatter(logging.Formatter(log_format))
        handler.setLevel(log_level)

        # Configure root logger
        logger.setLevel(log_level)
        logger.addHandler(handler)

        logger.info(f"Logging initialized. Logs will be written to {log_filename}")
        return True
    except OSError as e:
        # Log to stderr as a fallback if file logging fails
        print(f"Failed to set up logging to {log_filename}: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error during logging setup: {e}", file=sys.stderr)
        return False
