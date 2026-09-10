---
title: TypeVar and Generic — one container that remembers what is in it
difficulty: medium
tier: advanced
minutes: 20
prereqs: [57]
tags: [type-hints, classes]
source: fluentpython/example-code-2e 15-more-types (MIT, adapted)
---
# TypeVar and Generic — one container that remembers what is in it

*A `TypeVar` is a placeholder for a type the class does not pick. `Generic[T]` is how a class says "whatever you put in, that is what comes out".*

## Read first
- [`typing.TypeVar`](https://devdocs.io/python~3.14/library/typing#typing.TypeVar) — declaring the placeholder
- [`typing.Generic`](https://devdocs.io/python~3.14/library/typing#typing.Generic) — making a class take a type parameter
- [`collections.abc.Iterable`](https://devdocs.io/python~3.14/library/collections.abc#collections.abc.Iterable) — the right annotation for "anything you can loop over"

## Why
Three parts of the dispatch system queue things up and hand them out one at a time: parcels waiting for a van, refunds waiting for approval, alerts waiting for a human. The code is the same nine lines every time, so it gets copied twice and the third copy fixes a bug the other two keep.

Write it once and it holds "anything", which is honest and useless: the tool that reads your code can no longer tell you that the thing you took out of the parcel queue is being passed to the refund approver. A type parameter is how the class stays one class and still keeps that answer. `Drawer[Parcel]` and `Drawer[Refund]` are the same nine lines and two different promises.

## You get
nothing to start — you return a class. The test builds it itself, like

```python
Drawer = solve()
queue = Drawer[str](["a", "b"])
```

## You return
the class `Drawer`.

## Rules
- `Drawer` is generic over one type parameter. Declare a `TypeVar` and inherit from `Generic[T]`, so `Drawer[int]` is a legal thing to write.
- `Drawer(items)` takes anything iterable and keeps its own list of it, in order. The caller's list is not the drawer's list.
- `load(self, items)` adds more to the back. It returns nothing.
- `take(self)` removes and returns the item that has waited longest — the front. On an empty drawer it raises `LookupError("take from an empty Drawer")`.
- `remaining(self)` returns what is left, front first, as a `tuple`.

Annotate all of it in terms of `T`: `load` takes an `Iterable[T]`, `take` returns a `T`, `remaining` returns a `tuple[T, ...]`.

```python
Drawer = solve()

queue = Drawer[str](["ada", "grace"])
queue.load(["alan"])
queue.take()        # -> 'ada'
queue.remaining()   # -> ('grace', 'alan')
Drawer([]).take()   # -> LookupError
```

> [!WARNING]
> Every rule above can be satisfied by an ordinary class with no `Generic` anywhere, because none of the typing has any effect when the code runs. It fails on the one line that is the point of the task: `Drawer[str](...)` raises `TypeError: type 'Drawer' is not subscriptable`. The test writes that line.

> [!NOTE]
> `Drawer[str]` does not check anything at run time either — you can put integers in it and nothing complains. The subscription exists so a type checker can follow the element type through, which is the whole return on writing it.

## Hints
### Hint 1
`T = TypeVar("T")` at module level, then `class Drawer(Generic[T]):`. The name inside the quotes has to match the name you bound it to; it is how the type checker prints it back at you.
### Hint 2
Front first means `list.pop(0)` and `list.append`. Wrap the pop, or check the list first — an empty drawer has to raise `LookupError`, not `IndexError`.
### Hint 3
Same shape, different rule:

```python
from typing import Generic, TypeVar
from collections.abc import Iterable

T = TypeVar("T")

class Latest(Generic[T]):
    def __init__(self, items: Iterable[T]) -> None:
        self._items = list(items)

    def add(self, items: Iterable[T]) -> None:
        self._items.extend(items)

    def newest(self) -> T:
        return self._items[-1]

Latest[int]([1, 2, 3]).newest()   # -> 3
```

One class, and `Latest[int]` and `Latest[str]` are two different promises to anything that reads the code.

---
Adapted from fluentpython/example-code-2e — MIT
