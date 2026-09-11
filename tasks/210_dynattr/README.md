---
title: __getattr__ — a config you read with dots instead of brackets
difficulty: hard
tier: advanced
minutes: 28
prereqs: [57]
tags: [class-customization, dicts]
source: fluentpython/example-code-2e 22-dyn-attr-prop (MIT, adapted)
---
# __getattr__ — a config you read with dots instead of brackets

*`__getattr__` is Python's last resort when an attribute is not found, and `__setattr__` is the guard that stops a stray assignment from making that last resort unreachable.*

## Read first
- [`__getattr__`](https://devdocs.io/python~3.14/reference/datamodel#object.__getattr__) — called only after the normal lookup has already failed
- [`__setattr__`](https://devdocs.io/python~3.14/reference/datamodel#object.__setattr__) — called for *every* assignment, including the ones in `__init__`
- [`object.__setattr__`](https://devdocs.io/python~3.14/reference/datamodel#object.__setattr__) — the base implementation, and the way out of the recursion
- [`collections.abc.Mapping`](https://devdocs.io/python~3.14/library/collections.abc#collections.abc.Mapping) — the test for "is this thing dict-shaped"

## Why
A deployment reads its settings out of a nested JSON blob, and every line that touches it looks like `cfg["database"]["pool"]["max"]`. That is noisy, and worse, a typo in a bracket string is a `KeyError` deep in a request handler rather than at startup. Reading it as `cfg.database.pool.max` is the same lookup written the way the rest of the code reads.

Two things have to be true before that is safe. A name that is not in the config has to fail like a missing attribute, not come back as `None`, because a silent `None` becomes a connection to nowhere. And the object has to refuse writes: settings that can be assigned at runtime are settings that differ between two workers reading the same file, and the assignment would shadow the whole lookup anyway, so the next read would return the shadow instead of the config.

## You get
nothing to start — you return a class. The test builds it itself, like

```python
Config = solve()
Config({"db": {"pool": {"max": 20}}}).db.pool.max
```

## You return
the class `Config`.

## Rules
- `__init__(self, mapping)` keeps a plain `dict` copy of `mapping`. It must store it **without** going through the class's own assignment, or the guard below will refuse it.
- `__getattr__(self, name)` looks `name` up in that dict and returns the value, wrapped:
  - a value that is itself a mapping comes back as a new `Config`;
  - a value that is a list comes back as a list, with any mapping inside it wrapped as a `Config` and everything else left alone;
  - anything else comes back untouched.
- A name that is not in the dict raises `AttributeError`.
- `__setattr__(self, name, value)` raises `AttributeError` for every name. The config is read-only.
- `keys(self)` returns the dict's keys, so a caller can still ask what is there.

```python
Config = solve()
cfg = Config({"db": {"host": "10.0.0.4", "pool": {"max": 20}}, "regions": [{"id": "eu"}, "us"]})
cfg.db.host              # -> '10.0.0.4'
cfg.db.pool.max          # -> 20
cfg.regions[0].id        # -> 'eu'
cfg.regions[1]           # -> 'us'
sorted(cfg.keys())       # -> ['db', 'regions']
cfg.timeout              # -> AttributeError
hasattr(cfg, "timeout")  # -> False
cfg.timeout = 30         # -> AttributeError
```

> [!WARNING]
> Returning `None` for a missing name instead of raising is the failure this task is about. `hasattr` is built on catching `AttributeError`, so a `None`-returning config answers `True` to every question you ask it and the misconfiguration surfaces as a timeout in production. The test checks both the raise and `hasattr`.

> [!NOTE]
> `__getattr__` runs only when the normal lookup fails, and the dict you stored is a real instance attribute, so reading it inside `__getattr__` does not re-enter. Forget to store it and you get infinite recursion instead of a clean error — which is why the storing line matters as much as the lookup.

## Hints
### Hint 1
`__setattr__` intercepts `self._data = ...` in `__init__` too, and refuses it. Step around your own guard exactly once, with the base implementation: `object.__setattr__(self, "_data", dict(mapping))`.
### Hint 2
The wrapping is one small function used in two places — on a value straight out of the dict, and on each item of a list:

```python
def _wrap(value):
    if isinstance(value, abc.Mapping):
        return Config(value)
    if isinstance(value, list):
        return [_wrap(item) for item in value]
    return value
```
### Hint 3
The lookup itself is a `KeyError` translated into the exception attribute access is supposed to raise:

```python
def __getattr__(self, name):
    try:
        return _wrap(self._data[name])
    except KeyError:
        raise AttributeError(name) from None
```

`from None` keeps the traceback about the missing attribute rather than about a dict.

---
Adapted from fluentpython/example-code-2e — MIT
