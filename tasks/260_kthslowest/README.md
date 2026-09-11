---
title: quickselect — the kth slowest request, without sorting the rest
difficulty: hard
tier: advanced
minutes: 25
prereqs: [51, 143]
tags: [recursion, lists]
source: TheAlgorithms/Python searches/quick_select.py (MIT, adapted)
---
# quickselect — the kth slowest request, without sorting the rest

*Pick a pivot, split the list into what is below it, equal to it and above it, then recurse into the one third that can still hold the answer.*

## Read first
- [Recursion in the tutorial](https://devdocs.io/python~3.14/tutorial/controlflow#defining-functions) — the same function called again on a shorter list
- [List comprehensions](https://devdocs.io/python~3.14/tutorial/datastructures#list-comprehensions) — three of them build the three buckets in three lines
- [`random.Random.choice`](https://devdocs.io/python~3.14/library/random#random.choice) — picking the pivot at random is what keeps this fast on data that is already sorted
- [`sorted`](https://devdocs.io/python~3.14/library/functions#sorted) — the thing you are deliberately not doing to the whole list

## Why
A latency report wants one number: the slowest request that still counts, the tenth worst of the hour, the one you page on. Sorting the whole hour to read one entry out of it is work you throw away — the other 999,990 comparisons answered a question nobody asked.

Quickselect is the sort you stop early. You split the sample around a pivot, look at how big the "above the pivot" pile is, and that alone tells you which pile the answer is in. Then you throw the other two away and do it again. It is worth writing once because the idea generalises: partition, look at the sizes, recurse into one side is the same move behind quicksort, binary search on a partition, and every "top N" query a database plans.

## You get
- `latencies` — a list of `int` milliseconds, in no particular order, e.g. `[120, 45, 300, 45, 89]`. Values repeat often; slow requests come in bursts.
- `k` — an `int`, 1-based: `1` asks for the slowest of all, `2` for the second slowest, and so on. `1 <= k <= len(latencies)`.

## You return
An `int` — the kth largest value in `latencies`.

## Rules
- **kth largest by value, not kth distinct value.** In `[9, 9, 4]`, the slowest is `9`, the second slowest is also `9`, and the third is `4`
- `k` counts from `1`. `k == 1` is `max(latencies)` and `k == len(latencies)` is `min(latencies)`
- leave `latencies` alone: no `.sort()`, no `.pop()`, no assignment into it. The caller still needs the sample for its histogram
- split around a pivot and recurse into one side. `sorted(latencies)[-k]` gets the right answer by doing the work you are here to avoid

```python
solve([120, 45, 300, 45, 89], 1)   # -> 300
solve([120, 45, 300, 45, 89], 4)   # -> 45
solve([9, 9, 4], 2)                # -> 9
solve([7], 1)                      # -> 7
```

> [!WARNING]
> Two buckets are not enough. Splitting into "below the pivot" and "above the pivot" quietly loses every value equal to the pivot, and with repeated latencies that is most of the list — the counts you recurse on stop adding up to the length you started with, and the answer comes back one burst too fast. Three buckets, and the equal pile is how you know when to stop.

> [!NOTE]
> Picking the pivot at random costs one line and buys you the case that actually shows up: a list that is already sorted, or nearly so, because it came off a sorted index. Always taking the first element turns that case into the slow one.

## Hints
### Hint 1
Ask the question from the top. Let `bigger` be the values strictly above the pivot and `same` the values equal to it. If `k <= len(bigger)`, the answer is in `bigger` and `k` does not change. If `k <= len(bigger) + len(same)`, the answer **is** the pivot. Otherwise it is in `smaller`, and `k` shrinks by the two piles you just skipped past.
### Hint 2
Those three buckets are three comprehensions over the same list, or one loop with three `append`s. Either way you never touch the list you were handed, which is also how the rule about leaving it alone takes care of itself.
### Hint 3
Same shape, from the bottom instead, so you can see which arithmetic goes where:

```python
def kth_smallest(values, k):
    pivot = random.choice(values)
    smaller = [v for v in values if v < pivot]
    same = [v for v in values if v == pivot]
    if k <= len(smaller):
        return kth_smallest(smaller, k)
    if k <= len(smaller) + len(same):
        return pivot
    return kth_smallest([v for v in values if v > pivot], k - len(smaller) - len(same))
```

The recursion always shrinks, because `same` is never empty — the pivot itself is in it.

---
Adapted from TheAlgorithms/Python — MIT
