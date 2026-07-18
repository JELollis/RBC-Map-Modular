from imports import *
from constants import *


def get_logging_level_from_db(default: int = logging.INFO) -> int:
    """Retrieve logging level from the settings table, with safe fallback."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT setting_value FROM settings WHERE setting_name = 'log_level'"
            )
            row = cursor.fetchone()
            if row:
                return int(row[0])
    except Exception as exc:
        print(f"Failed to load log level from DB: {exc}", file=sys.stderr)
    return default


def setup_logging(
        log_dir: os.PathLike | str = LOG_DIR,
        log_level: int = DEFAULT_LOG_LEVEL,
        log_format: str = LOG_FORMAT,
) -> bool:
    """
    Configure file-based logging with daily log files.
    """
    log_filename: str | None = None

    try:
        log_filename = os.path.join(
            str(log_dir),
            datetime.now().strftime("rbc_%Y-%m-%d.log"),
        )

        logger = logging.getLogger()

        # Prevent duplicate handlers if re-initialized
        if logger.handlers:
            logger.handlers.clear()

        handler = logging.FileHandler(
            log_filename,
            mode="a",
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter(log_format))
        handler.setLevel(log_level)

        logger.setLevel(log_level)
        logger.addHandler(handler)

        logger.info(
            "Logging initialized. Logs will be written to %s",
            log_filename,
        )
        return True

    except OSError as exc:
        print(
            f"Failed to set up logging to {log_filename or '[unknown]'}: {exc}",
            file=sys.stderr,
        )
        return False
    except Exception as exc:
        print(
            f"Unexpected error during logging setup: {exc}",
            file=sys.stderr,
        )
        return False


# Initialize logging at startup
if not setup_logging(log_level=get_logging_level_from_db()):
    print(
        "Logging setup failed. Continuing without file logging.",
        file=sys.stderr,
    )
    logging.basicConfig(
        level=DEFAULT_LOG_LEVEL,
        format=LOG_FORMAT,
        stream=sys.stderr,
    )

logging.info("Launching app version %s", VERSION_NUMBER)


def save_logging_level_to_db(level: int) -> bool:
    """Persist the selected logging level to the settings table."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO settings (setting_name, setting_value)
                VALUES (?, ?)
                ON CONFLICT(setting_name)
                DO UPDATE SET setting_value = excluded.setting_value
                """,
                ("log_level", str(level)),
            )
            conn.commit()

        logging.info(
            "Log level updated to %s in settings",
            logging.getLevelName(level),
        )
        return True

    except Exception as exc:
        logging.error("Failed to save log level: %s", exc)
        return False
