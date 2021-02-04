
# JSON Browser (jbro)

<hr>

## Introduction

jbro offers a simple command-line tool for inspecting the contents of JSON files. It is motivated by the frustration of calling `head` on a very long JSON file without any newline characters. It is especially useful for dealing with JSON files that are not formatted nicely, e.g. without reasonable spacing or newline characters.

<hr>

## Usage

```Shell
usage: jbro [-h] [-q] [-t] [-d] [-s SAMPLE] [-c CHARS] [-f FIND] [-F FIND_RECURSIVE] [-k] [-K] [-l] filename

JSON browsing utility

positional arguments:
  filename              filename of JSON file

optional arguments:
  -h, --help            show this help message and exit
  -d, --describe        describe structure of file
  -s SAMPLE, --sample SAMPLE
                        sample n (key, value) pairs from file
  -c CHARS, --chars CHARS
                        sample n chars from file
  -f FIND, --find FIND  find given key, with nesting in form key1.key2 and return its value
  -F FIND_RECURSIVE, --find_recursive FIND_RECURSIVE
                        find given (unnested) key recursively (i.e. all occurrences) and return their values
  -k, --keys            list all keys at top level
  -K, --keys_recursive  list all keys recursively in form key1.key2
  -l, --less            pipe pretty print of file to less

flags:
  -q, --quiet           suppress output description
  -t, --truncate        truncate output to < 80 chars
```

<hr>

## Notes

If no inspection parameters (-d, -s, -c, -f, -F, -k, -K) are specified, or if the less (-l) flag is specified, the JSON file will be pretty-printed for browsing in less.

The inspection functions are not mutually exclusive. For example, to describe a file and sample the first 5 keys:

```bash
$ jbro depth.json -d -s 5

> Describe structure of file
Top-level keys 2
Total keys     6
Max depth      5
Total chars    46

> Sample first 5 (key, value) pairs from file
1	{u'2': {u'3': {u'4': {u'5': 0}}}}
a	b
```

It is not envisioned for inspection functions and the less (-l) flag to be used together, but it is possible. From the user's perspective, irst the JSON will be piped to less; upon exisitng less, any output specified will be available.

The quiet (-q) flag removes additional descriptions in the output. This makes piping the output to some other function a bit nicer.

```bash
$ jbro sample.json -s 100 | less
```

The truncate (-t) flag trims the line length of all output to 80 chars. 

Find (-f) attempts to return a single value given either a key or a nested key in form key1.key2... Recursive find (-F) attempts to find all values associated with a given key at any level of nesting. Although JSON technically has no restriction against duplicate keys at the same level of nesting, it is sensible practice and jbro makes such a uniqueness assumption (by virtue of using Python dicts). Note multiple keys may occur at the same level if the value consists of a list of dicts.

```python
find1 = {'a': 1,
	     'b': 2,
	     'c': {'d': 3}}
find2 = {'a': 1,
         'b': 2,
	     'c': {'a': 3}}
```

```bash
$ jbro find1.json -f a

> Find key a in data
1

$ jbro find1.json -f c.d

> Find key c.d in data
3

$ jbro find2.json -f a

> Find key a in data
1

$ jbro find2.json -F a

> Find key a recursively in data
Level 0 1
Level 1 3
```

The key listing (-k, -K) functions are intended to be used with less, grep, etc, where it is desirable to isolate keys in files.

