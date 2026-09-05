---
title: datetime — strptime, deltas, busiest minute
difficulty: medium
tier: core
minutes: 15
prereqs: []
tags: [files-text]
---
# datetime — strptime, deltas, busiest minute

*'When did it break, and for how long' is a datetime question, every time.*

## Read first
- [datetime](https://devdocs.io/python~3.14/library/datetime) — aware vs naive — the distinction that causes production bugs
- [strftime and strptime codes](https://devdocs.io/python~3.14/library/datetime#strftime-and-strptime-format-codes) — the format-code table

## Why
After an outage the incident review asks two questions: how long did the event window last, from the first request to the last, and which minute was the busiest? The web server's access log gives one line per request with a timestamp, but the lines are out of order because several servers' logs were merged. You turn the timestamps into real times you can subtract and count.

## You get
`lines` — a list of strings, each starting with a timestamp, like `["2026-08-12 10:31:04 GET /api/users", ...]`, in shuffled order. The test creates them and hands them to you; you never build them yourself.

## You return
a dict with `"span_seconds"` (a whole number of seconds from the earliest to the latest line) and `"busiest_minute"` (a string like `"2026-08-12 10:31"`).

## Rules
Each line starts with a timestamp, then a request:

```python
"2026-08-12 10:31:04 GET /api/users"
```

The lines arrive SHUFFLED, not in time order. Return:

```python
solve(lines)
# -> {"span_seconds": 517,                  # whole seconds, first event to last
#     "busiest_minute": "2026-08-12 10:31"} # minute with most events
```

- The timestamp is exactly the first 19 characters of a line; parse it with the format `"%Y-%m-%d %H:%M:%S"`.
- `span_seconds` is an `int`.

> [!WARNING]
> Ties on the busiest minute go to the **earliest** minute.

These stamps are naive — no timezone attached. In production you want an offset in the log and `%z` in the format so comparisons survive DST and multiple regions; Python refuses to compare naive with aware.

## Hints
### Hint 1
Strings that look like times are still strings. ISO-shaped ones happen to sort correctly, but you cannot subtract them — the moment the question is 'how long between', you need real datetime objects. Parse everything first; the rest is min, max and one subtraction.
### Hint 2
Slice the first 19 characters, parse with datetime.strptime and the given format. Subtracting two datetimes gives a timedelta; its .total_seconds() is the number you want, wrapped in int. For the busy minute, strftime each datetime back down to '%Y-%m-%d %H:%M', count with Counter, and on a tie prefer the smallest minute string.
### Hint 3
Different data, same moves:

```python
from datetime import datetime
fmt = '%Y-%m-%d %H:%M:%S'
a = datetime.strptime('2026-01-05 09:15:30', fmt)
b = datetime.strptime('2026-01-05 09:18:00', fmt)
print(int((b - a).total_seconds()))   # 150
print(a.strftime('%Y-%m-%d %H:%M'))   # 2026-01-05 09:15
```

Parse at the edge, compute in datetime-land, format back out only at the end.
