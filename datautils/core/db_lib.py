"""A lightweight database connection wrapper for common operations.
For ease of testing and modularity, database operations are standalone
functions, though the common ones are also wrapped by the DB class.
"""

from enum import Enum # type: ignore
import logging # type: ignore
import pandas as pd # type: ignore
from typing import List, Tuple, TypeVar # type: ignore
import re # type: ignore
import sqlite3 # type: ignore

from datautils.core import log_setup # type: ignore
from datautils.core.utils import Error, OK, Status # type: ignore

################################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.INFO)


################################################################################

class DB_Type(Enum):
    SQLITE = 1
    POSTGRES = 2

T = TypeVar('T')
Rows = List[List[T]]

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
        self.INVALID_STATUS = Error('Unknown DB_Type value.')
        self.db_name = db_name
        self.db_type = db_type
        self.log_level = log_level
        self.status : Status
        self.__connect__()

    def __connect__(self) -> None:
        """Establish DB connection."""
        if self.db_type is DB_Type.SQLITE:
            self.conn = sqlite3.connect(self.db_name)
            self.cur = self.conn.cursor()
            self.status = OK()
            logger.info('Connected to Sqlite DB: {}'.format(self.db_name))
        else:
            self.status = self.INVALID_STATUS
            logger.error('DB conn failed: {}'.format(self.INVALID_STATUS.msg))

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
            logger.error('Query failed: {}'.format(self.INVALID_STATUS.msg))
        return ret, status

    def insert(self,
               table: str,
               rows: Rows,
               schema_cast: bool = True
               ) -> Status:
        """Run insert."""
        if self.db_type is DB_Type.SQLITE:
            status = sqlite_insert(self.conn, self.cur, table, rows,
                                   schema_cast)
        else:
            status = self.INVALID_STATUS
            logger.error('Insert failed: {}'.format(self.INVALID_STATUS.msg))
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

def close(conn: Conn) -> Status:
    """Close DB connection object."""
    status : Status
    try:
        conn.close()
        status = OK()
        logger.info('Closed DB conn.')
    except Exception as e:
        status = Error(str(e))
        logger.error('Failed to close DB conn: {}'.format(str(e)))
    return status


################################################################################
# DB_Type.SQLITE Operations

RowsPair = Tuple[Rows, Status]
SqliteSchema = List[Tuple[str, type]]

def sqlite_query(cur: Cursor, q: str, hdr: bool = False) -> RowsPair:
    """Execute SQL query string."""
    status: Status
    if not valid_query(q):
        logger.error('Invalid query {}'.format(q))
        return [], Error('Invalid query {}'.format(q))
    try:
        result = cur.execute(q)
        if hdr:
            cols = [d[0] for d in result.description]
            rows = [cols] + [list(row) for row in result.fetchall()]
        else:
            rows = [list(row) for row in result.fetchall()]
        status = OK()
        logger.info('Query executed: {}'.format(q))
    except Exception as e:
        logger.error('Query exception: {}; {}'.format(q, str(e)))
        rows, status = [], Error(str(e))
    return rows, status

def sqlite_query_df(cur: Cursor, q: str) -> Tuple[pd.DataFrame, Status]:
    """Execute SQL query string and return result as DataFrame."""
    rows, status = sqlite_query(cur, q, True)
    if status != OK() or len(rows) < 2:
        logger.debug('Invalid status or not enough data, returning empty DF')
        return pd.DataFrame(), status
    df = pd.DataFrame(rows[1:], columns=rows[0])
    return df, status

def sqlite_insert(conn: Conn,
                  cur: Cursor,
                  table: str,
                  rows: Rows,
                  schema_cast: bool = True
                  ) -> Status:
    """Attempt to execute SQL insertion into specified table."""
    status: Status
    schema, (rows_, v) = sqlite_validate_insert(cur, table, rows, schema_cast)
    if v != OK(): return v

    try:
        cols = ','.join(name for name, _ in schema)
        vals = ','.join('?' * len(schema))
        i = 'INSERT INTO {}({}) VALUES ({})'.format(table, cols, vals)
        cur.executemany(i, rows_)
        conn.commit()
        status = OK()
        logger.info('Insertion to {} executed: {}'.format(table, i))
    except Exception as e:
        status = Error(str(e))
        logger.error('Insertion exception for {}: {}'.format(i, str(e)))

    return status

def sqlite_validate_insert(cur: Cursor,
                           table: str,
                           rows: Rows,
                           schema_cast: bool
                           ) -> Tuple[SqliteSchema, RowsPair]:
    """Validate insertion cols and optionally try casting to schema dtypes."""
    q = 'SELECT sql FROM sqlite_master WHERE type="table" and name="{}"'
    ret, status = sqlite_query(cur, q.format(table))
    if not ret or status != OK():
        msg = 'Schema validation query {} failed'.format(q)
        logging.error(msg)
        return [], ([], Error(msg))

    schema = sqlite_parse_schema(ret[0][0])

    if len(schema) != len(rows[0]):
        msg = 'Insertion validation error: {} has '.format(table)
        msg += '{} cols vs input {} cols'.format(len(schema), len(rows[0]))
        logger.error(msg)
        return [], ([], Error(msg))

    return (schema,
            sqlite_apply_schema(schema, rows) if schema_cast else (rows, OK()))

def sqlite_parse_schema(s: str) -> SqliteSchema:
    """Extract (col, type) pairs from schema string."""
    col_strs = re.findall(r'\((.*)\)', s)
    if not col_strs:
        logging.error('Schema parse failed, no cols between (): {}'.format(s))
        return []

    pairs = []
    for col in col_strs[0].split(','):
        if 'integer primary key' in col.lower(): continue
        tokens = col.strip().split(' ')
        name, dtypes = tokens[0], [t.lower() for t in tokens[1:]]
        pairs.append((name, sqlite_map_dtype(dtypes)))
    return pairs

def sqlite_map_dtype(ts: List[str]) -> type:
    """Map Sqlite data types to Python type (cast functions)."""
    return (int if 'int' in ' '.join(ts) else
            float if set(ts) & set(['real', 'float', 'double']) else
            str)

def sqlite_apply_schema(schema: SqliteSchema, rows: Rows) -> RowsPair:
    """Attempt to cast rows to primitive types in schema."""
    status : Status = OK()

    try:
        rows_ = []
        for row in rows:
            row_ = [cast(elem) for elem, (_, cast) in zip(row, schema)]
            rows_.append(row_)
    except Exception as e:
        msg = 'Insertion validation error: '
        msg += 'exception while casting {}: {}'.format(str(row), str(e))
        status = Error(msg)
        logger.error(msg)

    return rows_, status


################################################################################
# SQL String Helpers

def valid_query(q: str) -> bool:
    ws = [w.strip().lower() for w in q.split(' ')]
    return ('select' in ws and
            'from' in ws and
            'drop' not in ws and
            'delete' not in ws and
            'insert' not in ws)
