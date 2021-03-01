# df_lib

Utilities for working with Pandas DataFrames.

## DataFrame Diffs

Returns a dictionary describing the difference from the first DF to the second DF.

```python
In [66]: df1
df1
Out[66]: 
     a    b    c
0    1    2    3
1    4    5    6
2  100  101  102

In [67]: df2
df2
Out[67]: 
    a   b   c
0   1   2   4
1   4   5   6
2  90  91  92

# use column 'a' as key; don't ignore any data columns
In [68]: diff_dict, status = df_lib.diff_df(df1, df2, ['a'], [])
diff_dict, status = df_lib.diff_df(df1, df2, ['a'], [])

In [69]: status
status
Out[69]: OK(msg='OK')

# key in new DF but not in old DF
In [70]: diff_dict['adds']
diff_dict['adds']
Out[70]: 
    a   b   c
2  90  91  92

# key in old DF but not in new DF
In [71]: diff_dict['retires']
diff_dict['retires']
Out[71]: 
     a    b    c
2  100  101  102

# key in both DF, some data values changed
In [72]: diff_dict['mods']
diff_dict['mods']
Out[72]: [(['1'], [('c', '3', '4')])]
```
