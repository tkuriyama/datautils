""" JSON Browser
Simple command-line utility for inspecting contents of JSON files
"""

import json # type: ignore
import logging # type: ignore
from subprocess import Popen, PIPE # type: ignore
from typing import List, Optional # type: ignore

from datautils.core import log_setup # type: ignore
from datautils.core import utils # type: ignore

################################################################################
# Initialize Logging -- set logging level to > 50 to suppress all output

logger = log_setup.init_file_log(__name__, logging.WARNING)

################################################################################

def main(args):
    """Process args from argparse."""
    data = test_json(args.filename)
    if not data: return

    if args.describe:
        describe(data, args.quiet)
    if args.sample:
        sample(data, args.sample, args.quiet, args.truncate)
    if args.chars:
        get_chars(data, args.chars, args.quiet)
    if args.find:
        find(data, args.find, args.quiet, args.truncate)
    if args.find_recursive:
        find_rec(data, args.find_recursive, args.quiet, args.truncate)
    if args.keys:
        get_keys(data, args.quiet, args.truncate)
    if args.keys_recursive:
        get_all_keys(data, args.quiet, args.truncate)

    print('\n')

    other_args = [args.describe, args.sample, args.chars, args.find,
                  args.find_recursive, args.keys, args.keys_recursive]
    if args.less or not any(other_args):
        data_str = json.dumps(data, indent=2, sort_keys=True)
        print(data_str)
        less(data_str)

################################################################################
# Inspection Functions

def describe(data: dict, quiet: bool) -> None:
    """Describe key attributes of data."""
    print('\n> Describe structure of file' if not quiet else '\n')

    print('Top-level keys {:,d}'.format(len(data)))
    print('Total keys     {:,d}'.format(count_keys(data)))
    print('Max depth      {:,d}'.format(max_depth(data)))
    print('Total chars    {:,d}'.format(len(json.dumps(data))))

def sample(data: dict, n: int, quiet: bool, truncate: bool) -> None:
    """Sample first n (key, value) pairs."""
    msg = '\n> Sample first {:,d} (key, value) pairs'.format(n)

    print(msg if not quiet else '\n')
    keys = list(data)[:n]
    pairs = [join_pair(key, data[key], truncate) for key in keys]
    print('\n'.join(pairs))

def get_chars(data: dict, n: int, quiet: bool) -> None:
    """Print first n chars."""
    print('\n> Show first {:,d} chars'.format(n) if not quiet else '\n')
    data_str = json.dumps(data, indent=2, sort_keys=True)
    print(data_str[:n])

def get_keys(data: dict, quiet: bool, truncate: bool) -> None:
    """List all top-level keys in data."""
    print('\n> List all top-level keys' if not quiet else '\n')

    print_freq_keys(list(data), truncate)

def get_all_keys(search_d: dict, quiet: bool, truncate: bool) -> None:
    """Retrieve all keys in dict (BFS) in format key1.key2..."""
    print('\n> List all keys' if not quiet else '\n')

    all_keys = []
    dicts = [('', search_d)]

    while dicts:
        parent, d = dicts.pop()
        for key in d.keys():
            full_key = key if parent == '' else '.'.join([parent, key])
            all_keys.append(full_key)
            if isinstance(d[key], dict):
                dicts.append((full_key, d[key]))
            elif isinstance(d[key], list):
                dicts.extend((full_key, d_) for d_ in d[key]
                             if isinstance(d_, dict))

    print_freq_keys(all_keys, truncate)

################################################################################
# Search Functions

def find(data: dict, key: str, quiet: bool, truncate: bool) -> None:
    """Attempt to find key in dict, where nested key in form key1.key2..."""
    print('\n> Find key {}'.format(key) if not quiet else '\n')

    val = _find_key(data, key.split('.'))
    if val is not None:
        if truncate:
            print(trim(val, 80))
        elif isinstance(val, dict) or isinstance(val, list):
            print(json.dumps(val, indent=2, sort_keys=True))
        else:
            print(val)
    else:
        print('Key not found.')

