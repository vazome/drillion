---
title: dicts — removing items and reporting stock
difficulty: easy
tier: core
minutes: 12
prereqs: [106]
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

## Introduction
A dictionary (`dict`) in Python is a data structure that associates [hashable][term-hashable] _keys_ to _values_ and is known in other programming languages as a resizable [hash table][hashtable-wikipedia], hashmap, or [associative array][associative-array].
Dictionaries are Python's only built-in [mapping type][mapping-types-dict].

`Keys` must be hashable and unique across the dictionary.
Key types can include `numbers`, `str`, or `tuples` (of _immutable_ values).
They cannot contain _mutable_ data structures such as `lists`, `dict`s, or `set`s.
As of Python 3.7, `dict` key order is guaranteed to be the order in which entries are inserted.

`values` can be of any data type or structure.
 Values can also nest _arbitrarily_, so they can include lists-of-lists, sub-dictionaries, and other custom or compound data structures.

Given a `key`, dictionaries can retrieve a `value` in (on average) constant time (_independent of the number of entries_).
Compared to searching for a value within a `list` or `array` (_without knowing the `index` position_), a `dict` uses significantly more memory, but has very rapid retrieval.
Dictionaries are especially useful in scenarios where the collection of items is large and must be accessed and updated frequently.

### Dictionary Construction

Dictionaries can be created in many ways.
The two most straightforward are using the `dict()`constructor or declaring a `dict` _literal_.

#### The `dict()` Class Constructor

`dict()` (_the constructor for the dictionary class_) can be used with any iterable of `key`, `value` pairs or with a series of `<name>=<value>` _arguments_:

```python
#Passing a list of key,value tuples.
>>> wombat = dict([('name', 'Wombat'),('speed', 23),('land_animal', True)])
{'name': 'Wombat', 'speed': 23, 'land_animal': True}


#Using key=value arguments.
>>> bear = dict(name="Black Bear", speed=40, land_animal=True)
{'name': 'Black Bear', 'speed': 40, 'land_animal': True}
```

#### Dictionary Literals

A `dict` can also be directly entered as a _dictionary literal_, using curly brackets (`{}`) enclosing `key : value` pairs:

```python
>>> whale = {"name": "Blue Whale", "speed": 35, "land_animal": False}
{'name': 'Blue Whale', 'speed': 35, 'land_animal': False}
```

### Accessing Values in a Dictionary

You can access an entry in a dictionary using a _key_ in square (`[]`) brackets.
If a `key` does not exist in the `dict`, a `KeyError` is thrown:

```python
>>> bear["speed"]
40

>>> bear["color"]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: 'color'
```

Accessing an entry via the `.get(<key>, <default value>)` method can avoid the `KeyError`:

```python
>>> bear.get("color", 'not found')
'not found'
```

### Changing or Adding Dictionary Values

You can change an entry `value` by assigning to its _key_:

```python
#Assigning the value "Grizzly Bear" to the name key.
>>> bear["name"] = "Grizzly Bear"
{'name': 'Grizzly Bear', 'speed': 40, 'land_animal': True}

>>> whale["speed"] = 25
{'name': 'Blue Whale', 'speed': 25, 'land_animal': False}
```

New `key`:`value` pairs can be _added_ in the same fashion:

```python
# Adding a new "color" key with a new "tawney" value.
>>> bear["color"] = 'tawney'
{'name': 'Grizzly Bear', 'speed': 40, 'land_animal': True, 'color': 'tawney'}

>>> whale["blowholes"] = 1
{'name': 'Blue Whale', 'speed': 25, 'land_animal': False, 'blowholes': 1}
```

### Removing (Pop-ing) Dictionary Entries

You can use the `.pop(<key>)` method to delete a dictionary entry.
`.pop()` removes the (`key`, `value`) pair and returns the `value` for use.
Like `.get()`, `.pop(<key>)` accepts second argument (_`dict.pop(<key>, <default value>)`_) that will be returned if the `key` is not found.
This prevents a `KeyError` being raised:

