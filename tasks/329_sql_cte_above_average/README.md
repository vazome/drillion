---
title: customers above the average customer
kind: sql
edits: task.sql
difficulty: medium
minutes: 15
prereqs: [325]
tags: [cte, aggregates]
ordered: true
track: sql
---
# customers above the average customer

*A CTE names an intermediate result, so the question can be asked of it twice.*

## Read first
- [WITH queries](https://www.postgresql.org/docs/current/queries-with.html): common table expressions
- [Scalar subqueries](https://www.postgresql.org/docs/current/sql-expressions.html#SQL-SYNTAX-SCALAR-SUBQUERIES): a subquery that returns one value

## Why
Finance wants the customers who spend more than the typical customer. "The typical customer" is an average over customers, not over orders: first total each customer's spending, then average those totals. Averaging the orders instead answers a different question, the size of a typical order, and gives a different line.

The per-customer totals are needed twice: once to list, once to average. A `WITH` clause names them (`spend`), and the main query reads from that name like a table, both in `FROM` and in a subquery that returns the one average.

## You get
`customers` and `orders`, in the tab beside the editor.

## You return
Every customer whose total over their `{status}` orders is above the average of those totals.

## Rules
- two columns, in this order: `customer_id`, `spent` (their total over `{status}` orders)
- the average is over customers who have `{status}` orders, one total each
- the most spent first; ties in `customer_id` order

## Hints
### Hint 1
Write the inner part alone first: the total per customer over `{status}` orders. When it looks right, wrap it: `WITH spend AS ( ... ) SELECT * FROM spend`.

### Hint 2
`(SELECT avg(spent) FROM spend)` is one number, and can stand anywhere a number can, including after `>` in `WHERE`.

### Hint 3
The same shape on other tables, authors who sold more copies than the average author:

```sql
WITH sold AS (
  SELECT author_id, sum(copies) AS copies
  FROM sales
  GROUP BY author_id
)
SELECT author_id, copies
FROM sold
WHERE copies > (SELECT avg(copies) FROM sold)
ORDER BY copies DESC, author_id;
```
