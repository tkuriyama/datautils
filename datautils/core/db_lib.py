"""A lightweight database connection wrapper for common operations.
For ease of testing and modularity, database operations are standalone
functions, though the common ones are also wrapped by the DB class.
"""

from enum import Enum  # type: ignore
import logging  # type: ignore
import pandas as pd  # type: ignore
import pymysql  # type: ignore
from typing import List, Optional, Tuple, TypeVar, Union  # type: ignore
import sqlite3  # type: ignore

from datautils.core import log_setup  # type: ignore
from datautils.core.utils import Error, OK, Status  # type: ignore
from datautils.internal import db_sqlite  # type: ignore
from datautils.internal import db_mysql  # type: ignore


##########################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.INFO)


##########################################################################

class DB_Type(Enum):
    SQLITE = 1
    MYSQL = 2


T = TypeVar('T')
Rows = List[List[T]]
QueryResult = Union[Rows, pd.DataFrame]


##########################################################################

class DB:
    """A lightweight database connection state holder."""

    def __init__(self,
                 db_host: str,
                 db_type: DB_Type = DB_Type.SQLITE,
                 db_user: Optional[str] = None,
                 db_pwd: Optional[str] = None,
                 db_name: Optional[str] = None
                 ):
        self.INVALID_STATUS = Error('Unknown DB_Type value.')
        self.db_host = db_host
        self.db_type = db_type
        self.status: Status
        self.__connect__(db_user, db_pwd, db_name)

    def __connect__(self,
                    db_user: Optional[str],
                    db_pwd: Optional[str],
                    db_name: Optional[str]
                    ):
        """Establish DB connection."""
        if self.db_type is DB_Type.SQLITE:
            self.conn = sqlite3.connect(self.db_host)
            self.cur = self.conn.cursor()
            self.status = OK()
            self.conn.execute('PRAGMA foreign_keys = 1')
            logger.info(f'Connected to Sqlite DB: {self.db_host}')

        elif self.db_type is DB_Type.MYSQL:
            assert db_user is not None
            assert db_pwd is not None
            assert db_name is not None
            self.conn = pymysql.connections.Connection(host=self.db_host,
                                                       user=db_user,
                                                       password=db_pwd,
                                                       database=db_name)
            self.cur = self.conn.cursor()
            self.status = OK()
            logger.info('Connected to MySQL DB: {}'.format(self.db_host))

        else:
            self.status = self.INVALID_STATUS
            logger.error('DB conn failed: {}'.format(self.INVALID_STATUS.msg))

    def create(self, stmt: str) -> Status:
        """Create table."""
        if not safe_statement(stmt):
            msg = f'Safe statement check failed: {stmt}'
            logger.error(msg)
            return Error(msg)

        if self.db_type is DB_Type.SQLITE:
            status = db_sqlite.create(self.cur, stmt)
        elif self.db_type is DB_Type.MYSQL:
            status = db_mysql.create(self.cur, stmt)
        else:
            status = self.INVALID_STATUS
            logger.error(f'Create failed: {self.INVALID_STATUS.msg}')

        return status

    def query(self,
              q: str,
              hdr: bool = False,
              df: bool = False
              ) -> Tuple[QueryResult, Status]:
        """Run query."""
        if not valid_query(q):
            logger.error('Invalid query {}'.format(q))
            return [], Error('Invalid query {}'.format(q))

        if self.db_type is DB_Type.SQLITE:
            ret, status = (db_sqlite.query(self.cur, q, hdr) if not df else
                           db_sqlite.query_df(self.cur, q))
        elif self.db_type is DB_Type.MYSQL:
            ret, status = (db_mysql.query(self.cur, q, hdr) if not df else
                           db_mysql.query_df(self.cur, q))
        else:
            ret, status = [], self.INVALID_STATUS
            logger.error('Query failed: {}'.format(self.INVALID_STATUS.msg))

        return ret, status

    def insert(self,
               table: str,
               rows: Rows,
               cols: Optional[List[str]] = None
               ) -> Status:
        """Run insert."""
        if self.db_type is DB_Type.SQLITE:
            status = db_sqlite.insert(self.conn, self.cur, table, rows, True)
        elif self.db_type is DB_Type.MYSQL:
            status = db_mysql.insert(self.conn, self.cur, table,
                                     cols if cols else [], rows)
        else:
            status = self.INVALID_STATUS
            logger.error('Insert failed: {}'.format(self.INVALID_STATUS.msg))
        return status

    def close(self) -> Status:
        """Close DB connection."""
        status = close(self.conn)
        return status


