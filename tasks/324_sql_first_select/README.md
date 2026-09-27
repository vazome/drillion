---
title: the newest customers of one city
kind: sql
edits: task.sql
difficulty: easy
minutes: 8
prereqs: []
track: sql
tags: [filtering, sorting]
ordered: true
---
# the newest customers of one city

*A query is a question with three parts: which rows, in what order, and how many.*

## Read first
- [SELECT](https://www.postgresql.org/docs/current/sql-select.html): `WHERE`, `ORDER BY` and `LIMIT`, and the order they apply in
- [Sorting rows](https://www.postgresql.org/docs/current/queries-order.html): `DESC`, and sorting on more than one column

## Why
Marketing wants to welcome the newest customers in each city, and asks for a short list. Three things decide what that list holds. `WHERE` keeps the rows of one city. `ORDER BY` puts them in order, and a date sorts oldest first unless you say `DESC`. `LIMIT` keeps the first few of that order, which is why the order has to be right before the limit means anything.

Two customers can join on the same day. With nothing to break the tie, Postgres may return them in either order, and a list that changes between runs is a bug someone finds later. A second sort column makes the order total.

## You get
A `customers` table, in the tab beside the editor: an `id`, a `name`, the `city` they live in, and the date they `joined`.

## You return
The `{n}` customers from `{city}` who joined most recently.

## Rules
- two columns, in this order: `name`, then `joined`
- newest first; customers who joined on the same day in `name` order
- exactly `{n}` rows

## Hints
### Hint 1
Write it in the order Postgres reads it: `SELECT` the columns, `FROM` the table, `WHERE` the condition, `ORDER BY`, then `LIMIT`. Text values go in single quotes.

### Hint 2
`ORDER BY` takes a list, and each column gets its own direction. `ORDER BY a DESC, b` sorts by `a` from high to low, and by `b` from low to high where `a` ties.

### Hint 3
The same shape on another table, the five most expensive books by one publisher:

```sql
SELECT title, price
FROM books
WHERE publisher = 'Penguin'
ORDER BY price DESC, title
LIMIT 5;
```
