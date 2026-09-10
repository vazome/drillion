---
title: __slots__ — a value class that refuses to grow a typo
difficulty: medium
tier: advanced
minutes: 18
prereqs: [57]
tags: [class-customization, classes]
source: fluentpython/example-code-2e 11-pythonic-obj (MIT, adapted)
---
# __slots__ — a value class that refuses to grow a typo

*`__slots__` fixes the attribute names a class may ever have, and takes the per-instance dictionary away.*

## Read first
- [`__slots__`](https://devdocs.io/python~3.14/reference/datamodel#object.__slots__) — what declaring it does, and what it costs
- [Instance `__dict__`](https://devdocs.io/python~3.14/library/stdtypes#object.__dict__) — the mapping a normal object carries, and that a slotted one does not
- [`hasattr()`](https://devdocs.io/python~3.14/library/functions#hasattr) — how to ask whether an attribute is there at all

## Why
A poller reads six million sensor rows a night and turns each one into an object. Two things go wrong at that size. The cheap one is memory: every ordinary instance carries its own dictionary, and six million dictionaries is most of the process. The expensive one is quieter. Somebody writes `reading.celcius = 21.5` in a hotfix, Python creates the misspelt attribute without complaint, and the correct one keeps its old value — so the alert never fires and the log shows nothing wrong. Declaring the attribute names up front takes both problems away at once: the dictionary is gone, and a name that was never declared is an error at the moment it is assigned rather than a silent second field.

## You get
nothing to start — you return classes. The test builds them itself, like

```python
Reading, Tagged = solve()
Reading("furnace-2", 21.5).celsius
```

## You return
a tuple of the two classes, in the order `(Reading, Tagged)`.

## Rules
`Reading` is the value class:

- `__slots__` names exactly `"celsius"` and `"sensor"`.
- `__init__(self, sensor, celsius)` assigns both, plainly.
- `__repr__(self)` returns `Reading('furnace-2', 21.5)` — the class name, then the two values as `repr` shows them.

`Tagged(Reading)` is a reading that also carries the unit it was read in:

- It inherits from `Reading`.
- `__slots__` names exactly `"unit"`. The two names the parent declared are not repeated.
- `__init__(self, sensor, celsius, unit)` calls the parent's `__init__` for the first two and assigns `unit`.

```python
Reading, Tagged = solve()
r = Reading("furnace-2", 21.5)
r.celsius            # -> 21.5
r.celcius = 22.0     # -> AttributeError
hasattr(r, "__dict__")   # -> False
Tagged("furnace-2", 21.5, "C").unit   # -> 'C'
```

> [!WARNING]
> A subclass that does not declare `__slots__` of its own gets a dictionary back, and with it every undeclared name the parent was refusing. The test checks `Tagged` has no `__dict__` either, so leaving its `__slots__` out fails even though every value is right.

> [!NOTE]
> Repeating `"sensor"` and `"celsius"` in `Tagged.__slots__` is not an error, but it allocates a second, shadowing slot for each and gives back the space the parent saved. Declare only what is new.

## Hints
### Hint 1
`__slots__` is a class attribute assigned in the class body, and a tuple of strings is the usual form: `__slots__ = ("celsius", "sensor")`. A single string is read as one name, so `__slots__ = "sensor"` is legal and probably not what you meant.
### Hint 2
Inheritance is where the saving is won or lost. Slots accumulate down the chain, so a subclass declares only the names it adds. If it declares nothing, Python gives that subclass a `__dict__`, and every instance of it can take any attribute again.
### Hint 3
The same shape, one field:

```python
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

class Labelled(Point):
    __slots__ = ("label",)
    def __init__(self, x, y, label):
        super().__init__(x, y)
        self.label = label

p = Labelled(1, 2, "start")
p.lable = "typo"   # AttributeError: 'Labelled' object has no attribute 'lable'
```

`Labelled` declares only `label`, and still cannot take a name outside the two lists.

---
Adapted from fluentpython/example-code-2e — MIT
