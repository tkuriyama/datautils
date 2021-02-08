"""Pytest suite for db_lib.
"""

import pandas as pd # type: ignore

from datautils.core import db_lib # type: ignore
from datautils.core.utils import OK # type: ignore

################################################################################

class TestSqlite:
    """Test Sqlite operations."""

    def test_query_once(self, datadir):
        """Test simple query_once variants."""
        path = datadir.join('test.db')
        q = 'SELECT * FROM SelectTest WHERE TextCol="HelloWorld"'

        ret = db_lib.query_once(path, q)
        assert ret == [['HelloWorld', 7, 3.14]]

        ret = db_lib.query_once(path, q, True)
        assert ret == [['TextCol', 'IntCol', 'FloatCol'],
                       ['HelloWorld', 7, 3.14]]

        ret = db_lib.query_once(path, q, True, True)
        df = pd.DataFrame([['HelloWorld', 7, 3.14]],
                          columns=['TextCol', 'IntCol', 'FloatCol'])
        assert ret.equals(df)

    def test_query(self, datadir):
        """Test simple query variants."""
        path = datadir.join('test.db')
        q = 'SELECT * FROM SelectTest WHERE TextCol="HelloWorld"'
        db = db_lib.DB(path)

        ret, status = db.query(q)
        assert ret == [['HelloWorld', 7, 3.14]]
        assert status == db_lib.OK()

        ret, status = db.query(q, True)
        assert ret == [['TextCol', 'IntCol', 'FloatCol'],
                       ['HelloWorld', 7, 3.14]]
        assert status == db_lib.OK()

        ret, status = db.query(q, True, True)
        ret = db_lib.query_once(path, q, True, True)
        df = pd.DataFrame([['HelloWorld', 7, 3.14]],
                          columns=['TextCol', 'IntCol', 'FloatCol'])
        assert ret.equals(df)
        assert status == db_lib.OK()

        status = db.close()
        assert status == db_lib.OK()

    def test_parse_schema(self):
        """Test sqlite_parse_schema."""
        f = db_lib.sqlite_parse_schema
        s = 'CREATE TABLE SelectTest(TextCol TEXT,'
        s += 'IntCol INTEGER, FloatCol REAL);'

        assert f(s) == [('TextCol', str), ('IntCol', int),
                        ('FloatCol', float)]

        s2 = 'CREATE TABLE SelectTest(id INTEGER PRIMARY KEY,'
        s2 += 'TextCol TEXT, IntCol INTEGER, FloatCol DOUBLE);'

        assert f(s2) == [('TextCol', str), ('IntCol', int),
                         ('FloatCol', float)]

    def test_sqlite_apply_schema(self):
        """Test sqlite_apply_schema."""
        f = db_lib.sqlite_apply_schema
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

    def test_bad_insert(self, datadir):
        """Test inserts with schema violations fail."""
        path = datadir.join('test.db')
        db = db_lib.DB(path)

        # int('1.0') should fail schema casting
        rows = [['a', 1.0, 1.0],
                ['a', '1.0', '1.0']]
        assert db.insert('SelectTest', rows) != OK()

        # float('a') should fail schema casting
        rows2  = [['a', 1.0, 1.0],
                ['a', 1, 'a']]
        assert db.insert('SelectTest2', rows2) != OK()

        db.close()


################################################################################

class TestsQLHelpers:
    """Test SQL string helper functions."""

    def test_valid_query(self):
        f = db_lib.valid_query
        assert f('SELECT x FROM y') is True
        assert f('select * from x') is True
        assert f('DELETE * FROM x WHERE select') is False
        assert f('delete * FROM x WHERE select') is False
        assert f('INSERT INTO x WHERE select') is False
        assert f('insert INTO x WHERE select') is False
        assert f('drop table selecttable') is False

    def test_where(self):
        """Test where string generation,"""
        f = db_lib.where

        ts = [('col1', '>=', 1),
              ('col2', '=', 'asd')]
        assert f(ts) == 'WHERE col1>=1 AND col2="asd"'

        ts2 = [('col1', '>=', 1),
               ('col2', '=', '')]
        assert f(ts2) == 'WHERE col1>=1'