```python
#Using .pop() removes both the key and value, returning the value.
>>> bear.pop("name")
'Grizzly Bear'


#The "name" key is now removed from the dictionary.
#Attempting .pop() a second time will throw a KeyError.
>>> bear.pop("name")
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: 'name'


#Using a default argument with .pop() will prevent a KeyError from a missing key.
>>> bear.pop("name", "Unknown")
'Unknown'
```

### Looping through/Iterating over a Dictionary

Looping through a dictionary using `for item in dict` or `while item` will iterate over only the _keys_ by default.
You can access the _values_ within the same loop by using _square brackets_:

```python
>>> for key in bear:
>>>     print((key, bear[key])) #this forms a tuple of (key, value) and prints it.
('name', 'Black Bear')
('speed', 40)
('land_animal', True)
```

You can also use the `.items()` method, which returns (`key`, `value`) tuples automatically:

```python
#dict.items() forms (key, value tuples) that can be unpacked and iterated over.
>>> for key, value in whale.items():
>>>     print(key, ":", value)
name : Blue Whale
speed : 25
land_animal : False
blowholes : 1
```

Likewise, the `.keys()` method will return `keys` and the `.values()` method will return the `values`.

[associative-array]: https://en.wikipedia.org/wiki/Associative_array#:~:text=In%20computer%20science%2C%20an%20associative,a%20function%20with%20finite%20domain.
[hashtable-wikipedia]: https://en.wikipedia.org/wiki/Hash_table
[mapping-types-dict]: https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict
[term-hashable]: https://devdocs.io/python~3.14/glossary#term-hashable

## Instructions
In this exercise, you will be managing an inventory system.

The inventory should be organized by the item name and it should keep track of the number of items available.

You will have to handle adding items to an inventory.
Each time an item appears in a given list, the item's quantity should be increased by `1` in the inventory.
You will also have to handle deleting items from an inventory by decreasing quantities by `1` when requested.

Finally, you will need to implement a function that will return all the key-value pairs in a given inventory as a `list` of `tuples`.

### 1. Create an inventory based on a list

Implement the `create_inventory(<input list>)` function that creates an "inventory" from an input list of items.
It should return a `dict` containing each item name paired with their respective quantity.

```python
>>> create_inventory(["coal", "wood", "wood", "diamond", "diamond", "diamond"])
{"coal":1, "wood":2, "diamond":3}
```

### 2. Add items from a list to an existing dictionary

Implement the `add_items(<inventory dict>, <item list>)` function that adds a list of items to the passed-in inventory:

```python
>>> add_items({"coal":1}, ["wood", "iron", "coal", "wood"])
{"coal":2, "wood":2, "iron":1}
```

### 3. Decrement items from the inventory

Implement the `decrement_items(<inventory dict>, <items list>)` function that takes a `list` of items.
Your function should remove `1` from an item count for each time that item appears on the `list`:

```python
>>> decrement_items({"coal":3, "diamond":1, "iron":5}, ["diamond", "coal", "iron", "iron"])
{"coal":2, "diamond":0, "iron":3}
```

Item counts in the inventory should not be allowed to fall below 0.
 If the number of times an item appears on the input `list` exceeds the count available, the quantity listed for that item should remain at 0.
 Additional requests for removing counts should be ignored once the count falls to zero.

```python
>>> decrement_items({"coal":2, "wood":1, "diamond":2}, ["coal", "coal", "wood", "wood", "diamond"])
{"coal":0, "wood":0, "diamond":1}
```

### 4. Remove an entry entirely from the inventory

Implement the `remove_item(<inventory dict>, <item>)` function that removes an item and its count entirely from an inventory:

```python
>>> remove_item({"coal":2, "wood":1, "diamond":2}, "coal")
{"wood":1, "diamond":2}
```

If the item is not found in the inventory, the function should return the original inventory unchanged.

```python
>>> remove_item({"coal":2, "wood":1, "diamond":2}, "gold")
{"coal":2, "wood":1, "diamond":2}
```

### 5. Return the entire content of the inventory

