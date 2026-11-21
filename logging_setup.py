from imports import *
from constants import *
from directories import *

# -----------------------
# Logging setup
# -----------------------

def setup_logging():
    """
    Setup logging configuration to save logs in the 'logs' directory with the filename 'rbc_{date}.log'.
    """
    log_filename = datetime.now().strftime('logs/rbc_%Y-%m-%d.log')
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_filename,
        filemode='a'  # Append to the log file if it exists
    )
    print(f"Logging to: {log_filename}")
