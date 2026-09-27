---
title: the days nobody ordered
kind: sql
edits: task.sql
difficulty: hard
minutes: 20
prereqs: [327]
tags: [dates, cte, joins]
ordered: true
track: sql
---
# the days nobody ordered

*A row that does not exist cannot be grouped; make the calendar first, then join to it.*

## Read first
- [generate_series](https://www.postgresql.org/docs/current/functions-srf.html): a set of values, dates included
- [Date and time operators](https://www.postgresql.org/docs/current/functions-datetime.html): adding an `INTERVAL` to a date

## Why
The daily chart has a gap wherever nobody ordered, and a chart with gaps misleads: the eye joins the dots across the missing days. Grouping `orders` by day can only produce days that have orders. The empty days are not in the table at all.

So make them. `generate_series(start, stop, INTERVAL '1 day')` produces one row per day, a calendar. Left-join the orders to that calendar and count, and a day with no orders keeps its row with a count of 0, as 327 showed.

The last day of a month is the first of the next month minus a day, which spares you knowing how many days each month has.

## You get
`customers` and `orders`, in the tab beside the editor. `placed_at` is a timestamp.

## You return
Every day of `{month}`, first to last, with how many orders were placed on it.

## Rules
- two columns, in this order: `day` (a date), `orders` (0 on a day with none)
- every day of `{month}` has exactly one row, and no day outside it does
- in `day` order

## Hints
### Hint 1
Run the calendar alone first: `SELECT d::date FROM generate_series(DATE '2026-02-01', DATE '2026-02-28', INTERVAL '1 day') AS d`.

### Hint 2
Join on the day, not the timestamp: `o.placed_at::date = days.day`. Count a column from `orders`, so the empty days count 0.

### Hint 3
The same shape on other tables, every hour of one day with its page views:

```sql
WITH hours AS (
  SELECT h AS hour
  FROM generate_series(TIMESTAMP '2026-05-01 00:00', TIMESTAMP '2026-05-01 23:00', INTERVAL '1 hour') AS h
)
SELECT hours.hour, count(v.id) AS views
FROM hours
LEFT JOIN views AS v ON date_trunc('hour', v.at) = hours.hour
GROUP BY hours.hour
ORDER BY hours.hour;
```
