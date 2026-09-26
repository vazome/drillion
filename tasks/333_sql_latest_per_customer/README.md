---
title: each customer's latest order
kind: sql
edits: task.sql
difficulty: medium
minutes: 12
prereqs: [330]
tags: [top-n, sorting]
ordered: true
track: sql
---
# each customer's latest order

*`DISTINCT ON` keeps the first row of each group, and `ORDER BY` decides which row is first.*

## Read first
- [DISTINCT ON](https://www.postgresql.org/docs/current/sql-select.html#SQL-DISTINCT): Postgres's own clause, and its rule about `ORDER BY`

## Why
Support wants each customer's most recent order on one screen. That is 330's question with N = 1, and Postgres has a shorter answer than a window function: `DISTINCT ON (customer_id)` keeps one row per customer, the first one in the query's order.

So the order does the choosing. It has to start with the `DISTINCT ON` columns (Postgres insists), and what follows picks the row: `placed_at DESC` puts the latest first. Two orders can share a timestamp, and a last sort column settles which one wins.

`DISTINCT ON` is not standard SQL. It is worth knowing because Postgres code uses it everywhere, and worth recognising as the thing a window function would do elsewhere.

## You get
`customers` and `orders`, in the tab beside the editor.

## You return
For every customer with at least one `{status}` order, their latest `{status}` order.

## Rules
- three columns, in this order: `customer_id`, `order_id`, `placed_at`
- one row per customer; on equal `placed_at`, the higher order id
- in `customer_id` order

## Hints
### Hint 1
Write the plain query first: every `{status}` order, `ORDER BY customer_id, placed_at DESC`. The row you want is the first of each customer's block.

### Hint 2
`SELECT DISTINCT ON (customer_id) customer_id, ...` keeps exactly that first row. The parentheses are part of the syntax.

### Hint 3
The same shape on other tables, each sensor's most recent reading:

```sql
SELECT DISTINCT ON (sensor_id) sensor_id, value, read_at
FROM readings
ORDER BY sensor_id, read_at DESC, id DESC;
```
