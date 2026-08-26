---
title: none — seat the walk-ins, clear the tables
minutes: 13
prereqs: [203, 209, 224, 227, 239, 258]
tags: [exercism, none, core]
source: exercism/python concept/restaurant-rozalynn (MIT, adapted)
---
# none — seat the walk-ins, clear the tables

*`None` — writing the placeholder back, and the all-or-nothing update.*

## Why
Four people walk in without a reservation. Either the room can take all four or it can take none of them — you do not seat two and leave the couple standing, so the check has to happen before a single name goes on the chart. And when a table finishes, its seats have to go back to being genuinely empty, which means writing `None` over the names rather than deleting the keys, so the chart keeps its shape and the seat still exists to be given away again. Check-then-write, and reset-to-placeholder: the same two moves as a stock reservation in an ordering system, or releasing a lease back into a pool.

## Introduction

In Python, `None` is frequently used to represent the absence of a value -- a placeholder to define a `null` (empty) variable, object, or argument.

If you've heard about or used a `NULL` or `nil` type in another programming language, then this usage of `None` in Python will be familiar to you. `None` helps you to declare variables or function arguments that you don't yet have values for. These can then be re-assigned to specific values later as needed.

```python
a = None
print(a)
#=> None
type(a)
#=> <class 'NoneType'>

# Adding a Default Argument with `None`
def add_to_todos(new_task, todo_list=None):
  if todo_list is None:
    todo_list = []
    todo_list.append(new_task)
  return todo_list

```

`None` will evaluate to `False` when used in a conditional check, so it is useful for validating the "presence of" or "absence of" a value - _any_ value -- a pattern frequently used when a function or process might hand back an error object or message.

```python
a = None
if a: #=> a will be evaluated to False when its used in a conditional check.
    print("This will not be printed")
```

## Instructions

You are the Maître D' of a hotel restaurant.
Your task is to manage the seating arrangements for the dining room according to the number of seats available today, number of reservations, and the "walk in" guests currently waiting to be seated.
For the purposes of this exercise, seating is assigned by first available empty seat.

For this exercise, you have 6 different dining room organization challenges to complete.

### 1. Make Today's Seating Chart

Define the `new_seating_chart(<size=22>)` function that takes a size argument representing the number of seats that will be set in the dining room today.
If no `size` is given, the function should return a seating chart with 22 seats.
Seat values should have a placeholder of `None` to indicate they are available to assign to a guest.

### 2. Arrange Reservations

Define the `arrange_reservations(<guest_names>)` function with 1 parameter for a list of guest names.
This represents the number of people who have places reserved in the dining room today.

This function should return a `dict` seating chart of default size (22 seats), with guests assigned to seats in the order they appear on the reservation list.
All unassigned seats should be set to `None`.
If there are no guests, an "empty" seating chart with all `None` placeholders should be returned.

```python
>>> arrange_reservations(guests=["Walter", "Frank", "Jenny", "Carol", "Alice", "George"])
...
{1: 'Walter', 2: 'Frank', 3: 'Jenny', 4: 'Carol', 5: 'Alice', 6: 'George', 7: None, 8: None, 9: None, 10: None, 11: None, 12: None, 13: None, 14: None, 15: None, 16: None, 17: None, 18: None, 19: None, 20: None, 21: None, 22: None}
```

### 3. Find All the "Empty" Seats

Define the `find_all_available_seats(<seats>)` function that takes 1 parameter (_a seating chart dictionary_) and returns a `list` of seat numbers that are available for guests that are currently waiting.
If a seat is empty, It will be of `None` value in the dictionary. Occupied seats will have the name of the guest.

```python
>>> seats = {1: None, 2: 'Frank', 3: 'Jenny', 4: None, 5: 'Alice', 6: 'George', 7: None, 8: 'Carol', 9: None, 10: None, 11: None, 12: 'Walter'}

>>> find_all_available_seats(seats)
[1,4,7,9,10,11]
```

### 4. Current Empty Seating Capacity

Define the `current_empty_seat_capacity(<seats>)` function that takes 1 parameter - the `dict` of existing seat reservations.
The function should return the total number of seats that are empty.

```python
>>> curr_empty_seat_capacity({1: "Occupied", 2: None, 3: "Occupied"})
1

>>> curr_empty_seat_capacity({1: "Occupied", 2: None, 3: None})
2
```

### 5. Should we wait?

Define the `accommodate_waiting_guests(<seats>, <guests>)` function that takes two parameters.
The first parameter will be a seating chart `dict`.
The second parameter will be a `list` of guests who have "walked in" unexpectedly.
You'll first need to find out how many seats are available and whether or not you can even give the unannounced guests seats at this time.

If you do not have enough seats, return the seating chart `dict` unaltered.

If seats _are_ available, assign the guests places on the seating chart, and return it updated.
**Tip:** You can use previously defined functions to do the calculations for you.

