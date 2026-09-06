---
title: sets — dedupe the recipes, build the shopping list
difficulty: easy
tier: core
minutes: 14
prereqs: [25]
tags: [sets]
source: exercism/python concept/cater-waiter (MIT, adapted)
---
# sets — dedupe the recipes, build the shopping list

*Sets — the constructor, `union`, and `difference`, on a catering menu.*

## Read first
- [Set types — set, frozenset](https://devdocs.io/python~3.14/library/stdtypes#set) — the full method table, and the line that matters here: the `set()` constructor accepts any iterable
- [set.union()](https://devdocs.io/python~3.14/library/stdtypes#frozenset.union) — merge many collections into one set; the operator form is `|`
- [set.difference()](https://devdocs.io/python~3.14/library/stdtypes#frozenset.difference) — everything in the first set that is not in the others; the operator form is `-`
- [Real Python: Sets in Python](https://realpython.com/python-sets/) — a walk through the operations with pictures of the overlaps
- [Set and logic symbols cheat sheet](http://notes.imt-decal.org/sets/cheat-sheet.html) — the maths notation the method names come from

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A small catering firm has agreed to run an evening for a cooking club, and the recipes came in from a dozen different sources. The same ingredient is listed three times in one recipe, twice in another, and the shopping list is built by hand from all of them — so the firm buys three bags of chickpeas and forgets the cilantro. Three chores in this task are the whole of that problem: strip the duplicates out of one recipe, merge every recipe into one master shopping list, and take the tray-passed appetizers back out of the list of dishes that get plated. Each one is a single set operation. The same three moves show up whenever you merge config files, collect the unique hosts out of a log, or subtract an exclusion list from a target list.

## You get
Nothing. `solve()` takes **no arguments**; the ingredients arrive as arguments to the functions you hand back.

> [!NOTE]
> Exercism asks for all seven functions in one `sets.py`. Here the task is split in three: **this task covers tasks 1, 5 and 6** — the ones that are pure set arithmetic and need no reference data. Tasks 2 and 4 are task `033_cater_waiter`; tasks 3 and 7 are task `034_cater_waiter`.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"clean_ingredients"` | `dish_name` (a string), `dish_ingredients` (a list, possibly with repeats) | a tuple: the dish name unchanged, then the de-duplicated ingredients as a `set` |
| `"compile_ingredients"` | `dishes` — a list where each dish is a `set` of its ingredients | one `set` holding every ingredient that appears in any of the dishes |
| `"separate_appetizers"` | `dishes`, `appetizers` — two lists of dish *names*, either of which may contain duplicates | a `list` of the dish names that are not appetizers, each name appearing once |

```python
kitchen = solve()

kitchen["clean_ingredients"]("Punjabi-Style Chole", ["chickpeas", "ginger", "chickpeas"])
# -> ("Punjabi-Style Chole", {"chickpeas", "ginger"})

kitchen["compile_ingredients"]([{"tofu", "ginger"}, {"pears", "ginger"}])
# -> {"tofu", "ginger", "pears"}

kitchen["separate_appetizers"](["Barley Risotto", "Asparagus Puffs", "Barley Risotto"],
                              ["Asparagus Puffs"])
# -> ["Barley Risotto"]
```

## Rules
- the dict keys are exactly the three strings above, and each value is the function **itself** — `{"clean_ingredients": clean_ingredients}`, no parentheses
- `clean_ingredients` returns a **tuple** of two things, and the second one is a `set`, not a sorted list
- `compile_ingredients` returns a `set`, and an empty list of dishes gives back an empty set
- `separate_appetizers` returns a `list`, and any name that appears in both lists is gone from the result

> [!WARNING]
> `separate_appetizers` must return a `list` — the grader checks the type before it checks the contents, so handing back a `set` fails even when the names are right. Its order does not matter: the grader sorts both sides before comparing.

## Hints
### Hint 1
None of these three needs an `if`. Each one is a single set operation that Python already has a name for: "keep each item once" is what building a `set` from a list does for free; "everything from all of them" has a method whose operator is `|`; "these, but not those" has a method whose operator is `-`. The `set()` constructor takes any iterable, so a `list` of ingredients goes straight in.
### Hint 2
Shape of the work, one function at a time.

- `clean_ingredients` — build a set from `dish_ingredients`, then return two things separated by a comma. A comma in a `return` builds a tuple; the dish name goes first, untouched.
- `compile_ingredients` — start from an empty `set()` (curly braces on their own build an empty *dict*, so you need the constructor) and loop over the dishes, unioning each one in. `combined = combined | ingredients` and `combined |= ingredients` and `combined.union(ingredients)` all say the same thing.
- `separate_appetizers` — turn both lists into sets, subtract the appetizers from the dishes, and hand the result to `list()`, because a set is not a list and the grader checks.
### Hint 3
Different data, same three moves — cleaning up a fleet inventory:

```python
tags = ["prod", "eu-west-1", "prod", "team-a"]
unique_tags = set(tags)                       # -> {'prod', 'eu-west-1', 'team-a'}

all_tags = set()
for host in [{"prod", "db"}, {"prod", "web"}]:
    all_tags |= host                          # -> {'prod', 'db', 'web'}

hosts = ["web-1", "web-2", "web-1", "bastion"]
retired = ["bastion", "web-9"]
live = list(set(hosts) - set(retired))        # -> ['web-1', 'web-2'] in some order
```

The last line is the one to look at twice: `set(...) - set(...)` gives a set, and `list(...)` around it is what makes the return type match what the caller asked for.
