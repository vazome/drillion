---
title: typing.Protocol — a total that accepts anything shaped like a charge
difficulty: medium
tier: advanced
minutes: 18
prereqs: [57, 203]
tags: [type-hints, classes]
---
# typing.Protocol — a total that accepts anything shaped like a charge

*A `Protocol` says what an object must be able to do, not what it must inherit from, and `@runtime_checkable` lets `isinstance` ask that question at run time.*

## Read first
- [`typing.Protocol`](https://devdocs.io/python~3.14/library/typing#typing.Protocol) — declaring a structural type
- [`typing.runtime_checkable`](https://devdocs.io/python~3.14/library/typing#typing.runtime_checkable) — what it adds, and what it deliberately does not check
- [`isinstance`](https://devdocs.io/python~3.14/library/functions#isinstance) — the ordinary function a protocol quietly teaches a new trick

## Why
Billing adds up whatever the other teams hand it: subscriptions from one service, one-off fees from another, a bundle object a contractor wrote last year. They have nothing in common except that each one can tell you what it costs. Make them all inherit from a `Charge` base class and every team has to import yours, ship a release, and agree on where it lives — for a method they already wrote. Some of them will never do it, and their line quietly falls off the invoice.

A protocol turns that around. Billing states the shape it needs, once, and anything already that shape qualifies without knowing billing exists. Nothing to import, nothing to coordinate, and the objects that are *not* charges — a coupon, a note, an address — are still told apart from the ones that are.

## You get
nothing to start — you return a class and a function. The test builds its own objects, like

```python
Charged, total_due = solve()
total_due([subscription, coupon, one_off])
```

## You return
a tuple of `(Charged, total_due)`.

## Rules
- `Charged` is a `typing.Protocol` with one method, `amount_due(self) -> float`, and a body of `...`. It is a declaration; it never runs.
- `Charged` is decorated `@runtime_checkable`, so `isinstance(obj, Charged)` works.
- `total_due(items)` walks the list and adds up `item.amount_due()` for every item that **is** a `Charged`, skipping the rest. Return the total rounded to 2 decimal places.
- An empty list, or a list with nothing chargeable in it, totals `0.0`.

```python
Charged, total_due = solve()

class Subscription:          # never heard of Charged
    def amount_due(self): return 12.50

class Coupon:                # not a charge: no amount_due
    code = "WELCOME"

isinstance(Subscription(), Charged)   # -> True
isinstance(Coupon(), Charged)         # -> False
total_due([Subscription(), Coupon(), Subscription()])   # -> 25.0
```

> [!WARNING]
> An abstract base class passes every example you write yourself, because your own classes inherit from it. It fails the moment a class you did not write shows up: `isinstance` says no, its line is skipped, and the invoice is short. The test defines its charge classes without ever mentioning `Charged`.

> [!NOTE]
> Without `@runtime_checkable`, `isinstance(obj, Charged)` does not return `False` — it raises `TypeError`. The decorator is what makes the check legal at all.

## Hints
### Hint 1
`class Charged(Protocol):` with `def amount_due(self) -> float: ...` is the whole declaration. The `...` is the body; there is nothing to implement, because no `Charged` object is ever created.
### Hint 2
`@runtime_checkable` goes above `class Charged(Protocol):`. It checks that the named methods exist, and nothing about their signatures or what they return — that part is the type checker's job, not `isinstance`'s.
### Hint 3
Same shape, different rule:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closable(Protocol):
    def close(self) -> None: ...

def shut_down(resources):
    return [r for r in resources if isinstance(r, Closable) and r.close() is None]
```

A socket, a file and a database pool all qualify, and none of them imports `Closable`. A plain string does not, and is passed over instead of blowing up.
