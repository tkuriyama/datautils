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

class TestParsers:
    """Test parser functions."""

    def test_parse_date_name(self):
        """Test parse_date_name -- where month is name."""
        f = dt_lib.parse_date_name
        assert f('Feb 21, 2020') == dt.date(2020, 2, 21)
        assert f('21 Feb, 2020') == dt.date(2020, 2, 21)
        assert f('21/Feb/2020') == dt.date(2020, 2, 21)
        assert f('2020/Feb/21') == dt.date(2020, 2, 21)
        assert f('2020, Feb 21') == dt.date(2020, 2, 21)
        assert f('Feb  21  2020') == dt.date(2020, 2, 21)

    def test_maybe_date(self):
        """"Test maybe_date."""
        f = dt_lib.maybe_date
        assert f(None, None, None) is None
        assert f(2021, None, 1) is None
        assert f(2021, 12, None) is None
        assert f(2021, 12, 32) is None
        assert f(2021, 12, 1) == dt.date(2021, 12, 1)

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

    def test_month_to_int(self):
        """Test month_to_int."""
        f = dt_lib.month_to_int
        assert f('Jan') == 1
        assert f('December') == 12
        assert f('jibberish') == None
        assert f('janu') == None
