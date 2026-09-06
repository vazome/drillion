---
title: bisect — find the band without scanning the list
difficulty: medium
tier: core
minutes: 12
prereqs: [12]
tags: [bisect, sorted]
---
# bisect — find the band without scanning the list

*A sorted list already knows where a value belongs. `bisect` asks it, in log time, instead of walking.*

## Read first
- [bisect.bisect_right](https://devdocs.io/python~3.14/library/bisect#bisect.bisect_right) — the insertion point to the right of equal values, which is what a band lookup wants
- [bisect — Array bisection algorithm](https://devdocs.io/python~3.14/library/bisect) — the module intro, including the "searching sorted lists" recipes at the end
- [bisect.insort](https://devdocs.io/python~3.14/library/bisect#bisect.insort) — add to a sorted list and keep it sorted, without re-sorting

## Why
Latency numbers arrive one at a time and each has to be put in a bucket: fast, normal, slow, critical. Written as a chain of `if` it is four comparisons per number, rewritten every time the thresholds change, and easy to get wrong at the boundary. The thresholds are already sorted, so the position of a value inside them is a search, not a scan, and the standard library has done the search since 1997.

## You get
`thresholds` — a sorted list of boundary numbers, e.g. `[100, 300, 1000]`. `labels` — the names for the bands they cut, always one longer than `thresholds`, e.g. `["fast", "normal", "slow", "critical"]`. `values` — the measurements to classify, in any order.

## You return
a list of labels, one per value, in the same order as `values`.

## Rules
A value belongs to the band its position in `thresholds` selects.

- A value **equal to a threshold** belongs to the band **above** it: with `thresholds = [100, 300]`, the value `100` is `"normal"`, not `"fast"`.
- Everything below the first threshold takes the first label; everything at or above the last takes the last.

```python
solve([100, 300, 1000], ["fast", "normal", "slow", "critical"], [99, 100, 300, 5000])
# -> ["fast", "normal", "slow", "critical"]
```

> [!NOTE]
> `bisect_left` and `bisect_right` differ only on values that are exactly equal to a threshold, which is the boundary this task's data always includes. Picking the wrong one passes every case except the one that matters.

## Hints
### Hint 1
For one value, you want the count of thresholds it is at or above. `bisect` gives you that number directly, and it is already the index into `labels`.
### Hint 2
`bisect_right(thresholds, value)` returns where `value` would be inserted to keep the list sorted, after any equal entries. For `[100, 300]` and value `100` that is `1`, so `labels[1]` is `"normal"` — exactly the rule above.
### Hint 3
Different data, same shape:

```python
from bisect import bisect_right
grades, letters = [60, 70, 80, 90], ["F", "D", "C", "B", "A"]
print([letters[bisect_right(grades, s)] for s in (59, 60, 89, 90)])
# ['F', 'D', 'B', 'A']
```

One expression per value, and no `if` anywhere.
