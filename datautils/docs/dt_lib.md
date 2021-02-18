# dt_lib

Utilities for working with datetimes.

## Dates

Get date deltas and date ranges, with weekends and holidays as optional arguments.

```python
In [5]: from datautils.core import dt_lib

In [6]: import datetime as dt

In [7]: today = dt.date.today()

In [8]: today
Out[8]: datetime.date(2021, 2, 11)

# biz_date ignores weekends
In [9]: dt_lib.get_biz_date(today, -1)
Out[9]: datetime.date(2021, 2, 10)

# pass in holidays as argument
In [10]: holidays = [dt.date(2021,2,10), dt.date(2021,2,9)]

In [11]: dt_lib.get_biz_date(today, -1, holidays)
Out[11]: datetime.date(2021, 2, 8)

# get list of dates in delta range instead, with or without weekends
In [12]: dt_lib.get_dates(today, -5, False)
Out[12]: 
[datetime.date(2021, 2, 6),
 datetime.date(2021, 2, 7),
 datetime.date(2021, 2, 8),
 datetime.date(2021, 2, 9),
 datetime.date(2021, 2, 10),
 datetime.date(2021, 2, 11)]

In [13]: dt_lib.get_dates(today, -5, True)
Out[13]: 
[datetime.date(2021, 2, 4),
 datetime.date(2021, 2, 5),
 datetime.date(2021, 2, 8),
 datetime.date(2021, 2, 9),
 datetime.date(2021, 2, 10),
 datetime.date(2021, 2, 11)]
```

Parse date strings where the month is a name, returning an `Optional[date]` (either a `datetime.date` or `None`):

```
In [3]: dt_lib.parse_date_name('21 Feb, 2021')
Out[3]: datetime.date(2021, 2, 21)

# invalid month name
In [4]: dt_lib.parse_date_name('21 Fib, 2021')

In [5]: dt_lib.parse_date_name('1/Mar/1999')
Out[5]: datetime.date(1999, 3, 1)

# invalid year
In [6]: dt_lib.parse_date_name('1/Mar/0')

```
