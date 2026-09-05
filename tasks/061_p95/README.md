---
title: log analysis — nginx log -> top IPs, status mix, p95
difficulty: medium
tier: core
minutes: 30
prereqs: [4, 10, 16]
tags: [log-analysis]
---
# log analysis — nginx log -> top IPs, status mix, p95

*Whole-task task: the nginx log question, end to end.*

Combines topics 19 (Counter), 22 (set), 28 (str), 34 (percentile). Passing this cleanly pushes those components further out too.

## Read first
- [statistics.quantiles](https://devdocs.io/python~3.14/library/statistics#statistics.quantiles) — the percentile, without hand-rolling the index maths

## Why
The site was slow last night and the manager wants a quick read of the web server's access log: which three visitors (IP addresses) made the most requests, how the responses split between success and error classes (2xx, 4xx, 5xx), and how slow the slowest requests were. That last one is the "p95": the time that 95 percent of requests came in under. This is the single most common hands-on question in DevOps interviews.

## You get
`lines` — a list of strings, one per request, each in the standard nginx log format, like

```python
'10.0.0.1 - - [07/Aug/2026:10:12:33 +1000] "GET /api/users HTTP/1.1" 200 1234 0.043'
```

The test generates them and hands them to you.

## You return
a dict with three keys: `"top_ips"` (a list of the 3 busiest `(ip, count)` pairs, busiest first), `"statuses"` (a dict like `{"2xx": 5, "4xx": 1}`, only for classes that occur) and `"p95"` (a number of seconds).

## Rules
Parse access-log lines and return a summary dict:

```python
solve(lines)
# -> {"top_ips":  [(ip, count), ...],   # 3 busiest, most first
#     "statuses": {"2xx": 5, "4xx": 1}, # only classes that occur
#     "p95":      0.418}                # 95th percentile duration
```

A line looks like:

```text
10.0.0.1 - - [07/Aug/2026:10:12:33 +1000] "GET /api/users HTTP/1.1" 200 1234 0.043
^ip                                        ^method ^path            ^status ^bytes ^seconds
```

p95 uses the nearest-rank method: sort ascending, take the value at index `ceil(0.95 * len) - 1`. No interpolation.

> [!TIP]
> This is the most-asked DevOps screen question in existence. Narrate it out loud while you write it.

## Hints
### Hint 1
Do it in four separate passes, not one clever loop. Parse first: turn every line into the few fields you need, then answer each question from that. Clear beats compact — and the interviewer is listening to you explain, not admiring your line count.
### Hint 2
Fields come from line.split(). The status is at index 8, the duration is last. Status class: 500 // 100 gives 5, so f'{500//100}xx' builds '5xx'. For p95 you need math.ceil.
### Hint 3
Different data, same shape — the percentile piece alone:

```python
import math
vals = [0.5, 0.1, 0.9, 0.3]
idx = math.ceil(0.95 * len(vals)) - 1
print(sorted(vals)[idx])     # 0.9
```

The other three pieces are tasks you have already passed.
