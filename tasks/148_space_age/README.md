---
title: dicts — your age in years on any planet
difficulty: medium
tier: core
minutes: 10
prereqs: [106]
tags: [dicts]
source: exercism/python practice/space-age (MIT, adapted)
---
# dicts — your age in years on any planet

*space-age — one stored value, eight views of it, and a table instead of eight copies of the same formula.*

## Read first
- [A first look at classes](https://docs.python.org/3/tutorial/classes.html#a-first-look-at-classes) — `__init__`, `self`, and what a method actually is
- [Mapping types: dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict) — the natural home for eight planet-to-period constants
- [round()](https://docs.python.org/3/library/functions.html#round) — the second argument is the number of decimal places
- [Floating point arithmetic: issues and limitations](https://docs.python.org/3/tutorial/floatingpoint.html) — why you round once at the end rather than as you go

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A duration is stored once, in one unit — seconds, or milliseconds since the epoch — and then every screen wants it in a different one: minutes for the SLA report, days for the retention policy, business quarters for finance. The moment you write the conversion out by hand for the third time, one of the constants is wrong and nobody notices for a year. This task is that problem in fancy dress: eight conversions, one stored number, and eight constants that belong in a table rather than sprinkled through eight function bodies. The other half is the object: a small class that holds the raw value and answers questions about it, which is the cheapest useful class there is.

## Introduction
The year is 2525 and you've just embarked on a journey to visit all planets in the Solar System (Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus and Neptune).
The first stop is Mercury, where customs require you to fill out a form (bureaucracy is apparently _not_ Earth-specific).
As you hand over the form to the customs officer, they scrutinize it and frown.
"Do you _really_ expect me to believe you're just 50 years old?
You must be closer to 200 years old!"

Amused, you wait for the customs officer to start laughing, but they appear to be dead serious.
You realize that you've entered your age in _Earth years_, but the officer expected it in _Mercury years_!
As Mercury's orbital period around the sun is significantly shorter than Earth, you're actually a lot older in Mercury years.
After some quick calculations, you're able to provide your age in Mercury Years.
The customs officer smiles, satisfied, and waves you through.
You make a mental note to pre-calculate your planet-specific age _before_ future customs checks, to avoid such mix-ups.

> [!NOTE]
> If you're wondering why Pluto didn't make the cut, go watch [this YouTube video][pluto-video].
>
> [pluto-video]: https://www.youtube.com/watch?v=Z_2gbGXzFbs

## Instructions
Given an age in seconds, calculate how old someone would be on a planet in our Solar System.

One Earth year equals 365.25 Earth days, or 31,557,600 seconds.
If you were told someone was 1,000,000,000 seconds old, their age would be 31.69 Earth-years.

For the other planets, you have to account for their orbital period in Earth Years:

| Planet  | Orbital period in Earth Years |
| ------- | ----------------------------- |
| Mercury | 0.2408467                     |
| Venus   | 0.61519726                    |
| Earth   | 1.0                           |
| Mars    | 1.8808158                     |
| Jupiter | 11.862615                     |
| Saturn  | 29.447498                     |
| Uranus  | 84.016846                     |
| Neptune | 164.79132                     |

> [!NOTE]
> The actual length of one complete orbit of the Earth around the sun is closer to 365.256 days (1 sidereal year).
> The Gregorian calendar has, on average, 365.2425 days.
> While not entirely accurate, 365.25 is the value used in this exercise.
> See [Year on Wikipedia][year] for more ways to measure a year.
>
> [year]: https://en.wikipedia.org/wiki/Year#Summary

For the Python track, this exercise asks you to create a `SpaceAge` _class_ (_[concept:python/classes]()_) that includes methods for all the planets of the solar system.
Methods should follow the naming convention `on_<planet name>`.

Each method should `return` the age (_"on" that planet_) in years, rounded to two decimal places:

```python
#creating an instance with one billion seconds, and calling .on_earth().
>>> SpaceAge(1000000000).on_earth()

#This is one billion seconds on Earth in years
31.69
```

For more information on constructing and using classes, see:

-   [**A First Look at Classes**][first look at classes] from the Python documentation.
-   [**A Word About names and Objects**][names and objects] from the Python documentation.
-   [**Objects, values, and types**][objects, values and types] in the Python data model documentation.
-   [**What is a Class?**][what is a class] from Trey Hunners Python Morsels website.

[first look at classes]: https://docs.python.org/3/tutorial/classes.html#a-first-look-at-classes
[names and objects]: https://docs.python.org/3/tutorial/classes.html#a-word-about-names-and-objects
[objects, values and types]: https://docs.python.org/3/reference/datamodel.html#objects-values-and-types
[what is a class]: https://www.pythonmorsels.com/what-is-a-class/

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
