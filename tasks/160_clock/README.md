---
title: class-composition — a time-of-day class that wraps around midnight
difficulty: hard
tier: core
minutes: 20
prereqs: [29, 115]
tags: [class-composition, rich-comparisons, string-formatting]
source: exercism/python practice/clock (MIT, adapted)
---
# class-composition — a time-of-day class that wraps around midnight

*clock — normalise once in the constructor, and every other method becomes one line.*

## Read first
- [A first look at classes](https://docs.python.org/3/tutorial/classes.html#a-first-look-at-classes) — `__init__`, `self`, and what a method actually is
- [`object.__repr__` and `object.__str__`](https://docs.python.org/3/reference/datamodel.html#object.__repr__) — the two string forms: one for developers, one for humans
- [`object.__eq__`](https://docs.python.org/3/reference/datamodel.html#object.__eq__) — define `==` and Python derives `!=` from it for free
- [`object.__add__`](https://docs.python.org/3/reference/datamodel.html#object.__add__) — how `a + b` reaches your class
- [`divmod()`](https://docs.python.org/3/library/functions.html#divmod) — quotient and remainder in one call, and it floors, so negatives behave
- [Format specification mini-language](https://docs.python.org/3/library/string.html#format-specification-mini-language) — `02d` is "two digits, pad with zeros"

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Quiet hours, rota shifts, cron windows, "the batch runs 22:50 plus twenty minutes": plenty of real values are a time of day with no date attached, and all of them eventually have to wrap around midnight. The bug everybody ships once is fixing up the numbers at the moment of display instead of at the moment of construction — so `22:80` and `23:20` are the same instant to a human but two different objects to the code, the equality check says no, and the alert that should have fired at 00:10 never fires. This task is the small, sharp version of that: one class, one normalisation, and five special methods that all get trivial once the normalisation happens in the right place.

## Instructions
Implement a clock that handles times without dates.

You should be able to add and subtract minutes to it.

Two clocks that represent the same time should be equal to each other.

### How this exercise is implemented for the Python track

The tests for this exercise expect that your clock will be implemented in a Clock `class`.
If you are unfamiliar with classes in Python, [concept:python/classes]() and [classes][classes in python] (_from the Python docs_) are good places to start.

### Representing your class

When working with and debugging [objects][what-is-an-object], it's important to have a good representation of that object.
For example — if you were to create a new [`datetime.datetime`][datetime] object in the Python [REPL][REPL] environment, you could view its [string representation][str-rep-classes]:

```python
>>> from datetime import datetime
>>> new_date = datetime(2022, 5, 4)
>>> new_date
datetime.datetime(2022, 5, 4, 0, 0)
```

Your Clock `class` should create a custom `object` that handles times _without_ dates.
One important aspect of this `class` will be how it is represented as a _string_.
Other programmers who use or call Clock `objects` created from the Clock `class` will refer to this string representation for debugging and other activities.
However, the default representation on a custom `class` is not very helpful:

```python
>>> Clock(12, 34)
<Clock object st 0x102807b20 >
```

To create a more helpful representation, you can define a [`__repr__`][repr-method] [special method][dunder-methods] on the `class`.

Ideally, that `__repr__` method returns valid Python code that can be used to recreate the object when passed to [`eval()`][eval-built-in] — as laid out in the [specification for a `__repr__` method][repr-docs].
Returning valid Python code allows another developer to copy-paste the `str` directly into code or the REPL.
A `Clock` that represents 11:30 AM could look like this:

```python
 `Clock(11, 30)`
```

Defining a `__repr__` method is good practice for all custom classes.
Some additional things to consider:

- The information returned from this method should be beneficial when debugging issues.
- _Ideally_, the method returns a string that is valid Python code — although that might not always be possible.
- If valid Python code is not practical, returning a description between angle brackets: `< ...a practical description... >` is the convention.

#### String conversion

In addition to the `__repr__` method, there might also be a need for an alternative "human-readable" string representation of the `class`.
This might be used to format the object for program output or documentation.
This is done by writing a [`__str__`][str-dunder] special method.
Looking at `datetime.datetime` again:

```python
>>> str(datetime.datetime(2022, 5, 4))
'2022-05-04 00:00:00'
```

When a `datetime` object is asked to convert itself to a string representation, it returns a `str` formatted according to the [ISO 8601 standard][ISO 8601], which can be parsed by most datetime libraries into a human-readable date and time.

In this exercise, you will get a chance to write a `__str__` method for your Clock, as well as a `__repr__` method.

```python
>>> str(Clock(11, 30))
'11:30'
```

To support this string conversion, you will need to create a `__str__` special method on your `class` that returns a more "human-readable" string showing the Clock time.

If you don't create a `__str__` method and you call `str()` on your class, Python will try calling `__repr__` on your class as a fallback.
So if you only implement one of these two special methods, it would be better to create a `__repr__` rather than just a `__str__`.

[ISO 8601]: https://www.iso.org/iso-8601-date-and-time-format.html
[REPL]: https://pythonprogramminglanguage.com/repl/
[classes in python]: https://docs.python.org/3/tutorial/classes.html
[datetime]: https://docs.python.org/3/library/datetime.html#available-types
[dunder-methods]: https://www.pythonmorsels.com/every-dunder-method/
[eval-built-in]: https://docs.python.org/3/library/functions.html#eval
[repr-docs]: https://docs.python.org/3/reference/datamodel.html#object.__repr__
[repr-method]: https://docs.python.org/3/library/functions.html#repr
[str-dunder]: https://docs.python.org/3/reference/datamodel.html#object.__str__
[str-rep-classes]: https://www.digitalocean.com/community/tutorials/python-str-repr-functions#introduction
[what-is-an-object]: https://realpython.com/ref/glossary/object/

## You get
Nothing to start — you return a **class**. The grader builds it as `Clock(hour, minute)`, e.g. `Clock(8, 0)`, `Clock(0, 1723)` or `Clock(-25, -160)`. Both arguments are plain `int`s, and either one may be out of range: negative, or far past `23` and `59`.

> [!NOTE]
> Exercism's stub is a `class Clock` in `clock.py`. Here the entry point is `solve()`, which takes **no arguments** and returns the class itself — not an instance.

## You return
The class. The grader uses it like this:

```python
Clock = solve()
str(Clock(8, 0))                # -> "08:00"
repr(Clock(6, 45))              # -> "Clock(6, 45)"
str(Clock(0, 45) + 160)         # -> "03:25"
str(Clock(10, 3) - 30)          # -> "09:33"
Clock(10, 37) == Clock(34, 37)  # -> True
```

| member | is | behaviour |
| --- | --- | --- |
| `.hour`, `.minute` | attributes | the normalised time: `0 <= hour < 24` and `0 <= minute < 60` |
| `__repr__` | special method | `Clock(<hour>, <minute>)` — valid Python that rebuilds this object |
| `__str__` | special method | `HH:MM`, each half zero-padded to two digits |
| `__eq__` | special method | two clocks showing the same time are equal |
| `__add__` | special method | `clock + minutes` — the time that many minutes later |
| `__sub__` | special method | `clock - minutes` — the time that many minutes earlier |

## Rules
- normalise in `__init__`, not in the methods that read the clock: after construction `.hour` and `.minute` are already in range, and every other method just reports them
- 60 minutes roll into an hour, 24 hours roll into nothing — the day has no "tomorrow" here, `Clock(24, 0)` is `00:00`
- negative numbers roll the same way, backwards: `Clock(-1, 15)` is `23:15`, and the size of the negative number does not matter, `Clock(-91, 0)` is `05:00`
- `repr()` shows the **normalised** numbers, unpadded, with a comma and a space: `Clock(72, 8640)` reprs as `Clock(0, 0)`
- `+` and `-` take a plain `int` of minutes and **return a new Clock**; the clock they were called on keeps the time it had

```python
Clock = solve()
str(Clock(25, 160))     # -> "03:40"
str(Clock(-25, -160))   # -> "20:20"
repr(Clock(72, 8640))   # -> "Clock(0, 0)"
str(Clock(23, 59) + 2)  # -> "00:01"
str(Clock(0, 3) - 4)    # -> "23:59"
```

> [!WARNING]
> The two string forms are compared character for character and they are not the same. `str()` pads — `08:00`, never `8:0`. `repr()` does not pad — `Clock(6, 45)`, with exactly one space after the comma.

> [!WARNING]
> The grader adds to a clock and then asks that clock for its own time again. If `+` edits `self` instead of building a new instance, that check fails even though every Exercism case still passes.

## Hints
### Hint 1
Two numbers go in, one canonical time comes out. Decide *where* that canonicalisation happens before you write anything else — if it happens once, in the constructor, then `__str__`, `__repr__` and `__eq__` have nothing left to do but report two in-range numbers, and `+`/`-` have nothing left to do but hand a new pair to the constructor.

### Hint 2
Every case in this task gets easier if you first collapse the pair into a single quantity: how many minutes past midnight is this? Splitting that one number back into an hour and a minute is a division and a remainder, and Python's integer division rounds *down* rather than toward zero — which is exactly why the negative cases need no special branch, provided you never call `abs()` or test for `< 0` along the way. The hour then wraps into the day with one more remainder. For display, reach for a format spec rather than string concatenation; for `+` and `-`, return a freshly built instance; for `==`, compare the two normalised pairs.

### Hint 3
Different data, same shape — a compass bearing that has to stay inside 0–359:

```python
class Bearing:
    def __init__(self, degrees):
        self.degrees = degrees % 360

    def __repr__(self):
        return f'Bearing({self.degrees})'

    def __eq__(self, other):
        return self.degrees == other.degrees

    def __add__(self, turn):
        return Bearing(self.degrees + turn)

Bearing(350) + 20             # -> Bearing(10)
Bearing(-90) == Bearing(270)  # -> True
```

Notice what `__add__` does *not* do: it never wraps anything itself and it never touches `self`. It adds, hands the raw total to the constructor, and lets the one piece of wrapping logic in the class do its job. Clock is this with two numbers instead of one.
