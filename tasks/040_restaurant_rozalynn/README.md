---
title: none — find the empty seats and count them
difficulty: medium
tier: core
minutes: 12
prereqs: [39]
tags: [none]
source: exercism/python concept/restaurant-rozalynn (MIT, adapted)
---
# none — find the empty seats and count them

*`None` — `is None` as a test, over a dict's keys and values.*

## Read first
- [None (the standard type hierarchy)](https://devdocs.io/python~3.14/library/stdtypes#the-null-object) — one `None` object per program, so identity is the right test
- [`is` and `is not`](https://devdocs.io/python~3.14/reference/expressions#is-not) — identity, not equality; PEP 8 asks for `is None` specifically
- [dict.items()](https://devdocs.io/python~3.14/library/stdtypes#dict.items) — walk keys and values together in one loop
- [dict.values()](https://devdocs.io/python~3.14/library/stdtypes#dict.values) — when only the values matter
- [Real Python: Null in Python](https://realpython.com/null-in-python/) — `None`, falsiness, and the difference between them
- [List comprehensions](https://devdocs.io/python~3.14/tutorial/datastructures#list-comprehensions) — the one-line form of "collect the ones that match"

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Walk-in guests are waiting at the door and the maître d' has to answer two questions off the seating chart: which seats are free, and how many. The chart is a dict where a free seat holds `None` and a taken seat holds a name, so both answers come from scanning it for that one placeholder. The point worth carrying away is *how* you test for it: `is None`, never `== None` and never a bare truthiness check, because a guest called `""` or a seat holding `0` would slip through the second one. Every "which of these fields is unset?" report you write later is this loop.

## You get
Nothing. `solve()` takes **no arguments**; the seating charts arrive as arguments to the functions you hand back.

> [!NOTE]
> Exercism asks for all six functions in one `none.py`. Here the task is split in three: **this task covers tasks 3 and 4** — reading a chart. Tasks 1 and 2 are task `039_restaurant_rozalynn`; tasks 5 and 6 are task `041_restaurant_rozalynn`.

## You return
A dict with these two functions.

| key | parameters | returns |
| --- | --- | --- |
| `"find_all_available_seats"` | `seats` — a seating chart dict, seat number to guest name or `None` | a `list` of the seat **numbers** whose value is `None`, in the chart's own order |
| `"current_empty_seat_capacity"` | `seats` — the same kind of chart | an `int`: how many seats are empty |

```python
front_of_house = solve()

seats = {1: None, 2: "Frank", 3: "Jenny", 4: None, 5: "Alice",
         6: "George", 7: None, 8: "Carol", 9: None, 10: None, 11: None, 12: "Walter"}

front_of_house["find_all_available_seats"](seats)      # -> [1, 4, 7, 9, 10, 11]
front_of_house["current_empty_seat_capacity"](seats)   # -> 6

front_of_house["current_empty_seat_capacity"]({1: "Occupied", 2: None, 3: "Occupied"})
# -> 1
```

## Rules
- the dict keys are exactly the two strings above, and each value is the function **itself** — `{"find_all_available_seats": find_all_available_seats}`, no parentheses
- a seat is empty when its value **is** `None`; anything else means taken — including the string `"Occupied"`, a blank name `""`, and the number `0`
- `find_all_available_seats` returns the seat numbers (the dict's keys), not the values, and keeps them in the order the chart holds them
- `current_empty_seat_capacity` returns a number, not a list — and `0` when the room is full
- neither function changes the chart it was given

> [!WARNING]
> Test with `if value is None`, not `if not value`. A truthiness test also fires for `0`, `""` and an empty list, so it would report a seat as empty for the wrong reason — and the graders for later tasks in this set feed charts that punish it.

## Hints
### Hint 1
Both functions are one pass over the chart with one condition inside. The first one needs the seat number as well as the value, so loop over pairs; the second only needs the values. The condition is the same in both: is this value `None`? Use `is`, not `==`, and definitely not a bare `if value:`.
### Hint 2
`find_all_available_seats(seats)` — you need **both** halves of each pair, the seat number and who is in it, so iterate the dict's items rather than just its keys. Test the guest against `None` with `is`, not `==`, and collect the seat *number*, not the guest. A loop with an `append` is fine; a comprehension is the same thing on one line.

`current_empty_seat_capacity(seats)` — here the seat numbers are irrelevant, so iterate the dict's *values* instead and count how many are `None`. Three spellings all pass: a counter in a loop, the length of whatever the first function returns, or a single summing expression over a generator.
### Hint 3
Different data, same pass. A config dict where an unset option is `None`:

```python
config = {"region": "eu-west-1", "retries": None, "timeout": 0, "log_level": None}

missing = [key for key, value in config.items() if value is None]
# -> ['retries', 'log_level']
how_many = sum(1 for value in config.values() if value is None)
# -> 2
```

`timeout` is `0`, which is falsy but very much set — swap `value is None` for `not value` and it joins the missing list, which is the bug this task is teaching you to avoid.
