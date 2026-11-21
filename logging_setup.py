from imports import *
from constants import *
from directories import *

# -----------------------
# Logging Setup
# -----------------------

def setup_logging():
    """
    Set up logging configuration to save logs in the 'logs' directory.

    This function configures the logging system to record application events,
    errors, and debug information in a log file. The log file is named
    'rbc_{date}.log', where {date} is replaced with the current date in the
    format 'YYYY-MM-DD'. The log files are saved in the 'logs' directory,
    and log messages are formatted to include the timestamp, log level,
    and the message content.

    Logging levels used:
    - DEBUG: Detailed information, typically of interest only when diagnosing problems.
    - INFO: Confirmation that things are working as expected.
    - WARNING: An indication that something unexpected happened, or indicative of some problem.
    - ERROR: A more serious problem, the software has not been able to perform some function.

    If the 'logs' directory does not exist, it should be created by calling
    the 'ensure_directories_exist()' function before this function.
    """
    log_filename = datetime.now().strftime('./logs/rbc_%Y-%m-%d.log')
    logging.basicConfig(
        level=logging.DEBUG,  # Set the logging level to DEBUG to capture all events
        format='%(asctime)s - %(levelname)s - %(message)s',  # Define the log message format
        filename=log_filename,  # Log file path and name
        filemode='a'  # Append to the log file if it already exists
    )
    print(f"Logging to: {log_filename}")  # Print the log file location to the console
