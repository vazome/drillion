---
title: functools — memoise a recursion that would otherwise double every step
difficulty: hard
tier: advanced
minutes: 18
prereqs: [59, 143]
tags: [functools, recursion]
source: exercism/python practice/knapsack (MIT, adapted)
---
# functools — memoise a recursion that would otherwise double every step

*`lru_cache` on a recursive function is not a speedup. It is the difference between finishing and not.*

## Read first
- [functools.lru_cache](https://devdocs.io/python~3.14/library/functools#functools.lru_cache) — a decorator that remembers what a call already returned
- [functools.cache](https://devdocs.io/python~3.14/library/functools#functools.cache) — the same thing with no size limit and a shorter name

## Why
A courier has one van with a weight limit and a warehouse of parcels, each with a weight and a payout. Only some fit, and the best load is rarely the heaviest or the most numerous one. The natural way to write it is a recursion: for each parcel, either take it or leave it, and keep whichever branch pays more. That is correct on the first try and unusable on the second, because it explores two branches per parcel, so twenty parcels is a million calls and thirty is a billion. The calls repeat: the same parcel, the same weight left over, computed again and again down different paths. Remembering an answer the first time is the entire fix.

## You get
`capacity` — the van's weight limit, a whole number like `10`.
`items` — a list of `(weight, value)` pairs of whole numbers, one per parcel, like `[(5, 10), (4, 40)]`. The test creates them and hands them to you; you never build them yourself.

## You return
the largest total value that fits, as a whole number.

## Rules
Choose a subset of `items` whose weights sum to at most `capacity`, and return the largest total value any such subset reaches.

- Each parcel is taken at most once. There is one of each.
- Weights and values are whole numbers of at least 1; `capacity` may be `0`.
- An empty `items`, or nothing that fits, is `0`.

```python
solve(10, [(5, 10), (4, 40), (6, 30), (4, 50)])   # -> 90   (the 4s: 40 + 50)
solve(10, [(2, 15), (3, 20), (2, 10)])            # -> 45   (everything fits)
solve(4, [(5, 100)])                              # -> 0
```

> [!NOTE]
> The generated cases carry around twenty-six parcels each. Written as a plain recursion with no memory that is tens of millions of calls, and the grader stops a single test after ten seconds, so an uncached answer does not fail on correctness, it fails on the clock. The cached one returns instantly, because there are only a few thousand distinct questions to ask.

## Hints
### Hint 1
Write the recursion first, and only then make it remember. The question at each step is "starting from parcel `i`, with `left` of capacity remaining, what is the best I can do?" — either skip parcel `i`, or, when it fits, take its value and continue with less capacity. The answer is the larger of the two, and running out of parcels is `0`.
### Hint 2
The state is two whole numbers, `(i, left)`, so the same pair recurs constantly along different paths. Define the recursion as a nested function taking exactly those two arguments and put `@lru_cache(maxsize=None)` on it. Keep `capacity` and `items` out of its parameters: they never change, and closing over them keeps the cache key small. `functools.cache` is the same decorator without the parentheses.
### Hint 3
The classic small version, one argument instead of two:

```python
from functools import cache

@cache
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(80))            # instant; without @cache it never finishes
print(fib.cache_info())   # CacheInfo(hits=78, misses=81, ...)
```

Everything the decorator caches must be hashable, which whole numbers are. A list is not, and that is the usual reason a cached recursion refuses to run at all.

Adapted from exercism/python — MIT.
