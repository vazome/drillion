---
title: customers who never referred anyone
kind: sql
edits: task.sql
difficulty: medium
minutes: 12
prereqs: [327]
track: sql
tags: [joins, null-handling]
ordered: true
---
# customers who never referred anyone

*`NOT IN` over a column that holds a NULL is never true, so it quietly returns nothing.*

## Read first
- [EXISTS and NOT EXISTS](https://www.postgresql.org/docs/current/functions-subquery.html#FUNCTIONS-SUBQUERY-EXISTS): a subquery asked "is there any row?"
- [NOT IN](https://www.postgresql.org/docs/current/functions-subquery.html#FUNCTIONS-SUBQUERY-NOTIN): and what it does when the list holds a NULL

## Why
The referral team wants to nudge the customers who have never brought anyone in. A customer has referred someone when their `id` appears in another customer's `referred_by`, so the question is about rows that have no match: an anti-join.

The obvious query is `WHERE id NOT IN (SELECT referred_by FROM customers)`, and it returns no rows at all. Most customers found the shop on their own, so `referred_by` holds NULLs, and `x NOT IN (1, 2, NULL)` is not true but unknown: `x` might equal the NULL, for all SQL knows. `WHERE` keeps only rows that are true, so none survive.

`NOT EXISTS` asks a different question, "is there a row where `referred_by = c.id`?", and a NULL there is simply not a match. It is the anti-join that means what it says.

## You get
A `customers` table, in the tab beside the editor, with `referred_by` pointing at the customer who brought them, or empty.

## You return
Every customer in `{city}` whose `id` is nobody's `referred_by`.

## Rules
- two columns, in this order: `id`, `name`
- only customers in `{city}`
- in `id` order

## Hints
### Hint 1
Try the `NOT IN` version and look at what comes back. Then try `SELECT count(*) FROM customers WHERE referred_by IS NULL`.

### Hint 2
A correlated subquery refers to the outer row: inside `NOT EXISTS (SELECT 1 FROM customers AS r WHERE ...)`, the outer customer is still `c`. Give the inner table a different alias.

### Hint 3
The same shape on other tables, products nobody has ever reviewed:

```sql
SELECT p.id, p.name
FROM products AS p
WHERE NOT EXISTS (
  SELECT 1 FROM reviews AS rv WHERE rv.product_id = p.id
)
ORDER BY p.id;
```
