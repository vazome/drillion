---
title: dicts — building and topping up an inventory
difficulty: medium
tier: core
minutes: 14
prereqs: [23]
tags: [dicts]
source: exercism/python concept/inventory-management (MIT, adapted)
---
# dicts — building and topping up an inventory

*Counting into a dict — `setdefault`, `in`, and never below zero.*

## Read first
- [Mapping types — dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — every dict method in one table
- [Tutorial: dictionaries](https://devdocs.io/python~3.14/tutorial/datastructures#dictionaries) — the gentle introduction, with a worked counting example
- [hashable](https://devdocs.io/python~3.14/glossary#term-hashable) — why a string or a tuple may be a key and a list may not
- [dict.setdefault()](https://devdocs.io/python~3.14/library/stdtypes#dict.setdefault) — insert the default only if the key is missing, return the value either way
- [dict.items()](https://devdocs.io/python~3.14/library/stdtypes#dict.items) — the `(key, value)` view you loop over
- [w3schools: Python dictionaries](https://www.w3schools.com/python/python_dictionaries.asp) — quick reference with runnable snippets
- [collections.Counter](https://devdocs.io/python~3.14/library/collections#collections.Counter) — what production code reaches for once counting is the whole job

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A warehouse scanner produces a flat list of what came through the door: `["coal", "wood", "wood", "diamond"]`. Nobody can work with that. What the stock system needs is a count per item name, which is what a dictionary is for — key to number, updated in place as goods arrive and leave. The same shape shows up every time you tally anything: error codes per service, requests per client, files per extension.

## You get
Nothing. The inventory and the item lists arrive as arguments to your functions.

> [!NOTE]
> Exercism asks for five functions in one `dicts.py`. Here the task is split in two: **this task covers tasks 1–3**, and tasks 4–5 are task `026_inventory_management`. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"create_inventory"` | `items` — a list of item names, repeats meaning quantity | a brand-new inventory dict, `{name: count}` |
| `"add_items"` | `inventory` — an existing inventory dict; `items` — a list of names | the same inventory, each listed name up by one |
| `"decrement_items"` | `inventory`; `items` — a list of names to take out | the same inventory, each listed name down by one, floored at zero |

```python
stock = solve()
stock["create_inventory"](["coal", "wood", "wood", "diamond"])
# -> {'coal': 1, 'wood': 2, 'diamond': 1}
stock["add_items"]({"coal": 1}, ["wood", "iron", "coal", "wood"])
# -> {'coal': 2, 'wood': 2, 'iron': 1}
stock["decrement_items"]({"coal": 3, "diamond": 1}, ["diamond", "coal"])
# -> {'coal': 2, 'diamond': 0}
```

## Rules
- this task implements **Exercism tasks 1, 2 and 3 only** — `remove_item` and `list_inventory` belong to task `026_inventory_management`
- quantity is expressed by **repeats**: an item appearing three times in the list means three of it
- an item that is not in the inventory yet starts at `0` and becomes `1` when it is added
- a count never goes below `0`; once it is at `0`, further requests to decrement it are ignored
- decrementing an item the inventory has never heard of does nothing — it must **not** be created with a negative or zero count
- all three functions return the inventory dict (`add_items` / `decrement_items` update the one they were handed; returning a copy also passes)

> [!WARNING]
> `inventory[item] += 1` raises `KeyError` the first time an item is seen. Make sure the key exists before you add to it.

## Hints
### Hint 1
Each of these three functions is a `for` loop over the item list with one dictionary line inside it. The awkward moment is the first time an item shows up: `inventory[item] += 1` raises `KeyError` when the key is not there yet. [`dict.setdefault(key, 0)`](https://devdocs.io/python~3.14/library/stdtypes#dict.setdefault) makes that moment go away — it inserts the `0` only when the key is missing, and leaves an existing count alone.
### Hint 2
Write `add_items` first, then let `create_inventory` be a single line that calls it with a brand-new empty dict: an inventory built from scratch is just an empty inventory with items added to it. That is one of the two functions gone.

`decrement_items` is the mirror image, with two guards where the other had none. Skip items the inventory has never heard of — a plain `if item in inventory` covers that — and stop the count at zero instead of letting it slide negative; `max(count - 1, 0)` does that in one expression, no `if` needed.

All three hand the dictionary back at the end, so the caller sees the update.
### Hint 3
Different data, same shape. Counting HTTP statuses out of a log:

```python
def tally(codes):
    counts = {}
    for code in codes:
        counts.setdefault(code, 0)
        counts[code] += 1
    return counts

tally(["200", "404", "200", "500", "200"])
# -> {'200': 3, '404': 1, '500': 1}
```

`setdefault` is doing the "have I seen this before?" work, so the loop body stays two lines whether the code is new or the hundredth of its kind.
