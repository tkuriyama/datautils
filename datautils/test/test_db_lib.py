"""Pytest suite for db_lib.
"""

import pandas as pd # type: ignore

from datautils.core import db_lib # type: ignore

################################################################################

class TestSqlite:
    """Test Sqlite operations."""

    def test_query_once(self, datadir):
        """Test simple query_once variants."""
        path = datadir.join('test.db')
        q = 'SELECT * FROM SelectTest'

        ret = db_lib.query_once(path, q)
        assert ret == [('HelloWorld', 7, 3.14)]

        ret = db_lib.query_once(path, q, True)
        assert ret == [['TextCol', 'IntCol', 'FloatCol'],
                       ('HelloWorld', 7, 3.14)]

        ret = db_lib.query_once(path, q, True, True)
        df = pd.DataFrame([('HelloWorld', 7, 3.14)],
                          columns=['TextCol', 'IntCol', 'FloatCol'])
        assert ret.equals(df)

    def test_query(self, datadir):
        """Test simple query variants."""
        path = datadir.join('test.db')
        q = 'SELECT * FROM SelectTest'
        db = db_lib.DB(path)

        ret, status = db.query(q)
        assert ret == [('HelloWorld', 7, 3.14)]
        assert status == db_lib.OK()

        ret, status = db.query(q, True)
        assert ret == [['TextCol', 'IntCol', 'FloatCol'],
                       ('HelloWorld', 7, 3.14)]
        assert status == db_lib.OK()

        ret, status = db.query(q, True, True)
        ret = db_lib.query_once(path, q, True, True)
        df = pd.DataFrame([('HelloWorld', 7, 3.14)],
                          columns=['TextCol', 'IntCol', 'FloatCol'])
        assert ret.equals(df)
        assert status == db_lib.OK()

        status = db.close()
        assert status == db_lib.OK()

################################################################################

class TestsQLHelpers:
    """Test SQL string helper functions."""

    def test_valid_query(self):
        f = db_lib.valid_query
        assert f('SELECT x FROM y') is True
        assert f('DELETE FROM x WHERE select') is False
        assert f('INSERT INTO x WHERE select') is False
