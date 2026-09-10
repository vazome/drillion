---
title: __repr__, __str__ and __format__ — one object, three renderings
difficulty: medium
tier: advanced
minutes: 22
prereqs: [57]
tags: [class-customization, string-formatting]
source: fluentpython/example-code-2e 11-pythonic-obj (MIT, adapted)
---
# __repr__, __str__ and __format__ — one object, three renderings

*`__repr__` is for the person debugging, `__str__` is for the person reading, and `__format__` is for the person who wants three decimal places.*

## Read first
- [`__repr__` and `__str__`](https://devdocs.io/python~3.14/reference/datamodel#object.__repr__) — which one Python reaches for, and what it falls back to
- [`__format__`](https://devdocs.io/python~3.14/reference/datamodel#object.__format__) — the hook behind `format()` and behind `{}` in an f-string
- [Format specification mini-language](https://devdocs.io/python~3.14/library/string#format-specification-mini-language) — what `.2f` and `.3e` mean before you extend them
- [`math.atan2`](https://devdocs.io/python~3.14/library/math#math.atan2) — the angle of a point, with the quadrant handled for you

## Why
A delivery drone reports where it is, and three different readers want that same pair of numbers. The console the dispatcher watches wants `(3.0, 4.0)` and nothing else. The incident log wants text a developer can paste straight back into a Python prompt to reproduce the state, so it wants `Point(3.0, 4.0)`. And the flight report wants two decimal places, or the distance-and-bearing form the pilots actually use.

Give a class one rendering and the other two get built by hand at every call site, each slightly differently, and the log ends up with a line nobody can turn back into an object. Python has a separate hook for each reader, and the third one takes a format spec you get to extend, so `f"{position:.2fp}"` can mean something specific to your type without anyone writing a helper.

## You get
nothing to start — you return a class. The test builds it itself, like

```python
Point = solve()
format(Point(1, 1), ".3ep")
```

## You return
the class `Point`.

## Rules
- `__init__(self, x, y)` stores both as `float`, on `self.x` and `self.y`.
- `__repr__(self)` returns `Point(3.0, 4.0)` — the class name and the two values as `repr` shows them.
- `__str__(self)` returns `(3.0, 4.0)` — what `str()` of the pair `(x, y)` gives you.
- `__format__(self, spec="")` renders the two numbers, each one through the standard spec, and wraps them:
  - a spec ending in `"p"` means polar: drop the `"p"`, and the two numbers become the distance from the origin and the angle in radians, wrapped as `<distance, angle>`.
  - any other spec means cartesian: the two numbers are `x` and `y`, wrapped as `(x, y)`.
  - whatever is left of the spec after a trailing `"p"` is removed goes to **each number separately**, not to the finished string.

```python
Point = solve()
p = Point(3, 4)
repr(p)              # -> 'Point(3.0, 4.0)'
str(p)               # -> '(3.0, 4.0)'
format(p)            # -> '(3.0, 4.0)'
format(p, ".2f")     # -> '(3.00, 4.00)'
format(p, ".3e")     # -> '(3.000e+00, 4.000e+00)'
format(Point(1, 1), ".3ep")   # -> '<1.414e+00, 7.854e-01>'
f"{p:.1f}"           # -> '(3.0, 4.0)'
```

> [!WARNING]
> The spec belongs to the components, not to the whole line. A `__format__` that renders the object to a string first and then applies the spec to that string looks right for the empty spec and gets `.2f` wrong immediately — `format` refuses `.2f` on text. The test checks `format(p, ".2f")` for exactly that.

> [!NOTE]
> Leaving `__str__` out is not an error: `str()` falls back to `__repr__`, so everything still prints. It prints the debugging form on the dispatcher's console, which is the failure the test looks for.

## Hints
### Hint 1
`format(value, spec)` is the same machinery as `f"{value:spec}"`, and on a `float` it is the standard mini-language. So `__format__` is mostly about choosing which two numbers and which brackets, then calling `format` on each number with what is left of the spec.
### Hint 2
Peel the suffix off first, then branch:

```python
def __format__(self, spec=""):
    if spec.endswith("p"):
        spec = spec[:-1]
        coords, outer = (self._radius(), self._angle()), "<{}, {}>"
    else:
        coords, outer = (self.x, self.y), "({}, {})"
    return outer.format(*(format(c, spec) for c in coords))
```
### Hint 3
The polar pair is `math.hypot(x, y)` for the distance and `math.atan2(y, x)` for the angle. `atan2` takes `y` first — that argument order is deliberate and is the usual place this goes wrong.

---
Adapted from fluentpython/example-code-2e — MIT
