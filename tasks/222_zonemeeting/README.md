---
title: zoneinfo — the same meeting seen from two cities, across a clock change
difficulty: medium
tier: core
minutes: 20
prereqs: [65]
tags: [stdlib-ops]
---
# zoneinfo — the same meeting seen from two cities, across a clock change

*`ZoneInfo` is the difference between a clock reading and a moment in time, and `astimezone` is the only correct way to cross between them.*

## Read first
- [`zoneinfo`](https://devdocs.io/python~3.14/library/zoneinfo) — `ZoneInfo("Area/City")` and where the rules come from
- [`datetime.astimezone`](https://devdocs.io/python~3.14/library/datetime#datetime.datetime.astimezone) — the same instant, re-read on a different clock
- [`datetime.fromisoformat`](https://devdocs.io/python~3.14/library/datetime#datetime.datetime.fromisoformat) and [`isoformat`](https://devdocs.io/python~3.14/library/datetime#datetime.datetime.isoformat) — text in, text out

## Why
A standing meeting is booked at nine in the morning, Berlin time, every week. Somebody in New York needs the same series on their calendar. For most of the year that is a flat six hours earlier, and a spreadsheet with `-6` in a column will look correct for months. Then March arrives: the United States moves its clocks on the second Sunday and Europe waits until the last one, and for three weeks the gap is five hours instead of six. Anyone working from the fixed number turns up an hour late to three meetings and cannot explain why.

## You get
`stamps` — a list of naive local date-and-time strings such as `"2026-03-07 09:00"`, in `datetime.fromisoformat` format, read on the clock in `from_zone`.

`from_zone` and `to_zone` — IANA time zone names such as `"Europe/Berlin"` and `"America/New_York"`.

## You return
a list of strings, the same length and in the same order: each moment written as an ISO 8601 string on the clock in `to_zone`, offset included.

## Rules
- Attach `from_zone` to each parsed stamp, then convert to `to_zone`.
- Format the result with `isoformat()` and return it exactly as that gives it, offset and all.
- The offset between the two zones is not a constant. Convert every stamp on its own; the list is allowed to straddle a clock change in either zone.
- Every stamp is a real local time in `from_zone` — none of them falls in a gap or a repeated hour.

```python
solve(["2026-03-07 09:00", "2026-03-15 09:00"], "Europe/Berlin", "America/New_York")
# -> ['2026-03-07T03:00:00-05:00', '2026-03-15T04:00:00-04:00']
```

Nine in the morning both times, six hours back on the first date and five on the second, because the United States has changed its clocks and Europe has not yet.

> [!WARNING]
> `replace(tzinfo=...)` and `astimezone(...)` look interchangeable and are opposites. `replace` relabels the clock reading and moves the instant; `astimezone` keeps the instant and changes the reading. You want `replace` exactly once — to say which zone the naive input was read on — and `astimezone` for the crossing.

## Hints
### Hint 1
`datetime.fromisoformat("2026-03-07 09:00")` gives you a naive datetime: a clock reading with no zone, which is not yet a moment in time.
### Hint 2
`naive.replace(tzinfo=ZoneInfo(from_zone))` makes it a moment. `ZoneInfo` looks the offset up from the date, so the same call gives `+01:00` in March and `+02:00` in April on its own.
### Hint 3
One expression per stamp:

```python
ZoneInfo("Europe/Berlin")  # build each zone once, outside the loop
moment = datetime.fromisoformat(stamp).replace(tzinfo=source)
moment.astimezone(target).isoformat()
```
