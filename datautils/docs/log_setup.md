# log_setup

The module implements a helper for setting up module-specific logging in a consistent way.

The `core/log_setup.py` file contains a global `DEFAULTPATH`, which is set to `~/logs/` by default. All logs will be saved under the specified path (which must exist as a directory for logging to work).


## Example Usage

To setup logging in any module, only the following imports and single function call is required.

Note that diferent logging levels can be configured (per the [`logging docs`](https://docs.python.org/3/howto/logging.html)).

```python
import logging
from datautils.core import log_setup

logger = log_setup.init_file_log(__name__, logging.INFO)
```

Thereafter, the normal `logger` functions are avaiable for use (see the [`logging docs`](https://docs.python.org/3/howto/logging.html)), e.g.:

```python
logger.info('Database connected')
logger.error('Failed to connect')
```

## Example Output

```shell
datautils % tail -5 ~/logs/datautils.core.db_lib.log
2021-02-04 21:45:53,141 - INFO - Query executed: SELECT * FROM SelectTest
2021-02-04 21:45:53,142 - INFO - Connected to Sqlite DB: /private/var/folders/6l/s98yj7157bqc5gzrdr_35kk80000gn/T/pytest-of-tarokuriyama/pytest-58/test_query0/test.db
2021-02-04 21:45:53,143 - INFO - Query executed: SELECT * FROM SelectTest
2021-02-04 21:45:53,144 - INFO - Closed DB conn.
2021-02-04 21:45:53,146 - INFO - Closed DB conn.
```
