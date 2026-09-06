---
title: dicts — removing items and reporting stock
difficulty: easy
tier: core
minutes: 12
prereqs: [25]
tags: [dicts]
source: exercism/python concept/inventory-management (MIT, adapted)
---
# dicts — removing items and reporting stock

*`pop`, `in`, and turning a dict into a sorted list of pairs.*

## Read first
- [Mapping types — dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — every dict method in one table
- [Tutorial: dictionaries](https://devdocs.io/python~3.14/tutorial/datastructures#dictionaries) — the gentle introduction, with a worked counting example
- [hashable](https://devdocs.io/python~3.14/glossary#term-hashable) — why a string or a tuple may be a key and a list may not
- [dict.setdefault()](https://devdocs.io/python~3.14/library/stdtypes#dict.setdefault) — insert the default only if the key is missing, return the value either way
- [dict.items()](https://devdocs.io/python~3.14/library/stdtypes#dict.items) — the `(key, value)` view you loop over
- [w3schools: Python dictionaries](https://www.w3schools.com/python/python_dictionaries.asp) — quick reference with runnable snippets
- [collections.Counter](https://devdocs.io/python~3.14/library/collections#collections.Counter) — what production code reaches for once counting is the whole job
- [dict.pop()](https://devdocs.io/python~3.14/library/stdtypes#dict.pop) — remove a key and hand back its value, with an optional default instead of a `KeyError`
- [sorted()](https://devdocs.io/python~3.14/library/functions#sorted) — returns a new sorted list and leaves the original alone

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
The warehouse tally exists; now people want to *read* it. Someone discontinues a product and its row has to disappear entirely, not sit at zero. Someone else wants the stock list for the morning meeting — alphabetical, and without the lines that say "none left", because a report full of zeros is noise. Deleting a key safely and turning a mapping into an ordered list of pairs are the two moves behind almost every small report you will write.

## You get
Nothing. The inventory arrives as an argument to your functions.

> [!NOTE]
> Exercism asks for five functions in one `dicts.py`. Here the task is split in two: tasks 1–3 are task `025_inventory_management`, and **this task covers tasks 4–5**. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your two functions to the grader, keyed by name.

## You return
A dict with these two functions.

| key | parameters | returns |
| --- | --- | --- |
| `"remove_item"` | `inventory` — an inventory dict; `item` — the name to drop | the inventory without that entry; unchanged if the name was not there |
| `"list_inventory"` | `inventory` | a list of `(name, count)` tuples for the items still in stock, alphabetical by name |

```python
stock = solve()
stock["remove_item"]({"coal": 2, "wood": 1, "diamond": 2}, "coal")
# -> {'wood': 1, 'diamond': 2}
stock["remove_item"]({"coal": 2, "wood": 1, "diamond": 2}, "gold")
# -> {'coal': 2, 'wood': 1, 'diamond': 2}
stock["list_inventory"]({"coal": 7, "wood": 11, "diamond": 2, "silver": 0})
# -> [('coal', 7), ('diamond', 2), ('wood', 11)]
```

## Rules
- this task implements **Exercism tasks 4 and 5 only** — `create_inventory`, `add_items` and `decrement_items` belong to task `025_inventory_management`
- `remove_item` drops the key **and** its count; asked for a name that is not there it changes nothing and raises nothing
- `list_inventory` returns a list of **tuples**, not of lists and not a dict
- only items with a count **greater than zero** appear in that list; an item sitting at `0` is skipped but stays in the inventory
- the list is sorted alphabetically by name

> [!WARNING]
> Order matters in `list_inventory`: the tests compare the list position by position, so `[('coal', 7), ('diamond', 2)]` and `[('diamond', 2), ('coal', 7)]` are not the same answer.

## Hints
### Hint 1
Both functions are about what a `dict` already gives you. Removing an entry is [`dict.pop(key)`](https://devdocs.io/python~3.14/library/stdtypes#dict.pop) — but it raises `KeyError` on a key that is not there, and the task says an unknown item must leave the inventory untouched. Either check `item in inventory` first, or hand `pop` a second argument to fall back on.
### Hint 2
`list_inventory` stacks three jobs: get the pairs, drop the ones whose count is zero, and put what is left in alphabetical order.

[`dict.items()`](https://devdocs.io/python~3.14/library/stdtypes#dict.items) gives you the pairs, and each pair is **already a tuple** — exactly the shape the task asks for, so you never build one yourself. [`sorted()`](https://devdocs.io/python~3.14/library/functions#sorted) on those pairs orders them by the first element of each, which is the name. The filter can be an `if` inside a comprehension or an `if` inside a plain loop with `append`; both read fine here.
### Hint 3
Different data, same shape. Which feature flags are actually switched on:

```python
def enabled(flags):
    return [pair for pair in sorted(flags.items()) if pair[1] > 0]

enabled({"beta_ui": 1, "dark_mode": 0, "audit_log": 3})
# -> [('audit_log', 3), ('beta_ui', 1)]
```

`sorted` did the alphabetising, `.items()` produced the tuples, and the `if` dropped `dark_mode` without deleting it from the flag table.
