---
title: __missing__ — a settings dict that forgives the spelling, once
difficulty: medium
tier: advanced
minutes: 20
prereqs: [57]
tags: [dicts, class-customization]
source: fluentpython/example-code-2e 03-dict-set (MIT, adapted)
---
# __missing__ — a settings dict that forgives the spelling, once

*`__missing__` is the hook `dict` calls only when a key is genuinely not there, so a hit costs nothing and a miss gets a second chance.*

## Read first
- [`dict.__missing__`](https://devdocs.io/python~3.14/library/stdtypes#dict.__missing__) — who calls it, and who does not
- [`dict.get`](https://devdocs.io/python~3.14/library/stdtypes#dict.get) — and why it is not written in terms of `d[key]`
- [`dict.keys`](https://devdocs.io/python~3.14/library/stdtypes#dict.keys) — a view, and what `in` does to one

## Why
The service reads its settings from two places. The YAML file writes them the way people write YAML, `log_level`, and the process environment writes them the way environments do, `LOG_LEVEL`. Merged into one dict you get both spellings, and every caller has to guess which one landed there today.

The fix people reach for first is to normalise everything on the way in, which loses the distinction and quietly overwrites one source with the other. The fix that keeps working is to normalise on the way *out*, and only when the exact key was not found: what the file said is still what the file said, and a caller who spells it the other way still gets an answer instead of a stack trace at 3am.

## You get
nothing to start — you return a class. The test builds it itself, like

```python
Env = solve()
settings = Env({"DB_HOST": "db.internal", "log_level": "debug"})
```

## You return
the class `Env`.

## Rules
`Env` subclasses `dict` and changes nothing about how keys go in. Three methods:

- `__missing__(self, key)` — Python calls this when `settings[key]` found nothing. If `key` is not a string, or is a string that is already upper-case, that is a real miss: raise `KeyError(key)`. Otherwise look the key up again upper-cased, and let *that* lookup succeed or fail on its own.
- `get(self, key, default=None)` — return the value if the lookup works, and `default` if it raises `KeyError`.
- `__contains__(self, key)` — `True` when the key is stored, or when its upper-cased form is.

An exact match always wins. `settings["log_level"]` is a hit and never reaches `__missing__`.

```python
Env = solve()
settings = Env({"DB_HOST": "db.internal", "log_level": "debug"})

settings["DB_HOST"]      # -> 'db.internal'   exact
settings["db_host"]      # -> 'db.internal'   second chance
settings["log_level"]    # -> 'debug'         exact, and it stays exact
settings["LOG_LEVEL"]    # -> KeyError: 'LOG_LEVEL'
settings.get("db_host")  # -> 'db.internal'
settings.get("nope", "") # -> ''
"db_host" in settings    # -> True
```

> [!WARNING]
> Normalising inside `__getitem__` instead looks equivalent and is not. It runs on hits too, so `settings["log_level"]` becomes a lookup for `LOG_LEVEL`, which is not there, and the key the file actually set stops being reachable by the name the file used. `__missing__` runs only after the hit failed, which is what keeps the exact match exact.

> [!NOTE]
> `dict.get` and `in` do not go through `__missing__` — that is why you are writing both of them. Inside `__contains__`, ask `key in self.keys()`: `key in self` would call `__contains__` again, forever.

## Hints
### Hint 1
`__missing__` is only ever called by `dict.__getitem__`, and only after the real lookup failed. So the whole method is: decide whether this is hopeless, and if it is not, try `self[key.upper()]` — an ordinary lookup, which will call `__missing__` again if that one misses too. The upper-case guard is what stops that being forever.
### Hint 2
`get` is a four-line `try`/`except KeyError`. Writing `return self.get(key, default)` inside it, or forgetting it entirely, gives you a dict where `settings["db_host"]` works and `settings.get("db_host")` is `None`.
### Hint 3
Same shape, different rule:

```python
class TrimKeyDict(dict):
    def __missing__(self, key):
        if not isinstance(key, str) or key == key.strip():
            raise KeyError(key)
        return self[key.strip()]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        return key in self.keys() or (isinstance(key, str) and key.strip() in self.keys())

d = TrimKeyDict({"host": "a"})
d["  host "]   # -> 'a'
d["host"]      # -> 'a', and it never went near __missing__
d["missing"]   # -> KeyError: 'missing'
```

The guard is the same one twice: a key already in its normal form has had its chance.

---
Adapted from fluentpython/example-code-2e — MIT
