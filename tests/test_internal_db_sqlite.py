"""Pytest suite for db_lib.
"""

import logging  # type: ignore

from datautils.core import log_setup  # type: ignore
from datautils.core.utils import OK  # type: ignore
from datautils.internal import db_sqlite  # type: ignore
from datautils.internal.db_sqlite import DType  # type: ignore
#########################################################g################
# Supress Error logging during testing

db_sqlite.logger = log_setup.init_file_log(__name__, logging.CRITICAL)


##########################################################################

class TestCreate:
    """Test create table strings."""

    def test_gen_create_stmt(self):
        """Test gen_create_stmt."""
        f = db_sqlite.gen_create_stmt

        # create statements
        td = {'if_not_exists': True,
              'name': 'Table',
              'cols': [],
              'fks': [],
              'pk': [],
              'uniq': []
              }
        assert 'CREATE TABLE IF NOT EXISTS' in f(td)[0]
        td['if_not_exists'] = False
        assert ('CREATE TABLE IF NOT EXISTS' in f(td)[0]) is False
        assert 'CREATE TABLE' in f(td)[0]

        # create table with some cols
        td2 = {'if_not_exists': True,
               'name': 'Test',
               'cols': [('id', DType.INTEGER, True, False, False)],
               'fks': [],
               'pk': [],
               'uniq': []
               }
        s, status = f(td2)
        assert status == OK()
        s_ = 'CREATE TABLE IF NOT EXISTS Test(id INTEGER PRIMARY KEY\n);'
        assert s == s_

        td3 = {'if_not_exists': True,
               'name': 'Test',
               'cols': [('id', DType.INTEGER, True, False, False),
                        ('name', DType.TEXT, False, True, True),
                        ('height', DType.REAL, False, False, False)],
               'fks': [],
               'pk': [],
               'uniq': []
               }
        s, status = f(td3)
        assert status == OK()
        assert (db_sqlite.parse_schema(s) ==
                [('name', str), ('height', float)])
        assert 'name TEXT UNIQUE NOT NULL' in s

        # all table options for syntax verification
        td4 = {'if_not_exists': True,
               'name': 'Test',
               'cols': [('id', DType.INTEGER, True, False, False),
                        ('name', DType.TEXT, False, True, True),
                        ('height', DType.REAL, False, False, False)],
               'fks': [{'cols': ['height'],
                        'ref_table': 'Other',
                        'ref_cols': ['height']},
                       {'cols': ['name', 'height'],
                        'ref_table': 'Other',
                        'ref_cols': ['name', 'height']}],
               'pk': ['name', 'height'],
               'uniq': ['name', 'height']
               }
        s, status = f(td4)
        assert status == OK()
        assert (db_sqlite.parse_schema(s) ==
                [('name', str), ('height', float)])
        assert 'name TEXT UNIQUE NOT NULL' in s

        # bad foreign key spec
        td5 = {'if_not_exists': True,
               'name': 'Test',
               'cols': [('id', DType.INTEGER, True, False, False),
                        ('name', DType.TEXT, False, True, True),
                        ('height', DType.REAL, False, False, False)],
               'fks': [{'cols': ['name'],
                        'ref_table': 'Other',
                        'ref_cols': ['name', 'height']}],
               'pk': ['name', 'height'],
               'uniq': ['name', 'height']
               }
        s, status = f(td5)
        assert status != OK()

        # bad column spec, PK and Unique should not be used together
        td6 = {'if_not_exists': True,
               'name': 'Test',
               'cols': [('id', DType.INTEGER, True, True, False)],
               'fks': [],
               'pk': [],
               'uniq': []
               }
        assert f(td6) != OK()


class TestSchema:
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
