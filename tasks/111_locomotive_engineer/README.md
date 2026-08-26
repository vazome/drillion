---
title: unpacking-and-multiple-assignment — routes and the wagon depot grid
difficulty: medium
tier: core
minutes: 15
prereqs: [97, 101, 104, 106, 110]
tags: [unpacking-and-multiple-assignment]
source: exercism/python concept/locomotive-engineer (MIT, adapted)
---
# unpacking-and-multiple-assignment — routes and the wagon depot grid

*`**kwargs`, `{**a, **b}` and transposing a grid with `zip(*rows)`.*

## Why
Same friend, harder paperwork. The routing records need the intermediate stops folded in — and nobody knows in advance how many stops a route has, so they arrive as keyword arguments. Other routes are missing details that differ from route to route: speed here, temperature there, so the merge has to be generic. And the wagon depot is stored wrong: the rows are grouped by colour when the *columns* should be. All three are the double-star half of unpacking, plus the one line of `zip` that turns rows into columns.

## Introduction
Unpacking refers to the act of extracting the elements of a collection, such as a `list`, `tuple`, or `dict`, using iteration.
Unpacked values can then be assigned to variables within the same statement, which is commonly referred to as [Multiple assignment][multiple assignment].

The special operators `*` and `**` are often used in unpacking contexts and with multiple assignment.

> [!WARNING]
> `*<variable_name>` and `**<variable_name>` should not be confused with `*` and `**`. While `*` and `**` are used for multiplication and exponentiation respectively, `*<variable_name>` and `**<variable_name>` are used as packing and unpacking operators.

### Multiple assignment

In multiple assignment, the number of variables on the left side of the assignment operator (`=`) must match the number of values on the right side.
To separate the values, use a comma `,`:

```python
>>> a, b = 1, 2
>>> a
1
```

If the multiple assignment gets an incorrect number of variables for the values given, a `ValueError` will be thrown:

```python
>>> x, y, z = 1, 2

ValueError: too many values to unpack (expected 3, got 2)
```

Multiple assignment is not limited to one data type:

```python
>>> x, y, z = 1, "Hello", True
>>> x
1

>>> y
'Hello'

>>> z
True
```

Multiple assignment can be used to swap elements in `lists`.
This practice is pretty common in [sorting algorithms][sorting algorithms].
For example:

```python
>>> numbers = [1, 2]
>>> numbers[0], numbers[1] = numbers[1], numbers[0]
>>> numbers
[2, 1]
```

Since `tuples` are immutable, you can't swap elements in a `tuple`.

### Unpacking

> [!NOTE]
> The examples below use `lists` but the same concepts apply to `tuples`.

In Python, it is possible to [unpack the elements of `list`/`tuple`/`dictionary`][unpacking] into distinct variables.
Since values appear within `lists`/`tuples` in a specific order, they are unpacked into variables in the same order:

```python
>>> fruits = ["apple", "banana", "cherry"]
>>> x, y, z = fruits
>>> x
"apple"
```

If there are values that are not needed then you can use `_` to flag them:

```python
>>> fruits = ["apple", "banana", "cherry"]
>>> _, _, z = fruits
>>> z
"cherry"
```

#### Deep unpacking

Unpacking and assigning values from a `list`/`tuple` enclosed inside a `list` or `tuple` (_also known as nested lists/tuples_) works in the same way a shallow unpacking does — but often needs qualifiers to clarify the context or position:

```python
>>> fruits_vegetables = [["apple", "banana"], ["carrot", "potato"]]
>>> [[a, b], [c, d]] = fruits_vegetables
>>> a
"apple"

>>> d
"potato"
```

You can also deeply unpack just a portion of a nested `list`/`tuple`:

```python
>>> fruits_vegetables = [["apple", "banana"], ["carrot", "potato"]]
>>> [a, [c, d]] = fruits_vegetables
>>> a
["apple", "banana"]

>>> c
"carrot"
```

If the unpacking has variables with incorrect placement and/or an incorrect number of values, you will get a `ValueError`:

```python
>>> fruits_vegetables = [["apple", "banana"], ["carrot", "potato"]]
>>> [[a, b], [d]] = fruits_vegetables

ValueError: too many values to unpack (expected 1)
```

#### Unpacking a list/tuple with `*`

