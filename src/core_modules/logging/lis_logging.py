"""
Class containing all util methods to get the correct logger
"""
import logging
import os
import sys


def get_logger(logger_name: str, log_level: str = "INFO"):
    """
    Method to return the feedme logger or create it if needed
    :param str logger_name: The name of the logger.
    :param str log_level: The level the logger should log to. Default: INFO
    :return: the existing or newly created logger
    """
    if logger_name in logging.Logger.manager.loggerDict:
        return logging.getLogger(logger_name)
    return _setup_logger(logger_name, log_level)


def _setup_logger(logger_name: str, log_level: str):
    """
    Creates a logging instance for file and console logging.
    :param str logger_name: The name of the logger.
    :param str log_level: The level the logger should log to.
    :return: the created logger instance
    """
    # Basic logger-setup
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.propagate = False
    if not os.path.exists("./logs"):
        os.mkdir("./logs")
    handler = logging.FileHandler(f'./logs/latest.log', mode='a')
    formatter = logging.Formatter('%(asctime)s|%(name)s|%(levelname)s|%(message)s', "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    return logger
