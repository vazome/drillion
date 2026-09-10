---
title: cooperative super() — two mixins that both get a turn at the key
difficulty: hard
tier: advanced
minutes: 25
prereqs: [57]
tags: [class-inheritance, classes]
source: fluentpython/example-code-2e 14-inheritance (MIT, adapted)
---
# cooperative super() — two mixins that both get a turn at the key

*`super()` does not mean "my parent". It means "whoever is next in this object's method resolution order", and that is decided by the class the object actually is.*

## Read first
- [`super()`](https://devdocs.io/python~3.14/library/functions#super) — what the no-argument form binds to, and why it needs the class it was written in
- [Method resolution order](https://devdocs.io/python~3.14/glossary#term-method-resolution-order) — the single order Python builds from the bases you listed
- [`collections.UserDict`](https://devdocs.io/python~3.14/library/collections#collections.UserDict) — a dict written in Python, so overriding its methods actually works

## Why
Feature-flag names reach the registry from three places: a YAML file somebody indented by hand, an environment variable, and an admin form. The YAML ones come with trailing spaces. The form ones come lower-case. `checkout_v2` and `CHECKOUT_V2 ` are the same flag, and the day they stop being the same flag is the day half the traffic gets the old checkout.

Two separate clean-ups, then, each of them a rule someone can read on its own: trim it, and upper-case it. Write them as one class and the next registry that only needs trimming has to take the upper-casing too. Write them as two, and the class that needs both says so by listing both — provided each one hands the key onward instead of finishing the job itself.

## You get
nothing to start — you return three classes. The test builds them itself, like

```python
Trimmed, Upper, Registry = solve()
flags = Registry()
flags["  checkout_v2 "] = True
```

## You return
a tuple of the three classes, in the order `(Trimmed, Upper, Registry)`.

## Rules
`Trimmed` and `Upper` are **mixins**: neither one has a base class, and neither one is a mapping on its own. Each defines the same three methods, and each does one thing to the key and then passes it on with `super()`:

- `__setitem__(self, key, item)`
- `__getitem__(self, key)`
- `__contains__(self, key)`

`Trimmed` strips whitespace from both ends of the key. `Upper` upper-cases it. A key that is not a string is passed on untouched by both.

`Registry` is the class that uses them: it inherits from `Trimmed`, `Upper` and `collections.UserDict`, in that order, and has an empty body. Every key that goes in or comes out is trimmed *and* upper-cased, in that order.

```python
Trimmed, Upper, Registry = solve()
flags = Registry()

flags["  checkout_v2 "] = True
list(flags)            # -> ['CHECKOUT_V2']
flags["checkout_v2"]   # -> True
" CHECKOUT_V2" in flags   # -> True
flags[7] = "numbered"  # a non-string key survives as itself
list(flags)            # -> ['CHECKOUT_V2', 7]
```

> [!WARNING]
> `UserDict.__setitem__(self, key, item)` from inside `Trimmed` looks like the same thing as `super().__setitem__(key, item)` and works perfectly while `Trimmed` is the only mixin. Add `Upper` and the trimmed key jumps straight past it: the flag goes in as `checkout_v2`, the lookup asks for `CHECKOUT_V2`, and nothing is found. The test mixes each one in on its own as well as together, so the shortcut is visible.

> [!NOTE]
> A mixin's `super()` has no parent to point at — `Trimmed` inherits from nothing. It resolves against the MRO of whatever class is being used, which is why the same `Trimmed` works above `Upper` here and directly above `UserDict` elsewhere.

## Hints
### Hint 1
`Registry.__mro__` is `(Registry, Trimmed, Upper, UserDict, ...)`. Python built that list from `class Registry(Trimmed, Upper, UserDict)`, and every `super()` call inside any of those methods steps one place along it.
### Hint 2
Each method is one line: change the key, then `return super().__getitem__(new_key)`. Do not touch the item, and do not touch `self.data` — that is `UserDict`'s, and reaching into it directly is the same shortcut as naming `UserDict` directly.
### Hint 3
Same shape, different rule:

```python
import collections

class Prefixed:
    def __setitem__(self, key, item):
        super().__setitem__(f"app.{key}", item)

    def __getitem__(self, key):
        return super().__getitem__(f"app.{key}")

class Settings(Prefixed, collections.UserDict):
    pass

s = Settings()
s["debug"] = True
list(s)      # -> ['app.debug']
s["debug"]   # -> True
```

`Prefixed` names no base and works over `UserDict` here. Put another mixin between the two and it keeps working, because it never said who came next.

---
Adapted from fluentpython/example-code-2e — MIT
