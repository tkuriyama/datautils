"""Pytest suite for db_lib.
"""

import pandas as pd # type: ignore

from datautils.core import df_lib # type: ignore
from datautils.core.utils import OK, Error, Status # type: ignore


################################################################################

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
