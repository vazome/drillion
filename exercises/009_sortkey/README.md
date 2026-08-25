---
title: sorted with key=
minutes: 10
prereqs: []
tags: [core, rsample]
---
# sorted with key=

*sorted(key=...) — top-3 most-used Python in interviews.*

## Why
A team lead asks "which services are crashing the most?" You have a
list of services and how many times each one restarted this week. They
want the list ordered worst-first so the top of the page is where the
attention should go. Ordering a list of records by one particular field
is the single most common data task in ops reporting.

## You get
`services` — a list of two-item lists like [["api", 2], ["db",
9]], each holding a service name and its restart count. The test creates
it and hands it to you; you never build it yourself.

## You return
the same two-item lists, reordered so the highest restart
count comes first.

## Rules
Each item is [name, restarts]. Return the list sorted by restarts,
MOST restarts first. Keep the pairs intact.

```
[["api", 2], ["db", 9], ["web", 5]]
->  [["db", 9], ["web", 5], ["api", 2]]
```

## Read first
- https://docs.python.org/3/howto/sorting.html  — key=, reverse=, and why Python's sort is 'stable' (ties keep order)
- https://realpython.com/python-sort/  — same, slower and with pictures

> [!NOTE]
> **Take-home:** `sorted(rows, key=score)` in main.py

## Hints
### Hint 1
sorted() on pairs sorts by the FIRST element by default — the name. You need it to look at the second instead, and to count downwards.
### Hint 2
sorted() takes two extra arguments here: one that says which part of each item to compare, and one that flips the direction. The first wants a function, not a number.
### Hint 3
Different data, same shape:

```python
pairs = [['ny', 8.4], ['berlin', 3.6], ['tokyo', 14.0]]
print(sorted(pairs, key=lambda p: p[1], reverse=True))
# [['tokyo', 14.0], ['ny', 8.4], ['berlin', 3.6]]
```

lambda p: p[1] means 'given one pair, compare its second slot'.
