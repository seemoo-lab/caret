import logging
import os

def init(path):
    # Configure the logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a handler for stdout (info, warning, error, and critical levels)
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.INFO)  # Set the level to the lowest level you want to capture
    stdout_handler.setFormatter(formatter)

    # Create a handler for the file (info and debug levels)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    file_handler = logging.FileHandler(path)
    file_handler.setLevel(logging.DEBUG)  # Set the level to the lowest level you want to capture
    file_handler.setFormatter(formatter)

    # Create filters for each handler
    class InfoDebugFilter(logging.Filter):
        def filter(self, record):
            return record.levelno <= logging.DEBUG  # Capture info and debug levels

    class WarningErrorCriticalFilter(logging.Filter):
        def filter(self, record):
            return record.levelno > logging.DEBUG  # Capture warning, error, and critical levels

    # Attach filters to handlers
    stdout_handler.addFilter(WarningErrorCriticalFilter())
    file_handler.addFilter(InfoDebugFilter())

    # Attach handlers to the logger
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)

    return logger