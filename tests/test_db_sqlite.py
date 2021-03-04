"""Pytest suite for db_lib.
"""

import logging # type: ignore

from datautils.core import log_setup # type: ignore
from datautils.core.utils import OK # type: ignore
from datautils.internal import db_sqlite # type: ignore

#########################################################g#######################
# Supress Error logging during testing

db_sqlite.logger = log_setup.init_file_log(__name__, logging.CRITICAL)


################################################################################

class TestSqlite:
    """Test Sqlite operations."""

    def test_parse_schema(self):
        """Test parse_schema."""
        f = db_sqlite.parse_schema
        s = 'CREATE TABLE SelectTest(TextCol TEXT,'
        s += 'IntCol INTEGER, FloatCol REAL);'

        assert f(s) == [('TextCol', str), ('IntCol', int),
                        ('FloatCol', float)]

        s2 = 'CREATE TABLE SelectTest(id INTEGER PRIMARY KEY,'
        s2 += 'TextCol TEXT, IntCol INTEGER, FloatCol DOUBLE);'

        assert f(s2) == [('TextCol', str), ('IntCol', int),
                         ('FloatCol', float)]

        # if not exists
        s3 = 'CREATE TABLE IF NOT EXISTS SelectTest(id INTEGER PRIMARY KEY,'
        s3 += 'TextCol TEXT, IntCol INTEGER, FloatCol DOUBLE);'
        assert f(s3) == [('TextCol', str), ('IntCol', int),
                         ('FloatCol', float)]

        # multiline
        s4 = """CREATE TABLE IF NOT EXISTS SelectTest(
                   id INTEGER PRIMARY KEY,
                   TextCol TEXT, IntCol INTEGER,
                   FloatCol DOUBLE);"""
        assert f(s4) == [('TextCol', str), ('IntCol', int),
                         ('FloatCol', float)]


    def test_sqlite_apply_schema(self):
        """Test apply_schema."""
        f = db_sqlite.apply_schema
        schema = [('strcol', str), ('intcol', int), ('floatcol', float)]
        rows = [['a', '1', '2.0']]
        assert f(schema, rows) == ([['a', 1, 2.0]], OK())

        # int(1.0) is ok but int('1.0') is not
        rows2 = [['1', '1.0', '1']]
        _, status = f(schema, rows2)
        assert status != OK()

        # float('a') is not ok
        rows3 = [['1', '1', 'a']]
        _, status = f(schema, rows3)
        assert status != OK()