When [unpacking a `list`/`tuple`][packing and unpacking] you can use the `*` operator to capture the "leftover" values.
This is clearer than slicing the `list`/`tuple` (_which in some situations is less readable_).
For example, the first element can be extracted and then the remaining values can be placed into a new `list` without the first element:

```python
>>> fruits = ["apple", "banana", "cherry", "orange", "kiwi", "melon", "mango"]
>>> x, *last = fruits
>>> x
"apple"

>>> last
["banana", "cherry", "orange", "kiwi", "melon", "mango"]
```

We can also extract the values at the beginning and end of the `list` while grouping all the values in the middle:

```python
>>> fruits = ["apple", "banana", "cherry", "orange", "kiwi", "melon", "mango"]
>>> x, *middle, y, z = fruits
>>> y
"melon"

>>> middle
["banana", "cherry", "orange", "kiwi"]
```

We can also use `*` in deep unpacking:

```python
>>> fruits_vegetables = [["apple", "banana", "melon"], ["carrot", "potato", "tomato"]]
>>> [[a, *rest], b] = fruits_vegetables
>>> a
"apple"

>>> rest
["banana", "melon"]
```

#### Unpacking a dictionary

[Unpacking a dictionary][packing and unpacking] is a bit different from unpacking a `list`/`tuple`.
Iteration over dictionaries defaults to the **keys**.
So when unpacking a `dict`, you can only unpack the **keys** and not the **values**:

```python
>>> fruits_inventory = {"apple": 6, "banana": 2, "cherry": 3}
>>> x, y, z = fruits_inventory
>>> x
"apple"
```

If you want to unpack the values then you can use the `<dict>.values()` method:

```python
>>> fruits_inventory = {"apple": 6, "banana": 2, "cherry": 3}
>>> x, y, z = fruits_inventory.values()
>>> x
6
```

If both **keys** and **values** are needed, use the [`<dict>.items()`][items] method.
`<dict>.items()` generates an [iterable view][view-objects] containing **key-value** pairs.
These can be unpacked into a `tuple`:

```python
>>> fruits_inventory = {"apple": 6, "banana": 2, "cherry": 3}
>>> x, y, z = fruits_inventory.items()
>>> x
("apple", 6)
```

### Packing

[Packing][packing and unpacking] is the ability to group multiple values into one `list` that is assigned to a variable.
This is useful when you want to _unpack_ values, make changes, and then _pack_ the results back into a variable.
It also makes it possible to perform merges on 2 or more `lists`/`tuples`/`dicts`.

#### Packing a list/tuple with `*`

Packing a `list`/`tuple` can be done using the `*` operator.
This will pack all the values into a `list`/`tuple`.

```python
>>> fruits = ("apple", "banana", "cherry")
>>> more_fruits = ["orange", "kiwi", "melon", "mango"]

# fruits and more_fruits are unpacked and then their elements are packed into combined_fruits
>>> combined_fruits = *fruits, *more_fruits

# If there is no * on to the left of the "=" the result is a tuple
>>> combined_fruits
("apple", "banana", "cherry", "orange", "kiwi", "melon", "mango")

# If the * operator is used on the left side of "=" the result is a list.
# Note the trailing comma.
>>> *combined_fruits_too, = *fruits, *more_fruits
>>> combined_fruits_too
['apple', 'banana', 'cherry', 'orange', 'kiwi', 'melon', 'mango']
```

For more background on using `*` on the left-hand side, see [PEP 3132][pep-3132].

#### Packing a dictionary with `**`

Packing a dictionary is done by using the `**` operator.
This will pack all **key**-**value** pairs from one dictionary into another dictionary, or combine two dictionaries together.

```python
>>> fruits_inventory = {"apple": 6, "banana": 2, "cherry": 3}
>>> more_fruits_inventory = {"orange": 4, "kiwi": 1, "melon": 2, "mango": 3}

# fruits_inventory and more_fruits_inventory are unpacked into key-values pairs and combined.
>>> combined_fruits_inventory = {**fruits_inventory, **more_fruits_inventory}

# then the pairs are packed into combined_fruits_inventory
>>> combined_fruits_inventory
{"apple": 6, "banana": 2, "cherry": 3, "orange": 4, "kiwi": 1, "melon": 2, "mango": 3}
```

