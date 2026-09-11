---
title: __hash__ with __eq__ — a value object you can use as a dict key
difficulty: medium
tier: advanced
minutes: 20
prereqs: [57]
tags: [comparisons, classes]
---
# __hash__ with __eq__ — a value object you can use as a dict key

*Defining `__eq__` makes a class unhashable until you define `__hash__` too, and the two must agree or a set will hold the same value twice.*

## Read first
- [`__hash__`](https://devdocs.io/python~3.14/reference/datamodel#object.__hash__) — the rule that equal objects must hash equal, and what defining `__eq__` alone does to it
- [`__eq__`](https://devdocs.io/python~3.14/reference/datamodel#object.__eq__) — and why returning `NotImplemented` beats returning `False`
- [`hash()`](https://devdocs.io/python~3.14/library/functions#hash) — hashing a tuple of already-hashable things
- [`property`](https://devdocs.io/python~3.14/library/functions#property) — a read-only attribute

## Why
An on-call pager gets the same alert from four regions in one minute, and the operator should see it once. The natural way to say "same alert" is a small object holding the service and the error code, and the natural way to collapse duplicates is to drop those objects into a set.

That is where an ordinary class lets you down. Two separately built alert keys with identical fields are different objects, so a set keeps both and the pager fires four times. Teaching the class what equality means fixes the comparison and breaks the set entirely, because Python withdraws hashing from any class that redefines `__eq__` and says nothing further about it. The pair has to be written together, from the same fields, and the fields have to stop changing — a key whose hash moves after it is filed is a key that can never be found again.

## You get
nothing to start — you return a class. The test builds it itself, like

```python
AlertKey = solve()
{AlertKey("billing", 503), AlertKey("billing", 503)}
```

## You return
the class `AlertKey`.

## Rules
- `__init__(self, service, code)` takes a string and an integer and keeps both privately.
- `service` and `code` are readable as attributes and cannot be reassigned — `key.code = 500` raises `AttributeError`.
- `__eq__(self, other)` is `True` when `other` is an `AlertKey` with the same service and code. For anything else return `NotImplemented`, so `key == "billing"` comes out `False` instead of raising.
- `__hash__(self)` is built from the same two fields, so two equal keys always hash the same.
- `__repr__(self)` returns `AlertKey('billing', 503)`.

```python
AlertKey = solve()
a, b = AlertKey("billing", 503), AlertKey("billing", 503)
a == b                       # -> True
a is b                       # -> False
len({a, b})                  # -> 1
{a: "paged"}[b]              # -> 'paged'
a == AlertKey("search", 503) # -> False
a.code = 500                 # -> AttributeError
```

> [!WARNING]
> A class that defines `__eq__` and stops there is not merely missing a feature — `hash(key)` raises `TypeError`, and so does putting one in a set. That is Python protecting you from the worse bug, and it is the first thing the test checks.

> [!NOTE]
> Deriving the hash from the same fields as the comparison is not a style preference. Two objects that compare equal but hash differently land in different buckets, and a dict will happily hold both, which is exactly the duplicate the set was meant to remove.

## Hints
### Hint 1
Two leading underscores on an attribute name inside a class body get mangled, so `self.__code` becomes `self._AlertKey__code` and is awkward to reach from outside by accident. Pair it with a `@property` named `code` that just returns it, and the value is readable and not assignable.
### Hint 2
`hash()` already knows how to hash a tuple of hashable things, so the whole method is `return hash((self.service, self.code))` — the same two values the comparison uses, in the same order.
### Hint 3
The shape, in full, on one field:

```python
class Tag:
    def __init__(self, name):
        self.__name = name
    @property
    def name(self):
        return self.__name
    def __eq__(self, other):
        if isinstance(other, Tag):
            return self.name == other.name
        return NotImplemented
    def __hash__(self):
        return hash(self.name)

len({Tag("db"), Tag("db")})   # 1
Tag("db").name = "web"        # AttributeError: property 'name' has no setter
```
