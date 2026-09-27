---
title: reading a product's JSON attributes
kind: sql
edits: task.sql
difficulty: medium
minutes: 12
prereqs: [324]
tags: [jsonb, filtering]
ordered: true
track: sql
---
# reading a product's JSON attributes

*`->>` reads a key as text, `->` as JSON, and `@>` asks whether a document contains another.*

## Read first
- [JSON functions and operators](https://www.postgresql.org/docs/current/functions-json.html): `->`, `->>` and `@>`
- [jsonb containment](https://www.postgresql.org/docs/current/datatype-json.html#JSON-CONTAINMENT): what `@>` means, and why an index can use it

## Why
Suppliers send product details as JSON, and every supplier sends different keys. `jsonb` keeps them as they came, and SQL can still reach inside.

`attrs ->> 'size'` is the size as text, ready to show; `attrs -> 'size'` is the same value as JSON, quotes and all, which is right for passing JSON on and wrong for a report. A key that is missing gives NULL, which is what "no size" should look like.

`@>` followed by a JSON document asks whether `attrs` contains that document, which is the idiomatic filter on a JSON column. A number inside JSON comes out of `->>` as text, so it needs a cast before it can be compared as a number: `'9' > '10'` as text.

## You get
A `products` table, in the tab beside the editor. `attrs` always has `color` and `stock`, and usually `size`.

## You return
Every product whose colour is `{color}` and whose stock is above zero.

## Rules
- three columns, in this order: `name`, `size` (text, empty when the product has none), `price`
- colour `{color}`, stock above 0
- in `name` order

## Hints
### Hint 1
Look at the data first: `SELECT name, attrs FROM products LIMIT 5`.

### Hint 2
A JSON literal in SQL is a string: `attrs @> '{"color": "red"}'`. The stock is `(attrs ->> 'stock')::int`.

### Hint 3
The same shape on other tables, open tickets tagged urgent, with their assignee from JSON:

```sql
SELECT title, meta ->> 'assignee' AS assignee
FROM tickets
WHERE meta @> '{"tags": ["urgent"]}'
  AND (meta ->> 'age_days')::int > 2
ORDER BY title;
```
