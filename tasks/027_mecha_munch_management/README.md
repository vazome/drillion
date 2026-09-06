---
title: dict-methods — filling the shopping cart
difficulty: medium
tier: core
minutes: 14
prereqs: [25]
tags: [dict-methods]
source: exercism/python concept/mecha-munch-management (MIT, adapted)
---
# dict-methods — filling the shopping cart

*`setdefault`, `dict.fromkeys` and `update` — one method per task.*

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
Mecha Munch is a grocery-ordering app, and you have the cart end of the MVP: put things in the cart, start a cart from the list a customer typed into their notes app, and let the content team swap out a whole recipe's ingredients. Three tasks, and each one is really "which `dict` method already does this?". Knowing the method table is what separates a five-line loop with a `KeyError` in it from a one-liner that reads like the sentence in the ticket.

## You get
Nothing. Carts, notes and recipes arrive as arguments to your functions.

> [!NOTE]
> Exercism asks for six functions in one `dict_methods.py`. Here the task is split in two: **this task covers tasks 1–3**, and tasks 4–6 are task `028_mecha_munch_management`. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"add_item"` | `current_cart` — the cart dict; `items_to_add` — any list-like iterable of names, repeats meaning quantity | the cart with each listed item up by one, new items starting at one |
| `"read_notes"` | `notes` — any list-like iterable of item names | a fresh cart dict with every name at quantity `1` |
| `"update_recipes"` | `ideas` — a dict of `recipe name -> ingredients dict`; `recipe_updates` — an iterable of `(recipe name, ingredients dict)` pairs | the ideas dict with each named recipe replaced, or added when the name is new |

```python
app = solve()
app["add_item"]({'Banana': 3, 'Apple': 2}, ('Apple', 'Apple', 'Banana'))
# -> {'Banana': 4, 'Apple': 4}
app["read_notes"](('Banana', 'Apple', 'Orange'))
# -> {'Banana': 1, 'Apple': 1, 'Orange': 1}
app["update_recipes"](
    {'Apple Pie': {'Apple': 1, 'Pie Crust': 1}},
    (('Apple Pie', {'Apple': 3, 'Pie Crust': 1, 'Cinnamon': 1}),))
# -> {'Apple Pie': {'Apple': 3, 'Pie Crust': 1, 'Cinnamon': 1}}
```

## Rules
- this task implements **Exercism tasks 1, 2 and 3 only** — `sort_entries`, `send_to_store` and `update_store_inventory` belong to task `028_mecha_munch_management`
- `items_to_add` and `notes` may be a `list` **or** a `tuple` — anything you can loop over
- quantity is expressed by **repeats**: `'Apple'` three times in the iterable means three apples
- an item already in the cart goes up by one; an item new to the cart starts at `1`
- `read_notes` gives every item the quantity `1`, and a name that appears twice in the notes still ends up as one key
- an update **replaces the whole ingredients dict** for that recipe — it does not merge ingredient by ingredient
- all three functions return a dict

> [!WARNING]
> `current_cart[item] += 1` raises `KeyError` for an item the cart has never held. Reach for the method that takes a default instead of wrapping it in `try`.

## Hints
### Hint 1
Roughly one `dict` method per task. Task 1 is a loop with [`setdefault(item, 0)`](https://devdocs.io/python~3.14/library/stdtypes#dict.setdefault) in it, so a brand-new product does not raise `KeyError` before you add 1 to it. Task 2 needs no loop at all: there is a *classmethod* that builds an entire dictionary from an iterable of keys with one shared default value. Task 3 is famously a single call — the key word in the task title is *update*.
### Hint 2
For task 1, quantity is repeats, so one pass over the iterable adding 1 each time is exactly right; write the loop against *any* iterable rather than assuming a list, because the tests pass tuples too.

For task 2, the default value matters: [`dict.fromkeys(keys)`](https://devdocs.io/python~3.14/library/stdtypes#dict.fromkeys) with no second argument fills every value with `None`, and the app wants `1`.

For task 3, remember that [`dict.update()`](https://devdocs.io/python~3.14/library/stdtypes#dict.update) accepts an iterable of `(key, value)` pairs, not only another dict — which is precisely the shape the recipe updates arrive in. Each pair replaces the whole value under that key, or adds the key when it is new. Then return the dict you updated.
### Hint 3
Different data, same shape. A permissions table and a region health map:

```python
roles = {"viewer": {"read": True}}
roles.update((("editor", {"read": True, "write": True}),))
# roles == {'viewer': {'read': True},
#           'editor': {'read': True, 'write': True}}

dict.fromkeys(("eu-west-1", "us-east-1", "ap-south-1"), "healthy")
# -> {'eu-west-1': 'healthy', 'us-east-1': 'healthy', 'ap-south-1': 'healthy'}
```

Note the extra comma in `(("editor", {...}),)` — `update` wants an *iterable of pairs*, and one pair on its own still has to be wrapped in something iterable.
