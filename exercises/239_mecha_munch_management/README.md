---
title: dict-methods — filling the shopping cart
minutes: 14
prereqs: [236]
tags: [exercism, dict-methods, data-structures]
source: exercism/python concept/mecha-munch-management (MIT, adapted)
---
# dict-methods — filling the shopping cart

*`setdefault`, `dict.fromkeys` and `update` — one method per task.*

## Why
Mecha Munch is a grocery-ordering app, and you have the cart end of the MVP: put things in the cart, start a cart from the list a customer typed into their notes app, and let the content team swap out a whole recipe's ingredients. Three tasks, and each one is really "which `dict` method already does this?". Knowing the method table is what separates a five-line loop with a `KeyError` in it from a one-liner that reads like the sentence in the ticket.

## Introduction
The `dict` class in Python provides many useful [methods][dict-methods] for working with dictionaries.
Some were introduced in the concept for `dicts`.
Here we cover a few more - along with some techniques for iterating through and manipulating dictionaries.

### Use `setdefault()` for Error-Free Insertion

The dictionary concept previously covered that `.get(key, <default value>)` returns an existing `value` or the `default value` if a `key` is not found in a dictionary, thereby avoiding a `KeyError`.
This works well in situations where you would rather not have extra error handling but cannot trust that a looked-for `key` will be present.

For a similarly "safe" (_without KeyError_) insertion operation, there is the `.setdefault(key, <default value>)` method.
`setdefault(key, <default value>)` will return the `value` if the `key` is found in the dictionary.
If the key is **not** found, it will _insert_ the (`key`, `default value`) pair and return the `default value` for use.

```python
>>> palette_I = {'Grassy Green': '#9bc400', 'Purple Mountains Majesty': '#8076a3', 'Misty Mountain Pink': '#f9c5bd'}

# Looking for the value associated with key "Rock Brown".
# The key does not exist, so it is added with the default value, and the value is returned.
>>> palette_I.setdefault('Rock Brown', '#694605')
'#694605'

# The (key, default value) pair has now been added to the dictionary.
>>> palette_I
{'Grassy Green': '#9bc400', 'Purple Mountains Majesty': '#8076a3', 'Misty Mountain Pink': '#f9c5bd', 'Rock Brown': '#694605'}
```

### Use `fromkeys()` to Populate a Dictionary from an Iterable

To quickly populate a dictionary with various `keys` and default values, the _class method_ [`fromkeys(iterable, <default value>)`][fromkeys] will iterate through an iterable of `keys` and create a new `dict`.
All `values` will be set to the `default value` provided:

```python
>>> new_dict = dict.fromkeys(['Grassy Green', 'Purple Mountains Majesty', 'Misty Mountain Pink'], 'fill in hex color here')

{'Grassy Green': 'fill in hex color here',
 'Purple Mountains Majesty': 'fill in hex color here',
 'Misty Mountain Pink': 'fill in hex color here'}
```

### Iterating Over Entries in a Dictionary Via Views

The `.keys()`, `.values()`, and `.items()` methods return [_iterable views_][dict-views] of a dictionary.

These views can be used to easily loop over entries without altering them.
Views are also _dynamic_ -- when underlying dictionary data changes, the associated `view object` will reflect the change:

```python
>>> palette_I = {'Grassy Green': '#9bc400',
                 'Purple Mountains Majesty': '#8076a3',
                  'Misty Mountain Pink': '#f9c5bd'}

# Using .keys() returns a list of keys.
>>> palette_I.keys()
dict_keys(['Grassy Green', 'Purple Mountains Majesty', 'Misty Mountain Pink'])

# Using .values() returns a list of values.
>>> palette_I.values()
dict_values(['#9bc400', '#8076a3', '#f9c5bd'])

# Using .items() returns a list of (key, value) tuples.
>>> palette_I.items()
dict_items([('Grassy Green', '#9bc400'), ('Purple Mountains Majesty', '#8076a3'), ('Misty Mountain Pink', '#f9c5bd')])

# Views are dynamic.  Changing values in the dict changes all of the associated views.
>>> palette_I['Purple Mountains Majesty'] = (128, 118, 163)
>>> palette_I['Deep Red'] = '#932432'

>>> palette_I.values()
dict_values(['#9bc400', (128, 118, 163), '#f9c5bd', '#932432'])

>>> palette_I.keys()
dict_keys(['Grassy Green', 'Purple Mountains Majesty', 'Misty Mountain Pink', 'Deep Red'])

>>> palette_I.items()
dict_items([('Grassy Green', '#9bc400'), ('Purple Mountains Majesty', (128, 118, 163)), ('Misty Mountain Pink', '#f9c5bd'), ('Deep Red', '#932432')])
```

