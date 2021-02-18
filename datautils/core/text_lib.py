"""Text convenience functions.
"""

from enum import Enum # type: ignore
import logging # type: ignore

from datautils.core import log_setup # type: ignore


################################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.WARNING)


################################################################################
# Numbers

class NumberStyle(Enum):
    US = 0
    EU = 1

def str_to_float(n: str, style: NumberStyle = NumberStyle.US) -> float:
    """Parse string to float."""
    if style == NumberStyle.US:
        n = n.replace(',', '')
    elif style == NumberStyle.EU:
        n = n.replace('.', '')
        n = n.replace(',', '.')

    for c in ('\'', '"', ':', ';'):
        n = n.replace(c, '')

    return float(n.strip())

def str_to_int(n: str, style: NumberStyle = NumberStyle.US) -> int:
    """Parse string to integer."""
    return int(str_to_float(n, style))

