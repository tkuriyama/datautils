# JSON Browser
# Simple command-line utility for inspecting contents of JSON files

from subprocess import Popen, PIPE
import json

# Helpers

def test_json(filename):
    """Verify that given filename is valid JSON; if not, return None."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(e)
        data = None
    return data

def count_keys(d):
    """Count number of keys in given dict."""
    return (0 if not isinstance(d, dict) else
            len(d) + sum(count_keys(v) for v in d.values()))

def max_depth(d):
    """Return maximum depth of given dict."""
    return (0 if not isinstance(d, dict) or len(d) == 0 else
            1 + max(max_depth(v) for v in d.values()))

def trim(val, n, ellipsis='...'):
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

# Search Functions

def find_key(d, nested_key):
    """Attempt to find key in dict, where key may be nested key1.key2..."""
    keys = nested_key.split('.')
    key = keys[0]

    return (d[key] if len(keys) == 1 and key in d else
            None if len(keys) == 1 and key not in d else
            None if not isinstance(d[key], dict) else
            find_key(d[key], '.'.join(keys[1:])) if key in d else
            None)

def find_key_rec(search_d, search_key):
    """Attempt to find all search_key (BFS) in dict, return value and level."""
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

    return hits

def get_all_keys(search_d):
    """Retrieve all keys in dict (BFS) in format key1.key2..."""
    keys = []
    dicts = [('', search_d)]

    while dicts:
        parent, d = dicts.pop()
        for key in sorted(d.keys()):
            full_key = key if parent == '' else '.'.join([parent, key])
            keys.append(full_key)
            if isinstance(d[key], dict):
                dicts.append((full_key, d[key]))

    return keys

# Inspection Functions

def describe(data, quiet):
    """Describe structure of data."""
    if not quiet:
        print('\n> Describe structure of file')
    else:
        print('')

    print('Top-level keys {:,d}'.format(len(data)))
    print('Total keys     {:,d}'.format(count_keys(data)))
    print('Max depth      {:,d}'.format(max_depth(data)))
    print('Total chars    {:,d}'.format(len(json.dumps(data))))

    return True

def sample(data, n, quiet, truncate):
    """Sample first n (key, value) pairs of file."""
    if not quiet:
        print('\n> Sample first {:,d} (key, value) pairs from file'.format(n))
    else:
        print('')

    keys = sorted(data.keys())[:n]
    pairs = [join_pair(key, data[key], truncate) for key in keys]
    print('\n'.join(pairs))
    return True

def get_chars(data, n, quiet):
    """Print first n chars of file."""
    if not quiet:
        print('\n> Show first {:,d} chars of file'.format(n))
    else:
        print('')

    data_str = json.dumps(data, indent=2, sort_keys=True)
    print(data_str[:n])
    return True

def find(data, key, quiet, truncate):
    """Attempt to find key in dict, where key nesting in form key1.key2..."""
    if not quiet:
        print('\n> Find key {} in data'.format(key))
    else:
        print('')

    val = find_key(data, key)

    if val is not None:
        if truncate:
            print(trim(val, 80))
        elif isinstance(val, dict):
            print(json.dumps(val, indent=2, sort_keys=True))
        else:
            print(val)
    else:
        print('Key not found.')
    return True

def find_rec(data, key, quiet, truncate):
    """Find key recursively in data, return all occurences."""
    if not quiet:
        print('\n> Find key {} recursively in data'.format(key))
    else:
        print('')

    vals = find_key_rec(data, key)
    if vals is not []:
        found = [join_pair('Level {:,d}'.format(lvl), val, truncate)
                 for lvl, val in vals]
        print('\n'.join(found))
    else:
        print('Key not found.')
    return True

def get_keys(data, recursive, quiet, truncate):
    """List all top-level keys in data."""
    if not quiet:
        if recursive:
            print('\n> List all keys in data.')
        else:
            print('\n> List top-level keys in data.')
    else:
        print('')

    keys = get_all_keys(data) if recursive else sorted(data.keys())
    if keys is not []:
        if truncate:
            print('\n'.join([trim(key, 80) for key in keys]))
        else:
            print('\n'.join([str(key) for key in keys]))
    else:
        print('Empty file.')
    return

def less(data_str):
    """Pretty print JSON and pipe to less."""
    p = Popen('less', stdin=PIPE)
    p.stdin.write(data_str.encode())
    p.stdin.close()
    p.wait()
    return True

# Main

def main(args):
    """Process args from argparse."""
    data = test_json(args.filename)
    if not data: return False

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
        get_keys(data, False, args.quiet, args.truncate)
    if args.keys_recursive:
        get_keys(data, True, args.quiet, args.truncate)

    print('\n')

    other_args = [args.describe, args.sample, args.chars, args.find,
                  args.find_recursive, args.keys, args.keys_recursive]
    if args.less or not any(other_args):
        data_str = json.dumps(data, indent=2, sort_keys=True)
        print(data_str)
        less(data_str)

    return True
