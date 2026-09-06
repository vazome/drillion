---
title: heapq — merge sorted log streams, earliest first
difficulty: medium
tier: core
minutes: 15
prereqs: [52]
tags: [heapq, iteration]
---
# heapq — merge sorted log streams, earliest first

*Each file is already sorted. `heapq.merge` walks all of them at once and yields one ordered stream.*

## Read first
- [heapq.merge](https://devdocs.io/python~3.14/library/heapq#heapq.merge) — merge several already-sorted inputs into one sorted iterator, without loading them
- [heapq](https://devdocs.io/python~3.14/library/heapq) — the module's own summary: what a heap gives you that a sorted list does not
- [itertools.islice](https://devdocs.io/python~3.14/library/itertools#itertools.islice) — take the first n items of an iterator and stop, without building the whole thing

## Why
An incident spans four services, and each one wrote its own log file. Every file is already in time order, but the story is only readable when the four are interleaved into a single timeline, and you usually want the first screenful rather than the whole incident. Concatenating and re-sorting throws away the fact that the inputs were sorted to begin with, and forces every line into memory to answer a question about the first twenty.

## You get
`streams` — a list of already-sorted sequences, one per service, each holding `(timestamp, line)` pairs, e.g.

```python
[[("10:01", "api up"), ("10:04", "api slow")],
 [("10:02", "db up"), ("10:09", "db failover")]]
```

`n` — how many of the earliest entries to return, like `3`. Timestamps are unique across all streams, so the merged order is never ambiguous. The test creates them and hands them to you; you never build them yourself.

## You return
a list of the `n` earliest `(timestamp, line)` pairs, earliest first. Fewer than `n` when the streams hold fewer between them.

## Rules
Merge the streams by timestamp and keep the first `n`.

- The pairs come back unchanged, as pairs, in ascending timestamp order.
- Timestamps are strings that compare correctly as strings, so `"10:04" < "10:09"`. No parsing is needed.
- `n` may be larger than everything available, and `streams` may be empty or hold an empty stream.

```python
solve([[("10:01", "api up"), ("10:04", "api slow")],
       [("10:02", "db up")]], 2)
# -> [("10:01", "api up"), ("10:02", "db up")]
```

> [!NOTE]
> Sorting the concatenation also passes this test, at this size. The reason the merge is worth learning is what happens at the size where it matters: it holds one item per stream rather than every item, and stops as soon as you stop asking.

## Hints
### Hint 1
`heapq` has a function that takes several sorted iterables as separate arguments and gives you one sorted iterator. You will need `*streams` to spread the list into those arguments.
### Hint 2
The result is an iterator, not a list: it produces items only as you ask for them. `itertools.islice(it, n)` asks for at most `n`, and `list(...)` around it gives you the list to return.
### Hint 3
Different data, same shape:

```python
import heapq
from itertools import islice

a, b = [1, 4, 9], [2, 3, 10]
print(list(islice(heapq.merge(a, b), 4)))   # [1, 2, 3, 4]
```

Your items are tuples, and tuples compare on their first element first, which is the timestamp.
