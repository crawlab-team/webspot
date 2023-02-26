import logging

_loggers = {}


def get_logger(name: str):
    # Check if logger already exists
    if _loggers.get(name) is not None:
        return _loggers.get(name)

    # Logger
    logger = logging.getLogger(name)

    # Handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Store logger
    _loggers[name] = logger

    return logger
