import builtins
import logging
import os

try:
    import coloredlogs
    cl = True
except ModuleNotFoundError:
    cl = False


class Conf:
    LEVEL = logging.DEBUG
    LOG_PATH = './logs'
    LOG_FORMAT = "%(asctime)s %(name)-20s[%(process)-7d]: [%(filename)+10s:%(lineno)-4d] %(funcName)15s() [%(levelname)-8s]  %(message)s"
    ALL_LOGS = "all"
    LOG_FORMATTER = logging.Formatter(LOG_FORMAT)

    PRINT_ENABLED = True
    INPUT_ENABLED = True


def create_logger(nm) -> logging.Logger:
    """
    creates a logger with a name
    """
    logger = logging.getLogger(nm)
    logger.setLevel(Conf.LEVEL)

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

    fileHandler = logging.FileHandler("{}/{}.log".format(Conf.LOG_PATH, nm))
    fileHandler.setFormatter(Conf.LOG_FORMATTER)
    logger.addHandler(fileHandler)

    allFileHandler = logging.FileHandler(
        "{}/{}.log".format(Conf.LOG_PATH, Conf.ALL_LOGS))
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
