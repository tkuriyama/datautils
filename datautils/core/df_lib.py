"""Convenience functions for working with Pandas DataFrames.
"""

import logging # type: ignore
import pandas as pd # type: ignore
from typing import List, Tuple, TypedDict, TypeVar # type: ignore

from datautils.core import log_setup # type: ignore
from datautils.core.utils import Error, OK, Matrix, Status # type: ignore


################################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.INFO)


################################################################################
# Comparisons

Key = str
Record = str
Delta = str

Addition = Tuple[Key, Record]
Mod = Tuple[Key, Delta]
Retire = Tuple[Key, Record]

class DiffDict(TypedDict):
    adds: List[Addition]
    mods: List[Mod]
    retires: List[Retire]

def update(df1: pd.DataFrame,
           df2: pd.DataFrame,
           key_cols: List[str],
           ignore_cols: List[str]
           ) -> Tuple[pd.DataFrame, DiffDict, Status]:
    """Update df1 with df2, tracking diffs along the way."""
    dd : DiffDict = {'adds': [], 'mods': [], 'retires': []}

    dim_status = compare_dims(df1, df2, True, False)
    if dim_status != OK():
        return pd.DataFrame(), dd, dim_status

    # keep_keys, drop_keys = compare_keys(df1, df2, key_cols)


    return (pd.DataFrame(), dd, OK())

################################################################################
# Filtering

T = TypeVar('T')
ListPair = Tuple[T, List[T]]

def filter(df, **kwargs):
    """Filter DF with arbitrary kwargs.
    Applies naive (==) comparison on keys an values.
    """
    query_list = []
    for key in kwargs.keys():
        val = kwargs[key]
        val_str = f'"{val}"' if isinstance(val, str) else f'{str(val)}'
        query_list.append(f'{key}=={val_str}')
    query = ' & '.join(query_list)
    return df.query(query)

def filter_cols(df: pd.DataFrame, conds: List[ListPair]) -> pd.DataFrame:
    """Filter DF based on one or more column value filters."""
    query_list = []
    for col, vals in conds:
        query_list.append(f'{col}.isin({str(vals)})')
    query = ' & '.join(query_list)
    return df.query(query)


################################################################################
# Helpers

def df_to_matrix(df: pd.DataFrame, hdr: bool = False) -> Matrix:
    """Convert DF to list of lists."""
    m = df.to_numpy().tolist()
    return m if not hdr else [list(df.columns)] + m

def compare_dims(df1: pd.DataFrame,
                 df2: pd.DataFrame,
                 cols: bool = True,
                 rows: bool = False
                 ) -> Status:
    """Compare DF dimensions for compatibility."""
    status: Status
    cols1, cols2 = len(df1.columns), len(df2.columns)
    rows1, rows2 = len(df1), len(df2)

    if not cols and not rows:
        status = OK()
    elif cols and not rows:
        status = (OK() if cols1 == cols2 else
                  Error('Cols mismatch: {} vs {}'.format(cols1, cols2)))
    elif rows and not cols:
        status = (OK() if rows1 == rows2 else
                  Error('Rows mismatch: {} vs {}'.format(rows1, rows2)))
    else:
        status = (OK() if rows1 == rows2 and cols1 == cols2 else
                  Error('Matrix mismatch: {} x {} vs {} x {}'.format(rows1,
                                                                     cols1,
                                                                     rows2,
                                                                     cols2)))
    return status

def compare_keys(df1: pd.DataFrame,
                 df2: pd.DataFrame,
                 key_cols: List[str]
                 ) -> Tuple[List[str], List[str]]:
    """"""
    return [], []

