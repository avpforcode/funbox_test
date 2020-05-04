import logging
from logging.handlers import RotatingFileHandler


def init_log(name: str, level: int = logging.ERROR) -> logging.Logger:
    """ Create log instance operating during whole server process """
    log = logging.getLogger(name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
    file_handler = RotatingFileHandler('{}.log'.format(name), maxBytes=5 * 1024 * 1024, backupCount=1)

    file_handler.setFormatter(formatter)
    log.setLevel(level)
    log.addHandler(file_handler)

    return log