### More on `.keys()`, `.values()`, and `.items()`

In Python 3.7+, `dicts` preserve the order in which entries are inserted allowing First-in, First-out (_`FIFO`_),  iteration when using `.keys()`, `.values()`, or `.items()`.

In Python 3.8+, views are also _reversible_.
This allows keys, values, or (`key`, `value`) pairs to be iterated over in Last-in, First-out (`LIFO`) order by using `reversed(<dict>.keys())`, `reversed(<dict>.values())`, or `reversed(<dict>.items())`:

```python
>>> palette_II = {'Factory Stone Purple': '#7c677f', 'Green Treeline': '#478559', 'Purple baseline': '#161748'}

# Iterating in insertion order (First in, first out)
>>> for item in palette_II.items():
...     print(item)
...
('Factory Stone Purple', '#7c677f')
('Green Treeline', '#478559')
('Purple baseline', '#161748')


# Iterating in the reverse direction. (Last in, first out)
>>> for item in reversed(palette_II.items()):
...    print (item)
...
('Purple baseline', '#161748')
('Green Treeline', '#478559')
('Factory Stone Purple', '#7c677f')
```

### Sorting a Dictionary

Dictionaries do not have a built-in sorting method.
However, it is possible to sort a `dict` _view_ using the built-in function `sorted()` with `dict.items()`.
The sorted view can then be used to create a new dictionary.
Like iteration, the default sort is over the dictionary `keys`.

```python
# Default ordering for a dictionary is insertion order (First in, first out).
>>> color_palette = {'Grassy Green': '#9bc400', 
                    'Purple Mountains Majesty': '#8076a3', 
                    'Misty Mountain Pink': '#f9c5bd', 
                    'Factory Stone Purple': '#7c677f', 
                    'Green Treeline': '#478559', 
                    'Purple baseline': '#161748'}
 
 
# The default sort order for a dictionary uses the keys.
>>> sorted_palette = dict(sorted(color_palette.items()))
>>> sorted_palette
{'Factory Stone Purple': '#7c677f',
 'Grassy Green': '#9bc400',
 'Green Treeline': '#478559',
 'Misty Mountain Pink': '#f9c5bd',
 'Purple Mountains Majesty': '#8076a3',
 'Purple baseline': '#161748'}
```

### Combining Dictionaries with `.update()`

`<dict_one>.update(<dict_two>)` can be used to _combine_ two dictionaries.
This method will take the (`key`,`value`) pairs of `<dict_two>` and write them into `<dict_one>`:

```python
>>> palette_I = {'Grassy Green': '#9bc400',
                 'Purple Mountains Majesty': '#8076a3',
                  'Misty Mountain Pink': '#f9c5bd'}
>>> palette_II = {'Factory Stone Purple': '#7c677f',
                  'Green Treeline': '#478559',
                  'Purple Baseline': '#161748'}

>>> palette_I.update(palette_II)

# Note that new items from palette_II are added.
>>> palette_I
{'Grassy Green': '#9bc400', 'Purple Mountains Majesty': '#8076a3', 'Misty Mountain Pink': '#f9c5bd', 'Factory Stone Purple': '#7c677f', 'Green Treeline': '#478559', 'Purple Baseline': '#161748'}
```

Where keys in the two dictionaries _overlap_, the `value` in `dict_one` will be _overwritten_ by the corresponding `value` from `dict_two`:

```python
>>> palette_I =   {'Grassy Green': '#9bc400', 'Purple Mountains Majesty': '#8076a3', 'Misty Mountain Pink': '#f9c5bd', 
                   'Factory Stone Purple': '#7c677f', 'Green Treeline': '#478559', 'Purple baseline': '#161748'}
>>> palette_III = {'Grassy Green': (155, 196, 0), 'Purple Mountains Majesty': (128, 118, 163),
                   'Misty Mountain Pink': (249, 197, 189)}
>>> palette_I.update(palette_III)

# Overlapping values in palette_I are replaced with values from palette_III
>>> palette_I
{'Grassy Green': (155, 196, 0),
  'Purple Mountains Majesty': (128, 118, 163), 
  'Misty Mountain Pink': (249, 197, 189), 
  'Factory Stone Purple': '#7c677f', 
  'Green Treeline': '#478559', 'Purple baseline': '#161748'}
```

