"""Numerical functions.
"""

import logging # type: ignore
from typing import Optional # type: ignore

from datautils.core import log_setup # type: ignore

################################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.INFO)


################################################################################
# Floats

def approx_eq(f1: float,
              f2: float,
              epsilon: float = 0.0001,
              epsilon_abs: Optional[float] = None
              ) -> bool:
    """Approximate equality for floats.
    Use epsilon_abs as absolute value if given; else use epsilon as proportion.
    """
    diff = abs(epsilon_abs) if epsilon_abs else abs(epsilon * min(f1, f2))
    return abs(f2 - f1) <= diff
