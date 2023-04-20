"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: sim_desk_logging.py
@time: 2023/3/25 20:34
@desc:
"""
import os.path
from logging.handlers import RotatingFileHandler
import logging
current_path = os.path.dirname(__file__)
log_file_full_name = os.path.join(current_path, "../logs/GX1.log")
logger = logging.getLogger("GX1")
logger.setLevel(level=logging.DEBUG)
logger.addHandler(RotatingFileHandler(log_file_full_name))