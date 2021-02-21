"""Helper for setting up module-specific logging.
"""

import logging # type: ignore
from logging.handlers import RotatingFileHandler # type: ignore
from os.path import expanduser # type: ignore
from typing import Optional # type: ignore

################################################################################

DEFAULTPATH = '~/logs/'

################################################################################

def init_file_log(fname: str,
                  level: int = logging.INFO,
                  fmt: Optional[logging.Formatter] = None,
                  fpath:  str = DEFAULTPATH,
                  ) -> logging.Logger:
    """Initialize and return a file logger."""
    logger = logging.getLogger(fname)
    logger.setLevel(level)

    f = expanduser('{}{}.log'.format(fpath, fname))
    fh = RotatingFileHandler(f, maxBytes=10000000, backupCount=10)
    default_fmt = logging.Formatter(
        '%(asctime)s - %(levelname)s - {} - %(message)s'.format(fname))
    fh.setFormatter(default_fmt if fmt is None else fmt)
    logger.addHandler(fh)

    return logger
