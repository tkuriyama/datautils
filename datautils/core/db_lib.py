"""A lightweight database connection wrapper for common operations.
For ease of testing and modularity, database operations are standalone
functions, though the common ones are also wrapped by the DB class.
"""


from dataclasses import dataclass # type: ignore
from enum import Enum # type: ignore
from typing import (Optional, Tuple) # type: ignore

import pandas as pd # type: ignore
import sqlite3

################################################################################

class DB_Type(Enum):
    SQLITE = 1
    POSTGRES = 2

class Code(Enum):
    OK = 0
    ERROR = 1

@dataclass
class Status():
    def __init__(self, code: Code, error_msg : Optional[Exception] = None):
        self.code = code
        self.error_msg = error_msg
    def show(self) -> str:
        c = 'OK' if self.code is Code.OK else 'Error'
        return c + '' if not self.error_msg else ': {}'.format(self.error_msg)

Conn = sqlite3.Connection
Cursor = sqlite3.Cursor

################################################################################

class DB:
    """A lightweight database connection state holder."""
    def __init__(self,
                 db_name: str,
                 db_type: DB_Type = DB_Type.SQLITE,
                 log_level: str = 'WARNING'
                 ) -> None:
        self.INVALID_STATUS = Status(Code.ERROR, Exception('Unknown DB_Type'))
        self.db_name = db_name
        self.db_type = db_type
        self.log_level = log_level
        self.__connect__()

    def __connect__(self) -> None:
        """Establish DB connection."""
        if self.db_type is DB_Type.SQLITE:
            self.conn = sqlite3.connect(self.db_name)
            self.cur = self.conn.cursor()
            self.status = Status(Code.OK)
        else:
            self.status = self.INVALID_STATUS

    def query(self,
              q: str,
              hdr: bool = False,
              df: bool = False
              ) -> Tuple[list, Status]:
        """Run query."""
        if self.db_type is DB_Type.SQLITE:
            ret, status = (sqlite_query(self.cur, q, hdr) if not df else
                           sqlite_query_df(self.cur, q))
        else:
            ret, status = [], self.INVALID_STATUS
        return ret, status

    def insert(self, table: str, rows: list) -> Status:
        """Run insert."""
        if self.db_type is DB_Type.SQLITE:
            status = sqlite_insert(self.conn, self.cur, table, rows)
        else:
            status = self.INVALID_STATUS
        return status

    def close(self) -> Status:
        """Close DB connection."""
        status = close(self.conn)
        return status


################################################################################
# DB_Type Agnostic Operations

def query_once(db_name: str,
               q: str,
               hdr: bool = False,
               df: bool = False,
               db_type: DB_Type = DB_Type.SQLITE
               ) -> list:
    """Convenience function: run single query and close connection."""
    c = DB(db_name, db_type)
    ret, _ = c.query(q, hdr, df)
    c.close()
    return ret

def close(conn) -> Status:
    """Close DB connection object."""
    try:
        conn.close()
        status = Status(Code.OK)
    except Exception as e:
        status = Status(Code.ERROR, e)
    return status

################################################################################
# DB_Type.SQLITE Operations

def sqlite_query(cur: Cursor, q: str, hdr: bool) -> Tuple[list, Status]:
    """Execute SQL query string."""
    if not valid_query(q):
        return [], Status(Code.ERROR, Exception('Invalid query {}'.format(q)))
    try:
        result = cur.execute(q)
        if hdr:
            cols = [d[0] for d in result.description]
            ret = [cols] + result.fetchall()
        else:
            ret = result.fetchall()
        status = Status(Code.OK)
    except Exception as e:
        ret, status = [], Status(Code.ERROR, e)
    return ret, status

def sqlite_query_df(cur: Cursor, q: str) -> Tuple[pd.DataFrame, Status]:
    """Execute SQL query string and return result as DataFrame."""
    ret, status = sqlite_query(cur, q, True)
    if status.code is not Code.OK or len(ret) < 2:
        return pd.DataFrame(), status
    df = pd.DataFrame(ret[1:], columns=ret[0])
    return df, status

def sqlite_insert(conn: Conn, cur: Cursor, table: str, rows: list) -> Status:
    """Attempt to execute SQL insertion into specified table."""
    ret, _ = sqlite_query(cur, 'SELECT * FROM {} LIMIT 1'.format(table), True)
    if not ret or len(ret[0]) != len(rows[0]):
        e = '\nError: insertion not completed.'
        e += '\ndb {} cols vs input {} cols\n'.format(len(ret[0]), len(rows[0]))
        return Status(Code.ERROR, Exception(e))

    try:
        cols = '(' + ','.join(['?'] * len(ret[0])) + ')'
        cur.executemany('INSERT INTO {} VALUES {}'.format(table, cols), rows)
        conn.commit()
        status = Status(Code.OK)
    except Exception as e:
        status = Status(Code.ERROR, e)

    return status

################################################################################
# SQL String Helpers

def valid_query(q: str) -> bool:
    ql = q.lower()
    return ('select' in ql and
            'from' in ql and
            'delete' not in ql and
            'insert' not in ql)
