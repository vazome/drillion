---
title: custom exceptions — a ConfigError family
difficulty: medium
tier: core
minutes: 15
prereqs: [21, 36]
tags: [errors]
---
# custom exceptions — a ConfigError family

*Custom exceptions let callers catch a whole family of errors with one except.*

## Read first
- [User-defined Exceptions](https://devdocs.io/python~3.14/tutorial/errors#user-defined-exceptions) — subclass `Exception`, carry the context the caller needs

## Why
A deploy tool reads a list of service configs and applies the good ones. Bad configs must be skipped, but the report has to say exactly what was wrong with each: a missing field, or a field holding a nonsense value. Real tools solve this with a family of related error types: the checks raise the specific one, and the loop catches the whole family with a single handler. Interviewers ask for exactly this design.

## You get
`configs` — a list of dicts, like `[{"name": "web", "replicas": 3}, {"name": "db"}]`. The test creates it and hands it to you; you never build it yourself. The error classes `ConfigError`, `MissingKeyError` and `BadValueError` are already defined above.

## You return
a pair `(applied, rejected)`: `applied` is a list of the names of good configs; `rejected` is a list of (position, error class name) pairs.

## Rules
Validate a list of service configs. Each config should be a dict with a `"name"` (string) and `"replicas"` (an int, 0 or more).

For each config, in order:

- if `"name"` is missing, that is a `MissingKeyError`
- else if `"replicas"` is missing, that is a `MissingKeyError`
- else if replicas is not an int, or is negative, that is a `BadValueError`
- otherwise the config is good

Structure it the way real tools do: write the checks so they RAISE the specific exception, then wrap each config in `try/except ConfigError` — the base class catches both subtypes. Record `type(err).__name__` for rejects.

Return a pair `(applied, rejected)`:

- `applied` — list of names of good configs, in input order
- `rejected` — list of (index, exception class name) tuples, in input order

```python
solve([{"name": "web", "replicas": 3}, {"name": "db"}, {"name": "gw", "replicas": -1}])
# -> (["web"], [(1, "MissingKeyError"), (2, "BadValueError")])
```

Why a hierarchy: the loop only needs "this config is bad, skip it", so it catches `ConfigError`. The message still says exactly what was wrong. That is the whole pitch for custom exception classes in an interview.

## Hints
### Hint 1
Raise the most specific class you can; catch the most general one the caller can handle. Here the checks raise MissingKeyError or BadValueError, and the loop catches ConfigError — one except clause covers both, and plain bugs like TypeError still crash loudly, which you want.
### Hint 2
Inside a for-loop over enumerate(configs): a try block that checks 'name' then 'replicas' with `in`, raising MissingKeyError(key), then checks isinstance(value, int) and value >= 0, raising BadValueError. In `except ConfigError as err`, append (i, type(err).__name__).
### Hint 3
Different data, same shape:

```python
class ParseError(Exception): pass
class EmptyLine(ParseError): pass

def read(line):
    if not line:
        raise EmptyLine('blank')
    return line.upper()

for line in ['hi', '']:
    try:
        print(read(line))
    except ParseError as err:
        print('skipped:', type(err).__name__)
# HI
# skipped: EmptyLine
```

The raiser names the exact problem; the catcher only knows the family.
