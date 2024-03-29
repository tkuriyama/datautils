"""Internal module wrapping `sqlite3` operations for core/db_lib
For simplicity, only a subset of the sqlite specification is implemented.
"""

from enum import Enum  # type: ignore
import logging  # type: ignore
import pandas as pd  # type: ignore
from typing import List, Tuple, TypedDict, TypeVar  # type: ignore
import re  # type: ignore
import sqlite3  # type: ignore

from datautils.core import log_setup  # type: ignore
from datautils.core.utils import Error, OK, Status  # type: ignore


##########################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.INFO)


##########################################################################

T = TypeVar('T')
Rows = List[List[T]]

Conn = sqlite3.Connection
Cursor = sqlite3.Cursor


##########################################################################
# Create

Col = str
Name = str
Is_PK = bool
Is_Uniq = bool
Is_Not_Null = bool


class DType(Enum):
    INTEGER = 0
    REAL = 1
    TEXT = 2
    BOOLEAN = 3
    BLOB = 4


SchemaCol = Tuple[Name, DType, Is_PK, Is_Uniq, Is_Not_Null]


class SchemaForeignKey(TypedDict):
    cols: List[Col]
    ref_table: str
    ref_cols: List[Col]


class TableDef(TypedDict):
    if_not_exists: bool
    name: Name
    cols: List[SchemaCol]
    fks: List[SchemaForeignKey]
    pk: List[Col]
    uniq: List[Col]


def create(cur: Cursor, stmt: str) -> Status:
    """Create table."""
    status: Status
    try:
        cur.execute(stmt)
        status = OK()
        logger.info(f'Create statement executed: {stmt}')
    except Exception as e:
        logger.error(f'Create statement exception: {stmt}; {e}')
        status = Error(str(e))
    return status


def gen_create_stmt(td: TableDef) -> Tuple[str, Status]:
    """Translate TableDef into Create Table statement."""
    status: Status
    create, s1 = gen_create(td['if_not_exists'], td['name'])
    cols, s2 = gen_cols(td['cols'])
    fks, s3 = gen_fks(td['fks'])
    pk_uniq, s4 = gen_pk_uniq(td['pk'], td['uniq'])

    if all(s == OK() for s in (s1, s2, s3, s4)):
        spec = strip_comma(f'{cols}{fks}{pk_uniq}')
        stmt = f'{create}({spec});'
        status = OK()
    else:
        stmt = ''
        msg = ' | '.join(s.msg for s in (s1, s2, s3, s4) if s != OK())
        status = Error(msg)

    return stmt, status


def gen_create(if_not_exists: bool, name: str) -> Tuple[str, Status]:
    """Generate Create substring."""
    s = (f'CREATE TABLE {name}' if if_not_exists is False else
         f'CREATE TABLE IF NOT EXISTS {name}')
    return s, OK()


def gen_cols(cols: List[SchemaCol]) -> Tuple[str, Status]:
    """Generate columns substring."""
    status: Status
    if not cols:
        return '', OK()

    s, status = '', OK()
    for col in cols:
        name, dtype, pk, uniq, not_null = col
        if pk and uniq:
            s, status = '', Error(f'Col {name} specified as both PK and Uniq')
            break
        dtype_ = dtype_to_str(dtype)
        s += f'{name} {dtype_}'
        s += ' PRIMARY KEY' if pk else ' UNIQUE' if uniq else ''
        s += ' NOT NULL,\n' if not_null else ',\n'

    return s, status


def gen_fks(fks: List[SchemaForeignKey]) -> Tuple[str, Status]:
    """Generate Foreign Keys substring."""
    status: Status
    s, status = '', OK()
    for fk in fks:
        fk_cols, fk_ref_cols = fk['cols'], fk['ref_cols']
        if len(fk_cols) != len(fk_ref_cols):
            s, status = '', Error(
                f'Length mismatch {fk_cols} vs {fk_ref_cols}')
            break

        cols, ref_cols = ', '.join(fk_cols), ', '.join(fk_ref_cols)
        ref_table = fk['ref_table']
        s += f'FOREIGN KEY({cols}) REFERENCES {ref_table}({ref_cols}),\n'

    return f'{s}', status


