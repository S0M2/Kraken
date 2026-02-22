import logging
import os

def setup_logger(log_file_path, name=None):
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    logger = logging.getLogger(name or __name__)
    if not logger.handlers:
        handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
