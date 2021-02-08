"""Pytest suite for db_lib.
"""

import datetime as dt # type: ignore

from datautils.core import dt_lib # type: ignore


################################################################################

class TestDate:
    """Test date functions."""

    def test_get_dates(self):
        """Test get_date related functions."""
        fb = dt_lib.get_biz_date
        fg = dt_lib.get_date
        fgs = dt_lib.get_dates

        d1 = dt.date(2021, 2, 1)

        # get_biz_date and get_date relationship
        assert fb(d1, 100) == fg(d1, 100, True)
        assert fb(d1, 100) != fg(d1, 100, False)

        # get_date and get_dates relationship
        assert fg(d1, -200) == fgs(d1, -200)[0]
        assert fg(d1, 200) == fgs(d1, 200)[-1]

        # test get_dates
        assert fgs(d1, -2) == [dt.date(2021, 1,  30),
                               dt.date(2021, 1, 31),
                               dt.date(2021, 2, 1)]
        assert fgs(d1, -2, True) == [dt.date(2021, 1,  28),
                                     dt.date(2021, 1, 29),
                                     dt.date(2021, 2, 1)]
        assert fgs(d1, 2, True) == [dt.date(2021, 2, 1),
                                    dt.date(2021, 2, 2),
                                    dt.date(2021, 2, 3)]

        # test get_dates with holidays
        hs = [dt.date(2021, 2, 3)]
        assert fgs(d1, 2, True, hs) == [dt.date(2021, 2, 1),
                                        dt.date(2021, 2, 2),
                                        dt.date(2021, 2, 4)]


class TestHelpers:
    """Test helper functions."""

    def test_is_weekday(self):
        """Test is_weekday()."""
        f = dt_lib.is_weekday
        monday =  dt.date(2021, 2, 1)
        friday = dt.date(2021, 2, 5)
        saturday = dt.date(2021, 2, 6)
        sunday = dt.date(2021, 2, 7)

        assert f(monday) is True
        assert f(friday) is True
        assert f(saturday) is False
        assert f(sunday) is False
