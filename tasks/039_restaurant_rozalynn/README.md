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
