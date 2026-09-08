---
title: dataclasses — a frozen coordinate that validates itself
difficulty: medium
tier: core
minutes: 14
prereqs: [58, 160]
tags: [dataclasses]
source: exercism/python practice/queen-attack (MIT, adapted)
---
# dataclasses — a frozen coordinate that validates itself

*Two numbers that belong together, compared by value, checked once, and never edited afterwards.*

## Read first
- [dataclasses](https://devdocs.io/python~3.14/library/dataclasses) — `@dataclass`, `frozen=True`, and `__post_init__`
- [dataclasses.FrozenInstanceError](https://devdocs.io/python~3.14/library/dataclasses#dataclasses.FrozenInstanceError) — what assigning to a frozen field raises

## Why
A square on a chess board is two numbers that only mean anything together, and a tuple loses that the moment it is passed anywhere: nothing stops `(row, column)` being read as `(column, row)`, nothing rejects row 19, and nothing stops one half being reassigned halfway through a calculation. The same is true of the pairs your own code carries around — a latitude and a longitude, a page and an offset. Task 58 built a record. This one builds a **value**: it is equal to another by what it holds, it refuses to exist in an invalid state, and once made it cannot be changed.

## You get
nothing. `solve()` takes no arguments.

## You return
the class itself, so the test can make positions from it.

## Rules
Return a class named `Position` that is:

- a **dataclass** with exactly two fields, `row` then `column`, in that order and positional
- **frozen**, so `p.row = 4` raises rather than working
- self-checking: a row or column outside `0` to `7` raises `ValueError` when the position is made, not later

and that carries one method:

- `p.can_attack(other)` — `True` when a queen on `p` could take a queen on `other` in one move, `False` otherwise

A queen moves any distance along a row, a column, or a diagonal. A position never attacks itself.

```python
Position = solve()
a, b = Position(2, 3), Position(2, 7)
a.can_attack(b)                 # -> True   (same row)
a.can_attack(Position(5, 6))    # -> True   (diagonal: 3 down, 3 across)
a.can_attack(Position(4, 7))    # -> False
a == Position(2, 3)             # -> True   (equal by value, not identity)
Position(2, 3) == a             # the same object as far as a set or a dict key is concerned
Position(8, 0)                  # -> ValueError
```

> [!WARNING]
> Two squares on the same diagonal are the ones where the row gap and the column gap are equal in size. Compare the sizes, not the signed differences, or the two diagonals that run the other way stop counting.

## Hints
### Hint 1
The whole class is a decorator, two annotated names, one validating method and one attacking method. `@dataclass(frozen=True)` writes `__init__`, `__repr__`, `__eq__` and `__hash__` for you, so nothing about equality is yours to write. The two things left are where the validation goes, and what "same diagonal" means arithmetically.
### Hint 2
Validation belongs in `__post_init__`, which a dataclass calls at the end of the generated `__init__`. That is exactly the moment a bad value has to be refused. Attacking is three comparisons joined by `or`: same row, same column, or `abs(self.row - other.row) == abs(self.column - other.column)`.
### Hint 3
Different data — a frozen grid reference with the same three pieces:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Cell:
    x: int
    y: int

    def __post_init__(self):
        if not (0 <= self.x <= 9 and 0 <= self.y <= 9):
            raise ValueError("off the grid")

    def touches(self, other):
        return abs(self.x - other.x) <= 1 and abs(self.y - other.y) <= 1

print(Cell(1, 1) == Cell(1, 1))       # True — equal by value
print(len({Cell(1, 1), Cell(1, 1)}))  # 1 — frozen means hashable
Cell(1, 1).x = 5                      # FrozenInstanceError
```

`__post_init__` takes no extra arguments here, only `self`.
