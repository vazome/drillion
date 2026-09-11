---
title: prefix sums — thousands of range totals over one series of readings
difficulty: medium
tier: core
minutes: 15
prereqs: [140, 197]
tags: [itertools, numbers]
---
# prefix sums — thousands of range totals over one series of readings

*One running total, computed once, turns every "add up days 40 to 87" from a loop into a subtraction.*

## Read first
- [`itertools.accumulate`](https://devdocs.io/python~3.14/library/itertools#itertools.accumulate) — the running total of a sequence, already written
- [`sum`](https://devdocs.io/python~3.14/library/functions#sum) — what you are replacing, and what to check yourself against on a small input
- [List comprehensions](https://devdocs.io/python~3.14/tutorial/datastructures#list-comprehensions) — one line once the table is built
- [Unpacking in a for](https://devdocs.io/python~3.14/reference/compound_stmts#the-for-statement) — `for first, last in ranges` reads better than two subscripts

## Why
A tenant's electricity meter gives you one number per day. Billing then asks for totals over ranges that have nothing to do with each other: the calendar month, the tenancy that started mid-month, the two weeks the landlord is disputing, the quarter for the tax return. One page of an invoice run asks a few thousand of these against the same series of readings.

Summing the slice each time re-reads the same days over and over, and the cost is the number of ranges multiplied by how long they are, which is exactly the shape that turns a report into a timeout once a customer has a few years of history. Add up the series **once** into a table of running totals, and any range becomes one subtraction: everything up to the last day, minus everything before the first. The series is read once no matter how many ranges you are asked about.

## You get
- `readings` — a list of `int`, one reading per day, in order. It may be empty.
- `ranges` — a list of `(first, last)` tuples of day indexes, **both ends included**. Each one satisfies `0 <= first <= last < len(readings)`. It may be empty, and ranges may repeat and overlap freely.

## You return
A `list` of `int`, one total per range, in the order the ranges were given.

## Rules
- both ends are **inclusive**. `(2, 4)` is days 2, 3 and 4 — three readings, not two
- a range of one day is legal: `(5, 5)` is `readings[5]`
- the full range `(0, len(readings) - 1)` is the total of everything
- readings may be zero or negative — a credit, an export meter, a correction — so you cannot lean on totals only ever growing
- build the running totals **once**, before you look at any range. A `sum(readings[first:last + 1])` per range gives the right answers and is the thing this task exists to replace
- `readings` comes back untouched

```python
solve([3, 1, 4, 1, 5], [(0, 1), (2, 4), (3, 3), (0, 4)])
# -> [4, 10, 1, 14]
solve([], [])        # -> []
solve([7], [(0, 0)]) # -> [7]
```

> [!WARNING]
> With running totals in a list, `table[last] - table[first]` is the trap, and it is the one submission this task sees most. It drops the reading on day `first` — so `(3, 3)` comes back as `0` instead of `readings[3]`, and every multi-day range is short by exactly its own first day. The fix is to decide once what `table[i]` means, write it down, and be strict about it.

> [!NOTE]
> The tidiest convention is a table one entry **longer** than the series, where `table[i]` is the total of the first `i` readings — so `table[0]` is `0`, nothing is up to day zero. Then the inclusive range `(first, last)` is `table[last + 1] - table[first]`, and `first == 0` needs no special case.

## Hints
### Hint 1
Two steps, and they do not interleave. Step one builds a table from `readings` and never looks at `ranges`. Step two answers each range from the table and never looks at `readings`. If your code reads `readings` inside the loop over `ranges`, you are still doing the work you meant to hoist out.

### Hint 2
`itertools.accumulate(readings)` is the running total, but it starts at the first reading, which leaves you with no entry meaning "nothing yet" and so a special case for `first == 0`. `list(accumulate(readings, initial=0))` puts a leading `0` there and makes the table one longer than the series, which is what the note above is describing. Sanity-check it by hand on `[3, 1, 4]`: the table is `[0, 3, 4, 8]`, and `(1, 2)` is `8 - 3`, which is `5`.

### Hint 3
Same table, different question — the cumulative-to-date column of a running budget, and the burn between any two checkpoints:

```python
from itertools import accumulate

spend = [120, 0, 340, -50, 90]
table = list(accumulate(spend, initial=0))   # -> [0, 120, 120, 460, 410, 500]

between = lambda first, last: table[last + 1] - table[first]
between(0, 4)   # -> 500, everything
between(2, 3)   # -> 290, the big invoice and the refund against it
between(1, 1)   # -> 0, a day with no spend, not a missing day
```

The negative entry is worth staring at: the table stops rising there, which is why "find the day the total passed X" cannot be a binary search over this table unless you know the readings are all positive.
