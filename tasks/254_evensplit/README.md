---
title: subset sum — can this batch be split into two equal halves?
difficulty: medium
tier: advanced
minutes: 22
prereqs: [51, 188]
tags: [dynamic-programming, sets]
---
# subset sum — can this batch be split into two equal halves?

*Every total you can reach by picking some of the parcels, worked out in one pass, so the question "is exactly half reachable?" is a lookup.*

## Read first
- [Set operations](https://devdocs.io/python~3.14/library/stdtypes#set) — union, `in`, and why a set of reachable totals never grows a duplicate
- [Set comprehensions](https://devdocs.io/python~3.14/tutorial/datastructures#sets) — building the next set of totals from the current one
- [`bool`](https://devdocs.io/python~3.14/library/functions#bool) — the actual `True`/`False` object, which is what you have to hand back

## Why
A batch of parcels has to go out on two vans, and the depot wants the load split dead even — not roughly even, exactly even, because the vans are weighed at the gate and an imbalance is a fine. Nobody cares which parcels go on which van; the only question is whether an even split exists at all, and it has to be answered before the loading starts rather than discovered halfway through. The same question turns up as splitting a bill into two identical shares, or balancing two shards so neither is the hot one.

## You get
`weights` — the parcels, a list of positive `int` weights in the order they came off the belt, e.g. `[3, 1, 1, 2, 2, 1]`. It may be empty. Weights repeat freely.

## You return
a `bool` — `True` when the parcels can be split into two groups whose weights are equal, `False` when they cannot.

## Rules
Every parcel goes on one of the two vans; none is left behind and none is cut in half.

- An empty `weights` is `True` — two empty vans weigh the same.
- A total weight that is odd is `False`, and no amount of searching changes that.
- An even total is **not** enough on its own: `[1, 3]` totals 4 and still cannot be split.
- Return a real `bool`. The test compares with `is`, so `1`, `0` and a non-empty set are all wrong even when they look right.

```python
solve([3, 1, 1, 2, 2, 1])   # -> True    (3+1+1 and 2+2+1, both 5)
solve([1, 3])               # -> False   (total is even; the halves are not reachable)
solve([3, 3, 2, 2, 2])      # -> True    (3+3 and 2+2+2, both 6)
solve([2, 2, 3])            # -> False
solve([])                   # -> True
```

> [!WARNING]
> Two answers look right and are not. `sum(weights) % 2 == 0` gets `[1, 3]` wrong. Sorting the parcels heaviest-first and dropping each onto whichever van is lighter — the way a person would actually load them — gets `[3, 3, 2, 2, 2]` wrong: it puts a 3 on each van, then 2, 2, 2 to make 5, 5 and 7, and reports no split when there is one. Both appear in the test.

> [!NOTE]
> There are `2 ** len(weights)` ways to divide the parcels and the generated batches hold up to eighteen of them, so trying the divisions is a quarter of a million tries per case. There are only ever `sum(weights) // 2 + 1` distinct totals, which is a few hundred.

## Hints
### Hint 1
Turn the question round. Instead of "how do I divide these", ask "which totals can I reach by picking some subset of them?" — if half the total weight is one of those, the parcels you picked are one van and everything else is the other, and both weigh the same.
### Hint 2
Keep the reachable totals in a `set`, starting at `{0}` because picking nothing reaches nothing. Each parcel doubles the possibilities: every total you could already reach, plus that same total with this parcel added. Totals past half the batch are of no use to you, so drop them and the set stays small.
### Hint 3
Same idea, on which postage values three stamp denominations can make:

```python
reachable = {0}
for stamp in (3, 5, 8):
    reachable |= {total + stamp for total in reachable}
print(sorted(reachable))   # [0, 3, 5, 8, 11, 13, 16]
print(13 in reachable)     # True
```

`|=` on a set is "add all of these", and building the new totals in a comprehension rather than adding to the set you are looping over is what keeps a parcel from being used twice.
