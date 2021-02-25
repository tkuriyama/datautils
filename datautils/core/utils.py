"""Utility functions.
"""

from collections import defaultdict # type: ignore
import csv # type: ignore
from dataclasses import dataclass # type: ignore
import importlib.util # type: ignore
from os import path # type: ignore
import pandas as pd # type: ignore
from typing import Callable, Dict, List, Tuple, TypeVar, Union # type: ignore


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

def text_to_matrix(text: str, delim: str = ',') -> Matrix[str]:
    """Split text by delim to list of lists."""
    lines = text.split('\n')
    return [[elem.strip() for elem in line.strip().split(delim)]
            for line in lines if line]

def text_to_df(text: str, delim: str = ',') -> pd.DataFrame:
    """Split text by delim to Pandas DF."""
    rows = text_to_matrix(text, delim)
    return pd.DataFrame(rows[1:], columns=rows[0])

def csv_to_matrix(lines: List[str],
                  delim: str = ',',
                  quoted: bool = False,
                  quote: str = '"'
                  ) -> Matrix[str]:
    """Use the csv module reader to parse to list of lists."""
    return [line for line in
            csv.reader(lines,
                       quotechar=quote,
                       delimiter=delim,
                       quoting=(csv.QUOTE_ALL if quoted else csv.QUOTE_NONE),
                       skipinitialspace=True)]

def prepend_col(val: T, m: Matrix[T]) -> Matrix[T]:
    """Prepend column to list of lists."""
    return [[val] + row for row in m]

def append_col(val: T, m: Matrix[T]) -> Matrix[T]:
    """Append column to list of lists."""
    return [row + [val] for row in m]

def replace_with(m: Matrix[T], i: int, f: Callable[[T], T]) -> Matrix[T]:
    """Replace ith column in matrix using given function.
    Returns original matrix if i is out of bounds.
    """
    return (m if i > len(m[0]) else
            [line[:i] + [f(line[i])] + line[i+1:] for line in m])

def drop_col(i: int, m: Matrix[T]) -> Matrix[T]:
    """Drop ith column in matrix."""
    if i < 0 or i >= len(m[0]): return m
    return [row[:i] + row[i+1:] for row in m]

def valid_shape(m: Matrix[T]) -> bool:
    """Check if m has a valid shape."""
    return all(len(row) == len(m[0]) for row in m)


################################################################################
# Modules

def load_module(path: str, name: str):
    """Dynamically load module at given path."""
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m) # type: ignore
    return m


################################################################################
# Strings

def userpath(path_str: str, fname: str = None) -> str:
    """Expand ~ in path if present; optionallyjoin with filename."""
    path_str_ = path.expanduser(path_str)
    return (path.join(path_str_, fname) if fname else
            path_str_)