### Usage of `*` and `**` with functions

#### Packing with function parameters

When you create a function that accepts an arbitrary number of arguments, you can use [`*args` or `**kwargs`][args and kwargs] in the function definition.
`*args` is used to pack an arbitrary number of positional (_non-keyword_) arguments as a `tuple` and
`**kwargs` is used to pack an arbitrary number of keyword arguments as a dictionary.

Usage of `*args`:

```python
# This function is defined to take any number of positional arguments

>>> def my_function(*args):
...     print(args)

# Arguments given to the function are packed into a tuple

>>> my_function(1, 2, 3)
(1, 2, 3)

>>> my_function("Hello")
("Hello")

>>> my_function(1, 2, 3, "Hello", "Mars")
(1, 2, 3, "Hello", "Mars")
```

Usage of `**kwargs`:

```python
# This function is defined to take any number of keyword arguments

>>> def my_function(**kwargs):
...   print(kwargs)

# Arguments given to the function are packed into a dictionary

>>> my_function(a=1, b=2, c=3)
{"a": 1, "b": 2, "c": 3}
```

`*args` and `**kwargs` can also be used in combination with one another:

```python
>>> def my_function(*args, **kwargs):
...   print(sum(args))
...   for key, value in kwargs.items():
...       print(str(key) + " = " + str(value))

>>> my_function(1, 2, 3, a=1, b=2, c=3)
6
a = 1
b = 2
c = 3
```

You can also write parameters before `*args` to allow for specific positional arguments.
Individual keyword arguments then have to appear before `**kwargs`.

