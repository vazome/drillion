---
title: sqlite3 — a parameterised query, and one adjustment batch that either all lands or none does
difficulty: medium
tier: core
minutes: 20
prereqs: [73]
tags: [stdlib-ops, context-managers]
---
# sqlite3 — a parameterised query, and one adjustment batch that either all lands or none does

*The `?` placeholder is not a convenience over f-strings, and `with connection:` is not a convenience over calling `commit()`. Both are the only versions that are correct.*

## Read first
- [`sqlite3`](https://devdocs.io/python~3.14/library/sqlite3) — `connect`, `execute`, `executemany`, `fetchone`
- [Placeholders](https://devdocs.io/python~3.14/library/sqlite3#sqlite3-placeholders) — how a value gets into a statement without becoming part of it
- [Transaction control](https://devdocs.io/python~3.14/library/sqlite3#sqlite3-controlling-transactions) — what `with connection:` commits, and what it rolls back

## Why
Billing runs a nightly correction pass: a list of charge ids and the amount each one moves by, produced by a reconciliation job upstream. Two things go wrong with the obvious script. The first is the day a customer is called `O'Hare & Sons`, the apostrophe closes the string the query was built out of, and the report either crashes or — worse, and this is the version that gets written up afterwards — runs a statement nobody intended. The second is the correction that would take a charge below zero. The script raises on it, having already written the eleven corrections before it, and now the ledger is in a state no rule describes: not last night's numbers and not tonight's either. Finance can reconcile a batch that landed and a batch that did not. It cannot reconcile half a batch.

## You get
- `charges`, a list of `(id, team, amount)` tuples. Ids are unique, amounts are non-negative ints.
- `adjustments`, a list of `(id, delta)` tuples. Every id is one of the charges; a delta can be negative, and the same id can appear more than once.
- `team`, a team name to total up afterwards. It is taken from the data, and some team names contain an apostrophe.

## You return
a dict with exactly three keys:

| key | value |
|---|---|
| `applied` | `True` when the whole batch landed, `False` when it was rolled back |
| `amounts` | `{id: amount}` for every charge, as the table stands when you are done |
| `team_total` | the sum of `amount` over the rows whose `team` is `team`, read back with one query; `0` when that team has no rows |

## Rules
- Build the table yourself in an in-memory database: `charges(id INTEGER PRIMARY KEY, team TEXT, amount INTEGER)`, then load the rows you were given.
- Apply every adjustment in **one** transaction. The moment any charge would end up below zero, abandon the whole batch — including the adjustments that were already fine — and report `applied: False` with the amounts exactly as they were loaded.
- Deltas stack. Two adjustments of `-40` against a charge of `50` are a rollback, even though neither one alone is.
- Every value that comes from the arguments goes into a statement as a parameter, never as text spliced into the SQL.
- `team_total` is read out of the database with a `SELECT`, not summed from your own dict.

```python
solve([(1, "ops", 50), (2, "ops", 10)], [(1, -20), (2, 5)], "ops")
# -> {'applied': True, 'amounts': {1: 30, 2: 15}, 'team_total': 45}

solve([(1, "ops", 50), (2, "ops", 10)], [(1, -20), (2, -30)], "ops")
# -> {'applied': False, 'amounts': {1: 50, 2: 10}, 'team_total': 60}
```

> [!WARNING]
> `f"... WHERE team = '{team}'"` passes every test written with tidy names in it and fails on the first real customer. The generated data contains a team with an apostrophe in it, so this one is not a style note here — the query raises.

> [!NOTE]
> `with connection:` is not `with open(...)`: it does not close the connection. It commits when the block ends normally and rolls back when an exception leaves it, which is exactly the all-or-nothing you need — as long as the failure happens *inside* the block.

## Hints
### Hint 1
Two separate jobs, and it is worth doing them in this order: get the batch decided first, then ask the database for the total. That way the total is read off whatever state survived, and you do not have to reason about both at once.
### Hint 2
Let the failure be an exception. Inside `with connection:`, update the row, read the new amount back, and `raise` something of your own when it went below zero. Catch that exception outside the `with`, and the rollback has already happened by the time you do.
### Hint 3
The shape, on a different table:

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE seat (row INTEGER PRIMARY KEY, free INTEGER)")
con.executemany("INSERT INTO seat VALUES (?, ?)", [(1, 2), (2, 0)])
con.commit()

class Oversold(Exception): ...

try:
    with con:
        for row, taken in [(1, 1), (2, 1)]:
            con.execute("UPDATE seat SET free = free - ? WHERE row = ?", (taken, row))
            (left,) = con.execute("SELECT free FROM seat WHERE row = ?", (row,)).fetchone()
            if left < 0:
                raise Oversold(row)
except Oversold:
    pass                                     # row 1 is back to 2: the whole block was undone

dict(con.execute("SELECT row, free FROM seat ORDER BY row"))   # -> {1: 2, 2: 0}
```

A cursor is iterable, and each row is a tuple, so `dict(...)` over a two-column `SELECT` is the whole read-back. `fetchone()` on a `SUM` returns `(None,)` when no rows matched, which is not the same as `(0,)`.