Implement the `list_inventory(<inventory dict>)` function that takes an inventory and returns a list of `(item, quantity)` tuples.
The list should only include the _available_ items (_with a quantity greater than zero_):

```python
>>> list_inventory({"coal":7, "wood":11, "diamond":2, "iron":7, "silver":0})
[('coal', 7), ('diamond', 2), ('iron', 7), ('wood', 11)]
```

## You get
Nothing. The inventory arrives as an argument to your functions.

> [!NOTE]
> Exercism asks for five functions in one `dicts.py`. Here the task is split in two: tasks 1–3 are task `106_inventory_management`, and **this task covers tasks 4–5**. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your two functions to the grader, keyed by name.

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
- this task implements **Exercism tasks 4 and 5 only** — `create_inventory`, `add_items` and `decrement_items` belong to task `106_inventory_management`
- `remove_item` drops the key **and** its count; asked for a name that is not there it changes nothing and raises nothing
- `list_inventory` returns a list of **tuples**, not of lists and not a dict
- only items with a count **greater than zero** appear in that list; an item sitting at `0` is skipped but stays in the inventory
- the list is sorted alphabetically by name

> [!WARNING]
> Order matters in `list_inventory`: the tests compare the list position by position, so `[('coal', 7), ('diamond', 2)]` and `[('diamond', 2), ('coal', 7)]` are not the same answer.

## Exercism hints
### General

- [The Python Dictionary Tutorial][dict-tutorial] can be a great place to start.
- The Python docs on [Mapping Types - dicts][dict docs] is also pretty helpful.

### 1. Create an inventory based on a list

- You need a [for loop][for-loop] to iterate the list of items, then insert each item in the dictionary if missing and increment the item count using the dictionary accessor.
- You can use [`dict.setdefault`][dict setdefault] to make sure the value is set before incrementing the count of the item.
- This function should [return][return-keyword] a dict.

### 2. Add items from a list to an existing dictionary

- You need a [for loop][for-loop] to iterate the list of items, then insert each item if not already in the dictionary and [increment][increment] the item count using the dictionary accessor.
- You can use [`dict.setdefault`][dict setdefault] to make sure the value is set before incrementing the count of the item.
- The function `add_items` can be used by the `create_inventory` function with an empty dictionary in parameter.
- This function should [return][return-keyword] a dict.

### 3. Decrement items from the inventory

- You need [for loop][for-loop] to iterate the list of items, if the number of items is not `0` then [decrement][decrement] the current number of items.
- You can use the check `key in dict` that returns `True` if the key exists to make sure the value is in the dictionary before decrementing the number of items.
- This function should [return][return-keyword] a dict.

### 4. Remove an item entirely from the inventory

- If item is in the dictionary, [remove it][dict-pop].
- If item is not in the dictionary, do nothing.
- This function should [return][return-keyword] a dict.

### 5. Return the inventory content

- You need to use a [for loop][for-loop] on the inventory and if the number of item is greater of `0` then append the `tuple` to a `list`.
- You can use [`dict.items()`][dict items] to iterate on both the item and the value at the same time, `items()` returns a `tuple` that you can use or deconstruct, if needed.
- This function should [return][return-keyword] a [list][list] of [tuples][tuples].

[decrement]: https://www.w3schools.com/python/gloss_python_assignment_operators.asp
[dict docs]: https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict
[dict items]: https://devdocs.io/python~3.14/library/stdtypes#dict.items
[dict setdefault]: https://www.w3schools.com/python/ref_dictionary_setdefault.asp
[dict-pop]: https://www.w3schools.com/python/ref_dictionary_pop.asp
[dict-tutorial]: https://devdocs.io/python~3.14/tutorial/datastructures#dictionaries
[for-loop]: https://devdocs.io/python~3.14/tutorial/controlflow#for-statements
[increment]: https://www.w3schools.com/python/gloss_python_assignment_operators.asp
[list]: https://devdocs.io/python~3.14/tutorial/introduction#lists
[return-keyword]: https://www.w3schools.com/python/ref_keyword_return.asp
[tuples]: https://devdocs.io/python~3.14/tutorial/datastructures#tuples-and-sequences

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
