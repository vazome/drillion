---
title: pickle — round-trip your own object, and refuse a payload you did not write
difficulty: hard
tier: advanced
minutes: 25
prereqs: [173]
tags: [bytes, class-inheritance]
---
# pickle — round-trip your own object, and refuse a payload you did not write

*`pickle` rebuilds whatever the bytes tell it to rebuild. A restricted `Unpickler` is how you keep that list down to the one class you meant.*

## Read first
- [`pickle`](https://devdocs.io/python~3.14/library/pickle) — `dumps`, `loads`, and the warning at the top of the page
- [Restricting globals](https://devdocs.io/python~3.14/library/pickle#restricting-globals) — `Unpickler.find_class`, the one hook that decides what a payload may name
- [`pickle.UnpicklingError`](https://devdocs.io/python~3.14/library/pickle#pickle.UnpicklingError) — the exception the restriction is expected to raise

## Why
An agent on each host writes a snapshot of its health checks to a file, and a collector reads them back. Pickle is a fair choice for that: both ends are your code, the shape changes as often as the dataclass does, and nobody wants to hand-write a schema for an internal cache. What makes it a bad choice is the next quarter, when the cache directory is world-writable, or the snapshots start arriving over a socket, or someone restores them from a backup of unclear origin. Unpickling is not parsing. The payload names classes and callables and the machine goes and fetches them, so a file that has been tampered with is not bad data — it is a sentence someone else gets to finish. Keeping the format means saying out loud which single class a snapshot is allowed to mention.

## You get
`Snapshot`, a dataclass, is given to you above `solve`. `solve()` itself takes no arguments.

## You return
a tuple of two callables, `(dump, load)`:

- `dump(snapshot)` returns `bytes` that `load` can turn back into an equal `Snapshot`.
- `load(blob)` returns the `Snapshot` those bytes describe, and raises `pickle.UnpicklingError` when the payload names anything other than `Snapshot`.

```python
dump, load = solve()
snap = Snapshot("web-01", {"disk": "ok", "tls": "warn"})
load(dump(snap)) == snap            # -> True

import collections
load(pickle.dumps(collections.Counter("ab")))   # -> pickle.UnpicklingError
```

## Rules
- `dump` produces a real pickle of the `Snapshot`. The grader reads your bytes with its own loader and hands you bytes from its own dumper, so a private format of your own will not pass.
- `load` allows exactly one class through: the `Snapshot` defined in this file, recognised by its `__module__` and `__qualname__`. Everything else raises `pickle.UnpicklingError`, including classes that are perfectly harmless.
- An allowlist by name only. Do not accept `collections.Counter` because a snapshot happens to contain a dict, and do not accept a class merely because you have heard of it.
- `load` returns a new object, not the one `dump` was given.

> [!WARNING]
> `pickle.loads` on its own passes every round-trip test you can write and rejects nothing at all. The grader hands `load` three payloads it did not write, so the round trip is half the task.

> [!NOTE]
> `Unpickler` wants a binary file rather than a `bytes`, so `io.BytesIO(blob)` is the adapter. `find_class(self, module, name)` is called once for every global the payload names, with two strings — it has not imported anything yet, and if you do not return a class it never will.

## Hints
### Hint 1
`pickle.dumps` and `pickle.loads` are conveniences over the `Pickler` and `Unpickler` classes. Dumping stays a one-liner; loading is where you need the class, because that is the only place the hook exists.
### Hint 2
Subclass `pickle.Unpickler` and override `find_class`. Return the class when the two strings are the ones you expect, and `raise pickle.UnpicklingError(...)` otherwise. Do not call `super().find_class` in the refusal branch — that is the import you are trying not to do.
### Hint 3
Same idea, one allowed class:

```python
import io
import pickle


class Reading:
    def __init__(self, value):
        self.value = value


class _OnlyReading(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) == (Reading.__module__, Reading.__qualname__):
            return Reading
        raise pickle.UnpicklingError(f"{module}.{name} is not allowed here")


blob = pickle.dumps(Reading(3))
_OnlyReading(io.BytesIO(blob)).load().value          # -> 3
_OnlyReading(io.BytesIO(pickle.dumps(sum))).load()   # -> UnpicklingError: builtins.sum is not allowed here
```

`Reading.__module__` rather than the literal `"__main__"`: the same file is imported under different names by different runners, and a hard-coded module string stops matching the moment one of them does something you did not predict.
