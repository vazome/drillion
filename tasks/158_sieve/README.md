---
title: sets — find every prime up to a limit by crossing out multiples
difficulty: medium
tier: core
minutes: 20
prereqs: [32]
tags: [sets]
source: exercism/python practice/sieve (MIT, adapted)
---
# sets — find every prime up to a limit by crossing out multiples

*sieve — mark what cannot be, instead of testing what might be.*

## Read first
- [Sets](https://devdocs.io/python~3.14/tutorial/datastructures#sets) — a set of "already crossed out" numbers is one natural way to hold the marks
- [range() with a step](https://devdocs.io/python~3.14/library/stdtypes#range) — `range(p * p, limit + 1, p)` is every multiple of `p`, produced by addition
- [enumerate()](https://devdocs.io/python~3.14/library/functions#enumerate) — pairs a flag with the number it belongs to when you collect the survivors
- [Set difference](https://devdocs.io/python~3.14/library/stdtypes#frozenset.difference) — "everything from 2 to the limit, minus the crossed-out ones", in one expression

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
There are two ways to filter a big list: ask a question about every item, or mark the items you already know are out and keep the rest. The second is usually far cheaper, and it is the shape behind bloom filters, blocklists, bitmap indexes and "which of these million IDs have we already processed?". The Sieve of Eratosthenes is the oldest example of it — two thousand years old, still the fastest simple way to get all the primes below a limit — and it is short enough that you can feel exactly where the saving comes from.

## You get
`limit` — the largest number to consider, included:

```python
solve(10)
```

It may be as small as `0` or `1` (no primes at all) and as large as a few thousand.

> [!NOTE]
> Exercism's stub is `def primes(limit)`. Here the function is `solve(limit)`; nothing else about the task changes.

## You return
A `list` of `int` in ascending order — every prime `p` with `2 <= p <= limit`.

```python
solve(10)  # -> [2, 3, 5, 7]
solve(1)   # -> []
```

## Rules
- the limit is inclusive: `solve(13)` ends with `13`, because 13 is prime
- the result is ascending, with no duplicates, and it is a `list` — a set is not accepted, because a set has no order
- `limit` below 2 gives `[]`
- neither 0 nor 1 is ever in the result

```python
solve(1)   # -> []
solve(2)   # -> [2]
solve(13)  # -> [2, 3, 5, 7, 11, 13]
solve(30)  # -> [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

> [!WARNING]
> `solve(0)` and `solve(1)` must not blow up. A sieve that starts by writing `marked[0] = marked[1] = False` into a list sized `limit + 1` raises `IndexError` when `limit` is 0 — handle the small limits before you build anything.

## Hints
### Hint 1
Do the limit-10 example by hand with a pen: write 2 to 10 in a row and cross out as the instructions say. Notice what you are *not* doing — you never ask "is 9 divisible by anything?". You only ever cross out multiples of numbers you have already accepted. Decide how you will hold the marks: a set of crossed-out numbers, or a list of booleans indexed by the number itself.
### Hint 2
Walk the numbers upwards from 2. If the current number is still unmarked it is prime, so mark its multiples. Start marking at the number squared rather than at twice the number — everything below that has already been crossed out by a smaller prime — and step by the number itself, so `range` does the multiplication for you. You can stop the outer walk once the number squared passes the limit; from there on nothing new gets marked, and every number still standing is prime. At the end, collect the numbers from 2 to the limit that were never marked, in order.
### Hint 3
Different data, same "mark the impossible, keep the rest" shape — free ports in a range:

```python
allowed = range(8000, 8010)
taken = set()
for service_port in (8000, 8003):
    taken.update(range(service_port, 8010, 3))   # this service reserves every third port

free = [port for port in allowed if port not in taken]
free   # -> [8001, 8002, 8004, 8005, 8007, 8008]
```

No port is ever asked "are you free?" — the reservations are stamped in first, and the answer is whatever survives. `range(start, stop, step)` does the stamping without a multiplication in sight.
