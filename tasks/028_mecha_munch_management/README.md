---
title: dict-methods — sorting the cart and updating the shelves
difficulty: medium
tier: core
minutes: 15
prereqs: [27]
tags: [dict-methods]
source: exercism/python concept/mecha-munch-management (MIT, adapted)
---
# dict-methods — sorting the cart and updating the shelves

*Dict views, `sorted()`, and why insertion order is the answer.*

## Read first
- [Mapping types — dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — every method in one table; worth skimming end to end once
- [dict.setdefault()](https://devdocs.io/python~3.14/library/stdtypes#dict.setdefault) — insert-if-missing and return, in one call
- [dict.fromkeys()](https://devdocs.io/python~3.14/library/stdtypes#dict.fromkeys) — build a whole dict from an iterable of keys sharing one default value
- [dict.update()](https://devdocs.io/python~3.14/library/stdtypes#dict.update) — merge in another mapping *or* an iterable of pairs, in place
- [Dictionary view objects](https://devdocs.io/python~3.14/library/stdtypes#dict-views) — `.keys()`, `.values()` and `.items()` are live views, not copies
- [Sorting HOW TO](https://devdocs.io/python~3.14/howto/sorting) — `sorted()`, `key=` and `reverse=`
- [Real Python: dictionaries in Python](https://realpython.com/python-dicts/) — the long-form tour
- [David Beazley: Built-in Super Heroes (video)](https://www.youtube.com/watch?v=lyDLAutA88s) — why the plain built-in dict is usually the right answer

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
The cart works; now the app has to talk to the shop. Customers want their cart alphabetised so they can spot the "Potato" they already added as "potatoes". The pickers in the store want the same cart in reverse order with the aisle number and whether the item needs refrigeration attached. And the store's own stock has to come down by whatever just went out of the door, with anything that hits zero marked out of stock rather than left as a bare `0`. Three tasks, all of them about reading a dictionary through its views and rebuilding it in the order somebody else needs.

## You get
Nothing. Carts, aisle maps and inventories arrive as arguments to your functions.

> [!NOTE]
> Exercism asks for six functions in one `dict_methods.py`. Here the task is split in two: tasks 1–3 are task `027_mecha_munch_management`, and **this task covers tasks 4–6**. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"sort_entries"` | `cart` — a `{item: quantity}` dict | a new cart dict with the same entries, keys in alphabetical order |
| `"send_to_store"` | `cart`; `aisle_mapping` — `{item: [aisle, needs_refrigeration]}` | a fulfillment dict `{item: [quantity, aisle, needs_refrigeration]}`, keys in **reverse** alphabetical order |
| `"update_store_inventory"` | `fulfillment_cart` — what was just ordered; `store_inventory` — `{item: [count, aisle, needs_refrigeration]}` | the store inventory with each ordered count subtracted, and `'Out of Stock'` where a count reaches zero |

```python
app = solve()
app["sort_entries"]({'Banana': 3, 'Apple': 2, 'Orange': 1})
# -> {'Apple': 2, 'Banana': 3, 'Orange': 1}
app["send_to_store"]({'Apple': 2, 'Milk': 2},
                     {'Apple': ['Aisle 4', False], 'Milk': ['Aisle 2', True]})
# -> {'Milk': [2, 'Aisle 2', True], 'Apple': [2, 'Aisle 4', False]}
app["update_store_inventory"]({'Apple': [2, 'Aisle 4', False]},
                              {'Apple': [2, 'Aisle 4', False]})
# -> {'Apple': ['Out of Stock', 'Aisle 4', False]}
```

## Rules
- this task implements **Exercism tasks 4, 5 and 6 only** — `add_item`, `read_notes` and `update_recipes` belong to task `027_mecha_munch_management`
- `sort_entries` sorts by key, A→Z; `send_to_store` sorts by key, Z→A
- a fulfillment entry is a **new list** — `[quantity, aisle, needs_refrigeration]` — built from the cart's quantity and the aisle map's two values
- `aisle_mapping` may list items the customer did not order; only what is in the cart goes into the fulfillment dict
- `update_store_inventory` replaces the count with the string `'Out of Stock'` — spelled exactly like that, capitals included — when, and only when, the remaining count is exactly `0`; the aisle and refrigeration entries stay as they are
- the store inventory keeps its own key order; only the two sorting functions care about order

> [!WARNING]
> Two dicts with the same entries in a different order compare equal with `==`, so a wrong order will *not* look wrong when you print it. The tests compare the entries position by position, which is why `sort_entries` and `send_to_store` really do have to build the new dict in the right order.

## Hints
### Hint 1
A dictionary remembers the order its keys went in, and that is the whole trick behind the first two tasks: you cannot "sort a dict" in place, you build a **new** one whose keys are inserted in the order you want. [`sorted()`](https://devdocs.io/python~3.14/library/functions#sorted) over the pairs from [`.items()`](https://devdocs.io/python~3.14/library/stdtypes#dict.items) gives you that order, and `dict(...)` turns sorted pairs back into a dictionary.
### Hint 2
`sorted()` takes `reverse=True` when the store wants Z→A, so tasks 4 and 5 differ by one keyword argument at the end.

For the fulfillment cart, walk the **customer's cart** — its keys are the items actually ordered, and the aisle map may well list more — look each item up in the aisle map, and put the quantity in front of the aisle information in a *new* list, so nothing you were handed gets modified.

For the last task, [`.items()`](https://devdocs.io/python~3.14/library/stdtypes#dict.items) hands you the key and the value together, the value being the `[count, aisle, chilled]` list, so `store_inventory[key][0]` is the number to reduce. Check for zero *after* subtracting, and swap the number — not the whole list — for the out-of-stock message.
### Hint 3
Different data, same shape. Seats sold out of a venue:

```python
seats = {"balcony": [4, "upstairs"], "stalls": [10, "ground"]}
booked = {"balcony": [4, "upstairs"]}

for row, values in booked.items():
    seats[row][0] -= values[0]
    if seats[row][0] == 0:
        seats[row][0] = "Sold Out"

seats                                  # -> {'balcony': ['Sold Out', 'upstairs'],
                                       #     'stalls': [10, 'ground']}
dict(sorted(seats.items(), reverse=True))   # -> keys in the order 'stalls', 'balcony'
```

Only element `0` of each list changed; the rest of the row description is left exactly as it was.
