"""A lightweight database connection wrapper for common operations.
This module wraps `sqlite3` operations.
"""

from enum import Enum # type: ignore
import logging # type: ignore
import pandas as pd # type: ignore
from typing import List, Tuple, TypeVar, Union # type: ignore
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
QueryResult = Union[Rows, pd.DataFrame]

Conn = sqlite3.Connection
Cursor = sqlite3.Cursor


################################################################################
# QUery

RowsPair = Tuple[Rows, Status]
SqliteSchema = List[Tuple[str, type]]

def query(cur: Cursor, q: str, hdr: bool = False) -> RowsPair:
    """Execute SQL query string."""
    status: Status
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

def query_df(cur: Cursor, q: str) -> Tuple[pd.DataFrame, Status]:
    """Execute SQL query string and return result as DataFrame."""
    rows, status = query(cur, q, True)
    if status != OK() or not rows:
        logger.error('Query {} returned nvalid status or no data'.format(q))
        return pd.DataFrame(), status
    df = pd.DataFrame(rows[1:], columns=rows[0])
    return df, status


################################################################################
# Insert

def insert(conn: Conn,
           cur: Cursor,
           table: str,
           rows: Rows,
           schema_cast: bool = True
           ) -> Status:
    """Attempt to execute SQL insertion into specified table."""
    status: Status
    schema, (rows_, v) = validate_insert(cur, table, rows, schema_cast)
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

def validate_insert(cur: Cursor,
                    table: str,
                    rows: Rows,
                    schema_cast: bool
                    ) -> Tuple[SqliteSchema, RowsPair]:
    """Validate insertion cols and optionally try casting to schema dtypes."""
    q = 'SELECT sql FROM sqlite_master WHERE type="table" and name="{}"'
    ret, status = query(cur, q.format(table))
    if not ret or status != OK():
        msg = 'Schema validation query {} failed'.format(q.format(table))
        logger.error(msg)
        return [], ([], Error(msg))

    schema = parse_schema(ret[0][0])

    if len(schema) != len(rows[0]):
        msg = 'Insertion validation error: {} has '.format(table)
        msg += '{} cols vs input {} cols'.format(len(schema), len(rows[0]))
        logger.error(msg)
        return [], ([], Error(msg))

    return (schema,
            apply_schema(schema, rows) if schema_cast else (rows, OK()))

################################################################################
# Helpers

def parse_schema(s: str) -> SqliteSchema:
    """Extract (col, type) pairs from schema string. TODO: REWRITE
    Assumes form:
    CREATE TABLE(name dtype dargs... FOREIGN KEY and UNIQUE clauses);
    """
    regex=  r'(?:CREATE TABLE|CREATE TABLE IF NOT EXISTS)\s+'
    regex += r'[A-Z0-9_-]+\s*\((.*)\);?'
    spec = re.findall(regex, s.replace('\n', ' '), flags=re.IGNORECASE )
    if not spec:
        logger.error('Schema parse failed, no cols between (): {}'.format(s))
        return []

    cols = spec[0].split('FOREIGN')[0]
    pairs = []
    for col in cols.split(','):
        if ignore_column(col.lower()): continue
        tokens = col.strip().split(' ')
        if len(tokens) >= 2:
            name, dtypes = tokens[0], [t.lower() for t in tokens[1:]]
            pairs.append((name, map_dtype(dtypes)))
    return pairs

def map_dtype(ts: List[str]) -> type:
    """Map Sqlite data types to Python type (cast functions)."""
    return (int if 'int' in ' '.join(ts) else
            float if set(ts) & set(['real', 'float', 'double']) else
            str)

def apply_schema(schema: SqliteSchema, rows: Rows) -> RowsPair:
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

def ignore_column(col: str) -> bool:
    """Ignore columns that do not describe data types."""
    return ('integer primary key' in col.lower() or
            'foreign key' in col.lower() or
            'unique(' in col.lower())
