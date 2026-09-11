---
title: __call__ — a dispenser you invoke like a function and can still inspect
difficulty: medium
tier: advanced
minutes: 18
prereqs: [57]
tags: [classes, functions]
source: fluentpython/example-code-2e 07-1class-func (MIT, adapted)
---
# __call__ — a dispenser you invoke like a function and can still inspect

*`__call__` makes an instance usable with `()`, so an object with state can go anywhere a plain function is expected.*

## Read first
- [`__call__`](https://devdocs.io/python~3.14/reference/datamodel#object.__call__) — what `obj()` does when the class defines it
- [`callable()`](https://devdocs.io/python~3.14/library/functions#callable) — how to ask whether something can be invoked
- [`__len__`](https://devdocs.io/python~3.14/reference/datamodel#object.__len__) — making `len()` work on your own type
- [`list.pop`](https://devdocs.io/python~3.14/library/stdtypes#mutable-sequence-types) — taking an item off one end

## Why
A support desk hands out ticket numbers in order, and the queue widget that displays them wants nothing more than something it can call to get the next one. A plain function closing over a list satisfies that and stops there: you cannot ask it how many numbers are left, you cannot look at it in a debugger and see anything but a closure, and reloading it means rebuilding it.

An instance with `__call__` satisfies the same contract and keeps the state in the open. The widget calls it, the dashboard reads `len()` off it, the log prints it, and nothing at the call site has to know it is not a function. That is the trade the method exists for: the convenience of a function, with the state still an object you can look at.

## You get
nothing to start — you return a class. The test builds it itself, like

```python
Dispenser = solve()
desk = Dispenser(["T-01", "T-02"])
desk()
```

## You return
the class `Dispenser`.

## Rules
- `__init__(self, items)` takes an iterable and keeps its own `list` copy. A list passed in must not be touched — the caller keeps using theirs.
- `pick(self)` removes and returns the **first** item still waiting, so the order out is the order in.
- `pick` on an empty dispenser raises `LookupError("dispenser is empty")`.
- `__call__(self)` does exactly what `pick` does. Say so once; do not write the body twice.
- `__len__(self)` is how many are left.
- `__repr__(self)` returns `Dispenser(2 left)` — the class name and the count.

```python
Dispenser = solve()
desk = Dispenser(["T-01", "T-02"])
len(desk)          # -> 2
desk()             # -> 'T-01'
desk.pick()        # -> 'T-02'
repr(desk)         # -> 'Dispenser(0 left)'
callable(desk)     # -> True
desk()             # -> LookupError
```

> [!WARNING]
> A closure does the calling part in three lines, and that is the answer this task is not looking for: `solve()` must hand back a class, and the object it builds has to be inspectable between calls. The test asks whether what came back is a class and reads `len()` off an instance, so a factory returning a function fails at the first line.

> [!NOTE]
> `__call__` has to be found on the **class**, not stuck on the instance. `desk.__call__ = something` does not make `desk()` work, because Python looks up special methods on the type.

## Hints
### Hint 1
`self._items.pop(0)` takes from the front, `pop()` takes from the back. First in, first out means the front, which is `pop(0)`.
### Hint 2
`pop` on an empty list raises `IndexError`, and the rule asks for `LookupError` with a specific message. Catch the one and raise the other:

```python
def pick(self):
    try:
        return self._items.pop(0)
    except IndexError:
        raise LookupError("dispenser is empty") from None
```
### Hint 3
"Does exactly what `pick` does" is one line in the class body, not a copy of the method:

```python
class Dispenser:
    ...
    __call__ = pick
```

`pick` is already a plain function at that point in the class body, so binding a second name to it gives the class both, and they stay the same code forever.

---
Adapted from fluentpython/example-code-2e — MIT
