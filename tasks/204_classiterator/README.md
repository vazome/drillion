---
title: the iterator protocol — a class you can walk through twice
difficulty: medium
tier: advanced
minutes: 20
prereqs: [57]
tags: [iteration, classes]
source: fluentpython/example-code-2e 17-it-generator (MIT, adapted)
---
# the iterator protocol — a class you can walk through twice

*`__iter__` hands back a fresh walker each time, and `__next__` is the walker taking one step.*

## Read first
- [Iterator types](https://devdocs.io/python~3.14/library/stdtypes#iterator-types) — the two methods `for` actually calls
- [`iter()`](https://devdocs.io/python~3.14/library/functions#iter) — what a `for` loop does before its first step
- [`StopIteration`](https://devdocs.io/python~3.14/library/exceptions#StopIteration) — how a walker says it is finished

## Why
You have already written five of these as generators, and a generator is the right answer most days. This is the day it is not. A generator function returns one walker and that walker is used up: hand the same object to two `for` loops and the second one runs zero times, silently, and the count it produces is zero for a reason nothing in the code says out loud. Splitting the two roles apart is what fixes it. The collection knows what it holds and can be walked any number of times; the walker knows only where it has got to, and is thrown away at the end of each pass. Writing the protocol by hand once is what makes the generator version legible afterwards, because you can see which half it is collapsing.

## You get
nothing to start — you return classes. The test builds them itself, like

```python
Fields, FieldIterator = solve()
list(Fields("level service msg"))
```

## You return
a tuple of the two classes, in the order `(Fields, FieldIterator)`.

## Rules
`Fields` is the collection:

- `__init__(self, line)` splits the line on whitespace and keeps the parts as `self.parts`.
- `__iter__(self)` returns a **new** `FieldIterator` over those parts every time it is called. It is a plain `return`, not a `yield`.

`FieldIterator` is the walker:

- `__init__(self, parts)` keeps the parts and a position starting at zero.
- `__next__(self)` returns the part at the position and moves on, and raises `StopIteration` once there are none left. It keeps raising it on every later call.
- `__iter__(self)` returns `self`, because a walker is also something a `for` loop can be handed directly.

```python
Fields, FieldIterator = solve()
holder = Fields("level service msg")
list(holder)          # -> ['level', 'service', 'msg']
list(holder)          # -> ['level', 'service', 'msg']   the same, on purpose
walker = iter(holder)
next(walker)          # -> 'level'
next(walker)          # -> 'service'
```

> [!WARNING]
> `Fields.__iter__` must not be a generator function. One `yield` anywhere in it and it returns a generator instead of your `FieldIterator`, which passes the walking checks and fails the type one. Writing it out is the exercise.

> [!NOTE]
> `iter(holder) is not iter(holder)` is checked, and so is `iter(walker) is walker`. Those are not the same rule: a collection makes a new walker each time, and a walker hands back itself.

## Hints
### Hint 1
`for x in thing:` calls `iter(thing)` once, then `next(...)` on the result until it raises `StopIteration`. Two `for` loops over the same `Fields` call `iter` twice, so `__iter__` returning something new each time is what makes the second pass work.
### Hint 2
`__next__` needs somewhere to remember how far it has got, and that is an attribute on the iterator, not on the collection. Once the position reaches the length, `raise StopIteration` — with no value, and every time from then on.
### Hint 3
The same split, over something else:

```python
class Countdown:
    def __init__(self, start):
        self.start = start
    def __iter__(self):
        return CountdownIterator(self.start)

class CountdownIterator:
    def __init__(self, n):
        self.n = n
    def __iter__(self):
        return self
    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1

c = Countdown(3)
print(list(c), list(c))   # [3, 2, 1] [3, 2, 1]
```

`Countdown` never changes; each `CountdownIterator` is used once and discarded.

---
Adapted from fluentpython/example-code-2e — MIT
