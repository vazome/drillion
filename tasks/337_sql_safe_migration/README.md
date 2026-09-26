---
title: a required column on a table that has rows
kind: sql
edits: task.sql
difficulty: hard
minutes: 20
prereqs: [336]
tags: [ddl, constraints, modifying-data]
track: sql
---
# a required column on a table that has rows

*Add the column, fill it, then make it required: in that order, because the rows already exist.*

## Read first
- [ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html): `ADD COLUMN`, `ALTER COLUMN ... SET NOT NULL`, `ADD CONSTRAINT`
- [Modifying tables](https://www.postgresql.org/docs/current/ddl-alter.html): what adding a column does to the rows already there

## Why
Accounts are getting plans. Every account needs one, so the column has to be required, and the accounts that have paid should start on the paid plan, not on the free one.

`ALTER TABLE accounts ADD COLUMN plan text NOT NULL` fails the moment the table has rows: every existing row would get NULL, which the constraint forbids. A default would satisfy it, but it would put every account on the same plan, the paying ones included.

So a migration that has to look at data runs in three steps. Add the column, nullable. Fill it with an `UPDATE` that works out each row's value. Then tighten it: `SET NOT NULL`, a default for new rows, and a `CHECK` for the values allowed.

## You get
`accounts` and `payments`, in the tab beside the editor.

## You return
A migration that gives every account a `plan`.

## Rules
- `plan` is text, required, and either `free` or `{paid}`
- every existing account with at least one payment gets `{paid}`; the rest get `free`
- an account inserted later without a plan gets `free`

## Hints
### Hint 1
Try the one-line version, `ADD COLUMN plan text NOT NULL`, and read the error. That error is the task.

### Hint 2
`UPDATE accounts SET plan = CASE WHEN ... THEN ... ELSE ... END` fills every row at once, and `EXISTS (SELECT 1 FROM payments ...)` asks whether this account has paid.

### Hint 3
The same shape on other tables, giving every book a required `format`, from whether it has a file:

```sql
ALTER TABLE books ADD COLUMN format text;

UPDATE books
SET format = CASE WHEN EXISTS (SELECT 1 FROM files AS f WHERE f.book_id = books.id)
                  THEN 'ebook' ELSE 'paper' END;

ALTER TABLE books
  ALTER COLUMN format SET NOT NULL,
  ALTER COLUMN format SET DEFAULT 'paper',
  ADD CONSTRAINT books_format_known CHECK (format IN ('paper', 'ebook'));
```
