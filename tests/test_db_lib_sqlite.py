"""Pytest suite for db_lib with Sqlite DB type.
"""

import logging  # type: ignore
import pandas as pd  # type: ignore

from datautils.core import db_lib, log_setup  # type: ignore
from datautils.core.utils import OK  # type: ignore
from datautils.internal import db_sqlite  # type: ignore


#########################################################g################
# Supress Error logging during testing

db_lib.logger = log_setup.init_file_log(__name__, logging.CRITICAL)


##########################################################################

class TestSqlite:
    """Test Sqlite operations."""

    def test_create(self, datadir):
        """Test create."""
        td = {'name': 'TestCreate',
              'if_not_exists': True,
              'cols': [('id', db_sqlite.DType.INTEGER, True, 0, 0),
                       ('name', db_sqlite.DType.TEXT, 0, 0, 1),
                       ('desc', db_sqlite.DType.TEXT, 0, 0, 1)],
              'fks': [],
              'pk': [],
              'uniq': ['name', 'desc']
              }

        path = datadir.join('test.db')
        db = db_lib.DB(path)
        stmt, _ = db_lib.gen_sqlite_create(td)
        status = db.create(stmt)
        assert status == OK()

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

    def test_bad_insert(self, datadir):
        """Test inserts with schema violations fail."""

        path = datadir.join('test.db')
        db = db_lib.DB(path)

        # int('1.0') should fail schema casting
        rows = [['a', 1.0, 1.0],
                ['a', '1.0', '1.0']]
        assert db.insert('SelectTest', rows) != OK()

        # float('a') should fail schema casting
        rows2 = [['a', 1.0, 1.0],
                 ['a', 1, 'a']]
        assert db.insert('SelectTest2', rows2) != OK()

        db.close()

##########################################################################


class TestSqliteHelpers:
    """Test Sqlite helpers."""

    def test_dtype_to_str(self):
        """Test DType conversion."""
        assert (db_sqlite.dtype_to_str(db_sqlite.DType.INTEGER) ==
                'INTEGER')
        assert (db_sqlite.dtype_to_str(db_sqlite.DType.REAL) ==
                'REAL')
        assert (db_sqlite.dtype_to_str(db_sqlite.DType.BOOLEAN) ==
                'BOOLEAN')
        assert (db_sqlite.dtype_to_str(db_sqlite.DType.TEXT) ==
                'TEXT')
