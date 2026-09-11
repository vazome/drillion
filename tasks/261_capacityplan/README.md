---
title: binary search on the answer — the smallest worker that still finishes by morning
difficulty: hard
tier: advanced
minutes: 20
prereqs: [20, 171]
tags: [while, numbers]
---
# binary search on the answer — the smallest worker that still finishes by morning

*When you cannot compute the answer directly but you can test any guess, halve the range of guesses instead of the list.*

## Read first
- [The `while` statement](https://devdocs.io/python~3.14/reference/compound_stmts#the-while-statement) — two bounds closing in on each other, exactly as in a list search
- [`math.ceil`](https://devdocs.io/python~3.14/library/math#math.ceil) — and why `-(-a // b)` says the same thing without leaving the integers
- [Floor division `//`](https://devdocs.io/python~3.14/library/stdtypes#numeric-types-int-float-complex) — what it does to a partial hour, and why that is the wrong way to round here
- [`max`](https://devdocs.io/python~3.14/library/functions#max) — the top of the range you are searching

## Why
The nightly import arrives as a set of files and has to be finished before the business day starts. You size the import worker by how many rows an hour it can push, and that size is what you are paying for: a bigger instance finishes sooner and costs more every night, for ever. So the question finance keeps asking is the smallest one that still makes the window.

There is no formula for it. But there is something almost as good: given any proposed size, you can work out in one pass whether it makes the window. That is enough. The guesses are ordered — if a worker of a given size finishes in time then every bigger worker does too — so you can binary search the range of sizes the same way you binary search a sorted list, and the "is it there" test becomes "does it finish in time". Once you have seen this, half of capacity planning stops being a spreadsheet.

## You get
- `files` — a list of `int` row counts, one per file to import, each at least `1`, e.g. `[3, 6, 7, 11]`
- `hours` — an `int`, how many hours the import window is. It is always at least `len(files)`, so some capacity always works

## You return
An `int` — the smallest rows-per-hour capacity that finishes every file within `hours`.

## Rules
- the worker handles **one file per hour**: it never starts a second file in an hour it has already begun. So a file of `n` rows at capacity `c` occupies `ceil(n / c)` hours, and the total is the sum of those
- capacity is a whole number of rows per hour, and at least `1`
- return the smallest capacity whose total is `<= hours` — not the total, and not the file it belongs to
- halve the range of capacities. Trying `1`, `2`, `3`, … until one fits gives the right number and takes a million tries when the files are big

```python
solve([3, 6, 7, 11], 8)    # -> 4
solve([3, 6, 7, 11], 4)    # -> 11
solve([30, 11, 23, 4, 20], 5)   # -> 30
solve([12], 1)             # -> 12
```

> [!WARNING]
> `n // c` is the wrong rounding. A file of 7 rows at capacity 4 takes **two** hours, not one, because the three rows left over still need an hour of their own. Floor division reports every partial hour as free, so it always says a capacity fits when it does not, and hands back a worker that is one size too small and misses the window every night.

> [!NOTE]
> No capacity above `max(files)` ever helps: at that point every file already takes exactly one hour, and the total is `len(files)`. That is the top of the range, and `1` is the bottom.

## Hints
### Hint 1
Write the test first, on its own: given a capacity, how many hours does the whole import take? It is one `sum` over the files. Once that function exists, the search around it is the same loop you already know.
### Hint 2
The bounds are capacities, not indices, and the loop is the "leftmost that satisfies" shape: while `lo < hi`, take the midpoint; if that capacity fits, the answer is the midpoint **or something smaller**, so `hi = mid`; if it does not fit, `lo = mid + 1`. When the two meet you are standing on the answer.
### Hint 3
Ceiling division without leaving the integers, and the same search shape on a different question:

```python
def hours_needed(files, capacity):
    return sum(-(-n // capacity) for n in files)

lo, hi = 1, max(files)
while lo < hi:
    mid = (lo + hi) // 2
    if hours_needed(files, mid) <= hours:
        hi = mid
    else:
        lo = mid + 1
```

Never `hi = mid - 1` here: `mid` is still a candidate at the moment you learn it fits.
