"""Helper for setting up module-specific logging.
"""

import logging # type: ignore
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

    fh = logging.FileHandler(expanduser('{}{}.log'.format(fpath, fname)))
    fh.setLevel(level)
    default_fmt = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(fmt if fmt is not None else default_fmt)
    logger.addHandler(fh)

    return logger
