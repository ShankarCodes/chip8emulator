import builtins
import logging
from logging.handlers import RotatingFileHandler
import os

try:
    import coloredlogs
    cl = True
except ModuleNotFoundError:
    cl = False


class Conf:
    LEVEL = logging.INFO
    LOG_PATH = './logs'
    LOG_FORMAT = "%(asctime)s %(name)-20s[%(process)-7d]: [%(filename)+10s:%(lineno)-4d] %(funcName)15s() [%(levelname)-8s]  %(message)s"
    ALL_LOGS = "all"
    LOG_FORMATTER = logging.Formatter(LOG_FORMAT)
    PRINT_CONSOLE = True

    PRINT_ENABLED = True
    INPUT_ENABLED = True


def create_logger(nm) -> logging.Logger:
    """
    creates a logger with a name
    """
    logger = logging.getLogger(nm)
    logger.setLevel(Conf.LEVEL)
    if Conf.PRINT_CONSOLE:
        if cl:
            coloredlogs.install(level=Conf.LEVEL, milliseconds=True,
                                fmt=Conf.LOG_FORMAT, logger=logger)

        else:
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(Conf.LOG_FORMATTER)
            logger.addHandler(consoleHandler)

    if not os.path.exists(Conf.LOG_PATH):
        try:
            os.mkdir(Conf.LOG_PATH)
        except:
            print("Error creating "+Conf.LOG_PATH+", Please check permission")

    # Sets file logger with max size 10 megabytes
    fileHandler = RotatingFileHandler(
        "{}/{}.log".format(Conf.LOG_PATH, nm), maxBytes=10*1024*1024, backupCount=2)
    fileHandler.setFormatter(Conf.LOG_FORMATTER)
    logger.addHandler(fileHandler)

    allFileHandler = RotatingFileHandler(
        "{}/{}.log".format(Conf.LOG_PATH, Conf.ALL_LOGS),  maxBytes=50*1024*1024)
    allFileHandler.setFormatter(Conf.LOG_FORMATTER)
    logger.addHandler(allFileHandler)

    return logger


def print(*args, **kwargs):
    if PRINT_ENABLED:
        return builtins.print(*args, **kwargs)
    return None


def input(*args, **kwargs):
    if INPUT_ENABLED:
        return builtins.input(*args, **kwargs)
    return 'Input Disabled'
