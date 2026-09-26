---
title: the largest orders in each city
kind: sql
edits: task.sql
difficulty: medium
minutes: 18
prereqs: [326]
tags: [window-functions, top-n]
ordered: true
track: sql
---
# the largest orders in each city

*A window function computes over a group of rows without collapsing them into one.*

## Read first
- [Window functions, the tutorial](https://www.postgresql.org/docs/current/tutorial-window.html): `OVER`, `PARTITION BY`
- [Window functions, the list](https://www.postgresql.org/docs/current/functions-window.html): `row_number`, `rank`, `dense_rank`

## Why
Each city's manager wants their few biggest orders. "Top N per group" is the question `GROUP BY` cannot answer: grouping keeps one row per city, and these are several rows per city, each still an order.

`row_number() OVER (PARTITION BY city ORDER BY total DESC)` numbers the orders inside each city, 1 for the largest. The numbering happens after `WHERE`, so it cannot be filtered in the same query; wrap it, and filter the number outside.

Ties matter here. `rank()` gives two equal totals the same number and skips the next, so "the top 2" could be three rows; `row_number()` always counts 1, 2, 3, and a second sort column decides which of two equal totals comes first.

## You get
`customers` and `orders`, in the tab beside the editor. An order's city is its customer's.

## You return
The `{n}` largest orders in each city.

## Rules
- four columns, in this order: `city`, `order_id`, `total`, `place` (1 for the largest)
- exactly `{n}` rows for every city with at least `{n}` orders; equal totals are placed by the lower order id first
- by `city`, then `place`

## Hints
### Hint 1
Get the numbering right before filtering: select `city`, the order's id and total, and the `row_number()` expression, and look at one city's rows.

### Hint 2
A query in `FROM` needs an alias: `SELECT ... FROM ( ... ) AS ranked WHERE place <= ...`.

### Hint 3
The same shape on other tables, the three best-selling books of each genre:

```sql
SELECT genre, title, copies, place
FROM (
  SELECT genre, title, copies,
         row_number() OVER (PARTITION BY genre ORDER BY copies DESC, title) AS place
  FROM books
) AS ranked
WHERE place <= 3
ORDER BY genre, place;
```
