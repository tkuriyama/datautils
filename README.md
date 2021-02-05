
# datautils

A collection of lightweight utilities for working with data. Most things here are convenince functions that wrap lower-level libraries, intended to be used as components in a larger project, or as simple command-line utilities.

The code uses type annotations and is type checked with [`mypy`](https://mypy.readthedocs.io/en/latest/index.html) (see Build section below).

<hr>

## Install

Install locally with pip from the project root directory: `pip install -e .`

Not tested with Python versions < 3.9.1


## Components

### core

- [db_lib](https://github.com/tkuriyama/datautils/blob/master/datautils/docs/db_lib.md): perform common database operations
- email_lib: send SMTP emails

### ingest


### json

- [jbro](https://github.com/tkuriyama/datautils/tree/master/datautils/docs/jbro.md): command-line utility for browsing JSON files


## Build

There is no build per se, since this is a pure Python project, but the `all.do` script at the root collects a number of commands that are run to validate the code (`py.test`, `pyflakes`, `mypy` etc).

The script can be run conveniently with `redo all` on the command line if [redo](https://redo.readthedocs.io/en/latest/) is installed, though the script contents can also be run individually / independently.
