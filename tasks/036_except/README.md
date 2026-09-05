---
title: try/except — survive bad input
difficulty: easy
tier: core
minutes: 10
prereqs: [2]
tags: [errors]
---
# try/except — survive bad input

*try/except — catch the specific thing, not everything.*

## Why
A monitoring agent sends metrics as lines like "cpu=90". Now and then a line is garbage: truncated, missing the equals sign, or with a value that is not a number. A parser that crashes on the first bad line takes the whole dashboard down. The team wants a parser that keeps the good lines and quietly skips the bad ones, but only for the specific errors bad input causes, so real bugs still surface.

## You get
`rows` — a list of strings, like `["cpu=90", "junk", "mem=x", "disk=12"]`. The test creates it and hands it to you; you never build it yourself.

## You return
a dict from name to whole number for the rows that parsed, like `{"cpu": 90, "disk": 12}`.

## Rules
Each row is a string that SHOULD look like `"name=42"`.

Return `{name: number}` for every row that parses, silently skipping rows that are malformed (no `"="`, or a right-hand side that isn't a whole number).

```python
solve(["cpu=90", "junk", "mem=x", "disk=12"])  # -> {"cpu": 90, "disk": 12}
```

> [!TIP]
> Do not use a bare `except:` — catch the specific errors. Real log parsers live or die on this, and interviewers feed you dirty data on purpose.

## Hints
### Hint 1
Two different things can blow up: splitting a row with no '=' in it, and int() on something that isn't a number. Find out what each one raises.
### Hint 2
int('x') raises ValueError. Unpacking 'junk'.split('=') into two names raises ValueError too. So one except clause covers both here — but write the name, never a bare except.
### Hint 3
Different data, same shape:

```python
out = {}
for item in ['a:1', 'oops', 'b:2']:
    try:
        k, v = item.split(':')
        out[k] = int(v)
    except ValueError:
        continue          # skip it, keep going
print(out)     # {'a': 1, 'b': 2}
```
