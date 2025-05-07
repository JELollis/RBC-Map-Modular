from constants import LOG_DIR, LOG_FORMAT, DEFAULT_LOG_LEVEL, VERSION_NUMBER, DB_PATH
from imports import logging, datetime, sqlite3, sys

def get_logging_level_from_db(default=logging.INFO) -> int:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT setting_value FROM settings WHERE setting_name = 'log_level'")
            row = cursor.fetchone()
            if row:
                return int(row[0])
    except Exception as e:
        print(f"Failed to load log level from DB: {e}", file=sys.stderr)
    return default

def setup_logging(log_dir: str = LOG_DIR, log_level: int = DEFAULT_LOG_LEVEL, log_format: str = LOG_FORMAT) -> bool:
    """
    Set up logging configuration to save logs in the specified directory with daily rotation.
    """
    log_filename = None  # Predefine so it's always available in except blocks
    try:
        log_filename = datetime.now().strftime(f'{log_dir}/rbc_%Y-%m-%d.log')

        # Clear any existing handlers to avoid duplication if called multiple times
        logger = logging.getLogger()
        if logger.handlers:
            logger.handlers.clear()

        handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
        handler.setFormatter(logging.Formatter(log_format))
        handler.setLevel(log_level)

        logger.setLevel(log_level)
        logger.addHandler(handler)

        logger.info(f"Logging initialized. Logs will be written to {log_filename}")
        return True

    except OSError as e:
        print(f"Failed to set up logging to {log_filename or '[unknown]'}: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error during logging setup: {e}", file=sys.stderr)
        return False

# Initialize logging at startup
if not setup_logging(log_level=get_logging_level_from_db()):
    print("Logging setup failed. Continuing without file logging.", file=sys.stderr)
    logging.basicConfig(level=DEFAULT_LOG_LEVEL, format=LOG_FORMAT, stream=sys.stderr)  # Fallback to console

# Log app version
logging.info(f"Launching app version {VERSION_NUMBER}")

def save_logging_level_to_db(level: int) -> bool:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (setting_name, setting_value)
                VALUES (?, ?)
                ON CONFLICT(setting_name) DO UPDATE SET setting_value=excluded.setting_value
            """, ('log_level', str(level)))
            conn.commit()
            logging.info(f"Log level updated to {logging.getLevelName(level)} in settings")
            return True
    except Exception as e:
        logging.error(f"Failed to save log level: {e}")
        return False
