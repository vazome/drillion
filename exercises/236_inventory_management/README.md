---
title: dicts — building and topping up an inventory
minutes: 14
prereqs: [221, 227, 233]
tags: [exercism, dicts, data-structures]
source: exercism/python concept/inventory-management (MIT, adapted)
---
# dicts — building and topping up an inventory

*Counting into a dict — `setdefault`, `in`, and never below zero.*

## Why
A warehouse scanner produces a flat list of what came through the door: `["coal", "wood", "wood", "diamond"]`. Nobody can work with that. What the stock system needs is a count per item name, which is what a dictionary is for — key to number, updated in place as goods arrive and leave. The same shape shows up every time you tally anything: error codes per service, requests per client, files per extension.

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
[mapping-types-dict]: https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
[term-hashable]: https://docs.python.org/3/glossary.html#term-hashable

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
Nothing. The inventory and the item lists arrive as arguments to your functions.

> [!NOTE]
> Exercism asks for five functions in one `dicts.py`. Here the exercise is split in two: **this drill covers tasks 1–3**, and tasks 4–5 are drill `237_inventory_management`. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name.

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
- this drill implements **Exercism tasks 1, 2 and 3 only** — `remove_item` and `list_inventory` belong to drill `237_inventory_management`
- quantity is expressed by **repeats**: an item appearing three times in the list means three of it
- an item that is not in the inventory yet starts at `0` and becomes `1` when it is added
- a count never goes below `0`; once it is at `0`, further requests to decrement it are ignored
- decrementing an item the inventory has never heard of does nothing — it must **not** be created with a negative or zero count
- all three functions return the inventory dict (`add_items` / `decrement_items` update the one they were handed; returning a copy also passes)

> [!WARNING]
> `inventory[item] += 1` raises `KeyError` the first time an item is seen. Make sure the key exists before you add to it.

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
[dict docs]: https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
[dict items]: https://docs.python.org/3/library/stdtypes.html#dict.items
[dict setdefault]: https://www.w3schools.com/python/ref_dictionary_setdefault.asp
[dict-pop]: https://www.w3schools.com/python/ref_dictionary_pop.asp
[dict-tutorial]: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
[for-loop]: https://docs.python.org/3/tutorial/controlflow.html#for-statements
[increment]: https://www.w3schools.com/python/gloss_python_assignment_operators.asp
[list]: https://docs.python.org/3/tutorial/introduction.html#lists
[return-keyword]: https://www.w3schools.com/python/ref_keyword_return.asp
[tuples]: https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences

## Read first
- [Mapping types — dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict) — every dict method in one table
- [Tutorial: dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries) — the gentle introduction, with a worked counting example
- [hashable](https://docs.python.org/3/glossary.html#term-hashable) — why a string or a tuple may be a key and a list may not
- [dict.setdefault()](https://docs.python.org/3/library/stdtypes.html#dict.setdefault) — insert the default only if the key is missing, return the value either way
- [dict.items()](https://docs.python.org/3/library/stdtypes.html#dict.items) — the `(key, value)` view you loop over
- [w3schools: Python dictionaries](https://www.w3schools.com/python/python_dictionaries.asp) — quick reference with runnable snippets
- [collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter) — what production code reaches for once counting is the whole job

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Each of these three functions is a `for` loop over the item list with one dictionary line inside it. The awkward moment is the first time an item shows up: `inventory[item] += 1` raises `KeyError` when the key is not there yet. [`dict.setdefault(key, 0)`](https://docs.python.org/3/library/stdtypes.html#dict.setdefault) makes that moment go away — it inserts the `0` only when the key is missing, and leaves an existing count alone.
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
