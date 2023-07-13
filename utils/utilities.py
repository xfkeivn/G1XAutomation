#!/usr/bin/env python
# encoding: utf-8
"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: utilities.py
@time: 2023/4/1 15:07
@desc:
"""
import logging
import os
import string
import subprocess
from pathlib import Path

import setting

logger = logging.getLogger("GX1")


def get_home_log_folder():
    logfolder = os.path.join(Path.home(), "DVTFront", "logs")
    if not os.path.exists(logfolder):
        os.makedirs(logfolder)
    return logfolder


def get_screen_shot_home_folder():
    screenfolder = os.path.join(Path.home(), "DVTFront", "Screens")
    if not os.path.exists(screenfolder):
        os.makedirs(screenfolder)
    return screenfolder


def printable(text):
    return "".join([ch for ch in text if ch in string.printable])


def os_system_cmd(cmd_str):
    log_msg = "==== Executing system command: %s" % cmd_str
    logger.info(log_msg)
    _spp = subprocess.Popen(
        cmd_str,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = _spp.stdout.read()
    if type(output) != str:
        output = output.decode()
    output = printable(output)

    msg_out_lst = []
    for line in output.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        msg_out_lst.append(line)
    logger.info(msg_out_lst)

    return msg_out_lst


def get_python_exe_path():
    if setting.prod is False:
        venv_path = os.path.join(os.path.dirname(__file__), "../venv2")
        activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
        subprocess.call(activate_script, shell=True)
        # Start the subprocess using the virtual environment's Python interpreter
        python_path = os.path.join(venv_path, "Scripts", "python.exe")
        return python_path
        # subprocess.Popen([python_path, os.path.join(venv_path, 'Scripts', 'ride.py')])
    else:
        venv_path = os.path.join(os.path.dirname(__file__), "../../python3")
        python_path = os.path.join(venv_path, "python.exe")
        # subprocess.Popen([python_path, os.path.join(venv_path, 'Scripts', 'ride.py')])
        return python_path
