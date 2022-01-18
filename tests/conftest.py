"""PyTest Fixtures.
"""

from distutils import dir_util  # type: ignore
import os  # type: ignore
import pymysql  # type: ignore
from pytest import fixture  # type: ignore

from datautils.core import db_lib  # type: ignore


##########################################################################


@fixture
def datadir(tmpdir, request):
    """Datadir looks for test data stored in specific directories.
    The directory name should match the test name, e.g. test_a/ for test_a.py
    From https://stackoverflow.com/a/29631801/2649084
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))  # TODO: REPLACE

    return tmpdir


@fixture
def mysql_db():
    """Provide connection and cursor objects for MySQL test DB."""
    conn = pymysql.connections.Connection(host='localhost',
                                          user='testuser',
                                          password='testpassword',
                                          database='test')
    cursor = conn.cursor()
    yield (conn, cursor)
    conn.close()


@fixture
def mysql_db_obj():
    """Provide connection and cursor objects for MySQL test DB."""
    db = db_lib.DB('localhost',
                   db_lib.DB_Type.MYSQL,
                   'testuser',
                   'testpassword',
                   'test')
    yield db
    db.close()
