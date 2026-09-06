---
title: context managers — @contextmanager with guaranteed exit
difficulty: medium
tier: core
minutes: 12
prereqs: [46, 56, 72]
tags: [context-managers]
---
# context managers — @contextmanager with guaranteed exit

*`with` is a promise that cleanup runs — including on the way out through an error.*

## Read first
- [Context Managers and Python's with Statement](https://realpython.com/python-with-statement/) — `with` = setup, body, guaranteed cleanup (read the 'async with' section too)
- [contextlib](https://devdocs.io/python~3.14/library/contextlib) — `@contextmanager`, the short way

## Why
A deploy script writes "deploy started" and "deploy finished" into a shared event log so the dashboard knows when a deploy is in progress. One day a deploy crashes halfway, the "finished" marker never gets written, and the dashboard shows a deploy stuck for hours. You need a way to guarantee the closing marker is written even when the work in the middle fails, without hiding the failure from whoever ran the script.

## You get
`events` — a list like `[]` that you append markers to. `name` — the name of the operation, like `"deploy"`. The test creates them and hands them to you; you never build them yourself.

## You return
a context manager: something usable in a `with`-block that appends `"enter <name>"` when the block starts and `"exit <name>"` when it ends, no matter how it ends. Any error from the block must still escape to the caller.

## Rules
A context manager that brackets a block with two markers.

Entering appends `f"enter {name}"` to the list `events`. Leaving appends `f"exit {name}"` — always, including when the body of the `with`-block raises.

```python
events = []
with solve(events, "deploy"):
    events.append("work")
events   # -> ["enter deploy", "work", "exit deploy"]

events = []
try:
    with solve(events, "deploy"):
        raise ValueError("pod 404")
except ValueError:
    pass
events   # -> ["enter deploy", "exit deploy"]   <- exit still ran
```

> [!WARNING]
> The exception must still reach the caller; you are logging, not swallowing.

Build it with `contextlib.contextmanager`: put that decorator on this function and place exactly one `yield` where the `with`-block's body belongs. Nothing needs to come back out of the `yield` — a bare `yield` is fine, and the caller uses no `as`.

## Hints
### Hint 1
The easy half is a marker before and a marker after. The whole task is the second marker surviving a body that blows up. Ask what happens to the lines after the `yield` when the `with`-block raises — and which Python keyword exists precisely to make a block run either way.
### Hint 2
Import `contextmanager` from `contextlib` and decorate `solve` with it. That turns a generator into a context manager: everything before the `yield` runs on entry, everything after runs on exit. The catch is that an exception in the body is thrown back into your generator at the `yield`, so a plain line underneath it never executes. Wrap the `yield` in `try`, and put the exit marker in `finally`. Do not catch the exception — `finally` re-raises for you.
### Hint 3
Different data — a start/stop log around a block:

```python
from contextlib import contextmanager

@contextmanager
def phase(log):
    log.append('start')
    try:
        yield
    finally:
        log.append('stop')

log = []
try:
    with phase(log):
        raise RuntimeError('boom')
except RuntimeError:
    pass
print(log)        # ['start', 'stop']
```

Change `finally` to a bare line after the `yield` and the list stops at `['start']` — the file handle, the lock, the temp dir all leak the same way.
