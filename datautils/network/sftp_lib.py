"""Lightweight wrapper for the pysftp library.
"""

import logging # type: ignore
import pysftp # type: ignore

from datautils.core import log_setup # type: ignore
# from datautils.core.utils import Error, OK, Status # type: ignore

################################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.INFO)


################################################################################

class SFTP:
    """SFTP Connection."""

    def __init__(self, host: str, user: str, pw: str) -> None:
        self.host = host
        self.conn = pysftp.Connection(host,
                                      username = user,
                                      password = pw)
        logger.info(f'Connected to {host}')

    def __enter__(self):
        """Provde Connection object for `with` context."""
        return self.conn

    def __exit__(self):
        """Close Connection for `with` context."""
        self.conn.close()
        logger.info(f'Closed connection to {self.host}')
