---
title: context manager class — __enter__ and __exit__, swallowing one error and no more
difficulty: medium
tier: advanced
minutes: 18
prereqs: [57, 73]
tags: [context-managers, classes]
source: fluentpython/example-code-2e 18-with-match (MIT, adapted)
---
# context manager class — __enter__ and __exit__, swallowing one error and no more

*`with` is two methods on an object: one that changes something on the way in, one that puts it back on the way out and decides what happens to an exception.*

## Read first
- [The `with` statement](https://devdocs.io/python~3.14/reference/compound_stmts#the-with-statement) — what Python calls, and in what order
- [Context manager types](https://devdocs.io/python~3.14/reference/datamodel#with-statement-context-managers) — `__enter__`, `__exit__`, and what the return value of `__exit__` means
- [`contextlib.suppress`](https://devdocs.io/python~3.14/library/contextlib#contextlib.suppress) — the same "swallow one type" idea, already in the standard library

## Why
Before a deploy you flip the service into maintenance mode, drain the queue, and flip it back. The flip back is the part that gets forgotten: an early `return`, a raised exception, a branch somebody added last month, and the service stays in maintenance until a human notices. Written as a context manager the flip back is not a line anyone can skip past — it is the exit of the block, and the block always ends.

Draining is allowed to time out; that is what draining does when the queue is long, and it must not take the deploy down with it. Everything else that goes wrong in there is news, and news has to travel.

## You get
nothing to start — you return a class. The test builds it itself, like

```python
Window = solve()
settings = {"mode": "live", "region": "eu-west-1"}
with Window(settings) as previous:
    ...
```

## You return
the class `Window`.

## Rules
- `Window(settings)` takes a mutable dict and holds on to it. It changes nothing yet — entering is what changes things.
- `__enter__(self)` sets `settings["mode"]` to `"maintenance"` and returns whatever `settings["mode"]` was before. The block gets that value as the `as` target, so it can tell you what it is going back to.
- `__exit__(self, exc_type, exc_value, traceback)` puts the old value back under `"mode"`, whether the block finished or blew up. It touches no other key.
- If the block raised `TimeoutError`, `__exit__` returns `True` and the exception stops there.
- For anything else — including a clean block — `__exit__` returns nothing, and an exception carries on out of the `with`.

```python
Window = solve()
settings = {"mode": "live"}

with Window(settings) as previous:
    previous              # -> 'live'
    settings["mode"]      # -> 'maintenance'
settings["mode"]          # -> 'live'

with Window(settings):
    raise TimeoutError("queue still draining")
# no error here: the window swallowed it

with Window(settings):
    raise ValueError("bad payload")
# ValueError, and settings["mode"] is 'live' again
```

> [!WARNING]
> `return True` at the end of `__exit__` passes every test that raises a `TimeoutError` and hides every bug the block will ever have. A truthy return means *handled*, and Python believes it. The test raises a `ValueError` too and insists on catching it outside the `with`.

> [!NOTE]
> Restoring before you look at `exc_type` is the easy way to get this right — the exception path and the clean path do the same restore, so do it once, first.

## Hints
### Hint 1
`with expr as name:` calls `expr.__enter__()` and binds `name` to what it returns. Returning nothing means `name` is `None`, which is a legal context manager and a useless one here.
### Hint 2
`__exit__` is called with three arguments describing the exception, and all three are `None` when the block ended normally. `exc_type` is the class, so `exc_type is TimeoutError` is the whole test — no `isinstance` gymnastics, no bare `except`.
### Hint 3
Same shape, different rule:

```python
import os

class Chdir:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.previous = os.getcwd()
        os.chdir(self.path)
        return self.previous

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.previous)
        if exc_type is FileNotFoundError:
            return True
```

The directory goes back either way. Only the one named error is absorbed; a `PermissionError` still reaches the caller, which is the point of naming it.

---
Adapted from fluentpython/example-code-2e — MIT
