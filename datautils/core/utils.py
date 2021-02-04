"""Utility functions.
"""

from collections import defaultdict # type: ignore
from typing import Any, List, Tuple # type: ignore

################################################################################
# Lists

def count_freq(lst: list) -> dict:
    """Return frequency count of elements as dict."""
    d: dict
    d = defaultdict(int)
    for elem in lst:
        d[elem] += 1
    return d

def count_freq_list(lst: list) -> List[Tuple[Any, int]]:
    """Return frequncy count of elements as list of tuples."""
    d = count_freq(lst)
    return list(d.items())
