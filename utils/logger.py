"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: logger.py
@time: 2023/3/25 20:34
@desc:
"""
import logging
from utils.sim_desk_logging import logger as sim_desk_logger
from robot.api import logger as robot_logger
from executor_context import ExecutorContext
from utils.utilities import get_home_log_folder
import os

dir_name = os.path.dirname(__file__)
dir_upper_name = get_home_log_folder()
if not os.path.exists(dir_upper_name):
    os.makedirs(dir_upper_name)


def write(msg, level='INFO', html=False):
    """Writes the message to the log file using the given level.

    Valid log levels are ``TRACE``, ``DEBUG``, ``INFO`` (default), ``WARN``, and
    ``ERROR``. Additionally it is possible to use ``HTML`` pseudo log level that
    logs the message as HTML using the ``INFO`` level.

    Instead of using this method, it is generally better to use the level
    specific methods such as ``info`` and ``debug`` that have separate
    ``html`` argument to control the message format.
    """
    if ExecutorContext().is_robot_context():
        robot_logger.write(msg, level, html)
    else:
        level = {'TRACE': logging.DEBUG // 2,
                 'DEBUG': logging.DEBUG,
                 'INFO': logging.INFO,
                 'HTML': logging.INFO,
                 'WARN': logging.WARN,
                 'ERROR': logging.ERROR}[level]
        sim_desk_logger.log(level, msg)


def trace(msg, html=False):
    """Writes the message to the log file using the ``TRACE`` level."""
    write(msg, 'TRACE', html)


def debug(msg, html=False):
    """Writes the message to the log file using the ``DEBUG`` level."""
    write(msg, 'DEBUG', html)


def info(msg, html=False, also_console=False):
    """Writes the message to the log file using the ``INFO`` level.

    If ``also_console`` argument is set to ``True``, the message is
    written both to the log file and to the console.
    """
    write(msg, 'INFO', html)
    if also_console:
        console(msg)


def warn(msg, html=False):
    """Writes the message to the log file using the ``WARN`` level."""
    write(msg, 'WARN', html)


def error(msg, html=False):
    """Writes the message to the log file using the ``ERROR`` level.
    """
    write(msg, 'ERROR', html)


def console(msg, newline=True, stream='stdout'):
    """Writes the message to the console.

    If the ``newline`` argument is ``True``, a newline character is
    automatically added to the message.

    By default the message is written to the standard output stream.
    Using the standard error stream is possibly by giving the ``stream``
    argument value ``'stderr'``.
    """
    robot_logger.console(msg, newline, stream)
