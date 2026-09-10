---
title: descriptors — one validating field, reused by every attribute that needs it
difficulty: hard
tier: advanced
minutes: 25
prereqs: [57]
tags: [class-customization, classes]
source: fluentpython/example-code-2e 23-descriptor (MIT, adapted)
---
# descriptors — one validating field, reused by every attribute that needs it

*A descriptor is a class that says what happens when an attribute is read and written, so the rule lives in one place instead of in every setter.*

## Read first
- [Descriptor HowTo](https://devdocs.io/python~3.14/howto/descriptor) — `__get__` and `__set__`, and when Python calls them
- [`__set_name__`](https://devdocs.io/python~3.14/reference/datamodel#object.__set_name__) — how a descriptor learns which attribute it was assigned to
- [Instance `__dict__`](https://devdocs.io/python~3.14/library/stdtypes#object.__dict__) — where a per-object value actually lives

## Why
An order line has a weight and a price, and neither one is allowed to be zero or negative. Written the obvious way that is two `@property` pairs with the same four lines of checking in both, and the third quantity somebody adds next quarter is a third copy. Copies drift: one of them ends up rejecting zero and another one allowing it, and the invoice that comes out wrong is the one nobody can explain. A descriptor is that rule written once as a class, and `weight = Quantity()` is how an attribute opts into it.

## You get
nothing to start — you return classes. The test builds them itself, like

```python
Quantity, LineItem = solve()
LineItem("oak plank", 12, 3.5).subtotal()
```

## You return
a tuple of the two classes, in the order `(Quantity, LineItem)`.

## Rules
`Quantity` is the descriptor:

- `__set_name__(self, owner, name)` is called for you when the class body runs, once per attribute it was assigned to. Keep the `name`; it is how this descriptor knows whether it is the weight or the price.
- `__get__(self, instance, owner=None)` returns the value stored on that instance. When `instance` is `None` the attribute was read on the class rather than an object, and you return the descriptor itself.
- `__set__(self, instance, value)` raises `ValueError` when `value` is not greater than zero, and otherwise stores it in `instance.__dict__` under the name `__set_name__` gave you.

`LineItem` uses it twice:

- `weight = Quantity()` and `price = Quantity()` in the class body, one instance each.
- `__init__(self, description, weight, price)` assigns all three plainly. The two that are quantities go through the descriptor because of what is in the class body, not because `__init__` does anything special.
- `subtotal(self)` returns weight times price.

```python
Quantity, LineItem = solve()
item = LineItem("oak plank", 12, 3.5)
item.subtotal()          # -> 42.0
item.weight = 0          # -> ValueError
LineItem("bolt", 3, -1)  # -> ValueError
```

> [!WARNING]
> Storing the value under one fixed name makes `weight` and `price` the same slot, and setting one silently overwrites the other. The test sets `weight` and then reads `price`, so a hard-coded storage name fails even though every validation passes.

> [!NOTE]
> `instance.__dict__[name]` rather than `setattr(instance, name, value)`. `setattr` goes back through the descriptor, which calls `__set__`, which calls `setattr`, until Python gives up.

## Hints
### Hint 1
Two `Quantity()` instances are created when the class body runs, and Python calls `__set_name__` on each of them with the name it was bound to. That is the only chance to learn it, so store it on `self`.
### Hint 2
The instance dictionary is a plain dict, and a descriptor that defines `__set__` is consulted before it. So `instance.__dict__[self._name] = value` puts the value somewhere `__get__` can find it without either of them looping.
### Hint 3
Same shape, different rule:

```python
class NonEmpty:
    def __set_name__(self, owner, name):
        self._name = name
    def __get__(self, instance, owner=None):
        return self if instance is None else instance.__dict__[self._name]
    def __set__(self, instance, value):
        if not value:
            raise ValueError(f"{self._name} must not be empty")
        instance.__dict__[self._name] = value

class User:
    name = NonEmpty()
    email = NonEmpty()
    def __init__(self, name, email):
        self.name, self.email = name, email

User("ada", "")   # ValueError: email must not be empty
```

`name` and `email` share one class and keep separate values, because `__set_name__` told each descriptor which key to use.

---
Adapted from fluentpython/example-code-2e — MIT
