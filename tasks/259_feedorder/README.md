---
title: merge sort — how far out of order did this feed arrive?
difficulty: hard
tier: advanced
minutes: 25
prereqs: [12, 143]
tags: [recursion, sorted]
source: TheAlgorithms/Python divide_and_conquer/inversions.py (MIT, adapted)
---
# merge sort — how far out of order did this feed arrive?

*Sorting a list by splitting it in half and merging the halves back, and counting on the way out how badly the input was shuffled.*

## Read first
- [Recursion in the tutorial](https://devdocs.io/python~3.14/tutorial/controlflow#defining-functions) — a function that calls itself on two smaller lists
- [Slicing](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — `values[:mid]` and `values[mid:]` are the two halves, and slicing copies
- [`list.append` and `list.extend`](https://devdocs.io/python~3.14/tutorial/datastructures#more-on-lists) — building the merged list one item at a time, then draining whatever is left
- [`sorted`](https://devdocs.io/python~3.14/library/functions#sorted) — the answer you are checking yourself against, not the answer you hand in

## Why
A replica pulls events from an upstream feed and they are supposed to arrive in sequence order. They rarely do: a retry lands late, two partitions interleave, a batch is replayed. "Out of order" on its own tells you nothing useful, because one event that arrived two slots late and one event that arrived two thousand slots late are both out of order. What you want is a single number for how much reordering happened, so you can watch it over a week and see the day it got worse.

The number is the count of pairs that arrived the wrong way round: for every pair of positions, does the earlier arrival carry the later sequence number? Comparing every pair against every other pair gives you the answer and takes forever on a million events. Merge sort gives you the same number for free, because when you merge two already-sorted halves and you take an item from the right half, every item still waiting in the left half is a pair that was the wrong way round.

## You get
- `arrivals` — a list of `int` sequence numbers in the order they arrived, e.g. `[4, 1, 3, 2]`. It may be empty, and numbers may repeat.

## You return
A tuple `(ordered, swaps)`:

- `ordered` — a new list holding the same numbers, sorted ascending
- `swaps` — an `int`, the number of pairs of positions `i < j` where `arrivals[i] > arrivals[j]`

## Rules
- equal numbers are **not** a pair that is the wrong way round: `[2, 2]` counts `0`
- an empty list, and a list of one, both count `0`
- `ordered` is a **new** list; `arrivals` comes back untouched
- count the crossings during the merge, one pass. Comparing every position against every other position gives the right number and turns a nightly job into an hourly one
- `sorted(arrivals)` is a fine way to check yourself, but the merge is the task

```python
solve([4, 1, 3, 2])   # -> ([1, 2, 3, 4], 4)
solve([1, 2, 3])      # -> ([1, 2, 3], 0)
solve([3, 2, 1])      # -> ([1, 2, 3], 3)
solve([])             # -> ([], 0)
```

> [!WARNING]
> Counting only the neighbours that are the wrong way round is a different, much smaller number. `[3, 1, 2]` has one neighbouring pair out of order but **two** pairs in total, because `3` is ahead of both `1` and `2`. A feed that arrives fully reversed has `n - 1` bad neighbours and `n * (n - 1) / 2` bad pairs, and only the second one grows when the reordering gets worse.

## Hints
### Hint 1
The recursion is the easy half. A list of zero or one is already sorted and has no crossings, so return it and `0`. Otherwise split at `len(values) // 2`, solve each half, and you now have two sorted lists plus the crossings that happened entirely inside each of them.
### Hint 2
Merging two sorted lists is two indices walking forward, always taking the smaller head. The counting hangs off exactly one branch of that: the moment you take an item from the **right** list, every item not yet taken from the left list is larger than it and sat in front of it, so add the number of items left in the left half.
### Hint 3
Take from the left when the heads are equal. If you take from the right on a tie you count pairs of equal numbers, and the rule says those are not out of order:

```python
while i < len(left) and j < len(right):
    if left[i] <= right[j]:
        merged.append(left[i]); i += 1
    else:
        merged.append(right[j]); j += 1
        crossings += len(left) - i
```

---
Adapted from TheAlgorithms/Python — MIT
