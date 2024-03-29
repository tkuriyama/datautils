"""Convenience functions for working with Pandas DataFrames.
"""

from collections import OrderedDict  # type: ignore
import logging  # type: ignore
import pandas as pd  # type: ignore
from typing import (Collection, List, Set, Sequence, Tuple,
                    TypedDict, TypeVar)  # type: ignore

from datautils.core import log_setup  # type: ignore
from datautils.core.utils import Error, OK, Matrix, Status  # type: ignore


##########################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.INFO)


##########################################################################
# Logical Diff

Key = str
Col = str
Val = str
Delta = Tuple[Col, Val, Val]  # (col, old new)
Mod = Tuple[List[Key], List[Delta]]


class DiffDict(TypedDict):
    adds: pd.DataFrame
    mods: List[Mod]
    retires: pd.DataFrame


def diff_df(df1: pd.DataFrame,
            df2: pd.DataFrame,
            keys: List[Col],
            ignores: List[Col]
            ) -> Tuple[DiffDict, Status]:
    """Find diffs as a DiffDict of changes from df1 to df2."""
    dd: DiffDict = {'adds': None, 'mods': [], 'retires': None}

    dim_status = compare_dims(df1, df2, True, False)
    if dim_status != OK():
        return dd, dim_status

    df1_, df2_, retire_df, new_df = symm_diff_df(df1, df2, keys)
    mods, dim_status = find_mods(df1_, df2_, keys, ignores)
    if dim_status != OK():
        return dd, dim_status

    return {'adds': new_df, 'mods': mods, 'retires': retire_df}, OK()


def find_mods(df1: pd.DataFrame,
              df2: pd.DataFrame,
              keys: List[Col],
              ignores: List[Col] = []
              ) -> Tuple[List[Mod], Status]:
    """Find all changes as Mods from df1 to df2."""
    diff_cols = [col for col in df1.columns
                 if col not in keys and col not in ignores]
    dim_status = compare_dims(df1, df2, True, True)
    if dim_status != OK():
        return [], dim_status

    def f(x): return x.sort_values(by=keys).reset_index(drop=True)
    df1_, df2_ = f(df1), f(df2)

    mask = (df1_ != df2_).any(axis=1)
    df = df1_[mask].merge(df2_[mask], on=keys, suffixes=['_old', '_new'])
    pairs = [gen_mod(t._asdict(), keys, diff_cols)
             for t in df.itertuples(index=False)]

    return [pair for pair in pairs if pair[1]], OK()


def gen_mod(d: OrderedDict, keys: List[Col], diff_cols: List[Col]) -> Mod:
    """Generate Mod for a single row."""
    ks = [str(d[k]) for k in keys]
    vs = []
    for col in diff_cols:
        v_old, v_new = d[f'{col}_old'], d[f'{col}_new']
        if v_old != v_new:
            vs.append((col, str(v_old), str(v_new)))
    return ks, vs


def symm_diff_df(df1: pd.DataFrame,
                 df2: pd.DataFrame,
                 cols: List[Col]
                 ) -> Tuple[pd.DataFrame, pd.DataFrame,
                            pd.DataFrame, pd.DataFrame, ]:
    """Symmetric diff on given keys.
    Return tuple of DFs: (DF1 match, DF2 match, DF1 only, DF2 only).
    """
    both, df1_only, df2_only = symm_diff_cols(df1, df2, cols)
    def f(xs): return gen_list_pairs(cols, xs)
    return (filter_cols(df1, f(both)),
            filter_cols(df2, f(both)),
            filter_cols(df1, f(df1_only)),
            filter_cols(df2, f(df2_only)))


def empty_diff_dict(dd: DiffDict) -> bool:
    """Return true if DiffDict is empty."""
    return (len(dd['adds']) == 0 and
            len(dd['mods']) == 0 and
            len(dd['retires']) == 0)


##########################################################################
# Filtering

T = TypeVar('T')
ListPair = Tuple[Col, Sequence[T]]


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


def gen_list_pairs(cols: List[Col],
                   seqs: Collection[Sequence]
                   ) -> List[ListPair]:
    """Construct ListPairs."""
    pairs: List[ListPair] = []
    for i, col in enumerate(cols):
        pairs.append((col, [seq[i] for seq in seqs]))
    return pairs


##########################################################################
# Uniqueness

def split_unique(df: pd.DataFrame, keys: List[Col],) -> pd.DataFrame:
    """Split DF based on unique key cols.
    REturn (DF with duplicate key cols, DF with unique key cols).
    """
    dup_cols_set = [cols for cols, g in df.groupby(keys)
                    if len(g) >= 2]
    uniq_cols_set = [cols for cols, g in df.groupby(keys)
                     if len(g) == 1]

    dfs = []
    for cols_set in (dup_cols_set, uniq_cols_set):
        if not cols_set:
            dfs.append(pd.DataFrame())
            continue

        # cols_set should be List[Sequence[str]]
        if not isinstance(cols_set[0], tuple):
            cols_set = [[cols] for cols in cols_set]
        conds = gen_list_pairs(keys, cols_set)
        dfs.append(filter_cols(df, conds))

    dup_df, uniq_df = dfs[0], dfs[1]
    return dup_df, uniq_df


##########################################################################
# Converters

def df_to_matrix(df: pd.DataFrame, hdr: bool = False) -> Matrix:
    """Convert DF to list of lists."""
    m = df.to_numpy().tolist()
    return m if not hdr else [list(df.columns)] + m


def matrix_to_df(m: Matrix, hdr: bool = True) -> pd.DataFrame:
    """Convert list of lists to DF."""
    return (pd.DataFrame(m) if not hdr else
            pd.DataFrame(m[1:], columns=m[0]))


##########################################################################
# Helpers

ColsSet = Set[Tuple[Col, ...]]


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
                  Error(f'Cols mismatch: {cols1} vs {cols2}'))
    elif rows and not cols:
        status = (OK() if rows1 == rows2 else
                  Error(f'Rows mismatch: {rows1} vs {rows2}'))
    else:
        status = (OK() if rows1 == rows2 and cols1 == cols2 else
                  Error('Matrix mismatch: ' +
                        f'{rows1} x {cols1} vs {rows2} x {cols2}'))
    return status


def symm_diff_cols(df1: pd.DataFrame,
                   df2: pd.DataFrame,
                   cols: List[Col]
                   ) -> Tuple[ColsSet, ColsSet, ColsSet]:
    """Symmetric diff on given keys: in both, in df1 only, in df2 only."""
    k1 = cols_to_set(df1, cols)
    k2 = cols_to_set(df2, cols)
    return k1 & k2, k1 - k2, k2 - k1


def cols_to_set(df: pd.DataFrame, cols: List[str]) -> ColsSet:
    """Return given cols from DF as a set."""
    return set(tuple(ks) for ks in df_to_matrix(df[cols]))


##########################################################################
# Merging

def merge_rows(df: pd.DataFrame,
               sum_cols: List[str],
               avg_cols: List[str],
               uniq_cols: List[str]
               ) -> pd.DataFrame:
    s = df.apply(lambda col:
                 merge_col(col, sum_cols, avg_cols, uniq_cols))
    return s.to_frame().T


def merge_col(series: pd.Series,
              sum_cols: List[str],
              avg_cols: List[str],
              uniq_cols: List[str]
              ) -> pd.Series:
    name = series.name
    return (series.sum() if name in sum_cols else
            series.mean() if name in avg_cols else
            series.unique()[0])
