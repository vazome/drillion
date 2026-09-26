---
title: every customer, even the ones who bought nothing
kind: sql
edits: task.sql
difficulty: medium
minutes: 15
prereqs: [326]
track: sql
tags: [joins, null-handling]
ordered: true
---
# every customer, even the ones who bought nothing

*A left join keeps every row on the left, and fills the right side with NULL where nothing matched.*

## Read first
- [LEFT OUTER JOIN](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-JOIN): what happens to rows with no match
- [COALESCE](https://www.postgresql.org/docs/current/functions-conditional.html#FUNCTIONS-COALESCE-NVL-IFNULL): the first value that is not NULL

## Why
The city manager wants a line for every customer, with how many orders they have and what they spent, and the customers with nothing are the interesting ones. A plain `JOIN` drops them: no order, no match, no row. `LEFT JOIN` keeps them, with every `orders` column NULL.

Two things then go wrong quietly. `count(*)` counts rows, and a customer with no orders still has one row, so it says 1; `count(o.id)` counts the orders that exist, because `count` of a column skips NULLs. And `sum` over nothing is NULL, not 0, which is what `COALESCE` is for.

The subtlest one is where a condition on the right table goes. In `WHERE`, `o.status <> 'refunded'` is NULL for a customer with no orders, and a NULL condition drops the row: the left join is undone. In `ON`, it only decides which orders match.

## You get
`customers` and `orders`, in the tab beside the editor.

## You return
Every customer who lives in `{city}`, with their orders that were not refunded.

## Rules
- four columns, in this order: `customer_id`, `name`, `orders` (how many orders that were not refunded), `spent` (their total)
- every customer in `{city}` has a row, those with no such orders included, with `orders` 0 and `spent` 0
- in `customer_id` order

## Hints
### Hint 1
Run it without `GROUP BY` first: `SELECT c.id, o.id, o.status FROM customers AS c LEFT JOIN orders AS o ON o.customer_id = c.id WHERE c.city = '...'`. Look at the rows with `o.id` empty.

### Hint 2
The refunded filter belongs to the match, not to the result: `ON o.customer_id = c.id AND o.status <> 'refunded'`.

### Hint 3
The same shape on other tables, every reader with their open loans, zero included:

```sql
SELECT r.id AS reader_id, count(l.id) AS open_loans, COALESCE(sum(l.fine), 0) AS fines
FROM readers AS r
LEFT JOIN loans AS l ON l.reader_id = r.id AND l.returned IS NULL
GROUP BY r.id
ORDER BY r.id;
```
