"""Datetime convenience functions.
"""

import logging # type: ignore
import datetime as dt # type: ignore
from typing import Collection, List, Optional
import re # type: ignore

from datautils.core import log_setup # type: ignore


################################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.WARNING)


################################################################################
# Date Deltas

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
# Date Parsing

def parse_date_word(date: str) -> Optional[dt.date]:
    """Parse date with month as word."""
    p1 = r'([0-9]{1,2})[\s,/]+([a-z]+)[\s,/]+([0-9]{4})'
    p2 = r'([a-z]+)[\s,/]+([0-9]+)[\s,/]+([0-9]+)'
    p3 = r'([0-9]{4})[\s,/]+([a-z]+)[\s,/]+([0-9]{1,2})'

    mp1 = re.findall(p1, date, re.IGNORECASE)
    mp2 = re.findall(p2, date, re.IGNORECASE)
    mp3 = re.findall(p3, date, re.IGNORECASE)

    if mp1 and len(mp1[0]) == 3:
        d, m, y = mp1[0]
    elif mp2 and len(mp2[0]) == 3:
        m, d, y = mp2[0]
    elif mp3 and len(mp3[0]) == 3:
        y, m, d = mp3[0]
    else:
        y, m, d = 0, None, 0

    return maybe_date(int(y), month_to_int(m), int(d))

def maybe_date(my: Optional[int],
               mm: Optional[int],
               md: Optional[int]
               ) -> Optional[dt.date]:
    """Return a date if int args for year, month, date are valid."""
    return (dt.date(my, mm, md) if my and my in range(0, 3000) and
                                   mm and mm in range(1, 13) and
                                   md and md in range(1, 32) else
            None)

################################################################################
# Helpers

def is_weekday(date: dt.date) -> bool:
    """Return True if date is weekday (Mon - Fri)."""
    return dt.date.weekday(date) <= 4

def month_to_int(month: str) -> Optional[int]:
    """Attempt to parse month from word to int."""
    m = month.lower().strip()
    return (1 if m in ('jan', 'january') else
            2 if m in ('feb', 'february') else
            3 if m in ('mar', 'march') else
            4 if m in ('apr', 'april') else
            5 if m in ('may',) else
            6 if m in ('jun', 'june') else
            7 if m in ('jul', 'july') else
            8 if m in ('aug', 'august') else
            9 if m in ('sep', 'sept', 'september') else
            10 if m in ('oct', 'october') else
            11 if m in ('nov', 'november') else
            12 if m in ('dec', 'december') else
            None)