def _find_key(d: dict, keys: List[str]):
    """Implementation of find().
    Attempt to find the nested key key1.key2... and return its value.
    May return multiple values if the leaf key occurs in a list.
    """
    key = keys[0]

    return (d[key] if len(keys) == 1 and key in d else
            None if len(keys) == 1 and key not in d else
            _find_key_list(d[key], keys[1:]) if isinstance(d[key], list) else
            None if not isinstance(d[key], dict) else
            _find_key(d[key], keys[1:]) if key in d else
            None)

def _find_key_list(lst: list, keys: List[str]) -> list:
    """Map _find_key over list elems that are dicts."""
    return [_find_key(elem, keys) for elem in lst if isinstance(elem, dict)]

def find_rec(data: dict, key: str, quiet: bool, truncate: bool) -> None:
    """Find (unnested ) key recursively in data, return all occurences."""
    print('\n> Find key {} recursively'.format(key) if not quiet else '\n')

    vals = _find_key_rec(data, key)
    if vals:
        found = [join_pair('Level {:,d}'.format(lvl), val, truncate)
                 for lvl, val in vals]
        print('\n'.join(found))
    else:
        print('Key not found.')

def _find_key_rec(search_d: dict, search_key: str):
    """Implementation of find_rec().
    Attempt to find all instnaces of the unnested search_key (BFS) in dict.
    Return all found values and corresponding levels of nesting.
    """
    hits = []
    dicts = [(0, search_d)]

    while dicts:
        level, d = dicts.pop()
        for key in d:
            if key == search_key:
                hits.append((level, d[key]))
            else:
                if isinstance(d[key], dict):
                    dicts.append((level + 1, d[key]))
                elif isinstance(d[key], list):
                    dicts.extend((level + 1, d_) for d_ in d[key]
                                 if isinstance(d_, dict))

    return hits

################################################################################
# Helpers

def test_json(fname: str) -> Optional[dict]:
    """Return either JSON or None (if JSON parse fails)."""
    data: Optional[dict]
    try:
        with open(fname, 'r') as f:
            data = json.load(f)
    except Exception as e:
        msg = 'JSON parse failed for {}: {}'.format(fname, str(e))
        print(msg)
        logger.debug(msg)
        data = None
    return data

def count_keys(d: dict) -> int:
    """Count number of keys in given dict."""
    return (0 if not isinstance(d, dict) else
            len(d) + sum(count_keys(v) for v in d.values()))

def max_depth(d: dict) -> int:
    """Return maximum depth of given dict."""
    return (0 if not isinstance(d, dict) or len(d) == 0 else
            1 + max(max_depth(v) for v in d.values()))

def trim(val, n: int, ellipsis: str='...') -> str:
    """Trim value to max of n chars."""
    val_str = str(val)
    trim_len = max(n - len(ellipsis), 0)
    return (val_str[:trim_len] + ellipsis if len(val_str) > n else
            val_str)

def join_pair(v1, v2, truncate, sep='\t', left=20, max_len=80):
    """Format (v1, v2) pair as single string appropriate for printing.
    Args
        v1: obj passable to str(), first value
        v2: obj passable to str(), second value
        truncate: bool, trim total length based on left and max_len if true
        sep: str, separator between pair
        left: int, maximum length of left side of pair (v1)
        max_len: int, maximum length of string
    Returns
        String of joined pair.
    """
    right = max_len - min(left, len(v1)) - len(sep)
    return (sep.join([trim(v1, left), trim(v2, right)]) if truncate else
            sep.join([str(v1), str(v2)]))

def print_freq_keys(keys: List[str], truncate: bool) -> None:
    """Print keys with frequency counts."""
    if keys:
        keys_ = [trim(key, 70) if truncate else str(key) for key in keys]
        freq_list = utils.count_freq_list(keys_)
        print('\n'.join(': '.join([str(elem), str(freq)]) for elem, freq in
                        sorted(freq_list, key=lambda x: x[0])))
    else:
        print('Empty input.')

def less(data):
    """Pretty print JSON and pipe to less."""
    p = Popen('less', stdin=PIPE)
    p.stdin.write(data.encode())
    p.stdin.close()
    p.wait()

