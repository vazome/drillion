---
title: orders with their customer's name
kind: sql
edits: task.sql
difficulty: easy
minutes: 10
prereqs: [324]
track: sql
tags: [joins]
ordered: true
---
# orders with their customer's name

*A join puts two tables side by side, matched on the key one of them points with.*

## Read first
- [Joined tables](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-JOIN): `JOIN ... ON`, and table aliases
- [Column references](https://www.postgresql.org/docs/current/sql-expressions.html#SQL-EXPRESSIONS-COLUMN-REFS): why `id` alone is ambiguous here

## Why
The courier for one city wants the orders to pick up, with the customer's name on each. The name lives in `customers` and the order in `orders`, and `orders.customer_id` points at `customers.id`. A join follows that pointer, row by row, and gives one wide row per match.

Both tables have an `id`, so saying `id` alone is ambiguous and Postgres refuses it. An alias per table (`orders AS o`) keeps every column reference short and unambiguous. The `ON` condition is the part that decides what a match is, and matching the wrong pair of columns still runs: it just joins rows that have nothing to do with each other.

## You get
`customers` and `orders`, in the tab beside the editor.

## You return
Every order placed by a customer who lives in `{city}`.

## Rules
- three columns, in this order: `order_id` (the order's `id`), `name` (the customer's), `status`
- only customers whose `city` is `{city}`
- in `order_id` order

## Hints
### Hint 1
`FROM orders AS o JOIN customers AS c ON ...` is the whole join. What goes after `ON` is the question "which customer is this order's?"

### Hint 2
Rename a column in the output with `AS`: `o.id AS order_id`. The filter on city goes in `WHERE`, after the join.

### Hint 3
The same shape on other tables, loans with the reader's email, for one branch:

```sql
SELECT l.id AS loan_id, r.email, l.due
FROM loans AS l
JOIN readers AS r ON r.id = l.reader_id
WHERE r.branch = 'North'
ORDER BY l.id;
```
