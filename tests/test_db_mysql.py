"""Test db_mysql.

Assumes MySQL server is running on localhost with
user `testuser` and pwd `testpassword` with full access to
database `test`.
"""

from datautils.internal import db_mysql  # type: ignore
from datautils.core.utils import OK  # type: ignore
# import pymysql # type: ignore

##########################################################################

INTEGER = db_mysql.DTypeSpec(db_mysql.DType.INTEGER)
FLOAT = db_mysql.DTypeSpec(db_mysql.DType.FLOAT)
STRING = db_mysql.DTypeSpec(db_mysql.DType.VARCHAR, 20)


class TestMySQL:

    def test_create_table_normal(self, mysql_db):
        conn, cursor = mysql_db
        """Test normal create table."""
        table_def: db_mysql.TableDef = {
            'if_not_exists': True,
            'name': 'prices',
            'cols': [('period', INTEGER, 0, 0, 1),
                     ('symbol', STRING, 0, 0, 1),
                     ('price', FLOAT, 0, 0, 1)],
            'fks': [],
            'pk': ['period', 'symbol'],
            'uniq': []
        }
        stmt, stmt_status = db_mysql.gen_create_stmt(table_def)
        status = db_mysql.create(cursor, stmt)
        assert stmt_status == OK()
        assert status == OK()
        conn.commit()

    def test_create_table_fail(self, mysql_db):
        conn, cursor = mysql_db
        """Test normal create table."""
        table_def: db_mysql.TableDef = {
            'if_not_exists': False,
            'name': 'prices',
            'cols': [('period', INTEGER, 0, 0, 1),
                     ('symbol', STRING, 0, 0, 1),
                     ('price', FLOAT, 0, 0, 1)],
            'fks': [],
            'pk': ['period', 'symbol'],
            'uniq': []
        }
        stmt, stmt_status = db_mysql.gen_create_stmt(table_def)
        status = db_mysql.create(cursor, stmt)
        assert stmt_status == OK()
        assert status != OK()

    def test_insert_query_normal(self, mysql_db):
        """Test normal insertion."""
        conn, cursor = mysql_db
        ret, _ = db_mysql.query(cursor, 'SELECT MAX(period) FROM prices')
        period = ret[0][0]
        period = 1 if not period else period + 1

        rows, _ = db_mysql.query(cursor, 'SELECT * FROM prices')

        status = db_mysql.insert(conn, cursor,
                                 'prices',
                                 ['period', 'symbol', 'price'],
                                 [[period, 'AAPL', 100.1]],
                                 True)
        assert OK() != db_mysql.valid_lengths(cursor, 'prices',
                                              ['period', 'symbol'],
                                              [[0, 'AAPL']])
        assert status == OK()

        rows_, _ = db_mysql.query(cursor, 'SELECT * FROM prices')
        assert len(rows) + 1 == len(rows_)

        # insert without explicit columns
        status = db_mysql.insert(conn, cursor,
                                 'prices',
                                 [],
                                 [[period + 1, 'AAPL', 100.1]],
                                 True)
        assert status == OK()

    def test_insert_fail(self, mysql_db):
        """Test normal insertion."""
        conn, cursor = mysql_db

        status = db_mysql.insert(conn, cursor,
                                 'prices',
                                 ['period', 'symbol'],
                                 [[0, 'AAPL']],
                                 True)
        assert status != OK()

        status = db_mysql.insert(conn, cursor,
                                 'prices',
                                 ['period', 'symbol'],
                                 [[0, 'AAPL']],
                                 False)
        assert status != OK()


##########################################################################


class TestMySQLHelpers:

    def test_dtype_to_str(self):
        """Test DType to string conversion."""
        assert INTEGER.to_str() == 'INTEGER'
        assert FLOAT.to_str() == 'FLOAT'
        assert STRING.to_str() == 'VARCHAR(20)'
