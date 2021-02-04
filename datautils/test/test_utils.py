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
