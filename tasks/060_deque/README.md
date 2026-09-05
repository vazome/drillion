---
title: deque(maxlen) — tail of a stream
difficulty: medium
tier: core
minutes: 10
prereqs: [8]
tags: [deque-maxlen]
---
# deque(maxlen) — tail of a stream

*tail -f in Python: keep the newest few lines, forget the rest automatically.*

## Read first
- [collections.deque](https://devdocs.io/python~3.14/library/collections#collections.deque) — O(1) at both ends, and `maxlen` for a rolling window

## Why
An incident is in progress and the on-call engineer asks "what were the last five errors?" The log is a live stream, far too large to hold in memory, and you only get to read it once, front to back. You need to keep just the newest few matching lines as you go and forget the rest automatically. This is `tail -f` done in Python.

## You get
`lines` — a stream of log lines like `"10:01 ERROR boom"` that you can walk through exactly once. `n` — how many of the latest ERROR lines to keep, like `3`. The test creates them and hands them to you; you never build them yourself.

## You return
a list of the last `n` lines containing `"ERROR"`, oldest first (or all of them if there were fewer than `n`).

## Rules
Return the last `n` ERROR lines of a log stream, oldest first, as a list.

```python
solve(iter(["10:00 INFO ok", "10:01 ERROR boom", "10:02 ERROR again"]), 1)
# -> ["10:02 ERROR again"]
```

A line counts if it contains `"ERROR"`. If fewer than `n` match, return all of them.

> [!WARNING]
> `lines` is an ITERATOR — you can loop over it exactly once. No `len()`, no `lines[-n:]`, and buffering everything into a list defeats the point (pretend the stream is 10 GB).

## Hints
### Hint 1
You cannot slice an iterator, and keeping every line just to throw most away is the wrong shape. You want a container that holds at most `n` items and evicts the oldest by itself when a new one arrives.
### Hint 2
`collections.deque(maxlen=n)`. Loop once over the stream, append each matching line; once the deque is full, every append silently drops the oldest entry. Wrap it in `list()` at the end.
### Hint 3
Different data, same shape:

```python
from collections import deque
last3 = deque(maxlen=3)
for x in range(1, 8):
    last3.append(x)
print(list(last3))   # [5, 6, 7]
```

Same trick with lines instead of numbers, plus your filter before the append.
