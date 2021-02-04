"""Utility functions.
"""

from collections import defaultdict # type: ignore
from typing import Dict, List, Tuple, TypeVar # type: ignore

################################################################################
# Lists

T = TypeVar('T')

def count_freq(lst: List[T]) -> Dict[T, int]:
    """Return frequency count of elements as dict."""
    d: dict
    d = defaultdict(int)
    for elem in lst:
        d[elem] += 1
    return d

def count_freq_list(lst: List[T]) -> List[Tuple[T, int]]:
    """Return frequncy count of elements as list of tuples."""
    d = count_freq(lst)
    return list(d.items())