### Merge or Update Dictionaries Using Union (`|` and `|=`) Operators

Python 3.9 introduces a different means of merging `dicts`: the `union` operators.
`dict_one | dict_two` will create a **new dictionary**, made up of the (`key`, `value`) pairs of `dict_one` and `dict_two`.
When both dictionaries share keys, `dict_two` values take precedence.

```python
>>> palette_I = {'Grassy Green': '#9bc400', 'Purple Mountains Majesty': '#8076a3', 'Misty Mountain Pink': '#f9c5bd'}
>>> palette_II = {'Factory Stone Purple': '#7c677f', 'Green Treeline': '#478559', 'Purple baseline': '#161748'}
>>> new_dict = palette_I | palette_II
>>> new_dict
...
{'Grassy Green': '#9bc400',
 'Purple Mountains Majesty': '#8076a3',
 'Misty Mountain Pink': '#f9c5bd',
 'Factory Stone Purple': '#7c677f',
 'Green Treeline': '#478559',
 'Purple baseline': '#161748'}
```

`dict_one |= other` behaves similar to `<dict_one>.update(<other>)`, but in this case, `other` can be either a `dict` or an iterable of (`key`, `value`) pairs:

```python
>>> palette_III = {'Grassy Green': (155, 196, 0),
                   'Purple Mountains Majesty': (128, 118, 163),
                   'Misty Mountain Pink': (249, 197, 189)}
>>> new_dict |= palette_III
>>> new_dict
...
{'Grassy Green': (155, 196, 0),
'Purple Mountains Majesty': (128, 118, 163),
'Misty Mountain Pink': (249, 197, 189),
'Factory Stone Purple': '#7c677f',
'Green Treeline': '#478559',
'Purple baseline': '#161748'}
```

For a detailed explanation of dictionaries and methods for working with them, the [official tutorial][dicts-docs] and the [official library reference][mapping-types-dict] are excellent starting places.

[Real Python][how-to-dicts] and [Finxter][fi-dict-guide] also have very thorough articles on Python dictionaries.

[dict-methods]: https://docs.python.org/3/library/stdtypes.html#dict
[dict-views]: https://docs.python.org/3/library/stdtypes.html#dict-views
[dicts-docs]: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
[fi-dict-guide]: https://blog.finxter.com/python-dictionary
[fromkeys]: https://docs.python.org/3/library/stdtypes.html#dict.fromkeys
[how-to-dicts]: https://realpython.com/python-dicts/
[mapping-types-dict]: https://docs.python.org/3/library/stdtypes.html#mapping-types-dict

## Instructions
Mecha Munch™, a grocery shopping automation company, has just hired you to work on their ordering app.
Your team is tasked with building an MVP (_[minimum viable product][mvp]_) that manages all the basic shopping cart activities, allowing users to add, remove, and sort their grocery orders.
Thankfully, a different team is handling all the money and check-out functions!

### 1. Add Item(s) to the User's Shopping Cart

The MVP should allow the user to add items to their shopping cart.
This could be a single item or multiple items at once.
Since this is an MVP, item quantity is indicated by _repeats_.
If a user wants to add 2 Oranges, 'Oranges' will appear twice in the input iterable.
If the user already has the item in their cart, the cart quantity should be increased by 1.
If the item is _new_ to the cart, it should be added with a quantity of 1.

Create the function `add_item(<current_cart>, <items_to_add>)` that takes a cart dictionary and any list-like iterable of items to add as arguments.
It should return a new/updated shopping cart dictionary for the user.

```python
>>> add_item({'Banana': 3, 'Apple': 2, 'Orange': 1},
              ('Apple', 'Apple', 'Orange', 'Apple', 'Banana'))
{'Banana': 4, 'Apple': 5, 'Orange': 2}

>>> add_item({'Banana': 3, 'Apple': 2, 'Orange': 1},
              ['Banana', 'Orange', 'Blueberries', 'Banana'])
{'Banana': 5, 'Apple': 2, 'Orange': 2, 'Blueberries': 1}
```

### 2. Read in Items Listed in the User's Notes App

Uh-oh.
Looks like the product team is engaging in [feature creep][feature creep].
They want to add extra functionality to the MVP.
The application now has to create a shopping cart by reading items off a user's notes app.
Convenient for the users, but slightly more work for the team.