def gen_pk_uniq(pk: List[Col], uniq: List[Col]) -> Tuple[str, Status]:
    """Generate Primary Key or Unique substring."""
    s_pk = '' if not pk else 'PRIMARY KEY({})'.format(', '.join(pk))
    s_uniq = '' if not uniq else 'UNIQUE({})'.format(', '.join(uniq))
    s = ('' if not s_pk and not s_uniq else
         f'{s_pk}\n' if s_pk and not s_uniq else
         f'{s_uniq}\n' if s_uniq and not s_pk else
         f'{s_pk},\n{s_uniq}\n')
    return s, OK()


def dtype_to_str(dt: DType) -> str:
    """Map DType to string."""
    return ('INTEGER' if dt == DType.INTEGER else
            'REAL' if dt == DType.REAL else
            'TEXT' if dt == DType.TEXT else
            'BOOLEAN' if dt == DType.BOOLEAN else
            'BLOB')


def strip_comma(s: str) -> str:
    """Strip trailing comma."""
    return (s[:-1] if s and s[-1] == ',' else
            s[:-2] + '\n' if s and s[-2:] == ',\n' else
            s)


##########################################################################
# Query

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
        logger.info(f'Query executed: {q}')
    except Exception as e:
        logger.error(f'Query exception: {q}; {e}')
        rows, status = [], Error(str(e))
    return rows, status


def query_df(cur: Cursor, q: str) -> Tuple[pd.DataFrame, Status]:
    """Execute SQL query string and return result as DataFrame."""
    rows, status = query(cur, q, True)
    if status != OK() or not rows:
        logger.error(f'Query {q} returned nvalid status or no data')
        return pd.DataFrame(), status
    df = pd.DataFrame(rows[1:], columns=rows[0])
    return df, status


##########################################################################
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
    if v != OK():
        return v

    try:
        cols = ','.join(name for name, _ in schema)
        vals = ','.join('?' * len(schema))
        i = f'INSERT INTO {table}({cols}) VALUES ({vals})'
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
    q = f'SELECT sql FROM sqlite_master WHERE type="table" and name="{table}"'
    ret, status = query(cur, q)
    if not ret or status != OK():
        msg = f'Schema validation query {q} failed'
        logger.error(msg)
        return [], ([], Error(msg))

    schema = parse_schema(ret[0][0])

    if len(schema) != len(rows[0]):
        msg = f'Insertion validation error: {table} has '
        msg += f'{len(schema)} cols vs input {len(rows[0])} cols'
        logger.error(msg)
        return [], ([], Error(msg))

    return (schema,
            apply_schema(schema, rows) if schema_cast else (rows, OK()))


##########################################################################
# Helpers

def parse_schema(s: str) -> SqliteSchema:
    """Extract (col, type) pairs from schema string. TODO: REWRITE
    Assumes form:
    CREATE TABLE (name dtype dargs... FOREIGN KEY and UNIQUE clauses);
    CREATE TABLE IF NOT EXISTS is also valid
    """
    regex = r'(?:CREATE TABLE|CREATE TABLE IF NOT EXISTS)\s+'
    regex += r'["A-Z0-9_.-]+\s*\((.*)\);?'
    spec = re.findall(regex, s.replace('\n', ' '), flags=re.IGNORECASE)
    if not spec:
        logger.error(f'Schema parse failed, no cols between (): {s}')
        return []

    cols = spec[0].split('FOREIGN')[0]
    pairs = []
    for col in cols.split(','):
        if ignore_column(col.lower()):
            continue
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
    status: Status = OK()

    try:
        rows_ = []
        for row in rows:
            row_ = [cast(elem) for elem, (_, cast) in zip(row, schema)]
            rows_.append(row_)
    except Exception as e:
        msg = f'Insertion validation error: exception while casting {row}: {e}'
        status = Error(msg)
        logger.error(msg)

    return rows_, status


def ignore_column(col: str) -> bool:
    """Ignore columns that do not describe data types."""
    return ('integer primary key' in col.lower() or
            'foreign key' in col.lower() or
            'unique(' in col.lower())
