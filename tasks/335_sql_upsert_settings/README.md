---
title: an upsert that merges settings
kind: sql
edits: task.sql
difficulty: medium
minutes: 18
prereqs: [334]
tags: [modifying-data, jsonb]
track: sql
---
# an upsert that merges settings

*`ON CONFLICT DO UPDATE` turns an insert that would collide into an update of the row it hit.*

## Read first
- [INSERT, ON CONFLICT](https://www.postgresql.org/docs/current/sql-insert.html#SQL-ON-CONFLICT): the upsert, and the `excluded` row
- [jsonb operators](https://www.postgresql.org/docs/current/functions-json.html#FUNCTIONS-JSONB-OP-TABLE): `||`, which merges two objects

## Why
Overnight the mobile app sent a batch of settings changes. Some users are new, and need a row; others already have settings, and the batch only mentions the keys they touched. Doing it in two statements, update the ones that exist then insert the rest, is racy and easy to get wrong.

`INSERT ... ON CONFLICT (user_id) DO UPDATE` does both in one: try the insert, and where the key already exists, update that row instead. Inside `DO UPDATE`, `settings` is the row already there and `excluded` is the row the insert wanted to write.

Replacing the prefs would lose every key the batch did not mention. `settings.prefs || excluded.prefs` merges them: keys from both, and the batch's value where both have the key.

## You get
`settings`, one row per user, and `incoming`, the batch, in the tab beside the editor.

## You return
SQL that applies every row of `incoming` to `settings`, dated `{today}`.

## Rules
- a user with no settings yet gets a row with the batch's prefs and `updated_on` `{today}`
- a user who has settings keeps every key the batch does not mention, takes the batch's value for every key it does, and gets `updated_on` `{today}`
- users not in the batch are left alone

## Hints
### Hint 1
`INSERT INTO settings (user_id, prefs, updated_on) SELECT ... FROM incoming` inserts the whole batch. Run it alone and read the error it gives on the users who already exist.

### Hint 2
`ON CONFLICT (user_id) DO UPDATE SET ...` goes at the end of the insert. `excluded.prefs` is what the batch sent.

### Hint 3
The same shape on other tables, adding a day's page counts to running totals:

```sql
INSERT INTO page_totals (page, views)
SELECT page, views FROM today
ON CONFLICT (page) DO UPDATE
SET views = page_totals.views + excluded.views;
```
