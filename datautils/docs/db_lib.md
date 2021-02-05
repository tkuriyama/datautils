# db_lib

A lightweight database connection wrapper for common operations.

Currently supported databases:
- sqlite (`sqlite3` library)

A `DB` object can be initialized to hold connection state and execute database operations. Alterantively, there are single-use functions like `query_once` for simpler use cases.

## Eaxmple Usage

```python
In [1]: from datautils.core import db_lib

In [2]: db = db_lib.DB('test.db')

# standard query
In [3]: db.query('SELECT * FROM SelectTest')
Out[3]: ([('HelloWorld', 7, 3.14)], OK(msg='OK'))

# query strings are validated
In [4]: db.query('DELETE * FROM SelectText')
Out[4]: ([], Error(msg='Invalid query DELETE * FROM SelectText'))

# extract just the query result
In [5]: ret, _ = db.query('SELECT * FROM SelectTest')

In [6]: ret
Out[6]: [('HelloWorld', 7, 3.14)]

# include header in result
In [7]: df, _ = db.query('SELECT * FROM SelectTest', True)

In [8]: df
Out[8]: [['TextCol', 'IntCol', 'FloatCol'], ('HelloWorld', 7, 3.14)]

# return result as pandas DataFrame
In [9]: df, _ = db.query('SELECT * FROM SelectTest', True, True)

In [10]: df
Out[10]: 
      TextCol  IntCol  FloatCol
0  HelloWorld       7      3.14

In [11]: db.close()
Out[11]: OK(msg='OK')

# open connection, execute query, and close connection
In [12]: db_lib.query_once('test.db', 'SELECT * FROM SelectTest')
Out[12]: [('HelloWorld', 7, 3.14)]
```
