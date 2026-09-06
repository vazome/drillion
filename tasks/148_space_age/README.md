---
title: dicts — your age in years on any planet
difficulty: medium
tier: core
minutes: 10
prereqs: [25]
tags: [dicts]
source: exercism/python practice/space-age (MIT, adapted)
---
# dicts — your age in years on any planet

*space-age — one stored value, eight views of it, and a table instead of eight copies of the same formula.*

## Read first
- [A first look at classes](https://devdocs.io/python~3.14/tutorial/classes#a-first-look-at-classes) — `__init__`, `self`, and what a method actually is
- [Mapping types: dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — the natural home for eight planet-to-period constants
- [round()](https://devdocs.io/python~3.14/library/functions#round) — the second argument is the number of decimal places
- [Floating point arithmetic: issues and limitations](https://devdocs.io/python~3.14/tutorial/floatingpoint) — why you round once at the end rather than as you go

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A duration is stored once, in one unit — seconds, or milliseconds since the epoch — and then every screen wants it in a different one: minutes for the SLA report, days for the retention policy, business quarters for finance. The moment you write the conversion out by hand for the third time, one of the constants is wrong and nobody notices for a year. This task is that problem in fancy dress: eight conversions, one stored number, and eight constants that belong in a table rather than sprinkled through eight function bodies. The other half is the object: a small class that holds the raw value and answers questions about it, which is the cheapest useful class there is.

## You get
Nothing to start — you return a **class**. The grader builds it as `SpaceAge(seconds)`, where `seconds` is an age in seconds, e.g. `1000000000`.

> [!NOTE]
> Exercism's stub is a `class SpaceAge` in `space_age.py`. Here the entry point is `solve()`, which takes **no arguments** and returns the class itself — not an instance.

## You return
The class. The grader uses it like this:

```python
SpaceAge = solve()
age = SpaceAge(1000000000)
age.on_earth()    # -> 31.69
age.on_mercury()  # -> 131.57
age.on_neptune()  # -> 0.19
```

| member | is | value |
| --- | --- | --- |
| `.seconds` | attribute | the number the object was built with, unchanged |
| `.on_mercury()` … `.on_neptune()` | methods, one per planet | the age on that planet in that planet's years, a `float` rounded to 2 decimal places |

All eight methods must exist: `on_mercury`, `on_venus`, `on_earth`, `on_mars`, `on_jupiter`, `on_saturn`, `on_uranus`, `on_neptune`.

## Rules
- one Earth year is `31557600` seconds, and a planet's year is that many seconds multiplied by its orbital period from the table above
- each method returns `round(self.seconds / (31557600 * period), 2)` for its own planet's period
- the answer is a `float` rounded to two decimal places — round once, at the end, and do not format it as a string
- the object keeps the raw seconds it was given; nothing is converted in `__init__`

```python
SpaceAge = solve()
SpaceAge(2134835688).on_mercury()  # -> 280.88
SpaceAge(189839836).on_venus()     # -> 9.78
SpaceAge(2000000000).on_saturn()   # -> 2.15
SpaceAge(1821023456).on_neptune()  # -> 0.35
```

> [!WARNING]
> Eight methods that each repeat the same division is eight chances to mistype a constant. Put the periods in one dict or one table of class attributes; the grader does not care how you build the methods, only that all eight exist and answer correctly.

## Hints
### Hint 1
Write `on_earth` first and get `1000000000` to come out as `31.69`. Once one planet works, the other seven differ by a single number, so the real question becomes where that number should live: eight copies of the same three lines, or one table plus a way to reach it.

### Hint 2
The class needs almost nothing: `__init__` stores the seconds it is handed, and that is the whole state. Then decide how the eight methods get made. The plain route is a dict of planet name to orbital period as a class-level constant, one small helper method that does the arithmetic for a named planet, and eight one-line methods that each call it with their own name — repetitive, but obvious and easy to read. If you want to go further, note that a function that builds and returns a function lets you assign all eight as class attributes without writing eight bodies. Either way, the arithmetic itself appears exactly once.

### Hint 3
Different data, same one-value-many-views class — a duration held in seconds and read out in whatever unit the caller wants:

```python
class Duration:
    UNITS = {'minutes': 60, 'hours': 3600, 'days': 86400}

    def __init__(self, seconds):
        self.seconds = seconds

    def _as(self, unit):
        return round(self.seconds / self.UNITS[unit], 2)

    def in_minutes(self):
        return self._as('minutes')

    def in_hours(self):
        return self._as('hours')

Duration(9000).in_minutes()   # -> 150.0
Duration(9000).in_hours()     # -> 2.5
```

The constants sit in one dict, the conversion is written once in `_as`, and each public method is a one-line label on top of it. Swap "unit" for "planet" and the shape carries straight over.
