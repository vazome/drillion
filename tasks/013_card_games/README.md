---
title: lists — the poker round tracker
difficulty: medium
tier: core
minutes: 12
prereqs: [10]
tags: [lists]
source: exercism/python concept/card-games (MIT, adapted)
---
# lists — the poker round tracker

*Building, concatenating and searching a list — three one-liners and the `in` operator.*

## Read first
- [lists (Python tutorial)](https://devdocs.io/python~3.14/tutorial/datastructures) — the tour: literals, indexing, and what a list is for
- [the `list` type](https://devdocs.io/python~3.14/library/stdtypes#list) — the reference page, including the constructor and what it accepts
- [sequence types — `list`, `tuple`, `range`](https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range) — the operations every sequence shares, `+` and `in` among them
- [common sequence operations](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — the table with `x in s`, `s + t`, `len(s)` and slicing in it
- [lists and tuples in Python (Real Python)](https://realpython.com/python-lists-tuples/) — the same ground, slower, with pictures

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Elyse tracks which poker rounds she played. You track which instance IDs you already restarted, which alerts you already paged on, which config keys a deploy touched. Same three questions every time: build a small list from a starting point, stick two lists together when the data arrives in pieces, and ask whether a thing is in there at all. Python answers all three without a loop, and knowing that `number in rounds` *is* the membership test — a complete expression that already evaluates to `True` or `False` — is the difference between three lines and thirteen.

## You get
Nothing. `solve()` takes **no arguments**; it hands the grader your finished functions and the grader supplies the rounds. Rounds are plain integers and a "list of rounds" is a plain `list` of them, possibly empty.

> [!NOTE]
> Exercism asks for all seven functions in one `lists.py`. Here the task is split in two: **this task covers tasks 1–3**, and tasks 4–7 are task `014_card_games`. There is one entry point — `solve()` returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"get_rounds"` | `number` — the round being played right now, e.g. `27` | a list of three ints: this round and the next two, in order |
| `"concatenate_rounds"` | `rounds_1`, `rounds_2` — two lists of round numbers | one list: everything from the first, in order, followed by everything from the second |
| `"list_contains_round"` | `rounds`, `number` | `True` when `number` is one of the rounds, `False` otherwise |

```python
poker = solve()
poker["get_rounds"](27)                                  # -> [27, 28, 29]
poker["concatenate_rounds"]([27, 28, 29], [35, 36])      # -> [27, 28, 29, 35, 36]
poker["list_contains_round"]([27, 28, 29, 35, 36], 29)   # -> True
poker["list_contains_round"]([27, 28, 29, 35, 36], 30)   # -> False
```

## Rules
- this task implements **Exercism tasks 1, 2 and 3 only** — `card_average`, `approx_average_is_average`, `average_even_is_average_odd` and `maybe_double_last` belong to task `014_card_games`
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- `get_rounds` returns exactly three numbers, ascending, starting with the one it was given
- `concatenate_rounds` keeps both lists' order and copes with either (or both) being empty — two empty lists give `[]`
- `list_contains_round` on an empty list is `False`, never an error

> [!WARNING]
> `list_contains_round` is compared with `is True` / `is False`, so return a real boolean. `0` and `1` fail even though they compare equal.

## Hints
### Hint 1
All three are one line, and none of them needs a loop. Lists can be [constructed](https://devdocs.io/python~3.14/library/stdtypes#list) in several ways — the simplest is to write the elements out between square brackets, and elements may be *expressions*, not just literals. For the second and third, look at the [common sequence operations](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) table: one operator glues two sequences into a new one, and one operator answers "is this in there?".
### Hint 2
Task 1: you have the current round number and you need three consecutive numbers starting from it. Write the square brackets and put three arithmetic expressions inside them.

Task 2: `+` on two lists produces a **new** list with the left one's items followed by the right one's, and it leaves both originals alone. That is the whole function.

Task 3: `in` is a comparison operator, so `something in a_list` already *is* `True` or `False`. Do not wrap it in `if … return True else return False` — just return the expression. It also handles the empty list for free.
### Hint 3
Different data, same three moves — a port range, two lists of services, one membership check:

```python
port = 8080
[port, port + 1, port + 2]        # -> [8080, 8081, 8082]

healthy = ['api', 'db']
degraded = ['cache']
healthy + degraded                # -> ['api', 'db', 'cache']
healthy                           # -> ['api', 'db']    unchanged

'cache' in healthy + degraded     # -> True
'queue' in healthy + degraded     # -> False
```
