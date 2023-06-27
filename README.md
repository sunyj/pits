# pits – Point-In-Time Storage

**pits** provides Pythonic context-managed file object abstraction for point-in-time file storage.  pits supports plain or gzipped files.

**pits** is [listed on PyPI](https://pypi.org/project/pits/).


## Writing

```python
my_data = grab_my_data(...)

# write to plain file
with open('my-data.txt', 'w+') as f:
    f.write(my_data)

# write to gzip file
import gzip
with gzip.open('my-data.gz', 'wb') as f:
    f.write(my_data)

# write to point-in-time file
import pits
with pits.open('my-data', 'wb', gzip=True) as f:
    f.write(my_data)

# write as if we're at another point in time
with pits.goto('20220101-1200').open('my-data', 'wb', gzip=True) as f:
    f.write(my_data)
```


## Reading

```python
import pits

# read latest file
with pits.open('my-data') as f:
    f.write(my_data)

# read latest file as if we're at another point in time
with pits.goto('2022-12-18 15:00').open('my-data') as f:
    f.write(my_data)
```


## Datetime format

- Timestamp format for file name is `%Y.%m.%d-%H:%M:%S`.
- All non-numeric characters are omitted in timestamp parsing, e.g., `2022-12-18 15:00` is transformed to `202212181500` before parsing.
- All timestamps are local.
- `20221218` is recognized as `2022-12-18 23:59:59`, but `20221218-1500` is recognized as `2022-12-18 15:00:00`.
