---
title: a running total, day by day
kind: sql
edits: task.sql
difficulty: medium
minutes: 18
prereqs: [329]
tags: [window-functions, dates]
ordered: true
explain: true
track: sql
---
# a running total, day by day

*With `ORDER BY` inside `OVER`, an aggregate runs over every row up to this one.*

## Read first
- [Window function calls](https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS): frames, and what `ORDER BY` in `OVER` does to them
- [date_trunc](https://www.postgresql.org/docs/current/functions-datetime.html#FUNCTIONS-DATETIME-TRUNC): cutting a timestamp down to its month

## Why
The monthly report shows each day's revenue, how far the month has come, and whether today beat yesterday. Revenue per day is a plain `GROUP BY`. The other two look across rows.

`sum(revenue) OVER (ORDER BY day)` adds up every day up to the current one: a running total, without a subquery per row. `lag(revenue) OVER (ORDER BY day)` is the previous row's revenue, and NULL on the first day, which is honest: there is no day before it this month.

A timestamp becomes its day with `::date`, and `date_trunc('month', placed_at)` cuts it to the first of its month, which is an easy way to say "in this month".

## You get
`customers` and `orders`, in the tab beside the editor. `placed_at` is a timestamp.

## You return
One row for every day of `{month}` that has orders that were not refunded.

## Rules
- four columns, in this order: `day` (a date), `revenue` (that day's total), `running_total` (from the first such day of the month up to this one), `change` (this day's revenue minus the previous such day's, empty on the first)
- refunded orders do not count anywhere
- running_total and change come from window functions, not a subquery per row
- in `day` order

## Hints
### Hint 1
First the daily revenue alone, as a `WITH daily AS (...)`. Check it, then add the two window columns in the outer query.

### Hint 2
Both window columns order by day: `OVER (ORDER BY day)`. Neither needs `PARTITION BY`, since there is one month.

### Hint 3
The same shape on other tables, a reading log's pages per day, pages so far, and the change:

```sql
SELECT day, pages,
       sum(pages) OVER (ORDER BY day) AS so_far,
       pages - lag(pages) OVER (ORDER BY day) AS change
FROM reading_log
ORDER BY day;
```
