---
title: customers who keep paying
kind: sql
edits: task.sql
difficulty: easy
minutes: 10
prereqs: [324]
track: sql
tags: [aggregates, filtering]
ordered: true
---
# customers who keep paying

*`WHERE` filters rows before they are grouped; `HAVING` filters the groups.*

## Read first
- [GROUP BY and HAVING](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-GROUP): turning many rows into one per group
- [Aggregate functions](https://www.postgresql.org/docs/current/functions-aggregate.html): `count(*)` and the rest

## Why
A loyalty programme wants the customers who pay again and again. Every order is a row, so the question is about groups of rows: one group per customer, and a count of each.

`GROUP BY customer_id` makes those groups and `count(*)` counts the rows in each. Two filters are in play and they are easy to swap. Refunded and shipped orders must not count, and that is a filter on rows, before grouping: `WHERE`. "At least N of them" is a filter on the groups, after counting, and `WHERE` cannot see a count that does not exist yet: that is `HAVING`.

## You get
`customers` and `orders`, in the tab beside the editor. Each order has a `customer_id`, a `status` of `paid`, `shipped` or `refunded`, and a `total`.

## You return
Every customer with at least `{at_least}` paid orders.

## Rules
- two columns, in this order: `customer_id`, then `paid_orders`, the number of their orders whose status is `paid`
- only customers with `{at_least}` or more paid orders
- the most paid orders first; ties in `customer_id` order

## Hints
### Hint 1
Start from the rows you want counted: `SELECT * FROM orders WHERE status = 'paid'`. Run it, then group it.

### Hint 2
Once there is a `GROUP BY`, every column you select is either grouped on or inside an aggregate. A name after `AS` can be used in `ORDER BY`, but not in `HAVING`, which is why `HAVING` repeats `count(*)`.

### Hint 3
The same shape on other tables, authors with at least three books in print:

```sql
SELECT author_id, count(*) AS in_print
FROM books
WHERE out_of_print = false
GROUP BY author_id
HAVING count(*) >= 3
ORDER BY in_print DESC, author_id;
```
