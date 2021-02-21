"""Pytest suite for num_lib.
"""

import numpy as np

from datautils.core import num_lib # type: Ignore

################################################################################

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
