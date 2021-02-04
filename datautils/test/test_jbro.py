"""Pytest suite for jbro
"""

from datautils.json import jbro # type: ignore

################################################################################

class TestSearch:
    """Test the search functions."""

    def test_find_key(self):
        """Find key or nested keys in dict, return val."""
        f = jbro._find_key

        d1 = {'a': 'b'}
        d2 = {'a': 'b',
              'c': 'd',
              'e': {'f': 'g'}}
        d3 = {'a': {'b': {'c': 0}}}
        d4 = {'a': [{'b': 'miss'},
                    {'c': 'hit'}]}
        d5 = {'a': [{'b': 'miss'},
                    {'c': 'hit'},
                    {'c': 'hit2'}]}

        assert f(d1, 'a') == 'b'
        assert f(d2, 'e') == {'f': 'g'}
        assert f(d2, ['e', 'f']) == 'g'
        assert f(d3, ['a', 'b', 'c']) == 0
        assert f(d3, 'e') is None
        assert f(d3, ['a', 'd']) is None
        assert f(d4, ['a', 'c']) == ['hit']
        assert set(f(d5, ['a', 'c'])) == set(['hit', 'hit2'])

    def test_find_key_rec(self):
        """Find key recursively in dict."""
        f = jbro._find_key_rec

        d0 = {}
        d1 = {'a': 'b'}
        d2 = {'a': 'b',
              'c': 'd',
              'e': {'a': 'f'}}

        assert f(d0, 'a') == []
        assert f(d1, 'a') == [(0, 'b')]
        assert f(d2, 'a') == [(0, 'b'), (1, 'f')]

    def test_get_all_keys(self):
        """Retrieve all keys in dict"""
        f = jbro.get_all_keys

        d1 = {'a': '',
              'b': '',
              'c': ''}
        d2 = {'a': 'b',
              'c': 'd',
              'e': {'a': 'f'}}
        d3 = {'a': [{'b': ''},
                    {'c': ''}]}

        assert set(f(d1, 1, 0)) == set(['a', 'b', 'c'])
        assert set(f(d2, 1, 0)) == set(['a', 'c', 'e', 'e.a'])
        assert set(f(d3, 1, 0)) == set(['a', 'a.b', 'a.c'])

################################################################################

class TestHelpers:
    """Test the various helper functions."""

    def test_count_keys(self):
        """Count # keys in dict."""
        f = jbro.count_keys

        d0 = {}
        d1 = {'1': 0}
        d4 = {'1': {'2': 0},
              '3': 0,
              '4': [0, 0, 0]}

        assert f(d0) == 0
        assert f(d1) == 1
        assert f(d4) == 4

    def test_max_depth(self):
        """Find max depth of dict."""
        f = jbro.max_depth

        d6 = {1: {2: {3: {4: {5: {6: 'a'}}}}}}
        d0 = {}
        d1 = {'a': ['b', 1, 2, 3, {'4': '5'}]}

        assert f(d6) == 6
        assert f(d0) == 0
        assert f(d1) == 1

    def test_trim(self):
        """String trimming."""
        f = jbro.trim

        string = '0123456789abcdefg'
        assert f(string, 10) == '0123456...'
        assert f(string, 3) == '...'
        assert f(string, 0, '') == ''
        assert f(string, 100) == string

    def test_join_pair(self):
        """Joining pair to string."""
        f = jbro.join_pair

        v1, v2 = 'value1', 'value2'
        sep = '->'
        assert f(v1, v2, False, sep) == 'value1->value2'
        assert f(v1, v2, True, sep, 5) == 'va...->value2'
        assert f(v1, v2, True, sep, 5, 12) == 'va...->va...'
