---
title: itertools + deque — keep the latest reading changes
difficulty: medium
tier: core
minutes: 12
prereqs: [52, 60]
tags: [deque-maxlen, itertools]
---
# itertools + deque — keep the latest reading changes

*Produce adjacent differences, while retaining only the bounded tail.*

## Read first
- [itertools.pairwise](https://devdocs.io/python~3.14/library/itertools#itertools.pairwise) — adjacent overlapping pairs
- [deque](https://devdocs.io/python~3.14/library/collections#collections.deque) — `maxlen` discards old values automatically

## Why
A monitor wants recent changes rather than raw readings. `pairwise` expresses the adjacent relationship directly, and a bounded deque forgets older deltas while consuming them.

## You get
`readings`, a list of integers in arrival order, and `n`, how many of the newest changes to retain.

## You return
A list containing the last `n` differences, where each difference is `current - previous`.

```python
solve([10, 13, 12, 20, 25], 3)  # -> [-1, 8, 5]
```

## Rules
Feed a generator over `pairwise(readings)` into `deque(..., maxlen=n)`, then turn the deque into a list. One reading has no differences. `n=0` returns an empty list.

## Hints
### Hint 1
The pairs are `(readings[0], readings[1])`, then `(readings[1], readings[2])`, and so on. `pairwise` already produces that overlap.
### Hint 2
Generate `current - previous for previous, current in pairwise(readings)`.
### Hint 3
Wrap that generator in `deque(..., maxlen=n)`. Converting the finished deque with `list(...)` gives the requested return type.
