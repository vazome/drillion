---
title: Counter — top N by frequency
difficulty: easy
tier: core
minutes: 12
prereqs: [17]
tags: [counter]
---
# Counter — top N by frequency

*Top-N counting — the single most-asked DevOps screen question.*

## Why
A web server is under unusual load. The security lead asks "which IP addresses are hitting us the most?" so they can decide whether to block one. You have the access log, one request per line, and need the busiest few addresses with their request counts, biggest first. This is the single most-asked DevOps screening question.

## You get
`lines` — a list of log lines like

```python
"10.0.0.4 GET /health 200"
```

where the first word is the IP. `n` — how many top addresses to report, like `3`. The test creates them and hands them to you; you never build them yourself.

## You return
a list of `n` pairs `(ip, count)`, busiest first.

## Rules
Return the `n` most frequent IPs as a list of `(ip, count)` tuples, busiest first.

Each line looks like `"10.0.0.4 GET /health 200"`; the IP is the first field.

```python
solve(["10.0.0.4 GET /health 200",
       "10.0.0.4 GET /api/users 200",
       "10.0.0.9 GET /health 500"], 2)
# -> [("10.0.0.4", 2), ("10.0.0.9", 1)]
```

Ties: whichever order your tool produces is fine.

## Hints
### Hint 1
You need to count how often each IP appears, then take the biggest few. The `collections` module has a class built for exactly the counting half.
### Hint 2
`collections.Counter(some_list)` counts everything for you. Feed it just the IPs — one per line. Then look at `Counter`'s methods for one that returns the top N already sorted.
### Hint 3
Different data, same shape:

```python
from collections import Counter
words = ['a', 'b', 'a', 'c', 'a', 'b']
print(Counter(words).most_common(2))   # [('a', 3), ('b', 2)]
```

Your job is turning `lines` into that flat list of IPs first.
