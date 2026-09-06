---
title: none — lay the dining room out with empty seats
difficulty: medium
tier: core
minutes: 13
prereqs: [27]
tags: [none]
source: exercism/python concept/restaurant-rozalynn (MIT, adapted)
---
# none — lay the dining room out with empty seats

*`None` — the placeholder value, and the safe default argument.*

## Read first
- [None (the standard type hierarchy)](https://devdocs.io/python~3.14/library/stdtypes#the-null-object) — there is exactly one `None` object in a running program, which is why `is` is the way to test for it
- [Default argument values](https://devdocs.io/python~3.14/tutorial/controlflow#default-argument-values) — including the warning about mutable defaults, which is the reason `None` is used here
- [Real Python: Null in Python](https://realpython.com/null-in-python/) — `None` compared with `NULL`, `nil` and friends, and what it is *not*
- [Dict comprehensions](https://devdocs.io/python~3.14/tutorial/datastructures#dictionaries) — `{key: value for ...}`, the shortest way to lay out a chart
- [range()](https://devdocs.io/python~3.14/library/functions#func-range) — off by one lives here: `range(1, size + 1)` is the seats you want
- [enumerate()](https://devdocs.io/python~3.14/library/functions#enumerate) — walk a guest list and get the position alongside each name

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
The maître d' needs tonight's seating chart before a single guest walks in: twenty-two seats, all of them empty, each one ready to be given a name. "Empty" has to be a value you can actually store — not a missing key, not an empty string that later gets printed on a place card. That value is `None`, and this is the job it exists for. The second half of the task is the other place `None` earns its keep: as the default for an argument that might not be given, so `arrange_reservations()` with no reservation list still hands back a valid chart instead of blowing up.

## You get
Nothing. `solve()` takes **no arguments**; the guest lists arrive as arguments to the functions you hand back.

> [!NOTE]
> Exercism asks for all six functions in one `none.py`. Here the task is split in three: **this task covers tasks 1 and 2** — building charts. Tasks 3 and 4 are task `040_restaurant_rozalynn`; tasks 5 and 6 are task `041_restaurant_rozalynn`.

## You return
A dict with these two functions.

| key | parameters | returns |
| --- | --- | --- |
| `"new_seating_chart"` | `size` — how many seats to set today, **defaulting to 22** when the caller does not say | a `dict` whose keys are the seat numbers `1` to `size` and whose every value is `None` |
| `"arrange_reservations"` | `guests` — a list of names, **defaulting to no list at all** so the function can be called with no arguments | a 22-seat chart with the guests seated from seat 1 upwards in the order they were listed, every remaining seat still `None` |

```python
front_of_house = solve()

front_of_house["new_seating_chart"](3)
# -> {1: None, 2: None, 3: None}

len(front_of_house["new_seating_chart"]())
# -> 22

front_of_house["arrange_reservations"](["Walter", "Frank", "Jenny"])
# -> {1: "Walter", 2: "Frank", 3: "Jenny", 4: None, 5: None, ... 22: None}

front_of_house["arrange_reservations"]()
# -> {1: None, 2: None, ... 22: None}
```

## Rules
- the dict keys are exactly the two strings above, and each value is the function **itself** — `{"new_seating_chart": new_seating_chart}`, no parentheses
- seat numbers start at **1**, not 0, and run up to `size` with no gaps
- an empty seat holds `None` — not `0`, not `""`, not a missing key
- `new_seating_chart()` called with no argument gives 22 seats; `arrange_reservations()` called with no argument gives 22 empty seats
- `arrange_reservations` always returns a **22-seat** chart, whatever the length of the guest list, and there are never more guests than seats
- the first guest in the list sits in seat 1, the second in seat 2, and so on

> [!WARNING]
> Do not write `def arrange_reservations(guests=[])`. A list written in a `def` line is created **once**, shared by every call, and starts collecting whatever previous calls put in it. `None` is the default that cannot be mutated — take it and build the real list inside the function.

> [!NOTE]
> Exercism's own test file for task 2 disagrees with its instructions here: the test expects the first guest to be dropped (`{1: 'Frank', ...}`), which is an off-by-one in Exercism's example solution. This task grades the behaviour the **instructions** describe — `{1: 'Walter', 2: 'Frank', ...}`.

## Hints
### Hint 1
A seating chart is a dict from seat number to whoever is sitting there, and "nobody" is a real value you store: `None`. Build the whole chart empty first — every seat number mapped to `None` — and then the second function only has to overwrite the front of it. The number range is the fiddly part: seats are numbered from 1, so the range you loop over is not the one you would use for a list index.
### Hint 2
`new_seating_chart(size=22)` — the `= 22` in the parameter list is the whole "default size" requirement. Inside, a dict comprehension over `range(1, size + 1)` mapping every number to `None` is one line; a loop that starts from `{}` and assigns each key is the same thing spelled out.

`arrange_reservations(guests=None)` — start by calling `new_seating_chart()` with no argument, so you get the standard 22 seats. Then, if there is a guest list at all, walk it and put each name in the next seat. `enumerate(guests)` gives you `0, "Walter"` on the first pass, and the seat number you want is that index **plus one**. When `guests` is `None` there is nothing to do and the empty chart is already the right answer — `if guests:` covers both `None` and an empty list.
### Hint 3
Different data, same shape. Slots on a maintenance window, then the jobs booked into them:

```python
def new_window(slots=6):
    return {minute: None for minute in range(1, slots + 1)}

def book(jobs=None):
    window = new_window()
    if jobs:
        for index, job in enumerate(jobs):
            window[index + 1] = job
    return window

new_window(2)                  # -> {1: None, 2: None}
book(["backup", "reindex"])    # -> {1: 'backup', 2: 'reindex', 3: None, ... 6: None}
book()                         # -> {1: None, 2: None, ... 6: None}
```

`book()` with no arguments still returns a full window: that only works because the default is `None` and the real work happens inside the function.
