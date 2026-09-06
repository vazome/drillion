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
