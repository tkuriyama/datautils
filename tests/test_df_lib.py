"""Pytest suite for db_lib.
"""

import pandas as pd # type: ignore

from datautils.core import df_lib # type: ignore
from datautils.core.utils import OK # type: ignore


################################################################################

class TestFilters:
    """Test filter functions."""

    def test_filter(self):
        """Test filter."""
        f = df_lib.filter
        df = pd.DataFrame([[1, 2, 3], [4, 5, 6]],
                          columns=['a', 'b', 'c'])
        df2 = pd.DataFrame([[1, 2, 3]],
                           columns=['a', 'b', 'c'])
        assert f(df, **{'b': 2}).equals(df2) is True

        df = pd.DataFrame([['1', '2', '3'], ['4', '5', '6']],
                          columns=['a', 'b', 'c'])
        df2 = pd.DataFrame([['1', '2', '3']],
                           columns=['a', 'b', 'c'])
        assert f(df, **{'b': '2'}).equals(df2) is True

    def test_filter_cols(self):
        """Test filter."""
        f = df_lib.filter_cols
        df = pd.DataFrame([[1, 2, 3], [4, 5, 6]],
                          columns=['a', 'b', 'c'])
        df2 = pd.DataFrame([[1, 2, 3]],
                           columns=['a', 'b', 'c'])

        assert f(df, [('a', [1, 4])]).equals(df) is True
        assert f(df, [('a', [1, 4, 9])]).equals(df) is True
        assert f(df, [('a', [1])]).equals(df2) is True
        assert len(f(df, [('a', [])])) == 0


class TestHelpers:
    """Test helper funcs."""

    def test_df_to_matrix(self):
        """Test df_to_matrix."""
        f = df_lib.df_to_matrix
        df = pd.DataFrame([[1, 2, 3], [4, 5, 6]],
                          columns=['a', 'b', 'c'])

        assert f(df) == [[1, 2, 3],
                         [4, 5, 6]]
        assert f(df, True) == [['a', 'b', 'c'],
                               [1, 2, 3],
                               [4, 5, 6]]

    def test_compare_dims(self):
        """Test compare_dims"""
        f = df_lib.compare_dims
        df1 = pd.DataFrame([[1, 2], [3, 4]])
        df2 = pd.DataFrame([[1, 2, 3], [4, 5, 6]])
        df3 = pd.DataFrame([[1, 2], [3, 4], [5, 6]])
        df4 = pd.DataFrame([[8, 9], [10, 11]])

        assert f(df1, df2, False, True) == OK()
        assert f(df1, df2, True, False) != OK()
        assert f(df1, df3, True, False) == OK()
        assert f(df1, df3, False, True) != OK()
        assert f(df1, df4, True, True) == OK()