Create the function `read_notes(<notes>)` that can take any list-like iterable as an argument.
The function should parse the items and create a user shopping cart/dictionary.
Each item should be added with a quantity of 1.
The new user cart should then be returned.

```python
>>> read_notes(('Banana','Apple', 'Orange'))
{'Banana': 1, 'Apple': 1, 'Orange': 1}

>>> read_notes(['Blueberries', 'Pear', 'Orange', 'Banana', 'Apple'])
{'Blueberries' : 1, 'Pear' : 1, 'Orange' : 1, 'Banana' : 1, 'Apple' : 1}
```

### 3. Update Recipe "Ideas" Section

The app has an "ideas" section that's filled with finished recipes from various cuisines.
The user can select any one of these recipes and have all its ingredients added to their shopping cart automatically.
The project manager has asked you create a way to edit these "ideas" recipes, since the content team keeps changing around ingredients and quantities.

Create the function `update_recipes(<ideas>, <recipe_updates>)` that takes an "ideas" dictionary and an iterable of recipe updates as arguments.
The function should return the new/updated "ideas" dictionary.

```python
>>>update_recipes(
    {'Banana Bread' : {'Banana': 1, 'Apple': 1, 'Walnuts': 1, 'Flour': 1, 'Eggs': 2, 'Butter': 1},
     'Raspberry Pie' : {'Raspberry': 1, 'Orange': 1, 'Pie Crust': 1, 'Cream Custard': 1}},
    (('Banana Bread', {'Banana': 4,  'Walnuts': 2, 'Flour': 1, 'Butter': 1, 'Milk': 2, 'Eggs': 3}),)
    )
...

{'Banana Bread': {'Banana': 4, 'Walnuts': 2, 'Flour': 1, 'Butter': 1, 'Milk': 2, 'Eggs': 3}, 
 'Raspberry Pie': {'Raspberry': 1, 'Orange': 1, 'Pie Crust': 1, 'Cream Custard': 1}}

>>> update_recipes(
    {'Banana Bread' : {'Banana': 1, 'Apple': 1, 'Walnuts': 1, 'Flour': 1, 'Eggs': 2, 'Butter': 1},
    'Raspberry Pie' : {'Raspberry': 1, 'Orange': 1, 'Pie Crust': 1, 'Cream Custard': 1},
    'Pasta Primavera': {'Eggs': 1, 'Carrots': 1, 'Spinach': 2, 'Tomatoes': 3, 'Parmesan': 2, 'Milk': 1, 'Onion': 1}},
    [('Raspberry Pie', {'Raspberry': 3, 'Orange': 1, 'Pie Crust': 1, 'Cream Custard': 1, 'Whipped Cream': 2}),
    ('Pasta Primavera', {'Eggs': 1, 'Mixed Veggies': 2, 'Parmesan': 2, 'Milk': 1, 'Spinach': 1, 'Bread Crumbs': 1}),
    ('Blueberry Crumble', {'Blueberries': 2, 'Whipped Creme': 2, 'Granola Topping': 2, 'Yogurt': 3})]
    )
...

{'Banana Bread': {'Banana': 1, 'Apple': 1, 'Walnuts': 1, 'Flour': 1, 'Eggs': 2, 'Butter': 1}, 
 'Raspberry Pie': {'Raspberry': 3, 'Orange': 1, 'Pie Crust': 1, 'Cream Custard': 1, 'Whipped Cream': 2}, 
 'Pasta Primavera': {'Eggs': 1, 'Mixed Veggies': 2, 'Parmesan': 2, 'Milk': 1, 'Spinach': 1, 'Bread Crumbs': 1},
 'Blueberry Crumble': {'Blueberries': 2, 'Whipped Creme': 2, 'Granola Topping': 2, 'Yogurt': 3}}
```

### 4. Sort the Items in the User Cart

Once a user has started a cart, the app allows them to sort their items alphabetically.
This makes things easier to find, and helps when there are data-entry errors like having 'potatoes' and 'Potato' in the database.

Create the function `sort_entries(<cart>)` that takes a shopping cart/dictionary as an argument and returns a new, alphabetically sorted one.

```python
>>> sort_entries({'Banana': 3, 'Apple': 2, 'Orange': 1})
{'Apple': 2, 'Banana':3, 'Orange': 1}
```

### 5. Send User Shopping Cart to Store for Fulfillment

