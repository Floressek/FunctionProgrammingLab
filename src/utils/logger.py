import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """Return a logger with the specified name and level."""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = RotatingFileHandler(log_file, backupCount=2)  # max 5MB =  maxBytes=5*1024*1024,
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    if not logger.hasHandlers():  # Avoid adding multiple handlers
        logger.addHandler(logging.StreamHandler())
    return logger
