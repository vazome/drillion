---
title: none — seat the walk-ins, clear the tables
difficulty: medium
tier: core
minutes: 13
prereqs: [40]
tags: [none]
source: exercism/python concept/restaurant-rozalynn (MIT, adapted)
---
# none — seat the walk-ins, clear the tables

*`None` — writing the placeholder back, and the all-or-nothing update.*

## Read first
- [None (the standard type hierarchy)](https://devdocs.io/python~3.14/library/stdtypes#the-null-object) — the placeholder you write back into a seat
- [`is` and `is not`](https://devdocs.io/python~3.14/reference/expressions#is-not) — how to spot an empty seat without tripping over `0` or `""`
- [dict.items()](https://devdocs.io/python~3.14/library/stdtypes#dict.items) — walking keys and values together to find the empty ones
- [Assigning into a dict](https://devdocs.io/python~3.14/tutorial/datastructures#dictionaries) — `chart[seat] = name` adds or overwrites in place; the dict you were handed is the dict the caller sees
- [enumerate()](https://devdocs.io/python~3.14/library/functions#enumerate) — pairing each guest with a position so you can index into the list of empty seats
- [len()](https://devdocs.io/python~3.14/library/functions#len) — the comparison that decides whether anybody sits down

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Four people walk in without a reservation. Either the room can take all four or it can take none of them — you do not seat two and leave the couple standing, so the check has to happen before a single name goes on the chart. And when a table finishes, its seats have to go back to being genuinely empty, which means writing `None` over the names rather than deleting the keys, so the chart keeps its shape and the seat still exists to be given away again. Check-then-write, and reset-to-placeholder: the same two moves as a stock reservation in an ordering system, or releasing a lease back into a pool.

## You get
Nothing. `solve()` takes **no arguments**; the seating charts arrive as arguments to the functions you hand back.

> [!NOTE]
> Exercism asks for all six functions in one `none.py`. Here the task is split in three: **this task covers tasks 5 and 6** — updating a chart. Tasks 1 and 2 are task `039_restaurant_rozalynn`; tasks 3 and 4 are task `040_restaurant_rozalynn`. Exercism suggests reusing the functions from those tasks; here you are welcome to write the one or two lines you need inline instead.

## You return
A dict with these two functions.

| key | parameters | returns |
| --- | --- | --- |
| `"accommodate_waiting_guests"` | `seats` — a seating chart dict; `guests` — a list of walk-in names | the chart. If there are at least as many empty seats as guests, every guest is seated, filling the empty seats from the lowest seat number upwards, in the order the guests are listed. If there are not enough, the chart comes back **unchanged** |
| `"empty_seats"` | `seats` — a seating chart dict; `seat_numbers` — a list of seat numbers to free up | the chart, with each of those seats set back to `None` |

```python
front_of_house = solve()

chart = {1: None, 2: None, 3: None, 4: "Carol", 5: "Alice", 6: "George", 7: None, 8: None}
front_of_house["accommodate_waiting_guests"](chart, ["Mort", "Suze", "Phillip", "Tony"])
# -> {1: "Mort", 2: "Suze", 3: "Phillip", 4: "Carol",
#     5: "Alice", 6: "George", 7: "Tony", 8: None}

full = {1: "Carol", 2: "Alice", 3: "George", 4: None, 5: None, 6: None,
        7: "Frank", 8: "Walter"}
front_of_house["accommodate_waiting_guests"](full, ["Mort", "Suze", "Phillip", "Tony"])
# -> the same chart, untouched: 4 guests, only 3 empty seats

front_of_house["empty_seats"]({1: "Alice", 2: None, 3: "Bob", 4: "George", 5: "Gloria"},
                              [5, 3, 1])
# -> {1: None, 2: None, 3: None, 4: "George", 5: None}
```

## Rules
- the dict keys are exactly the two strings above, and each value is the function **itself** — `{"empty_seats": empty_seats}`, no parentheses
- both functions **return the chart**, not `None` — updating in place and then returning it is exactly what Exercism's tests expect
- `accommodate_waiting_guests` is all or nothing: with fewer empty seats than guests, nothing is written at all
- the guests fill the empty seats in seat-number order — first guest into the lowest-numbered empty seat, and note that a seat in the middle of the chart may be the lowest empty one
- an empty seat is one whose value **is** `None`; `empty_seats` makes a seat empty by assigning `None` to it, never by deleting the key
- `empty_seats` with an empty list of seat numbers leaves the chart exactly as it was
- a seat number handed to `empty_seats` is always already in the chart

> [!WARNING]
> "Enough seats" means `len(guests) <= number of empty seats` — equal counts still work, and the room simply ends up full. Seat the guests one at a time only **after** that check has passed; writing as you go and stopping when you run out leaves half the party seated, which the grader fails.

## Hints
### Hint 1
`empty_seats` is a loop with one assignment in it — for each seat number you were given, put `None` in that slot, then return the chart. `accommodate_waiting_guests` is that same idea with a gate in front of it: first work out which seats are empty, then compare how many there are against how many guests are waiting, and only start writing if the answer is yes.
### Hint 2
`accommodate_waiting_guests(seats, guests)` — start with the list of empty seat numbers, the same pass you wrote for 258. That list does double duty: its **length** is the capacity you compare against `len(guests)`, and its **contents**, in order, are the seats to fill. To put the first guest in the first empty seat you need the guest *and* its position in the queue at the same time — one builtin hands you both while looping. Return `seats` on both paths: inside the `if` and outside it, the same object goes back.

`empty_seats(seats, seat_numbers)` — walk the seat numbers you were handed and clear each one. No need to check whether a seat was occupied first; clearing an already-empty seat is harmless.
### Hint 3
Different data, same two moves. Handing out connections from a pool, and giving them back:

```python
def lease(pool, jobs):
    free = [slot for slot, holder in pool.items() if holder is None]
    if len(jobs) <= len(free):
        for index, job in enumerate(jobs):
            pool[free[index]] = job
    return pool

def release(pool, slots):
    for slot in slots:
        pool[slot] = None
    return pool

pool = {1: None, 2: "backup", 3: None}
lease(pool, ["reindex"])           # -> {1: 'reindex', 2: 'backup', 3: None}
lease(pool, ["a", "b"])            # -> unchanged: 2 jobs, 1 free slot
release(pool, [1, 2])              # -> {1: None, 2: None, 3: None}
```

`release` writes `None` rather than doing `del pool[slot]`: the slot has to still exist to be leased again.
