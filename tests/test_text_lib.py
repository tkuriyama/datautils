"""Pytest suite for text_lib.
"""

from datautils.core import text_lib


class TestNumbers:
    """Test number functions."""

    def test_str_to_float(self):
        """Test str_to_float conversion."""
        f = text_lib.str_to_float

        assert f('218,762.0001') == 218762.0001
        assert f('218.762,00', style=text_lib.NumberStyle.EU) == 218762.00
        assert f('218,762') == 218762.0
        assert f('762') == 762.0

    def test_str_to_int(self):
        """Test str_to_float conversion."""
        f = text_lib.str_to_int

        assert f('218,762.0001') == 218762
        assert f('218.762,00', style=text_lib.NumberStyle.EU) == 218762
        assert f('218,762') == 218762
        assert f('762') == 762
