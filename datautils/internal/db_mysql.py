"""Internal module wrapping `mysql` operations for core/db_lib
For simplicity, only a subset of the MySQL specification is implemented.
"""

from dataclasses import dataclass  # type: ignore
from enum import Enum  # type: ignore
import logging  # type: ignore
import pandas as pd  # type: ignore
from typing import Any, List, Tuple, TypedDict, TypeVar  # type: ignore
# import pymysql  # type: ignore

from datautils.core import log_setup  # type: ignore
from datautils.core.utils import Error, OK, Status  # type: ignore


##########################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.INFO)


##########################################################################


T = TypeVar('T')
Rows = List[List[T]]

Conn = Any  # : TypeAlias = pymysql.connections.Connection
Cursor = Any  # : TypeAlias = pymysql.cursors.Cursor


##########################################################################
# Create


Col = str
Name = str
Is_PK = bool
Is_Uniq = bool
Is_Not_Null = bool


class DType(Enum):
    INTEGER = 0
    BIGINT = 1
    FLOAT = 2
    DOUBLE = 3
    BOOLEAN = 4
    VARCHAR = 5
    DATE = 6
    DATETIME = 7


@dataclass
class DTypeSpec:
    dtype: DType
    varchar_size: int = 0

    def to_str(self) -> str:
        return ('INTEGER' if self.dtype == DType.INTEGER else
                'BIGINT' if self.dtype == DType.BIGINT else
                'FLOAT' if self.dtype == DType.FLOAT else
                'DOUBLE' if self.dtype == DType.DOUBLE else
                'BOOLEAN' if self.dtype == DType.BOOLEAN else
                'DATE' if self.dtype == DType.DATE else
                'DATETIME' if self.dtype == DType.DATETIME else
                f'VARCHAR({self.varchar_size})')


SchemaCol = Tuple[Name, DTypeSpec, Is_PK, Is_Uniq, Is_Not_Null]


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
        name, dtype_spec, pk, uniq, not_null = col
        if pk and uniq:
            s, status = '', Error(f'Col {name} specified as both PK and Uniq')
            break
        dtype_ = dtype_spec.to_str()
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
    s_pk = '' if not pk else 'PRIMARY KEY ({})'.format(', '.join(pk))
    s_uniq = '' if not uniq else 'UNIQUE ({})'.format(', '.join(uniq))
    s = ('' if not s_pk and not s_uniq else
         f'{s_pk}\n' if s_pk and not s_uniq else
         f'{s_uniq}\n' if s_uniq and not s_pk else
         f'{s_pk},\n{s_uniq}\n')
    return s, OK()


def strip_comma(s: str) -> str:
    """Strip trailing comma."""
    return (s[:-1] if s and s[-1] == ',' else
            s[:-2] + '\n' if s and s[-2:] == ',\n' else
            s)


##########################################################################
# Query


RowsPair = Tuple[Rows, Status]


def query(cur: Cursor, q: str, hdr: bool = False) -> RowsPair:
    """Execute SQL query string."""
    status: Status
    try:
        cur.execute(q)
        if hdr:
            cols = [d[0] for d in cur.description]
            rows = [cols] + [list(row) for row in cur.fetchall()]
        else:
            rows = [list(row) for row in cur.fetchall()]
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
# Insert

def insert(conn: Conn,
           cur: Cursor,
           table: str,
           cols: List[str],
           rows: Rows,
           verify_length: bool = True
           ) -> Status:
    """Attempt to execute SQL insertion into specified table."""
    status: Status
    length_status = valid_lengths(cur, table, cols, rows)
    if length_status != OK():
        return length_status

    try:
        cols_ = ', '.join(cols)
        maybe_cols = f' ({cols_})' if cols else ''
        vals = ', '.join(['%s'] * len(rows[0]))
        i = f'INSERT INTO {table}{maybe_cols} VALUES ({vals})'
        affected = cur.executemany(i, rows)
        if rows and affected > 0:
            conn.commit()
            status = OK()
            logger.debug(f'Insertion to {table} executed: {i}')
        else:
            err_msg = f'Insertion {i} affected 0 rows with {len(rows)} of data'
            status = Error(err_msg)
            logger.error(err_msg)
    except Exception as e:
        status = Error(str(e))
        logger.error(f'Insertion exception for {i}: {e}')

    return status


def valid_lengths(cur: Cursor,
                  table: str,
                  cols: List[str],
                  rows: Rows
                  ) -> Status:
    """Verify all lengths are uniform and match table.
    This validation disallows insertions withou all columns specified
    (i.e. no defaults!).
    """
    status: Status

    db_rows, q_status = query(cur, f'SELECT * FROM {table} LIMIT 1', True)
    if q_status != OK():
        return q_status

    conditions = [len(db_rows[0]) == len(cols) if cols else True,
                  all(len(db_rows[0]) == len(row) for row in rows)]

    return (OK() if all(conditions) is True else
            Error(f'Length mismatch occured in insertioo to {table}'))
