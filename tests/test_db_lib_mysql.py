"""Pytest suite for db_lib with MySQL DB type.
"""

import logging  # type: ignore
import pandas as pd  # type: ignore

from datautils.core import db_lib, log_setup  # type: ignore
from datautils.core.utils import OK  # type: ignore
from datautils.internal import db_mysql  # type: ignore


#########################################################g################
# Supress Error logging during testing

db_lib.logger = log_setup.init_file_log(__name__, logging.CRITICAL)


##########################################################################

HOST = 'localhost'
USER = 'testuser'
PWD = 'testpassword'
NAME = 'test'

INTEGER = db_mysql.DTypeSpec(db_mysql.DType.INTEGER)
STRING = db_mysql.DTypeSpec(db_mysql.DType.VARCHAR, 20)


class TestMySQL:
    """Test MySQL operations."""

    def test_create(self, mysql_db_obj):
        """Test create."""

        td: db_mysql.TableDef = {
            'name': 'TestCreate',
            'if_not_exists': True,
            'cols': [('id', INTEGER, 0, 0, 1),
                     ('name', STRING, 0, 0, 1),
                    ('description', STRING, 0, 0, 1)],
            'fks': [],
            'pk': [],
            'uniq': ['name', 'description']
            }

        db = mysql_db_obj
        stmt, _ = db_lib.gen_mysql_create(td)
        status = db.create(stmt)
        assert status == OK()


    def test_query_once(self, mysql_db_obj):
        """Test simple query_once variants."""
        q = 'SELECT * FROM prices WHERE price > 0'

        ret = db_lib.query_once(HOST, q, True, False,
                                db_lib.DB_Type.MYSQL, USER, PWD, NAME)
        df = db_lib.query_once(HOST, q, True, True,
                               db_lib.DB_Type.MYSQL, USER, PWD, NAME)

        df2 = pd.DataFrame(ret[1:], columns=ret[0])
        assert df2.equals(df)

        ret2, _ = mysql_db_obj.query(q, True, False)
        assert ret == ret2


    def test_bad_insert(self, mysql_db_obj):
        """Test inserts with schema violations fail."""
        db = mysql_db_obj

        db.insert('TestCreate', [], [[1, 'myname', 'mydesc']])

        # violates uniqueness
        status = db.insert('TestCreate', [], [[1, 'myname', 'mydesc']])
        assert status != OK()