> [!WARNING]
> [Arguments have to be structured](https://www.python-engineer.com/courses/advancedpython/18-function-arguments/) like this:
>
> `def my_function(<positional_args>, *args, <key-word_args>, **kwargs)`
>
> If you don't follow this order then you will get an error.

```python
>>> def my_function(a, b, *args):
...   print(a)
...   print(b)
...   print(args)

>>> my_function(1, 2, 3, 4, 5)
1
2
(3, 4, 5)
```

Writing arguments in an incorrect order will result in an error:

```python
>>>def my_function(*args, a, b):
... print(args)

>>>my_function(1, 2, 3, 4, 5)
Traceback (most recent call last):
  File "c:\something.py", line 3, in <module>
    my_function(1, 2, 3, 4, 5)
TypeError: my_function() missing 2 required keyword-only arguments: 'a' and 'b'
```

#### Unpacking into function calls

You can use `*` to unpack a `list`/`tuple` of arguments into a function call.
This is very useful for functions that don't accept an `iterable`:

```python
>>> def my_function(a, b, c):
...   print(c)
...   print(b)
...   print(a)

numbers = [1, 2, 3]
>>> my_function(*numbers)
3
2
1
```

Using `*` unpacking with the [`zip()` built-in][zip] is another common use case.
The `zip()` function takes multiple iterables and returns a `list` of `tuples` with the values from each `iterable` grouped:

```python
>>> values = (['x', 'y', 'z'], [1, 2, 3], [True, False, True])
>>> a, *rest = zip(*values)
>>> rest
[('y', 2, False), ('z', 3, True)]
```

[args and kwargs]: https://www.geeksforgeeks.org/args-kwargs-python/
[items]: https://docs.python.org/3/library/stdtypes.html#dict.items
[multiple assignment]: https://www.geeksforgeeks.org/assigning-multiple-variables-in-one-line-in-python/
[packing and unpacking]: https://www.geeksforgeeks.org/packing-and-unpacking-arguments-in-python/
[pep-3132]: https://peps.python.org/pep-3132/
[sorting algorithms]: https://realpython.com/sorting-algorithms-python/
[unpacking]: https://www.geeksforgeeks.org/unpacking-arguments-in-python/?ref=rp
[view-objects]: https://docs.python.org/3/library/stdtypes.html#dict-views
[zip]: https://docs.python.org/3/library/functions.html#zip

## Instructions
Your friend Linus is a Locomotive Engineer who drives cargo trains between cities.
Although they are amazing at handling trains, they are not amazing at handling logistics or computers.
They would like to enlist your programming help organizing train details and correcting mistakes in route data.

> [!NOTE]
> This exercise could easily be solved using slicing, indexing, and various `dict` methods.
> However, we would like you to practice packing, unpacking, and multiple assignment in solving each of the tasks below.

### 1. Create a list of all wagons

Your friend has been keeping track of each wagon identifier (ID), but they are never sure how many wagons the system is going to have to process at any given time. It would be much easier for the rest of the logistics program to have this data packaged into a unified `list`.

Implement a function `get_list_of_wagons()` that accepts an arbitrary number of wagon IDs.
Each ID will be a positive integer.
The function should then `return` the given IDs as a single `list`.

```python
>>> get_list_of_wagons(1, 7, 12, 3, 14, 8, 5)
[1, 7, 12, 3, 14, 8, 5]
```

### 2. Fix the list of wagons

At this point, you are starting to get a feel for the data and how it's used in the logistics program.
The ID system always assigns the locomotive an ID of **1**, with the remainder of the wagons in the train assigned a randomly chosen ID greater than **1**.

Your friend had to connect two new wagons to the train and forgot to update the system!
Now, the first two wagons in the train `list` have to be moved to the end, or everything will be out of order.

To make matters more complicated, your friend just uncovered a second `list` that appears to contain missing wagon IDs.
All they can remember is that once the new wagons are moved, the IDs from this second `list` should be placed directly after the designated locomotive.

Linus would be really grateful to you for fixing their mistakes and consolidating the data.

Implement a function `fix_list_of_wagons()` that takes two `lists` containing wagon IDs.
It should reposition the first two items of the first `list` to the end, and insert the values from the second `list` behind (_on the right hand side of_) the locomotive ID (**1**).
The function should then `return` a `list` with the modifications.

```python
>>> fix_list_of_wagons([2, 5, 1, 7, 4, 12, 6, 3, 13], [3, 17, 6, 15])
[1, 3, 17, 6, 15, 7, 4, 12, 6, 3, 13, 2, 5]
```

### 3. Add missing stops

Now that all the wagon data is correct, Linus would like you to update the system's routing information.
Along a transport route, a train might make stops at a few different stations to pick up and/or drop off cargo.
Each journey could have a different number of these intermediary delivery points.
Your friend would like you to update the systems routing `dict` with any missing/additional delivery information.

Implement a function `add_missing_stops()` that accepts a routing `dict` followed by a variable number of keyword arguments.
These arguments could be in the form of a `dict` holding one or more stops, or any number of `stop_number=city` keyword pairs.
Your function should then return the routing `dict` updated with an additional `key` that holds a `list` of all the added stops in order.

```python
>>> add_missing_stops({"from": "New York", "to": "Miami"},
                      stop_1="Washington, DC", stop_2="Charlotte", stop_3="Atlanta",
                      stop_4="Jacksonville", stop_5="Orlando")

{"from": "New York", "to": "Miami", "stops": ["Washington, DC", "Charlotte", "Atlanta", "Jacksonville", "Orlando"]}
```

### 4. Extend routing information

Linus has been working on the routing program and has noticed that certain routes are missing some important details.
Initial route information has been constructed as a `dict` and your friend would like you to update that `dict` with whatever might be missing.
Every route in the system requires slightly different details, so Linus would really prefer a generic solution.

Implement a function called `extend_route_information()` that accepts two `dicts`.
The first `dict` contains the origin and destination cities the train route runs between.

The second `dict` contains other routing details such as train speed, length, or temperature.
The function should return a consolidated `dict` with all routing information.

> [!NOTE]
> The second `dict` can contain different/more properties than the ones shown in the example.

```python
>>> extend_route_information({"from": "Berlin", "to": "Hamburg"}, {"length": "100", "speed": "50"})
{"from": "Berlin", "to": "Hamburg", "length": "100", "speed": "50"}
```

### 5. Fix the wagon depot

When Linus was surveying the wagon depot they noticed that the wagons were not getting stored in the correct order.
In addition to an ID, each wagon has a color that corresponds to the type of cargo it carries.
Wagons are stored in the depot in grids, where each column in the grid has wagons of the same color.

However, the logistics system shows `lists` of wagons to be stored in the depot have their _rows_ grouped by color.
But for the storage grid to work correctly, each _row_ should have three different colors so that the _columns_ align by color.
Your friend would like you to sort out the wagon depot `lists`, so that the wagons get stored correctly.

Implement a function called `fix_wagon_depot()` that accepts a `list` of three items.
Each `list` item is a sublist (or "row") that contains three `tuples`.
Each `tuple` is a `(<wagon ID>, <wagon color>)` pair.

Your function should return a `list` with the three "row" `lists` reordered to have the wagons swapped into their correct positions.

```python
>>> fix_wagon_depot([
                    [(2, "red"), (4, "red"), (8, "red")],
                    [(5, "blue"), (9, "blue"), (13,"blue")],
                    [(3, "orange"), (7, "orange"), (11, "orange")],
                    ])

[
[(2, "red"), (5, "blue"), (3, "orange")],
[(4, "red"), (9, "blue"), (7, "orange")],
[(8, "red"), (13,"blue"), (11, "orange")]
]
```

## You get
Nothing. Routes, extra details and depot rows arrive as arguments to your functions.

> [!NOTE]
> Exercism asks for five functions in one `locomotive_engineer.py`. Here the task is split in two: tasks 1–2 are task `110_locomotive_engineer`, and **this task covers tasks 3–5**. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"add_missing_stops"` | `route` — a dict like `{'from': 'Berlin', 'to': 'Hamburg'}`; then **any number of `stop_n=city` keyword arguments** | a dict with the route's entries plus one extra key `"stops"` holding the stop names as a list, in the order given |
| `"extend_route_information"` | `route`; `more_route_information` — a dict of whatever extra details this route has | one dict holding both sets of entries |
| `"fix_wagon_depot"` | `wagons_rows` — a list of three rows, each a list of three `(wagon_id, colour)` tuples | the same wagons with rows and columns swapped: three rows, each holding one wagon of each colour |

```python
depot = solve()
depot["add_missing_stops"]({'from': 'Berlin', 'to': 'Hamburg'},
                           stop_1='Leipzig', stop_2='Hannover')
# -> {'from': 'Berlin', 'to': 'Hamburg', 'stops': ['Leipzig', 'Hannover']}
depot["add_missing_stops"]({'from': 'New York', 'to': 'Philadelphia'})
# -> {'from': 'New York', 'to': 'Philadelphia', 'stops': []}
depot["extend_route_information"]({'from': 'Berlin', 'to': 'Hamburg'},
                                  {'length': '100', 'speed': '50'})
# -> {'from': 'Berlin', 'to': 'Hamburg', 'length': '100', 'speed': '50'}
depot["fix_wagon_depot"]([[(2, 'red'), (4, 'red'), (8, 'red')],
                          [(5, 'blue'), (9, 'blue'), (13, 'blue')],
                          [(3, 'orange'), (7, 'orange'), (11, 'orange')]])
# -> [[(2, 'red'), (5, 'blue'), (3, 'orange')],
#     [(4, 'red'), (9, 'blue'), (7, 'orange')],
#     [(8, 'red'), (13, 'blue'), (11, 'orange')]]
```

## Rules
- this task implements **Exercism tasks 3, 4 and 5 only** — `get_list_of_wagons` and `fix_list_of_wagons` belong to task `110_locomotive_engineer`
- `add_missing_stops` receives the stops as **keyword arguments**, so its signature ends with a `**` parameter; only their *values* go into the `"stops"` list, and they keep the order they were passed in
- with no stops at all, `"stops"` is still there, holding an empty list
- `extend_route_information` merges the two dicts; the second dict's keys can be anything, and its value wins if a key appears in both
- both route functions build and return a **new** dict rather than mutating the one they were handed
- `fix_wagon_depot` is a transpose: the wagon at row *i*, column *j* ends up at row *j*, column *i*; the depot is always 3 rows of 3
- the rows it returns are `list`s of tuples — the `(id, colour)` pairs stay tuples, the rows do not

> [!NOTE]
> Exercism asks you to reach for packing, unpacking and multiple assignment here rather than for `dict` methods, slicing and index arithmetic. The tests cannot tell the difference — that is just what the task is for.

## Exercism hints
### General

- A function can be defined to take multiple arguments packaged together by using the `*args` parameter for `list` & `tuple` arguments, or the `**kwargs` parameter for dictionary/keyword-based arguments.
- To pack or unpack use the `*` or `**` operator.

### 1. Create a list of all wagons

- Multiple arguments in the function parameters can be packed with the `*args` operator.

### 2. Fix list of wagons

- Using unpacking with the `*` operator allows you to extract the first two elements of a `list` while keeping the rest intact.
- To add another `list` into an existing `list`, you can use the `*` operator to "spread" the `list`.

### 3. Add missing stops

- Using `**kwargs` as a function parameter will allow an arbitrary number of keyword arguments to be passed.
- Using `**<dict>` as an argument will unpack a dictionary into keyword arguments.
- You can put keyword arguments in a `{}` or `dict()`.
- To get the values out of a dictionary, you can use the `<dict>.values()` method.

### 4. Extend routing information

- Using `**<dict>` as an argument will unpack a dictionary into keyword arguments.
- You can put keyword arguments in a `{}` or `dict()`.

### 5. Fix the wagon depot

- `zip(*iterators)` can be used to transpose a nested `list`.
- To extract data from zipped iterators, you can use a for loop.
- you can also unpack zipped iterators using `*`.
  `[*content] = zip(iterator_1, iterator_2)` will unzip the `tuple` produced by `zip()` into a `list`.

## Read first
- [Trey Hunner: asterisks in Python](https://treyhunner.com/2018/10/asterisks-in-python-what-they-are-and-how-to-use-them/) — the one article that covers every use of `*` and `**`
- [Trey Hunner: tuple unpacking improves readability](https://treyhunner.com/2018/03/tuple-unpacking-improves-python-code-readability/) — why naming the parts beats indexing them
- [PEP 3132: extended iterable unpacking](https://peps.python.org/pep-3132/) — the `first, *rest = seq` form and why it exists
- [PEP 448: additional unpacking generalizations](https://peps.python.org/pep-0448/) — `[*a, *b]` and `{**a, **b}` in literals and calls
- [Stack Abuse: unpacking beyond parallel assignment](https://stackabuse.com/unpacking-in-python-beyond-parallel-assignment/) — worked examples of each form
- [Arbitrary argument lists](https://docs.python.org/3/tutorial/controlflow.html#arbitrary-argument-lists) — `*args` and `**kwargs` in a function definition
- [Dan Bader: nested unpacking](https://dbader.org/blog/python-nested-unpacking) — unpacking a structure that is itself full of structures
- [zip()](https://docs.python.org/3/library/functions.html#zip) — pairs up the items of several iterables; with `*` in front of a list of rows it transposes them

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Two stars this time. `**kwargs` in a parameter list collects any number of `name=value` arguments into a dictionary; `{**a, **b}` in an expression pours two dictionaries into one new one, with the later one winning wherever the keys overlap. Between them they cover tasks 3 and 4 in about a line each.
### Hint 2
For task 3, the stops arrive as keyword arguments, so *inside* the function they are already a dict — you only need their values, in order, under one new key. Build the answer as a new dict literal that spreads the route in and then adds the extra key, rather than mutating the dict you were handed. [`<dict>.values()`](https://docs.python.org/3/library/stdtypes.html#dict.values) gives you the values, and `list(...)` fixes them as a list.

Task 5 is a transpose. `zip(*rows)` feeds each row to [`zip`](https://docs.python.org/3/library/functions.html#zip) as a separate argument, so `zip` pairs up first-of-each, second-of-each, third-of-each — which is exactly the swap the depot needs. `zip` yields tuples, though, and the depot wants each row as a *list* of tuples; a starred assignment target like `[*row] = ...` unpacks one of those into a list for you, and you can name all three rows in a single multiple assignment.
### Hint 3
Different data, same shape. Tagging a server record, and turning a table of columns into a table of rows:

```python
def with_tags(server, **tags):
    return {**server, "tags": list(tags.values())}

with_tags({"host": "db-1"}, env="prod", tier="gold")
# -> {'host': 'db-1', 'tags': ['prod', 'gold']}

grid = [[("a", 1), ("b", 2)], [("c", 3), ("d", 4)]]
[*top], [*bottom] = zip(*grid)
[top, bottom]
# -> [[('a', 1), ('c', 3)], [('b', 2), ('d', 4)]]
```

`with_tags` never says how many tags there are, and the transpose never indexes a row.