The app needs to send a given user's cart to the store for fulfillment.
However, the shoppers in the store need to know which store aisle the item can be found in and if the item needs refrigeration.
So (_rather arbitrarily_) the "fulfillment cart" needs to be sorted in reverse alphabetical order with item quantities combined with location and refrigeration information.

Create the function `send_to_store(<cart>, <aisle_mapping>)` that takes a user shopping cart and a dictionary that has store aisle number and a `True`/`False` for refrigeration needed for each item.
The function should `return` a combined "fulfillment cart" that has (quantity, aisle, and refrigeration) for each item the customer is ordering.
Items should appear in _reverse_ alphabetical order.

```python
>>> send_to_store({'Banana': 3, 'Apple': 2, 'Orange': 1, 'Milk': 2},
                  {'Banana': ['Aisle 5', False], 'Apple': ['Aisle 4', False], 'Orange': ['Aisle 4', False], 'Milk': ['Aisle 2', True]})
{'Orange': [1, 'Aisle 4', False], 'Milk': [2, 'Aisle 2', True], 'Banana': [3, 'Aisle 5', False], 'Apple': [2, 'Aisle 4', False]}
```

### 6. Update the Store Inventory to Reflect what a User Has Ordered.

The app can't just place customer orders endlessly.
Eventually, the store is going to run out of various products.
So your app MVP needs to update the store inventory every time a user sends their order to the store.
Otherwise, customers will order products that aren't actually available.

Create the function `update_store_inventory(<fulfillment_cart>, <store_inventory>)` that takes a "fulfillment cart" and a store inventory.
The function should reduce the store inventory amounts by the number "ordered" in the "fulfillment cart" and then return the updated store inventory.
Where a store item count falls to 0, the count should be replaced by the message 'Out of Stock'.

```python
>>> update_store_inventory({'Orange': [1, 'Aisle 4', False], 'Milk': [2, 'Aisle 2', True], 'Banana': [3, 'Aisle 5', False], 'Apple': [2, 'Aisle 4', False]},
{'Banana': [15, 'Aisle 5', False], 'Apple': [12, 'Aisle 4', False], 'Orange': [1, 'Aisle 4', False], 'Milk': [4, 'Aisle 2', True]})

{'Banana': [12, 'Aisle 5', False], 'Apple': [10, 'Aisle 4', False], 'Orange': ['Out of Stock', 'Aisle 4', False], 'Milk': [2, 'Aisle 2', True]}
```

[feature creep]: https://en.wikipedia.org/wiki/Feature_creep
[mvp]: https://en.wikipedia.org/wiki/Minimum_viable_product

## You get
Nothing. Carts, notes and recipes arrive as arguments to your functions.

> [!NOTE]
> Exercism asks for six functions in one `dict_methods.py`. Here the exercise is split in two: **this drill covers tasks 1–3**, and tasks 4–6 are drill `240_mecha_munch_management`. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name.

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
- this drill implements **Exercism tasks 1, 2 and 3 only** — `sort_entries`, `send_to_store` and `update_store_inventory` belong to drill `240_mecha_munch_management`
- `items_to_add` and `notes` may be a `list` **or** a `tuple` — anything you can loop over
- quantity is expressed by **repeats**: `'Apple'` three times in the iterable means three apples
- an item already in the cart goes up by one; an item new to the cart starts at `1`
- `read_notes` gives every item the quantity `1`, and a name that appears twice in the notes still ends up as one key
- an update **replaces the whole ingredients dict** for that recipe — it does not merge ingredient by ingredient
- all three functions return a dict

> [!WARNING]
> `current_cart[item] += 1` raises `KeyError` for an item the cart has never held. Reach for the method that takes a default instead of wrapping it in `try`.

## Exercism hints
### General

Remember, this is an [MVP][mvp].
That means you don't need to get too fancy with error handling or different "edge case" scenarios.
It's OK to be simple and direct with the functions you are writing.

The dictionary section of the [official tutorial][dicts-docs] and the mapping type [official library reference][mapping-types-dict] are excellent places to look for more help with all these methods.

### 1. Add Item(s) to the User's Shopping Cart

- You will need to iterate through each item in `items_to_add`.
- You can avoid a `KeyError` when a key is missing by using a `dict` [method][set-default] that takes a _default value_ as one of its arguments.
- It is also possible to accomplish the same thing manually in the `loop` by using some checking and error handling, but the `dict` method is easier.

### 2. Read in Items Listed in the User's Notes App

