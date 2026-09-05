---
title: os.environ.get — config with defaults
difficulty: medium
tier: core
minutes: 12
prereqs: [9]
tags: [stdlib-ops]
---
# os.environ.get — config with defaults

*Twelve-factor apps read config from the environment, so every ops script does too.*

## Read first
- [os.environ](https://devdocs.io/python~3.14/library/os#os.environ) — reading config, and `os.environ.get` for the optional case

## Why
A service runs inside a container. Operators change its port, timeout, debug mode and region by setting environment variables (named settings the operating system hands to a process at start) instead of editing files. Some settings have sensible defaults; the database address does not, and booting against a guessed database is an incident waiting to happen. You write the startup code that reads them all and converts them from text to the right types.

## You get
nothing — you build the thing from scratch. The test sets the environment variables before calling you; you read them.

## You return
a dict with the keys `"port"`, `"timeout"`, `"debug"`, `"region"` and `"database_url"`, typed as described in the rules below. If `DATABASE_URL` is not set you do not return at all: the lookup must fail with a `KeyError` that you let escape.

## Rules
Read this program's config out of the environment and return it. `solve` takes no arguments: the environment IS the input. Read `os.environ`.

| Variable | Type | Default |
| --- | --- | --- |
| `APP_PORT` | `int` | `8080` |
| `APP_TIMEOUT` | `float` | `5.0` |
| `APP_DEBUG` | `bool` | `False` |
| `APP_REGION` | `str` | `"us-east-1"` |
| `DATABASE_URL` | `str` | REQUIRED — no default |

`APP_DEBUG` is true when its value, lowercased, is in `TRUTHY` (given above); anything else is false. Every environment value arrives as a string, so `"8080"` is not `8080` and `"0"` is not `False` — convert deliberately.

Return exactly:

```python
solve()
# -> {"port": 9000, "timeout": 2.5, "debug": True,
#     "region": "eu-west-1", "database_url": "postgres://db-7/app"}
```

> [!WARNING]
> `DATABASE_URL` has no sensible default, so do not invent one. Read it with `os.environ["DATABASE_URL"]` and let the `KeyError` escape. A container that dies at startup with a named missing variable is a five-minute fix; one that boots against the wrong default database is an incident.

## Hints
### Hint 1
os.environ is a plain dict-like object of strings. Two ways to read from it, and the difference is the whole task: the method that takes a fallback never fails, square brackets fail loudly. Optional settings want the first, required settings want the second. Nothing in there is ever an int, a float or a bool — every value is a string, including "0".
### Hint 2
os.environ.get(NAME, default) returns a string, so wrap it: int(os.environ.get('APP_PORT', '8080')). For the bool there is no builtin parser — lowercase the string and test membership in TRUTHY. For the required one use os.environ['DATABASE_URL'] with no try/except.
### Hint 3
Different program, same shape:

```python
import os
cfg = {
    'host': os.environ.get('SMTP_HOST', 'localhost'),
    'port': int(os.environ.get('SMTP_PORT', '25')),
    'tls': os.environ.get('SMTP_TLS', 'no').lower() in {'1', 'true', 'yes', 'on'},
    'password': os.environ['SMTP_PASSWORD'],   # required, no default
}
```

Defaults for what you can guess, a hard failure for what you cannot.
