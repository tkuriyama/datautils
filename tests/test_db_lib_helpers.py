"""Pytest suite for db_lib helpers.
"""

import logging  # type: ignore

from datautils.core import db_lib, log_setup  # type: ignore


#########################################################g################
# Supress Error logging during testing

db_lib.logger = log_setup.init_file_log(__name__, logging.CRITICAL)


##########################################################################


class TestsQLHelpers:
    """Test SQL string helper functions."""

    def test_safe_statement(self):
        """Test safe_statement"""
        f = db_lib.safe_statement
        assert f('DROP TABLE xys') is False
        assert f(' DELETE FROM xys') is False
        assert f(' UPDATE xys SET abc WHERE 123') is False
        assert f('CREATE TABLE abc') is True

    def test_valid_query(self):
        """Test valid_query"""
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

        ts = [('col1', '>=', '1'),
              ('col2', '=', '"asd"')]
        assert f(ts) == 'WHERE col1 >= 1 AND col2 = "asd"'

        ts2 = [('col1', '>=', '1'),
               ('col2', '=', '')]
        assert f(ts2) == 'WHERE col1 >= 1'
