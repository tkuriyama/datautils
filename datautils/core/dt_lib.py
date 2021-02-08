"""Datetime convenience functions.
"""

import logging # type: ignore
import datetime as dt # type: ignore
from typing import Collection, List, Optional

from datautils.core import log_setup # type: ignore


################################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.WARNING)


################################################################################
# Date

def get_biz_date(date: dt.date,
                 delta: int,
                 holidays: Optional[Collection[dt.date]] = None
                 ) -> dt.date:
    """Get business date with specified time delta."""
    return get_date(date, delta, True, holidays)

def get_date(date: dt.date,
             delta: int,
             skip_weekend: bool = False,
             holidays: Optional[Collection[dt.date]] = None
             ) -> dt.date:
    """Get date with specifid time delta."""
    i = 0 if delta <= 0 else -1
    return get_dates(date, delta, skip_weekend, holidays)[i]

def get_dates(date: dt.date,
             delta: int,
             skip_weekend: bool = False,
             holidays: Optional[Collection[dt.date]] = None
             ) -> List[dt.date]:
    """Get dates in give delta range, inclusive of date."""
    i = -1 if delta < 0 else 1
    date_, dates = date, [date]
    while delta != 0:
        date_ += dt.timedelta(days=i)
        if (skip_weekend and not is_weekday(date_) or
            holidays and date_ in holidays):
            pass
        else:
            dates.append(date_)
            delta -= i
    return sorted(dates)


################################################################################
# Helpers

def is_weekday(date: dt.date) -> bool:
    """Return True if date is weekday (Mon - Fri)."""
    return dt.date.weekday(date) <= 4
