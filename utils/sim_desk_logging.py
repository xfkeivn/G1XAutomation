"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: sim_desk_logging.py
@time: 2023/3/25 20:34
@desc:
"""
import logging
import os.path
from logging.handlers import RotatingFileHandler

from utils.utilities import get_home_log_folder

dir_upper_name = get_home_log_folder()
if not os.path.exists(dir_upper_name):
    os.mkdir(dir_upper_name)

current_path = os.path.dirname(__file__)
log_file_full_name = os.path.join(dir_upper_name, "GX1.log")
logger = logging.getLogger("GX1")
logger.setLevel(level=logging.DEBUG)
logger.addHandler(RotatingFileHandler(log_file_full_name))
