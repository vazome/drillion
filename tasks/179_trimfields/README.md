---
title: string methods — removeprefix, removesuffix, rpartition
difficulty: medium
tier: core
minutes: 12
prereqs: [55]
tags: [string-methods, strings]
---
# string methods — removeprefix, removesuffix, rpartition

*`strip` takes a set of characters. `removeprefix` takes a string. They are not the same tool, and one of them eats your data.*

## Read first
- [str.removeprefix and str.removesuffix](https://devdocs.io/python~3.14/library/stdtypes#str.removeprefix) — take off exactly that text, or leave the string alone
- [str.lstrip](https://devdocs.io/python~3.14/library/stdtypes#str.lstrip) — read the note: the argument is a **set of characters**, not a prefix. This is the trap the task is built on.
- [str.rpartition](https://devdocs.io/python~3.14/library/stdtypes#str.rpartition) — split once, from the right, and always get three pieces back

## Why
Object-store URIs come in from a dozen tools and have to be broken into bucket, key and file name before anything else can happen. The obvious `uri.lstrip("s3://")` looks right on the first ten URIs, then quietly mangles the eleventh, because it removes *characters* rather than a *prefix*: a bucket named `s3-logs-prod` loses its leading `s3` and nobody notices until a nightly job writes to a bucket that does not exist.

## You get
`uri` — a string like `"s3://logs-prod/2026/08/api.log.gz"`. Some buckets start with the letters `s`, `3` or a dash. Not every URI ends in `.gz`, and not every key has a slash in it.

## You return
a tuple `(bucket, key, name, stem)`.

## Rules
Break the URI apart:

- `bucket` — what comes after `s3://` and before the next `/`.
- `key` — everything after that first `/`, unchanged.
- `name` — the last segment of the key, i.e. everything after the final `/`. When the key has no `/`, the name is the whole key.
- `stem` — `name` without a trailing `.gz`. When it does not end in `.gz`, `stem` is `name` unchanged.

```python
solve("s3://logs-prod/2026/08/api.log.gz")
# -> ("logs-prod", "2026/08/api.log.gz", "api.log.gz", "api.log")

solve("s3://s3-archive/dump.sql")
# -> ("s3-archive", "dump.sql", "dump.sql", "dump.sql")
```

> [!WARNING]
> The second example is the whole point. `"s3://s3-archive/dump.sql".lstrip("s3:/")` returns `"archive/dump.sql"` — the bucket's own `s3-` is gone, because `lstrip` keeps removing any of the characters `s`, `3`, `:` and `/` until it meets one that is not in that set. `removeprefix("s3://")` removes the five characters `s3://` and stops.

## Hints
### Hint 1
Four steps, one method each, in this order: take the scheme off the front, split once on the first `/`, split once on the last `/`, take `.gz` off the end.
### Hint 2
`partition("/")` splits on the FIRST slash and `rpartition("/")` on the LAST, and both always return three pieces — before, the separator, after — so they never raise on a string that has no slash. For the name, the third piece of `rpartition` is what you want, and when there was no slash it holds the whole string already.
### Hint 3
Different data, same shape:

```python
path = "logs/http/access.log.gz"
print(path.rpartition("/")[2])                 # access.log.gz
print("access.log.gz".removesuffix(".gz"))     # access.log
print("access.log".removesuffix(".gz"))        # access.log  (unchanged, no error)
```