##########################################################################
# DB_Type Agnostic Operations


def query_once(db_host: str,
               q: str,
               hdr: bool = False,
               df: bool = False,
               db_type: DB_Type = DB_Type.SQLITE,
               db_user: Optional[str] = None,
               db_pwd: Optional[str] = None,
               db_name: Optional[str] = None
               ) -> QueryResult:
    """Convenience function: run single query and close connection."""
    c = DB(db_host, db_type, db_user, db_pwd, db_name)
    ret, _ = c.query(q, hdr, df)
    c.close()
    return ret


def query_cols(db_host: str,
               table: str,
               db_type: DB_Type = DB_Type.SQLITE,
               db_user: Optional[str] = None,
               db_pwd: Optional[str] = None,
               db_name: Optional[str] = None
               ) -> List[str]:
    """Convenience function: get table column names."""
    db = DB(db_host, db_type, db_user, db_pwd, db_name)
    ret, _ = db.query(f'SELECT * FROM {table} LIMIT 1', True)
    db.close()
    return ret[0]


def insert_once(db_host: str,
                table: str,
                rows: Rows,
                db_type: DB_Type = DB_Type.SQLITE,
                db_user: Optional[str] = None,
                db_pwd: Optional[str] = None,
                db_name: Optional[str] = None
                ) -> Status:
    """Convenience function: insert and close connection."""
    db = DB(db_host, db_type, db_user, db_pwd, db_name)
    status = db.insert(table, rows)
    db.close()
    return status


def close(conn) -> Status:
    """Close DB connection object."""
    status: Status
    try:
        conn.close()
        status = OK()
        logger.info('Closed DB conn.')
    except Exception as e:
        status = Error(str(e))
        logger.error('Failed to close DB conn: {}'.format(str(e)))
    return status


##########################################################################
# SQL String Helpers

V = TypeVar('V', str, int, float)
CondTriple = Tuple[str, str, V]


def safe_statement(stmt: str) -> bool:
    """Validate if statement is safe."""
    stmt_ = stmt.lower()
    return ('drop table' not in stmt_ and
            'delete' not in stmt_ and
            'update' not in stmt_)


def valid_query(q: str) -> bool:
    """Validate if query string is valid."""
    ws = [w.strip().lower() for w in q.split(' ')]
    return ('select' in ws and
            'from' in ws and
            'drop' not in ws and
            'delete' not in ws and
            'insert' not in ws)


def where(triples: List[CondTriple]) -> str:
    """Return where clause string."""
    clauses = []
    for col, op, val in triples:
        if not val:
            continue  # ignore clauses if comparison value missing
        clause = '{} {} {}'.format(col, op, val)
        clauses.append(clause)
    return 'WHERE {}'.format(' AND '.join(clauses))


###########################################################################
# Exposing DB-Specific Operations


def gen_sqlite_create(td: db_sqlite.TableDef) -> Tuple[str, Status]:
    """Generate CREATE TABLE string from TableDef dict."""
    return db_sqlite.gen_create_stmt(td)


def gen_mysql_create(td: db_mysql.TableDef) -> Tuple[str, Status]:
    """Generate CREATE TABLE string from TableDef dict."""
    return db_mysql.gen_create_stmt(td)
