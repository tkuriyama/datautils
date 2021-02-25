"""PyTest suite for utils.py
"""

from datautils.core import utils # type: ignore

################################################################################

class TestListUtils:
    """Test List utility functions."""

    def test_count_freq(self):
        """Test count freq"""
        f = utils.count_freq
        fl = utils.count_freq_list

        lst = [1, 1, 2, 3, 2]

        assert f(lst) == {1: 2, 2: 2, 3: 1}
        assert sorted(fl(lst), key=lambda x: x[0]) == [(1, 2), (2, 2), (3, 1)]

    def test_text_to_matrix(self):
        """Test text to list of lists transform."""
        f = utils.text_to_matrix

        t1 = 'A,B,C \n1,2,3'
        assert f(t1, ',') == [['A', 'B', 'C'], ['1', '2', '3']]

        t2 = ''
        assert f(t2, ',') == []

    def test_csv_to_matrix(self):
        """Test csv to list of lists transform."""
        f = utils.csv_to_matrix

        t1 = ['A,B,C', '1,2,3']
        assert f(t1, ',') == [['A', 'B', 'C'], ['1', '2', '3']]

        t2 = ''
        assert f(t2, ',') == []

        t3 = ['A,B,C', '1,2,"3,4"']
        quoted = [['A', 'B', 'C'], ['1', '2', '3,4']]
        assert utils.csv_to_matrix(t3, ',', True) == quoted


    def test_prepend_col(self):
        """Test matrix column prepend."""
        f = utils.prepend_col
        m1 = [[]]
        m2 = [[1], [2]]

        assert f('a', m1) == [['a']]
        assert f(0, m2) == [[0, 1], [0, 2]]

    def test_append_col(self):
        """Test matrix column append."""
        f = utils.append_col
        m1 = [[]]
        m2 = [[1], [2]]

        assert f('a', m1) == [['a']]
        assert f(0, m2) == [[1, 0], [2, 0]]

    def test_drop_col(self):
        """Test drop_col"""
        f = utils.drop_col
        m = [[1,2,3], [4,5,6]]
        assert f(3, m) == m
        assert f(2, m) == [[1, 2], [4, 5]]
        assert f(-1, m) == m
        assert f(0, m) == [[2, 3], [5, 6]]

    def test_replace_with(self):
        """Test replace_with matrix function."""
        f = utils.replace_with
        g = lambda x: x+1
        m = [[1,2,3], [4,5,6]]
        assert f(m, 1, g) == [[1,3,3], [4,6,6]]
        assert f(m, 4, g) == m

    def test_valid_shape(self):
        """Test valid shape function."""
        f = utils.valid_shape

        assert f([[0], [1]]) is True
        assert f([]) is True
        assert f([[1,2], [3,4], [5,6]]) is True
        assert f([[0], [1,2]]) is False
        assert f([[], [1]]) is False
