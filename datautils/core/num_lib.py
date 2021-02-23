"""Numerical functions.
"""

import logging # type: ignore
import numpy as np # type: ignore
from typing import Collection, List, Optional, TypeVar # type: ignore

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


################################################################################
# Statistics

T = TypeVar('T')
Percentile = float

def windsorize(xs: Collection[T],
               lower: Percentile,
               upper: Percentile
               ) -> List[T]:
    """Windsorize given collection.
    Percentiles are defined in range [0.0, 100.0].
    Values are bound by the lower and upper percentile args.
    """
    if not approx_eq(lower, 100 - upper):
        logger.warning('Asymmetric bounds {} and {}'.format(lower, upper))
    if lower < 1.0 and upper < 1.0:
        msg = 'Percentiles defined in range [0.0, 100.0], got {}, {}'
        logger.warning(msg.format(lower, upper))

    low_val = np.percentile(list(xs), lower, interpolation='nearest')
    up_val = np.percentile(list(xs), upper, interpolation='nearest')

    return [low_val if x < low_val else up_val if x > up_val else x
            for x in xs]
