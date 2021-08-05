import builtins
import logging
import os

try:
    import coloredlogs
    cl = True
except ModuleNotFoundError:
    cl = False

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
    logger.setLevel(LEVEL)

    if cl:
        coloredlogs.install(level=LEVEL, milliseconds=True,
                            fmt=LOG_FORMAT, logger=logger)

    else:
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(LOG_FORMATTER)
        logger.addHandler(consoleHandler)

    if not os.path.exists(LOG_PATH):
        try:
            os.mkdir(LOG_PATH)
        except:
            print("Error creating "+LOG_PATH+", Please check permission")

    fileHandler = logging.FileHandler("{}/{}.log".format(LOG_PATH, nm))
    fileHandler.setFormatter(LOG_FORMATTER)
    logger.addHandler(fileHandler)

    allFileHandler = logging.FileHandler(
        "{}/{}.log".format(LOG_PATH, ALL_LOGS))
    allFileHandler.setFormatter(LOG_FORMATTER)
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
