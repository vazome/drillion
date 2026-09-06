---
title: p95 latency — nearest-rank percentile
difficulty: medium
tier: core
minutes: 10
prereqs: [12]
tags: [files-text]
---
# p95 latency — nearest-rank percentile

*Mean latency lies; the p95 is the number on the dashboard and in the interview.*

## Read first
- [statistics](https://devdocs.io/python~3.14/library/statistics) — `mean`, `median`, and `quantiles` for the percentile itself

## Why
The service promise (SLO) says 95 percent of requests must finish under 300 ms. An average hides the slow requests that make customers complain, so the dashboard shows the p95: the response time that 95 percent of requests are faster than. Given a list of measured response times, you compute that number the way the team has agreed to define it.

## You get
`values` — a list of numbers (response times), like `[0.1, 0.5, 0.9, 0.3]`. The test creates it and hands it to you; you never build it yourself.

`pct` — a whole number from 1 to 100, like 95.

## You return
one number — an actual element of the list, the pct-th percentile.

## Rules
Return the pct-th percentile of `values` using the nearest-rank method: sort ascending, take the element at index `ceil(pct/100 * n) - 1`.

```python
solve([0.1, 0.5, 0.9, 0.3], 95)  # -> 0.9
solve([4, 1, 3, 2], 50)          # -> 2
```

- `values` is never empty.
- `1 <= pct <= 100`.
- Return an actual element of the list, never an average of neighbours (no interpolation — this is the same definition the nginx task uses).
- Do not modify the caller's list.

## Hints
### Hint 1
Percentile questions are really sorting questions. p95 means: line the values up ascending and point at the one 95 percent of the way along. The whole task is the off-by-one — ranks count from 1, list indexes from 0.
### Hint 2
sorted(values) — not .sort(), the caller keeps their list. math.ceil of pct / 100 times the length gives the 1-based rank; subtract 1 to index. That is nearest-rank: you always return a real sample.
### Hint 3
Different data, same three moves:

```python
import math
vals = [12, 7, 45, 30, 22]
rank = math.ceil(90 / 100 * len(vals))   # 5
print(sorted(vals)[rank - 1])            # 45
```

p50, p95, p99 are the same code — only the fraction changes.
