---
title: itertools — chain, islice, groupby (sort first)
difficulty: medium
tier: core
minutes: 15
prereqs: [12, 21, 29]
tags: [itertools]
---
# itertools — chain, islice, groupby (sort first)

*itertools glues paged streams together; groupby bites everyone exactly once.*

## Read first
- [itertools](https://devdocs.io/python~3.14/library/itertools) — the whole module — `groupby`, `chain`, `islice` are the ones that pay off
- [itertools recipes](https://devdocs.io/python~3.14/library/itertools#itertools-recipes) — composites worth stealing

## Why
An on-call engineer is paged at 2am. The log service hands back log lines in pages (batches), the way an API says "here are the next 50 results". The incident lead asks: "in the first N lines after the alert fired, how many came from each service?" to see which service got noisy first. You stitch the pages into one stream, stop after N lines, and count per service.

## You get
`pages` — a list of lists of strings; each inner list is one page of log lines, like

```python
[["api ERROR boom", "db INFO ok"], ["api WARN slow"]]
```

Every line starts with the service name. The test creates it and hands it to you; you never build it yourself.

`first_n` — a whole number like `3`: how many lines from the start of the combined stream to look at.

## You return
a list of `(service, count)` pairs sorted by service name, like `[("api", 2), ("db", 1)]`.

## Rules
Count log lines per service in the head of a paged stream.

`pages` is a list of pages, each page a list of log lines — the shape a paginated API hands you. The service name is the first word of a line. Look at only the FIRST `first_n` lines of the combined stream, and return `[(service, count), ...]` sorted by service name.

```python
pages = [["api ERROR boom", "db INFO ok"], ["api WARN slow", "db INFO ok"]]
solve(pages, 3)   # -> [("api", 2), ("db", 1)]
```

Use `itertools`: chain the pages into one stream, islice the head, groupby to count.

> [!WARNING]
> The lines are interleaved on purpose — `groupby` on unsorted data will give you the same service more than once.

## Hints
### Hint 1
Three small jobs: flatten the pages into one stream, cut it to the first N, count per service. `itertools` has a tool for each. The counting one has a famous catch: it only merges neighbours.
### Hint 2
`chain.from_iterable(pages)` flattens; `islice(stream, n)` takes the head without materialising the rest; `groupby(rows, key=...)` yields `(key, group)` pairs — but only for ADJACENT equal keys, so sort by that same key first. `len(list(group))` counts a group.
### Hint 3
Different data, same trap:

```python
from itertools import groupby
animals = ['cat', 'dog', 'cat', 'cat', 'dog']
print([(k, len(list(g))) for k, g in groupby(animals)])
# [('cat', 1), ('dog', 1), ('cat', 2), ('dog', 1)]   <- unsorted: wrong
print([(k, len(list(g))) for k, g in groupby(sorted(animals))])
# [('cat', 3), ('dog', 2)]
```

`groupby` is a run-length grouper, not SQL `GROUP BY`.