- Remember, Python's got a method for _everything_. This one is a _classmethod_ that's an easy way to [populate a `dict`][fromkeys] with keys.
- This `dict` method returns a _new dictionary_, populated with default values. If no value is given, the default value will become `None`

### 3. Update Recipe "Ideas" Section

- Don't overthink this one!  This can be solved in **one** `dict` method call.
- The key word here is .... [_update_][update].

### 4. Sort the Items in the User's Cart

- What method would you call to get an [iterable view of items][items] in the dictionary?
- If you had a `list` or a `tuple`, what [`built-in`][builtins] function might you use to sort them?
- The built-in function you want is the one that returns a _copy_, and doesn't mutate the original.

### 5. Send the User's Shopping Cart to the Store for Fulfillment

- Having a fresh, empty dictionary here as the `fulfillment_cart` might be handy for adding in items.
- `Looping` through the members of the cart might be the most direct way of accessing things here.
- What method would you call to get an [iterable view of just the keys][keys] of the dictionary?
- Remember that you can get the `value` of a given key by using `<dict name>[<key_name>]` syntax.
- If you had a `list` or a `tuple`, what [`built-in`][builtins] function might you use to sort them?
- Remember that the `built-in` function can take an optional `reverse=True` argument.

### 6. Update the Store Inventory to Reflect what a User Has Ordered.

- There is a method that will give you an iterable view of (`key`, `value`) pairs from the dictionary.
- You can access an item in a _nested tuple_ using _bracket notation_:  `<tuple>[<nested_tuple>][<index_of_value>]`
- Don't forget to check if an inventory count falls to zero, you'll need to add in the "Out of Stock" message.

[builtins]: https://docs.python.org/3/library/functions.html
[dicts-docs]: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
[fromkeys]: https://docs.python.org/3/library/stdtypes.html#dict.fromkeys
[items]: https://docs.python.org/3/library/stdtypes.html#dict.items
[keys]: https://docs.python.org/3/library/stdtypes.html#dict.keys
[mapping-types-dict]: https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
[mvp]: https://en.wikipedia.org/wiki/Minimum_viable_product
[set-default]: https://docs.python.org/3/library/stdtypes.html#dict.setdefault
[update]: https://docs.python.org/3/library/stdtypes.html#dict.update

## Read first
- [Mapping types — dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict) — every method in one table; worth skimming end to end once
- [dict.setdefault()](https://docs.python.org/3/library/stdtypes.html#dict.setdefault) — insert-if-missing and return, in one call
- [dict.fromkeys()](https://docs.python.org/3/library/stdtypes.html#dict.fromkeys) — build a whole dict from an iterable of keys sharing one default value
- [dict.update()](https://docs.python.org/3/library/stdtypes.html#dict.update) — merge in another mapping *or* an iterable of pairs, in place
- [Dictionary view objects](https://docs.python.org/3/library/stdtypes.html#dict-views) — `.keys()`, `.values()` and `.items()` are live views, not copies
- [Sorting HOW TO](https://docs.python.org/3/howto/sorting.html) — `sorted()`, `key=` and `reverse=`
- [Real Python: dictionaries in Python](https://realpython.com/python-dicts/) — the long-form tour
- [David Beazley: Built-in Super Heroes (video)](https://www.youtube.com/watch?v=lyDLAutA88s) — why the plain built-in dict is usually the right answer

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Roughly one `dict` method per task. Task 1 is a loop with [`setdefault(item, 0)`](https://docs.python.org/3/library/stdtypes.html#dict.setdefault) in it, so a brand-new product does not raise `KeyError` before you add 1 to it. Task 2 needs no loop at all: there is a *classmethod* that builds an entire dictionary from an iterable of keys with one shared default value. Task 3 is famously a single call — the key word in the task title is *update*.
### Hint 2
For task 1, quantity is repeats, so one pass over the iterable adding 1 each time is exactly right; write the loop against *any* iterable rather than assuming a list, because the tests pass tuples too.

For task 2, the default value matters: [`dict.fromkeys(keys)`](https://docs.python.org/3/library/stdtypes.html#dict.fromkeys) with no second argument fills every value with `None`, and the app wants `1`.

For task 3, remember that [`dict.update()`](https://docs.python.org/3/library/stdtypes.html#dict.update) accepts an iterable of `(key, value)` pairs, not only another dict — which is precisely the shape the recipe updates arrive in. Each pair replaces the whole value under that key, or adds the key when it is new. Then return the dict you updated.
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
