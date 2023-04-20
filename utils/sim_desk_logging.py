import os.path
from logging.handlers import RotatingFileHandler
import logging
current_path = os.path.dirname(__file__)
log_file_full_name = os.path.join(current_path, "../logs/GX1.log")
logger = logging.getLogger("GX1")
logger.setLevel(level=logging.DEBUG)
logger.addHandler(RotatingFileHandler(log_file_full_name))