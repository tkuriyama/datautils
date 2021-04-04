"""Pytest suite for db_lib.
"""

import pandas as pd # type: ignore

from datautils.core import df_lib # type: ignore
from datautils.core.utils import OK # type: ignore


################################################################################

class TestComparison:
    """Test comparison functions."""

    def test_diff_df(test):
        """Test diff_df()."""
        f = df_lib.diff_df
        df1 = pd.DataFrame([[1,2,3],
                            [4,5,6],
                            [7,8,9],
                            [12, 13, 14]],
                           columns=['a', 'b', 'c'])
        df2 = pd.DataFrame([[1,2,4],
                            [4,5,6],
                            [7,10,9],
                            [15, 16, 17]],
                           columns=['a', 'b', 'c'])

        adds = df2[df2['a'] == 15]
        mods = [(['7'], [('b', '8', '10')])]
        retires = df1[df1['a'] == 12]

        d, status = f(df1, df2, ['a'], ['c'])
        assert d['adds'].equals(adds)
        assert d['mods'] == mods
        assert d['retires'].equals(retires)
        assert status == OK()

    def test_find_mods(self):
        """Test find mod."""
        f = df_lib.find_mods

        df1 = pd.DataFrame([[1,2,3],
                            [4,5,6],
                            [7,8,9]],
                           columns=['a', 'b', 'c'])
        df2 = pd.DataFrame([[1,2,4],
                            [4,5,6],
                            [7,10,9]],
                           columns=['a', 'b', 'c'])

        assert f(df1, df2, ['a'], ['b', 'c']) == ([], OK())
        assert (f(df1, df2, ['a'], ['c']) ==
                ([(['7'], [('b', '8', '10')])], OK())
                )
        assert (f(df1, df2, ['a'], []) ==
                ([(['1'], [('c', '3', '4')]),
                  (['7'], [('b', '8', '10')])], OK())
                )

    def test_gen_mod(self):
        """Test gen_mod"""
        f = df_lib.gen_mod
        d = {'key': 1,
             'a_old': 2, 'a_new': 3,
             'b_old': 'same', 'b_new': 'same',
             'c_old': 'diff1', 'c_new': 'diff2'
             }
        assert f(d, ['key'], []) == (['1'], [])
        assert f(d, ['key'], ['a']) == (['1'], [('a', '2', '3')])

    def test_symm_diff_df(self):
        """Test symM_diff_df."""
        f = df_lib.symm_diff_df
        df = pd.DataFrame([[1, 2, 3],
                           [4, 5, 6]],
                          columns=['a', 'b', 'c'])
        df2 = pd.DataFrame([[1, 2, 4],
                            [7, 8, 9]],
                           columns=['a', 'b', 'c'])

        df_ = pd.DataFrame([[1, 2, 3]],
                           columns=['a', 'b', 'c'])
        df_only = pd.DataFrame([[4, 5, 6]],
                               columns=['a', 'b', 'c'])
        df2_ = pd.DataFrame([[1, 2, 4]],
                            columns=['a', 'b', 'c'])
        df2_only = pd.DataFrame([[7, 8, 9]],
                                columns=['a', 'b', 'c'])

        quad = (df_, df2_, df_only, df2_only)
        assert all(a.reset_index(drop=True).equals(b) for (a, b) in
                   zip(f(df, df2, ['a', 'b']), quad)) is True

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

class TestUniques:
    """Test uniqueness functions."""

    def test_split_unique(self):
        """Test split_unique."""
        f = df_lib.split_unique

        df = pd.DataFrame([[1, 2, 3], [1, 3, 4], [2, 5, 6]],
                          columns=['TestKey', 'b', 'c'])

        df2 = pd.DataFrame([[1, 2, 3], [1, 3, 4]],
                           columns=['TestKey', 'b', 'c'])
        df3 = pd.DataFrame([[2, 5, 6]],
                           columns=['TestKey', 'b', 'c'])

        dup_df, uniq_df = f(df, ['TestKey'])
        assert dup_df.reset_index(drop=True).equals(df2)
        assert uniq_df.reset_index(drop=True).equals(df3)

        dup_df, uniq_df = f(df, ['TestKey', 'b'])
        assert dup_df.equals(pd.DataFrame())
        assert uniq_df.equals(df)

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

    def test_symm_diff_cols(self):
        """Test symm_diff_cols."""

        f = df_lib.symm_diff_cols
        df = pd.DataFrame([[1, 2, 3],
                           [4, 5, 6]],
                          columns=['a', 'b', 'c'])
        df2 = pd.DataFrame([[1, 2, 3],
                            [7, 8, 9]],
                           columns=['a', 'b', 'c'])

        triple = set([(1, 2)]), set([(4, 5)]), set([(7, 8)])
        assert f(df, df2, ['a', 'b']) == triple

    def test_cols_to_set(self):
        """Test cols_to_set."""
        f = df_lib.cols_to_set
        df = pd.DataFrame([[1, 2, 3],
                           [4, 5, 6],
                           [1, 5, 9]],
                          columns=['a', 'b', 'c'])

        assert f(df, ['a']) == set([(1, ), (4, )])
        assert f(df, ['a', 'b']) == set([(1, 2), (4, 5), (1, 5)])

    def test_empty_diff_dict(self):
        """Test empty_diff_dict."""
        f = df_lib.empty_diff_dict
        dd : df_lib.DiffDict = {
            'adds': pd.DataFrame(),
            'mods': [],
            'retires': pd.DataFrame()
        }
        assert f(dd) is True
        dd['mods'] = [('a', 'b')]
        assert f(dd) is False


class TestMerge:
    """Test merge functions."""

    def test_merge_rows(self):
        """Test merge rows"""
        f = df_lib.merge_rows

        cols = ['Ticker', 'Shares', 'Price', 'Type']
        df = pd.DataFrame([['A', 1, 2, 'C'],
                           ['A', 2, 3, 'D']],
                          columns = cols)
        df2 = pd.DataFrame([['A', 3, 2.5, 'C']],
                           columns = cols)

        assert (f(df, ['Shares'], ['Price'], []) == (df2)).all().all()
