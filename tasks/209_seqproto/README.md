---
title: the sequence protocol — a window of readings you can slice like a list
difficulty: medium
tier: advanced
minutes: 24
prereqs: [57, 204]
tags: [sequences, slicing]
source: fluentpython/example-code-2e 12-seq-hacking (MIT, adapted)
---
# the sequence protocol — a window of readings you can slice like a list

*`__len__` and `__getitem__` are all Python asks for before `len()`, indexing, slicing, iteration and `in` start working on your class.*

## Read first
- [Emulating container types](https://devdocs.io/python~3.14/reference/datamodel#emulating-container-types) — `__len__`, `__getitem__`, and what they unlock for free
- [`slice`](https://devdocs.io/python~3.14/library/functions#slice) — the object `s[1:4]` actually hands your method
- [`operator.index`](https://devdocs.io/python~3.14/library/operator#operator.index) — turning a key into a real index, or rejecting it
- [`type()`](https://devdocs.io/python~3.14/library/functions#type) — asking an object which class built it

## Why
A monitoring job holds the last few thousand samples from a sensor and does the same handful of things to them: how many are there, what was the latest one, and what did the last hour look like. If that window is a plain list you get all of it for free but you have nowhere to hang the methods that belong to it. If it is a class wrapping a list you get the methods and lose every one of the conveniences, so the calling code goes back to reaching inside for `window.values[-1]`.

Two methods buy the conveniences back. The one that is easy to get wrong is slicing: `window[-60:]` is still a window, and every method the window has should still be there on the result. Hand back a bare list instead and the caller's next line breaks, one step further away from the mistake.

## You get
nothing to start — you return a class. The test builds it itself, like

```python
Series = solve()
Series([1, 2, 3, 4])[1:3]
```

## You return
the class `Series`.

## Rules
- `__init__(self, values)` takes an iterable of numbers and stores them as a tuple of `float` on `self.values`.
- `__repr__(self)` returns `Series(1.0, 2.0, 3.0)` — the class name, then the values as `repr` shows them, comma-separated.
- `__len__(self)` is how many values there are.
- `__getitem__(self, key)`:
  - a `slice` gives back **a new object of the same class** holding that slice of the values.
  - an integer gives back that one value, with negative indices working the way they do on a list.
  - anything else raises `TypeError`.

```python
Series = solve()
s = Series([10, 20, 30, 40, 50])
len(s)          # -> 5
s[0]            # -> 10.0
s[-1]           # -> 50.0
s[1:4]          # -> Series(20.0, 30.0, 40.0)
list(s)         # -> [10.0, 20.0, 30.0, 40.0, 50.0]
30.0 in s       # -> True
s["first"]      # -> TypeError
```

> [!WARNING]
> `type(self)(...)` rather than `Series(...)`. Naming the class outright works until somebody subclasses it, and then slicing a `SmoothedSeries` quietly returns a plain `Series` and the smoothing is gone. The test subclasses your class and slices it, so the hard-coded name fails there even though every value is right.

> [!NOTE]
> You are not asked to write `__iter__` or `__contains__`. `list(s)` and `30.0 in s` work anyway, because Python falls back to calling `__getitem__` with 0, 1, 2 … until it raises `IndexError` — which a tuple lookup does for you. That fallback is the whole reason these two methods are called a protocol.

## Hints
### Hint 1
`s[1:4]` does not pass you three numbers. It passes one `slice` object, and a tuple already knows what to do with one: `self.values[key]` returns the sliced tuple. Your job is deciding what to wrap it in.
### Hint 2
Branch on the key before you use it:

```python
def __getitem__(self, key):
    if isinstance(key, slice):
        return type(self)(self.values[key])
    return self.values[operator.index(key)]
```

`operator.index` accepts an `int` and anything that behaves like one, and raises `TypeError` for a string — which is exactly the third rule, without you writing it.
### Hint 3
Why `type(self)` is not fussiness:

```python
class Smoothed(Series):
    def average(self):
        return sum(self.values) / len(self)

Smoothed([1, 2, 3, 4])[1:3].average()
```

That last call only exists if the slice came back as a `Smoothed`. With `Series(...)` hard-coded it is an `AttributeError`.

---
Adapted from fluentpython/example-code-2e — MIT
