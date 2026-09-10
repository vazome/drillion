---
title: operator overloading — a route leg you can add, scale and measure
difficulty: hard
tier: advanced
minutes: 28
prereqs: [57]
tags: [class-customization, comparisons]
source: fluentpython/example-code-2e 16-op-overloading (MIT, adapted)
---
# operator overloading — a route leg you can add, scale and measure

*`__add__`, `__mul__`, `__eq__` and `__abs__` let `+`, `*`, `==` and `abs()` mean something for your own type — and `NotImplemented` is how you decline politely instead of blowing up.*

## Read first
- [Emulating numeric types](https://devdocs.io/python~3.14/reference/datamodel#emulating-numeric-types) — `__add__`, `__mul__`, `__abs__` and the reflected `__radd__`
- [`NotImplemented`](https://devdocs.io/python~3.14/library/constants#NotImplemented) — the value that means "I cannot, ask the other operand"
- [`itertools.zip_longest`](https://devdocs.io/python~3.14/library/itertools#itertools.zip_longest) — pairing two runs of different length
- [`math.hypot`](https://devdocs.io/python~3.14/library/math#math.hypot) — straight-line length of any number of components
- [`__iter__`](https://devdocs.io/python~3.14/reference/datamodel#object.__iter__) — what makes an object usable wherever an iterable is expected

## Why
A picking robot's route is a list of legs, each one an offset from where it stood. Two questions get asked of that list all day: what is the net displacement of the whole route, and how far did it actually go. Written with plain functions that is `add_legs(a, b)` and `scale_leg(leg, 2)` sprinkled through the planner, and every caller has to remember which helper goes with which type. Written as operators it is `a + b` and `leg * 2` and `abs(leg)`, and the planner reads like the arithmetic it is.

The part that is easy to get wrong is what happens when the other operand is not a leg at all. Raising an error there looks correct and quietly breaks `(10, 20) + leg`, because Python's rule is that the left operand gets first refusal and the *right* one gets a second chance — but only if the left one declined rather than exploded.

## You get
nothing to start — you return a class. The test builds it itself, like

```python
Move = solve()
Move([3, 4]) + Move([1, 1])
```

## You return
the class `Move`.

## Rules
- `__init__(self, components)` takes an iterable of numbers and stores them as a tuple of `float` on `self.components`. `Move([3, 4]).components` is `(3.0, 4.0)`.
- `__iter__(self)` walks the components, so a `Move` is itself one of the iterables `__add__` accepts.
- `__repr__(self)` returns `Move(3.0, 4.0)` — the class name, then the components as `repr` shows them, comma-separated.
- `__abs__(self)` returns the straight-line length of the offset.
- `__eq__(self, other)` is `True` when `other` is a `Move` with the same components. When `other` is anything else, return `NotImplemented` and let Python fall back to identity, so `Move([1, 2]) == (1.0, 2.0)` is `False` rather than an error.
- `__add__(self, other)` pairs `self.components` with `other`, padding the shorter side with `0.0`, and returns a new `Move` of the sums. `other` is any iterable of numbers, not only a `Move`. When the pairing or the addition cannot be done, return `NotImplemented`.
- `__radd__(self, other)` handles the case where the value on the left of the `+` could not do the job — `(10, 20) + Move([1, 1])`. Addition here is symmetric, so it is one line.
- `__mul__(self, scalar)` returns a new `Move` with every component multiplied. When `scalar` is not a number, return `NotImplemented`.

```python
Move = solve()
leg = Move([3, 4])
abs(leg)                  # -> 5.0
leg + Move([1, 1])        # -> Move(4.0, 5.0)
leg + [1, 1, 1]           # -> Move(4.0, 5.0, 1.0)
(10, 20) + leg            # -> Move(13.0, 24.0)
leg * 3                   # -> Move(9.0, 12.0)
leg == Move([3, 4])       # -> True
leg == (3.0, 4.0)         # -> False
leg + "nope"              # -> TypeError
```

> [!WARNING]
> `raise TypeError(...)` and `return NotImplemented` look interchangeable, and are not. Raising ends the expression; returning hands the operation to the other operand's reflected method, which is the only reason `(10, 20) + leg` can work at all. The test calls `__add__` and `__mul__` directly and checks the returned value, so a version that raises fails there even though every good case is right.

> [!NOTE]
> `NotImplemented` is a value you return. `NotImplementedError` is an exception you raise, and it is for an abstract method nobody filled in. They are different tools with confusingly similar names.

## Hints
### Hint 1
`itertools.zip_longest(self.components, other, fillvalue=0.0)` does the padding for you, in both directions, for free. What is left is summing each pair and handing the result to `Move(...)`.
### Hint 2
The cheapest way to decide whether `other` can be added is to try it and catch `TypeError`:

```python
def __add__(self, other):
    try:
        pairs = itertools.zip_longest(self.components, other, fillvalue=0.0)
        return Move(a + b for a, b in pairs)
    except TypeError:
        return NotImplemented
```

Note that the generator is consumed inside `Move.__init__`, which is inside the `try` — so an iterable of the wrong *kind* of thing, like `"nope"`, is caught too.
### Hint 3
Reflected operators, in miniature:

```python
class Cents:
    def __init__(self, n):
        self.n = n
    def __add__(self, other):
        if isinstance(other, int):
            return Cents(self.n + other)
        return NotImplemented
    def __radd__(self, other):
        return self + other

Cents(5) + 3     # __add__ handles it
3 + Cents(5)     # int.__add__ returns NotImplemented, so Cents.__radd__ runs
Cents(5) + "x"   # both sides decline -> TypeError, raised by Python, not by you
```

---
Adapted from fluentpython/example-code-2e — MIT
