
# datautils

A collection of lightweight utilities for working with data. Most things here are convenince functions that wrap lower-level libraries, intended to be used as components in a larger project, or as simple command-line utilities.

- The code uses type annotations and is type checked with [`mypy`](https://mypy.readthedocs.io/en/latest/index.html) (see Build section below)
- Most modules implement logging, using Python's native [`logging`](https://docs.python.org/3/howto/logging.html) library

<hr>

## Install

Install locally with pip from the project root directory: `

```shell
pip install -r requirements.txt
pip install .
```

Not tested with Python versions < 3.9.1


## Modules

### core

- [db_lib](https://github.com/tkuriyama/datautils/blob/master/datautils/docs/db_lib.md): perform common database operations
- [dt_lib](https://github.com/tkuriyama/datautils/blob/master/datautils/docs/dt_lib.md): helper functions for datetime
- email_lib: send SMTP emails
- [log_setup](https://github.com/tkuriyama/datautils/blob/master/datautils/docs/log_setup.md): setup logging
- utils: small utility functions

### ingest
- http_lib: wrapper for the `requests` library

### json

- [jbro](https://github.com/tkuriyama/datautils/tree/master/datautils/docs/jbro.md): command-line utility for browsing JSON files


## Build

There is no build per se, since this is a pure Python project, but the `all.do` script at the root collects a number of commands that are run to validate the code (`py.test`, `pyflakes`, `mypy` etc).

The script can be run conveniently with `redo all` on the command line if [redo](https://redo.readthedocs.io/en/latest/) is installed, though the script contents can also be run individually / independently.

```
datautils % redo all
redo  all

> PyTest coverage
============================= test session starts ==============================
platform darwin -- Python 3.9.1, pytest-6.2.2, py-1.10.0, pluggy-0.13.1
rootdir: /.../datautils
plugins: cov-2.11.1
collected 11 items

datautils/test/test_db_lib.py ...                                        [ 27%]
datautils/test/test_jbro.py .......                                      [ 90%]
datautils/test/test_utils.py .                                           [100%]                                                               

---------- coverage: platform darwin, python 3.9.1-final-0 -----------
Name                          Stmts   Miss  Cover
-------------------------------------------------
datautils/core/db_lib.py        108     35    68%
datautils/core/email_lib.py      30     30     0%
datautils/core/log_setup.py      14      0   100%
datautils/core/utils.py          11      0   100%
datautils/json/jbro.py          133     68    49%
-------------------------------------------------
TOTAL                           296    133    55%


============================== 11 passed in 0.66s ==============================
                                                                                                                                              
> Running pyflakes
                                                                                                                                              
> Running mypy
Success: no issues found in 13 source files 
```
