---
title: enums — an enum that classifies, not just names
difficulty: medium
tier: core
minutes: 12
prereqs: [11, 38]
tags: [enums]
source: exercism/python practice/perfect-numbers (MIT, adapted)
---
# enums — an enum that classifies, not just names

*An enum member is an object, so the rule that picks it can live on the enum itself.*

## Read first
- [enum](https://devdocs.io/python~3.14/library/enum) — `Enum`, member values, and the fact that members are instances of their class
- [classmethod](https://devdocs.io/python~3.14/library/functions#classmethod) — a method that gets the class, which is what a factory on an enum needs

## Why
Nicomachus sorted every number into three kinds by comparing it with the sum of the numbers that divide it. Your code has the same shape whenever it labels something: a disk is healthy, filling or full; a payment is settled, pending or failed. The label is a small closed set, so it wants to be an enum. What usually goes wrong is that the enum names the three states and the rule that picks between them ends up somewhere else, in an `if` chain in a different file, so a fourth state can be added to one and not the other. An enum is a class, so the rule can live on it.

## You get
`n` — a positive whole number, like `6` or `28`. The test creates it and hands it to you; you never build it yourself.

## You return
the enum class itself, not a classification. `solve()` takes no arguments.

## Rules
Return an `Enum` named `Kind` with exactly three members and a classifier on it.

The members, with these names and these values:

| member | value | when |
| --- | --- | --- |
| `PERFECT` | `"perfect"` | the divisors add up to `n` |
| `ABUNDANT` | `"abundant"` | they add up to more than `n` |
| `DEFICIENT` | `"deficient"` | they add up to less than `n` |

The divisors are the whole numbers below `n` that divide it exactly, so `1` counts and `n` does not. For `6` they are `1, 2, 3`, which add up to `6`.

`Kind` must also carry a classifier reached from the class:

```python
Kind = solve()
Kind.of(6)        # -> Kind.PERFECT
Kind.of(12)       # -> Kind.ABUNDANT
Kind.of(13).value # -> "deficient"
list(Kind)        # -> [Kind.PERFECT, Kind.ABUNDANT, Kind.DEFICIENT]
```

`Kind.of(n)` is called with `n >= 1`. `1` has no divisors below it, so the sum is `0` and it is deficient.

> [!WARNING]
> Order matters here in a way it does not in most enums: `list(Kind)` must give perfect, abundant, deficient, in that order, because that is the order they are written in the class body.

## Hints
### Hint 1
Two halves. The enum is three lines, the same shape as any other enum with string values. The classifier is one method that adds up the divisors and returns one of the three members. Put the method inside the class body, below the members, and it belongs to the enum the same way any method belongs to its class.
### Hint 2
The method needs the class, not a member, because it is called as `Kind.of(...)` before any member is chosen. That is what `@classmethod` is for: the first parameter is the class, and inside the method `cls.PERFECT` is the member. Adding up the divisors is one `sum` over a range that stops at `n`, keeping the values that divide `n` exactly.
### Hint 3
Different data — a status enum that decides its own member from a percentage:

```python
from enum import Enum

class Disk(Enum):
    HEALTHY = "healthy"
    FILLING = "filling"
    FULL = "full"

    @classmethod
    def of(cls, percent):
        if percent >= 100:
            return cls.FULL
        return cls.FILLING if percent >= 80 else cls.HEALTHY

print(Disk.of(91))          # Disk.FILLING
print(Disk.of(91).value)    # 'filling'
print(list(Disk))           # [<Disk.HEALTHY: 'healthy'>, ...] — class-body order
```

The divisor sum is the only arithmetic here: `sum(d for d in range(1, n) if n % d == 0)`.
