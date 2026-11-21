from imports import *
from constants import *
from directories import *

# -----------------------
# Logging Setup
# -----------------------

def setup_logging():
    """
    Set up logging configuration to save logs in the 'logs' directory.
    """
    log_filename = datetime.now().strftime('./logs/rbc_%Y-%m-%d.log')

    logging.basicConfig(
        level=logging.DEBUG,  # Capture all log events
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_filename,
        filemode='a'
    )

    logging.info(f"Logging initialized. Logs will be written to {log_filename}")
