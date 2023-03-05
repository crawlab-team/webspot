import logging
import os
import sys

_loggers = {}

log_level_name = os.environ.get('WEBSPOT_LOG_LEVEL', 'info')
log_level = logging.getLevelName(log_level_name.upper())


def get_logger(name: str, stream=sys.stdout):
    # check if logger already exists
    if _loggers.get(name) is not None:
        return _loggers.get(name)

    # logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # handler
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # add handler
    logger.addHandler(handler)

    # store logger
    _loggers[name] = logger

    return logger
