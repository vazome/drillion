---
title: two pointers — the pair of shards that fills an upload part exactly
difficulty: medium
tier: core
minutes: 15
prereqs: [12, 171]
tags: [sorted, sequences]
---
# two pointers — the pair of shards that fills an upload part exactly

*Two indexes walking towards each other from the ends of a sorted list: one comparison decides which one moves, and neither ever goes back.*

## Read first
- [`while`](https://devdocs.io/python~3.14/reference/compound_stmts#the-while-statement) — two indexes moving at different times is a `while`, not a `for`
- [Common sequence operations](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — indexing from both ends, and why `sizes[-1]` is the largest here
- [`None`](https://devdocs.io/python~3.14/library/constants#None) — the honest answer when no pair exists, and not the same thing as an empty tuple
- [Tuples](https://devdocs.io/python~3.14/tutorial/datastructures#tuples-and-sequences) — the return value is a plain 2-tuple

## Why
An archiver has to push a day of log shards to object storage, and the storage API bills and retries in fixed-size parts. Two shards packed into one part is cheap; a part left half-empty is a wasted request, and a part overfilled is a rejected upload. So the packer keeps asking the same question: given the shard sizes still waiting, is there a pair that adds up to exactly one part?

The sizes arrive sorted, because the shard index is written in size order. That is the fact worth exploiting. Checking every pair against every other pair is the honest first version and it squares with the number of shards, which is fine for a hundred and not for a hundred thousand on every part. Sorted, you can stand at both ends at once: if the two smallest-and-largest pair is too small, no smaller partner will ever help the small one, so it is out; if it is too big, the large one is out. Each step eliminates a shard for good, so one walk answers it.

## You get
- `sizes` — a list of `int` shard sizes, **already sorted ascending**. It may be empty, may hold one entry, and values may repeat.
- `target` — an `int`, the exact part size to fill.

## You return
A tuple `(smaller, larger)` of the two sizes that add up to `target` — or `None` when no pair does.

## Rules
- two **different** shards. One shard cannot fill a part with itself, so `sizes = [4]` and `target = 8` is `None`
- two shards of the same size are still two shards. `[4, 4]` and `target = 8` is `(4, 4)`, because there really are two of them in the list
- when several pairs work, return the one with the **smallest first size**. `[1, 2, 3, 4, 5]` and `target = 6` gives `(1, 5)`, not `(2, 4)`
- the tuple is in ascending order: `(smaller, larger)`, and they are equal when both shards are
- `sizes` is already sorted — do not sort it again, and do not rearrange it
- one walk over the list. Two nested loops give the right pair and are the thing being replaced

```python
solve([1, 2, 3, 4, 5], 6)     # -> (1, 5)
solve([2, 4, 4, 9], 8)        # -> (4, 4)
solve([2, 4, 9], 8)           # -> None
solve([], 8)                  # -> None
solve([1, 3, 5, 7], 12)       # -> (5, 7)
```

> [!WARNING]
> The loop condition is `low < high`, strictly. Write `low <= high` and the two indexes are allowed to land on the same shard, which reports `(4, 4)` for a list holding a single `4` — a pair invented out of one shard, and an upload that fails at the API rather than in your code. The test asks for `solve([4], 8)` directly.

> [!NOTE]
> No pair is `None`, not `()` and not `(0, 0)`. The caller tests it with `if pair is None`, and a zero-size shard is a thing that exists.

## Hints
### Hint 1
Start with `low = 0` and `high = len(sizes) - 1` and add the two sizes they point at. Three cases, and each one is one line: the sum equals `target` and you are done; the sum is too small, so the smaller shard can never be part of the answer and `low` moves right; the sum is too big, so the larger shard can never be and `high` moves left. Loop while `low < high`; fall out of the loop and return `None`.

### Hint 2
Convince yourself of the "smallest first size" rule rather than adding code for it — the walk already obeys it. `low` only ever moves when the largest shard still available is not enough to reach `target` alongside it, which means no pair with that shard can exist at all. So the first pair the walk finds holds the smallest possible first size, for free.

### Hint 3
Same two-index walk, different question — the pair whose sum comes **closest** to the target, which is what the packer asks next when nothing fits exactly:

```python
def closest_sum(sizes, target):
    low, high, best = 0, len(sizes) - 1, None
    while low < high:
        total = sizes[low] + sizes[high]
        if best is None or abs(total - target) < abs(best - target):
            best = total
        if total < target:
            low += 1
        elif total > target:
            high -= 1
        else:
            return total
    return best

closest_sum([2, 4, 9, 16], 12)   # -> 11
```

Same skeleton, one extra line, and a tie goes to whichever pair the walk met first — `4 + 9` is just as close to 12 as `2 + 9` is. Deciding what a tie means is the part a two-pointer walk will not decide for you.
