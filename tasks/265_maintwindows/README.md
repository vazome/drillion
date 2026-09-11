---
title: interval merging — collapse maintenance windows into the real downtime
difficulty: medium
tier: core
minutes: 18
prereqs: [12, 24]
tags: [sorted, tuples]
---
# interval merging — collapse maintenance windows into the real downtime

*Sort by start, then walk once: each window either extends the one you are holding or begins a new one.*

## Read first
- [`sorted`](https://devdocs.io/python~3.14/library/functions#sorted) — tuples sort by their first item, then their second, which is exactly the order this needs
- [Tuple comparison](https://devdocs.io/python~3.14/tutorial/datastructures#comparing-sequences-and-other-types) — why no `key=` is required here
- [`max`](https://devdocs.io/python~3.14/library/functions#max) — the one call that stops a long window from being swallowed by a short one
- [More on lists](https://devdocs.io/python~3.14/tutorial/datastructures#more-on-lists) — the result is built with `append`, and its last entry is the one you keep adjusting

## Why
Four teams book maintenance windows against the same cluster, and the change calendar ends up holding overlapping bookings: the database upgrade 01:00–03:00, the kernel patch 02:30–04:00, the certificate rotation 04:00–04:30. Somebody now has to publish a status-page notice and answer "how long are we actually down for". That is not the sum of the bookings, and it is not the longest one.

What the notice needs is the set of periods when *at least one* window is open, collapsed so no two of them touch. Three bookings become one outage of 01:00–04:30, and a fifth booking that lands entirely inside an existing one adds nothing at all. The same collapse answers the other question the calendar gets asked — can this new request go in without extending the announced outage — which is why the new booking goes in through the same function rather than a special case beside it.

## You get
- `booked` — a list of `(start, end)` tuples of `int` minutes from midnight, in **no particular order**, possibly overlapping, possibly empty. `start <= end` in each one.
- `proposed` — one more `(start, end)` tuple, the window somebody has just asked for.

## You return
A new `list` of `(start, end)` tuples: `booked` plus `proposed`, collapsed so no two overlap or touch, sorted by start.

## Rules
- windows that **touch** merge. `(60, 120)` and `(120, 180)` become `(60, 180)`: the service is down straight through, and publishing two notices is wrong
- a window entirely inside another disappears into it. `(0, 600)` with `(60, 120)` is just `(0, 600)`
- a zero-length window is legal — `(120, 120)`, a booking somebody has not filled in yet — and it merges into anything that contains its minute
- the result holds plain 2-tuples of `int`, sorted by start. With no overlaps left, sorting by start also sorts by end
- `booked` and the tuples in it come back untouched: build a new list

```python
solve([(60, 180), (150, 240), (240, 270)], (600, 660))
# -> [(60, 270), (600, 660)]
solve([(0, 600)], (60, 120))
# -> [(0, 600)]
solve([], (30, 45))
# -> [(30, 45)]
```

> [!WARNING]
> When two windows merge, the end of the merged window is the **later** of the two ends, not the end of the one that arrived second. Sorting by start says nothing about ends: `(0, 600)` sorts before `(60, 120)`, so a merge that just takes the newer end turns a ten-hour outage into a one-hour one and the status page tells everybody the wrong thing. The test includes a short window nested inside a long one, and that is the single assertion most submissions fail.

> [!NOTE]
> Sort first, unconditionally. Walking an unsorted list cannot work in one pass: two windows that overlap may be at opposite ends of the calendar, and you would need a second pass to notice.

## Hints
### Hint 1
Put `proposed` into the same list as `booked` before you do anything else, and the rest of the task has no special cases in it. `sorted([*booked, proposed])` gives you one list in start order; a tuple compares on its first item first, so no `key=` is needed.

### Hint 2
Then one pass, holding the last window you appended. For each `(start, end)`:

- if the result is empty, or `start` is past the held window's end, this window starts a fresh outage — `append` it
- otherwise it overlaps or touches, so replace the held window with one that runs from the held start to `max(held_end, end)`

"Past the held end" is `start > held_end`, strictly — `start == held_end` is the touching case, and that one merges.

### Hint 3
Same walk, different data — free slots on a meeting-room calendar, found by collapsing the bookings and reading the gaps between them:

```python
def free_slots(bookings, day_end):
    busy = []
    for start, end in sorted(bookings):
        if busy and start <= busy[-1][1]:
            busy[-1] = (busy[-1][0], max(busy[-1][1], end))
        else:
            busy.append((start, end))
    free, at = [], 0
    for start, end in busy:
        if start > at:
            free.append((at, start))
        at = end
    if at < day_end:
        free.append((at, day_end))
    return free

free_slots([(540, 600), (570, 630), (780, 840)], 1020)
# -> [(0, 540), (630, 780), (840, 1020)]
```

The 09:00–10:00 and 09:30–10:30 bookings collapse into one, so there is no imaginary free minute between them. Reading the gaps only makes sense *after* the merge, which is a fair description of why the merge exists.
