"""Pytest suite for num_lib.
"""

import numpy as np  # type: ignore

from datautils.core import num_lib  # type: Ignore

##########################################################################


class TestFloat:
    """Test float functions."""

    def test_approx_eq(self):
        """Test approx_eq"""
        f = num_lib.approx_eq
        assert f(1.0, 1.0) is True

        assert f(1.0, 0.5) is False
        assert f(1.0, 0.5, 0.0, 0.5) is True

        assert f(1.0, 0.9, 0.1) is False
        assert f(1.0, 0.99, 0.1) is True
        assert f(np.pi, 3.14159) is True


class TestStatistics:
    """Test statistics functions."""

    def test_windsorize(self):
        """Test windsozie."""
        f = num_lib.windsorize

        xs = [x for x in range(1, 101)]
        xs_set = set(xs)

        xs_ = f(xs, 5, 95)
        assert all([x >= 5 and x <= 95 for x in xs_]) is True

        xs_set_ = f(xs_set, 5, 95)
        assert all([x >= 5 and x <= 95 for x in xs_set_]) is True