```python
# Guests cannot be accommodated.
>>> starting_reservations = {1: 'Carol', 2: 'Alice', 3: 'George', 4: None, 5: None, 6: None, 7: 'Frank', 8: 'Walter'}
>>> accommodate_guests(starting_reservations, ["Mort", "Suze", "Phillip", "Tony"])
...
{1: 'Carol', 2: 'Alice', 3: 'George', 4: None, 5: None, 6: None, 7: 'Frank', 8: 'Walter'}

# Guests can be accommodated.
>>> starting_reservations = {1: None, 2: None, 3: None, 4: 'Carol', 5: 'Alice', 6: 'George', 7: None, 8: None, 9: None, 10: None, 11: None, 12: None, 13: None, 14: None, 15: None, 16: None, 17: None, 18: 'Frank', 19:  'Jenny', 20: None, 21: None, 22: 'Walter'}
>>> accommodate_guests(starting_reservations, ["Mort", "Suze", "Phillip", "Tony"])
...
{1: 'Mort', 2: 'Suze', 3: 'Phillip', 4: 'Carol', 5: 'Alice', 6: 'George', 7: 'Tony', 8: None, 9: None, 10: None, 11: None, 12: None, 13: None, 14: None, 15: None, 16: None, 17: None, 18: 'Frank', 19: 'Jenny', 20: None, 21: None, 22: 'Walter'}
```

### 6. Empty Seats

Define the `empty_seats(<seats>, <seat_numbers>)` function that takes two parameters.
The first parameter will be a seating chart dictionary.
The second parameter is a list of seat numbers you need to "free up" or empty -- that is, you need to assign the seat number value to `None`.

Return the `dict` of seats after updating the "to empty" seat values.

```python
>>> empty_seats(seats={1: "Alice", 2: None, 3: "Bob", 4: "George", 5: "Gloria"}, seat_numbers=[5,3,1])
{1: None, 2: None, 3: None, 4: "George", 5: None}
```

## You get
Nothing. `solve()` takes **no arguments**; the seating charts arrive as arguments to the functions you hand back.

> [!NOTE]
> Exercism asks for all six functions in one `none.py`. Here the task is split in three: **this task covers tasks 5 and 6** — updating a chart. Tasks 1 and 2 are task `257_restaurant_rozalynn`; tasks 3 and 4 are task `258_restaurant_rozalynn`. Exercism suggests reusing the functions from those tasks; here you are welcome to write the one or two lines you need inline instead.

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

## Exercism hints

### General

- In Python, `None` is frequently used as a placeholder to represent the **absence of a value** for a variable, object, or argument.

### 1. Make New Seating Chart

Remember, you will need to create an empty dictionary first. Next, fill the dictionary _keys_ with however many seats are available and set their _values_ to a **placeholder** to indicate that they are available but unassigned.

### 2. Arrange Reservations

- If there isn't a guest list, you will want to return a `new_seating_chart()` filled with placeholders. A `default argument` for your function might be helpful here. If you do have a guest list, you can start with a `new_seating_chart()`, then loop from 1 to the number of guests and assign them to seats in order.

### 3. Find all Available Seats

- You can loop through all the (key, value) pairs in a dictionary by calling `dict.items()`. You can verify that a variable or value is None through an `if statement` -- `if var is None` will return True if the value is `None`. You can add things to a `list` by calling `list.append()`

### 4. Current seating capacity

- You can loop through all of the values in the dict object by calling `dict.values()`. Seats are available when their value is `None`.

### 5. Accommodate Waiting Guests

- You need to find the current number of empty seats and check to see if it is greater than or equal to the number of guests waiting. If the guests can be accommodated, you will need to call `find_all_available_seats()` to get a list of seat numbers you can assign guests to. Remember that `range()` can take any sort of number as an argument....**including** the number returned from calling `len()` on a list. Also remember that using `list[index_number]` will return the **value** that is located at the **index number** inside the brackets.

### 6. Empty the Seats

- Given the seating chart `dict`, and a `list` of seat numbers, you'll want to indicate the seat is now available for another guest by replacing their name with a placeholder. Looping through the seat number list and looking for those seats in the dictionary might be helpful here.

## Read first
- [None (the standard type hierarchy)](https://docs.python.org/3/library/stdtypes.html#the-null-object) — the placeholder you write back into a seat
- [`is` and `is not`](https://docs.python.org/3/reference/expressions.html#is-not) — how to spot an empty seat without tripping over `0` or `""`
- [dict.items()](https://docs.python.org/3/library/stdtypes.html#dict.items) — walking keys and values together to find the empty ones
- [Assigning into a dict](https://docs.python.org/3/tutorial/datastructures.html#dictionaries) — `chart[seat] = name` adds or overwrites in place; the dict you were handed is the dict the caller sees
- [enumerate()](https://docs.python.org/3/library/functions.html#enumerate) — pairing each guest with a position so you can index into the list of empty seats
- [len()](https://docs.python.org/3/library/functions.html#len) — the comparison that decides whether anybody sits down

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

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
