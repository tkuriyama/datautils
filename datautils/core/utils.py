"""Utility functions.
"""

from collections import defaultdict # type: ignore
from dataclasses import dataclass # type: ignore
from typing import Dict, List, Tuple, TypeVar, Union # type: ignore

################################################################################

@dataclass(frozen=True)
class OK:
    msg: str = 'OK'

@dataclass(frozen=True)
class Error:
    msg: str

Status = Union[OK, Error]

################################################################################
# Lists

T = TypeVar('T')
Matrix = List[List[T]]

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

def text_to_lists(text: str, delim: str) -> Matrix[str]:
    """Split text by delim to list of lists."""
    lines = text.split('\n')
    return [[elem.strip() for elem in line.strip().split(delim)]
            for line in lines]

def prepend_col(val: T, m: Matrix[T]) -> Matrix[T]:
    """Prepend column to list of lists."""
    return [[val] + row for row in m]

def append_col(val: T, m: Matrix[T]) -> Matrix[T]:
    """Append column to list of lists."""
    return [row + [val] for row in m]
