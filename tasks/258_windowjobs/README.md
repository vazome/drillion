---
title: weighted interval scheduling — the most you can fit in one maintenance window
difficulty: hard
tier: advanced
minutes: 26
prereqs: [12, 188]
tags: [dynamic-programming, sorted]
---
# weighted interval scheduling — the most you can fit in one maintenance window

*Sort by when things finish, and every job only has to ask one question: what was the best I could do before I started?*

## Read first
- [`sorted()` with `key=`](https://devdocs.io/python~3.14/library/functions#sorted) — ordering the jobs by the field that makes the problem answerable
- [`bisect.bisect_right`](https://devdocs.io/python~3.14/library/bisect#bisect.bisect_right) — how many jobs finish at or before a given time, without scanning them
- [`max()`](https://devdocs.io/python~3.14/library/functions#max) — take it or leave it, whichever is worth more
- [Tuple unpacking in a `for`](https://devdocs.io/python~3.14/reference/compound_stmts#the-for-statement) — `for start, end, value in jobs`

## Why
You have one maintenance window on Saturday night and more change requests than fit in it. Each request has a fixed slot it must run in — it cannot be moved, because it is pinned to a vendor's own downtime or to a batch job's schedule — and a value: how much risk it retires, how many tickets it closes, whatever the change board scored it. Only one change runs at a time. So the question is which set of non-overlapping requests is worth the most, and the two instincts both lose money. Take the highest-scored request first and one eight-hour migration can block three cheap changes that together beat it. Take whatever finishes earliest, the rule that fits the *most* requests in, and you fill the night with trivia while the one change everybody asked for misses the window.

## You get
`jobs` — the change requests, a list of `(start, end, value)` tuples of whole numbers. `start` and `end` are hours within the window, `value` is at least 1. The list may be empty, jobs are in no particular order, and several may overlap. The test creates it and hands it to you; you never build it yourself.

## You return
the largest total `value` any non-overlapping set of the jobs reaches, as a whole number.

## Rules
Pick a set of jobs, none of which overlaps another, and return the largest total value such a set can reach.

- A job occupies its slot from `start` up to but **not including** `end`. So a job ending at `5` and a job starting at `5` do not overlap and may both be taken.
- Every job is taken at most once, and `start < end` always.
- An empty `jobs` is `0`.

```python
solve([(0, 5, 10), (5, 9, 7)])                          # -> 17  (touching, so both fit)
solve([(0, 5, 10), (4, 9, 7)])                          # -> 10  (overlapping, so one of them)
solve([(0, 10, 10), (0, 3, 6), (3, 6, 6), (6, 10, 6)])  # -> 18  (the three lean ones)
solve([(0, 3, 1), (1, 10, 50)])                         # -> 50
```

> [!WARNING]
> Sorting by value and taking each job that still fits is the near-miss. It is the answer that reads as obviously right, and the third example is what it costs: it takes the `10` that fills the whole window and returns `10` where `18` was available. That case is in the test, and so is the one that defeats taking whatever finishes earliest.

> [!NOTE]
> Overlap is the only constraint, and it is not a total: two jobs that each last an hour conflict when they are the same hour and do not when they are different hours, so there is no capacity to add up. That is what makes sorting by end time the move — it turns "which jobs came before this one" into a prefix.

## Hints
### Hint 1
Sort the jobs by their `end`. Then walk them in that order and ask, for each one, *what is the best total using only the first `k` jobs?* Either you do not take job `k`, and the answer is the best over the first `k - 1`; or you take it, and the answer is its value plus the best over every job that had already finished when it started. The larger of the two is the answer for `k`.
### Hint 2
"Every job that had already finished when this one started" is a *prefix* of the sorted list, because the ends are in order — which is the whole reason for sorting by end. Keep a list of the ends and let `bisect_right(ends, start)` tell you how many of them are at or before `start`. Because a job's own end is greater than its own start, that count is never more than the number of jobs you have already answered for. Keep your running answers in a list whose index is that count, with a `0` at the front for "no jobs yet", and the lookup is direct.
### Hint 3
`bisect_right` is the piece that is easy to get wrong by one, so check it against what the rules say:

```python
from bisect import bisect_right

ends = [3, 5, 5, 9]
bisect_right(ends, 5)   # 3 — three jobs finish at or before 5
bisect_right(ends, 4)   # 1
bisect_right(ends, 0)   # 0
```

`bisect_right` counts the entries `<= 5`, and `bisect_left` would count the ones `< 5`. The rules say a job starting at `5` may follow one ending at `5`, so `bisect_right` is the one that matches, and `bisect_left` silently throws away a job that fits.
