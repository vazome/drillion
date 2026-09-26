---
title: a trigger that keeps updated_at honest
kind: sql
edits: task.sql
difficulty: hard
minutes: 22
prereqs: [336]
tags: [ddl]
track: sql
---
# a trigger that keeps updated_at honest

*A `BEFORE` row trigger can change the row on its way in, which is what `updated_at` needs.*

## Read first
- [CREATE TRIGGER](https://www.postgresql.org/docs/current/sql-createtrigger.html): `BEFORE` and `AFTER`, `FOR EACH ROW`, and `WHEN`
- [Trigger functions in PL/pgSQL](https://www.postgresql.org/docs/current/plpgsql-trigger.html): `NEW`, `OLD`, and what to return

## Why
The editor sorts documents by when they last changed, and every program that writes to `documents` is supposed to set `updated_at`. One forgets, and the list lies. A trigger sets it in the database, for every writer.

A trigger is two pieces: a function that returns `trigger`, and the `CREATE TRIGGER` that says when it runs. In a `BEFORE UPDATE ... FOR EACH ROW` trigger, `NEW` is the row about to be written, and the function can change it before it lands; an `AFTER` trigger sees the row once it is already written, too late to change.

Not every update is a change worth recording. `WHEN (OLD.x IS DISTINCT FROM NEW.x)` runs the trigger only when `x` really changed. `IS DISTINCT FROM` rather than `<>`, because it treats NULL as a value, and an update that sets a column to what it already was changes nothing.

## You get
A `documents` table, in the tab beside the editor.

## You return
A PL/pgSQL trigger function and a trigger on `documents`.

## Rules
- an `UPDATE` that changes `{watched}` sets `updated_at` to the current time
- an `UPDATE` that changes only `{other}`, or sets `{watched}` to the value it already had, leaves `updated_at` alone
- an `INSERT` is left alone

## Hints
### Hint 1
The function first: `CREATE FUNCTION name() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN ... RETURN NEW; END; $$;`. The body sets one field of `NEW`.

### Hint 2
Then the trigger: `CREATE TRIGGER name BEFORE UPDATE ON documents FOR EACH ROW WHEN (...) EXECUTE FUNCTION name();`. The condition compares `OLD` and `NEW`.

### Hint 3
The same shape on other tables, counting a product's price changes:

```sql
CREATE FUNCTION count_price_change() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
  NEW.price_changes := OLD.price_changes + 1;
  RETURN NEW;
END;
$$;

CREATE TRIGGER products_price_changes
BEFORE UPDATE ON products
FOR EACH ROW
WHEN (OLD.price IS DISTINCT FROM NEW.price)
EXECUTE FUNCTION count_price_change();
```
