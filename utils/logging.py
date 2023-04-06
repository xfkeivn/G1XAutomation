from logging.handlers import RotatingFileHandler
import logging
logger = logging.getLogger("GX1")
logger.setLevel(level=logging.DEBUG)
logger.addHandler(RotatingFileHandler(r'GX1.log'))