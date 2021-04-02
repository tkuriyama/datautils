"""Pytest suite for http_lib.
"""

from datautils.network import http_lib # type: ignore

class TestHelpers:
    """Test helper functions."""

    def test_url_join(self):
        """"Test url_join"""
        f = http_lib.url_join
        assert f(['www.example.com', 'v1']) == 'www.example.com/v1'
        assert f(['www.example.com/', 'v1']) == 'www.example.com/v1'
        assert f(['www.example.com/', 'v1/']) == 'www.example.com/v1'

        assert f(['www.example.com/', 'v1/'], {}) == 'www.example.com/v1'
        d = {'auth': 'abcde'}
        assert (f(['www.example.com/', 'v1/'], d)
                == 'www.example.com/v1?auth=abcde')
        d = {'auth': 'abcde', 'user': '1'}
        assert (f(['www.example.com/', 'v1/'], d)
                == 'www.example.com/v1?auth=abcde&user=1')
