#!/usr/bin/env python
# encoding: utf-8
"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSCUDSStudio
@file: utilties.py
@time: 2023/4/1 15:07
@desc:
"""
import subprocess
import logging
import string
logger = logging.getLogger("GX1")


def printable(text):
    return "".join([ch for ch in text if ch in string.printable])


def os_system_cmd(cmd_str):
    log_msg = "==== Executing system command: %s" % cmd_str
    logger.info(log_msg)
    _spp = subprocess.Popen(cmd_str, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = _spp.stdout.read()
    if type(output) != str:
        output = output.decode()
    output = printable(output)

    msg_out_lst = []
    for line in output.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        msg_out_lst.append(line)
    logger.info(msg_out_lst)

    return msg_out_lst