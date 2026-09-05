---
title: lists — the poker round tracker
difficulty: medium
tier: core
minutes: 12
prereqs: [95]
tags: [lists]
source: exercism/python concept/card-games (MIT, adapted)
---
# lists — the poker round tracker

*Building, concatenating and searching a list — three one-liners and the `in` operator.*

## Read first
- [lists (Python tutorial)](https://devdocs.io/python~3.14/tutorial/datastructures) — the tour: literals, indexing, and what a list is for
- [the `list` type](https://devdocs.io/python~3.14/library/stdtypes#list) — the reference page, including the constructor and what it accepts
- [sequence types — `list`, `tuple`, `range`](https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range) — the operations every sequence shares, `+` and `in` among them
- [common sequence operations](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — the table with `x in s`, `s + t`, `len(s)` and slicing in it
- [lists and tuples in Python (Real Python)](https://realpython.com/python-lists-tuples/) — the same ground, slower, with pictures

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Elyse tracks which poker rounds she played. You track which instance IDs you already restarted, which alerts you already paged on, which config keys a deploy touched. Same three questions every time: build a small list from a starting point, stick two lists together when the data arrives in pieces, and ask whether a thing is in there at all. Python answers all three without a loop, and knowing that `number in rounds` *is* the membership test — a complete expression that already evaluates to `True` or `False` — is the difference between three lines and thirteen.

## Introduction
A [`list`][list] is a mutable collection of items in _sequence_.
Like most collections (_see the built-ins [`tuple`][tuple], [`dict`][dict] and [`set`][set]_), lists can hold reference to any (or multiple) data type(s) - including other lists.
Like any [sequence][sequence type], items can be accessed via `0-based index` number from the left and `-1-based index` from the right.
Lists can be copied in whole or in part via [slice notation][slice notation] or `<list>.copy()`.

Lists support both [common][common sequence operations] and [mutable][mutable sequence operations] sequence operations such as `min()`/`max()`, `<list>.index()`, `<list>.append()` and `<list>.reverse()`.
List elements can be iterated over using the `for item in <list>` construct.
 `for index, item in enumerate(<list>)` can be used when both the element index and the element value are needed.

Under the hood, `lists` are implemented as [dynamic arrays][dynamic array] -- similar to Java's [`ArrayList`][arraylist] type, and are most often used to store groups of similar data (_strings, numbers, sets etc._) of unknown length.
Lists are an extremely flexible and useful data structure and many built-in methods and operations in Python produce lists as their output.


### Construction

A `list` can be declared as a _literal_ with square `[]` brackets and commas between elements:


```python
>>> no_elements = []

>>> no_elements
[]

>>> one_element = ["Guava"]

>>> one_element
['Guava']

>>> elements_separated_with_commas = ["Parrot", "Bird", 334782]

>>> elements_separated_with_commas
['Parrot', 'Bird', 334782]
```

For readability, line breaks can be used when there are many elements or nested data structures within a `list`:


```python
>>> lots_of_entries = [
      "Rose",
      "Sunflower",
      "Poppy",
      "Pansy",
      "Tulip",
      "Fuchsia",
      "Cyclamen",
      "Lavender"
   ]
   
>>> lots_of_entries
['Rose', 'Sunflower', 'Poppy', 'Pansy', 'Tulip', 'Fuchsia', 'Cyclamen', 'Lavender']

# Each data structure is on its own line to help clarify what they are.
>>> nested_data_structures = [
      {"fish": "gold", "monkey": "brown", "parrot": "grey"},
      ("fish", "mammal", "bird"),
      ['water', 'jungle', 'sky']
   ]
   
>>> nested_data_structures
[{'fish': 'gold', 'monkey': 'brown', 'parrot': 'grey'}, ('fish', 'mammal', 'bird'), ['water', 'jungle', 'sky']]
```

The `list()` constructor can be used empty or with an _iterable_ as an argument.
 Elements in the iterable are cycled through by the constructor and added to the `list` in order:


```python
>>> no_elements = list()

>>> no_elements
[]

# The tuple is unpacked and each element is added.
>>> multiple_elements_from_tuple = list(("Parrot", "Bird", 334782))

>>> multiple_elements_from_tuple
['Parrot', 'Bird', 334782]

# The set is unpacked and each element is added.
>>> multiple_elements_from_set = list({2, 3, 5, 7, 11})

>>> multiple_elements_from_set
[2, 3, 5, 7, 11]
```

Results when using a `list` constructor with a `string` or a `dict` may be surprising:


```python
# String elements (Unicode code points) are iterated through and added *individually*.
>>> multiple_elements_string = list("Timbuktu")

>>> multiple_elements_string
['T', 'i', 'm', 'b', 'u', 'k', 't', 'u']

# Unicode separators and positioning code points are also added *individually*.
>>> multiple_code_points_string = list('अभ्यास')

>>> multiple_code_points_string
['अ', 'भ', '्', 'य', 'ा', 'स']

# The iteration default for dictionaries is over the keys, so only key data is inserted into the list.
>>> source_data = {"fish": "gold", "monkey": "brown"}

>>> multiple_elements_dict_1 = list(source_data)
['fish', 'monkey']
```

Because the `list` constructor will only take _iterables_ (or nothing) as arguments, objects that are _not_ iterable will throw a type error.
 Consequently, it is much easier to create a one-item `list` via the literal method.

```python
# Numbers are not iterable, and so attempting to create a list with a number passed to the constructor fails.
>>> one_element = list(16)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'int' object is not iterable

# Tuples *are* iterable, so passing a one-element tuple to the constructor does work, but it's awkward
>>> one_element_from_iterable = list((16,))

>>> one_element_from_iterable
[16]
```

### Accessing elements

Items inside lists (_as well as items in other sequence types `str` & `tuple`_) can be accessed via `0-based index` and _bracket notation_.
 Indexes can be from **`left`** --> **`right`** (_starting at zero_) or **`right`** --> **`left`** (_starting at -1_).


index from left ⟹

|  0 👇🏾 	|  1 👇🏾 	|  2 👇🏾 	|  3 👇🏾 	|  4 👇🏾 	|  5 👇🏾 	|
|:--------:	|:--------:	|:--------:	|:--------:	|:--------:	|:--------:	|
|     P    	|     y    	|     t    	|     h    	|     o    	|     n    	|
| 👆🏾 -6 	| 👆🏾 -5 	| 👆🏾 -4 	| 👆🏾 -3 	| 👆🏾 -2 	| 👆🏾 -1 	|

⟸ index from right


```python
>>> breakfast_foods = ["Oatmeal", "Fruit Salad", "Eggs", "Toast"]

# Oatmeal is at index 0 or index -4.
>>> breakfast_foods[0]
'Oatmeal'

>>> breakfast_foods[-4]
'Oatmeal'

# Eggs are at index -2 or 2
>>> breakfast_foods[-2]
'Eggs'

>>> breakfast_foods[2]
'Eggs'

# Toast is at -1
>>> breakfast_foods[-1]
'Toast'
```

A section of the elements inside a `list` can be accessed via _slice notation_ (`<list>[start:stop]`).
 A _slice_ is defined as an element sequence at position `index`, such that `start <= index < stop`.
 _Slicing_ returns a copy of the "sliced" items and does not modify the original `list`.


A `step` parameter can also be used `[start:stop:step]` to "skip over" or filter the `list` elements (_for example, a `step` of 2 will select every other element in the range_):


```python
>>> colors = ["Red", "Purple", "Green", "Yellow", "Orange", "Pink", "Blue", "Grey"]

# If there is no step parameter, the step is assumed to be 1.
>>> middle_colors = colors[2:6]

>>> middle_colors
['Green', 'Yellow', 'Orange', 'Pink']

# If the start or stop parameters are omitted, the slice will
# start at index zero, and will stop at the end of the list.
>>> primary_colors = colors[::3]

>>> primary_colors
['Red', 'Yellow', 'Blue']
```

### Working with lists

The usage of the built-in `sum()` function on a list will return the sum of all the numbers in the list:

```python
>>> number_list = [1, 2, 3, 4]
>>> sum(number_list)
10
```

You can also get the _length_ of a list by using the `len()` function:

```python
>>> long_list = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
>>> len(long_list)
10
```

Lists can be also combined in various ways:

```python
# Using the plus + operator unpacks each list and creates a new list, but it is not efficient.
>>> new_via_concatenate = ["George", 5] + ["cat", "Tabby"]

>>> new_via_concatenate
['George', 5, 'cat', 'Tabby']

# Likewise, using the multiplication operator * is the equivalent of using + n times.
>>> first_group = ["cat", "dog", "elephant"]
>>> multiplied_group = first_group * 3

>>> multiplied_group
['cat', 'dog', 'elephant', 'cat', 'dog', 'elephant', 'cat', 'dog', 'elephant']
```

Lists supply an _iterator_, and can be looped through/over in the same manner as other _sequence types_.

```python
#  Looping through the list and printing out each element.
>>> colors = ["Orange", "Green", "Grey", "Blue"]

>>> for item in colors:
...     print(item)
...
Orange
Green
Grey
Blue
```

_For a more in-depth explanation, of `loops` and `iterators`, complete the `loops` concept._

[arraylist]: https://beginnersbook.com/2013/12/java-arraylist/
[common sequence operations]: https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations
[dict]: https://devdocs.io/python~3.14/library/stdtypes#dict
[dynamic array]: https://en.wikipedia.org/wiki/Dynamic_array
[list]: https://devdocs.io/python~3.14/library/stdtypes#list
[mutable sequence operations]: https://devdocs.io/python~3.14/library/stdtypes#typesseq-mutable
[sequence type]: https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range
[set]: https://devdocs.io/python~3.14/library/stdtypes#set
[slice notation]: https://devdocs.io/python~3.14/reference/expressions#slicings
[tuple]: https://devdocs.io/python~3.14/library/stdtypes#tuple

## Instructions
Elyse is really looking forward to playing some poker (and other card games) during her upcoming trip to Vegas.
 Being a big fan of "self-tracking" she wants to put together some small functions that will help her with tracking tasks and has asked for your help thinking them through.

### 1. Tracking Poker Rounds

Elyse is especially fond of poker, and wants to track how many rounds she plays - and _which rounds_ those are.
 Every round has its own number, and every table shows the round number currently being played.
 Elyse chooses a table and sits down to play her first round. She plans on playing three rounds.

Implement a function `get_rounds(<round_number>)` that takes the current round number and returns a single `list` with that round and the _next two_ that are coming up:

```python
>>> get_rounds(27)
[27, 28, 29]
```

### 2. Keeping all Rounds in the Same Place

Elyse played a few rounds at the first table, then took a break and played some more rounds at a second table ... but ended up with a different list for each table!
 She wants to put the two lists together, so she can track all of the poker rounds in the same place.

Implement a function `concatenate_rounds(<rounds_1>, <rounds_2>)` that takes two lists and returns a single `list` consisting of all the rounds in the first `list`, followed by all the rounds in the second `list`:

```python
>>> concatenate_rounds([27, 28, 29], [35, 36])
[27, 28, 29, 35, 36]
```

### 3. Finding Prior Rounds

Talking about some of the prior Poker rounds, another player remarks how similarly two of them played out.
 Elyse is not sure if she played those rounds or not.

Implement a function `list_contains_round(<rounds>, <round_number>)` that takes two arguments, a list of rounds played and a round number.
 The function will return `True` if the round is in the list of rounds played, `False` if not:

```python
>>> list_contains_round([27, 28, 29, 35, 36], 29)
True

>>> list_contains_round([27, 28, 29, 35, 36], 30)
False
```

### 4. Averaging Card Values

Elyse wants to try out a new game called Black Joe.
 It's similar to Black Jack - where your goal is to have the cards in your hand add up to a target value - but in Black Joe the goal is to get the _average_ of the card values to be 7.
 The average can be found by summing up all the card values and then dividing that sum by the number of cards in the hand.

Implement a function `card_average(<hand>)` that will return the average value of a hand of Black Joe.

```python
>>> card_average([5, 6, 7])
6.0
```

### 5. Alternate Averages

In Black Joe, speed is important. Elyse is going to try and find a faster way of finding the average.

She has thought of two ways of getting an _average-like_ number:

- Take the average of the _first_ and _last_ number in the hand.
- Using the median (middle card) of the hand.
  
Implement the function `approx_average_is_average(<hand>)`, given `hand`, a list containing the values of the cards in your hand.

Return `True` if either _one_ `or` _both_ of the, above named, strategies result in a number _equal_ to the _actual average_.

Note: _The length of all hands are odd, to make finding a median easier._

```python
>>> approx_average_is_average([1, 2, 3])
True

>>> approx_average_is_average([2, 3, 4, 8, 8])
True

>>> approx_average_is_average([1, 2, 3, 5, 9])
False
```

### 6. More Averaging Techniques

Intrigued by the results of her averaging experiment, Elyse is wondering if taking the average of the cards at the _even_ positions versus the average of the cards at the _odd_ positions would give the same results.
 Time for another test function!

Implement a function `average_even_is_average_odd(<hand>)` that returns a Boolean indicating if the average of the cards at even indexes is the same as the average of the cards at odd indexes.

```python
>>> average_even_is_average_odd([1, 2, 3])
True

>>> average_even_is_average_odd([1, 2, 3, 4])
False
```

### 7. Bonus Round Rules

Every 11th hand in Black Joe is a bonus hand with a bonus rule: if the last card you draw is a Jack, you double its value.

Implement a function `maybe_double_last(<hand>)` that takes a hand and checks if the last card is a Jack (11).
 If the last card **is** a Jack (11), double its value before returning the hand.

```python
>>> hand = [5, 9, 11]
>>> maybe_double_last(hand)
[5, 9, 22]

>>> hand = [5, 9, 10]
>>> maybe_double_last(hand)
[5, 9, 10]
```

## You get
Nothing. `solve()` takes **no arguments**; it hands the grader your finished functions and the grader supplies the rounds. Rounds are plain integers and a "list of rounds" is a plain `list` of them, possibly empty.

> [!NOTE]
> Exercism asks for all seven functions in one `lists.py`. Here the task is split in two: **this task covers tasks 1–3**, and tasks 4–7 are task `098_card_games`. There is one entry point — `solve()` returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"get_rounds"` | `number` — the round being played right now, e.g. `27` | a list of three ints: this round and the next two, in order |
| `"concatenate_rounds"` | `rounds_1`, `rounds_2` — two lists of round numbers | one list: everything from the first, in order, followed by everything from the second |
| `"list_contains_round"` | `rounds`, `number` | `True` when `number` is one of the rounds, `False` otherwise |

```python
poker = solve()
poker["get_rounds"](27)                                  # -> [27, 28, 29]
poker["concatenate_rounds"]([27, 28, 29], [35, 36])      # -> [27, 28, 29, 35, 36]
poker["list_contains_round"]([27, 28, 29, 35, 36], 29)   # -> True
poker["list_contains_round"]([27, 28, 29, 35, 36], 30)   # -> False
```

## Rules
- this task implements **Exercism tasks 1, 2 and 3 only** — `card_average`, `approx_average_is_average`, `average_even_is_average_odd` and `maybe_double_last` belong to task `098_card_games`
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- `get_rounds` returns exactly three numbers, ascending, starting with the one it was given
- `concatenate_rounds` keeps both lists' order and copes with either (or both) being empty — two empty lists give `[]`
- `list_contains_round` on an empty list is `False`, never an error

> [!WARNING]
> `list_contains_round` is compared with `is True` / `is False`, so return a real boolean. `0` and `1` fail even though they compare equal.

## Exercism hints
### General

### 1. Tracking Poker Rounds

- Lists in Python may be [constructed][constructed] in multiple ways.
- This function should [return][return] a `list`.

### 2. Keeping all Rounds in the Same Place

- Sequence types such as `list` support [common operations][common sequence operations].
- This function should [return][return] a `list`.

### 3. Finding Prior Rounds

- Sequence types such as `list` support a few [common operations][common sequence operations].
- This function should [return][return] a `bool`.

### 4. Averaging Card Values

- To get the average, this function should count how many items are in the `list` and sum up their values. Then, return the sum divided by the count.

### 5. Alternate Averages

- Sequence types such as `list` support a few [common operations][common sequence operations].
- To access an element, use the square brackets (`<list>[]`) notation.
- Remember that the first element of the `list` is at index 0 from the **left-hand** side.
- In Python, negative indexing starts at -1 from the **right-hand** side. This means that you can find the last element of a `list` by using `<list>[-1]`.
- Think about how you could reuse the code from the functions that you have already implemented.

### 6. More Averaging Techniques

- Sequence types such as `list` already support a few [common operations][common sequence operations].
- Think about reusing the code from the functions that you just implemented.
- The slice syntax supports a _step value_ (`<list>[<start>:<stop>:<step>]`).

### 7. Bonus Round Rules

- Lists are _mutable_. Once a `list` is created, you can modify, delete or add any type of element you wish.
- Python provides a wide range of [ways to modify `lists`][ways to modify `lists`].


[common sequence operations]: https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range
[constructed]: https://devdocs.io/python~3.14/library/stdtypes#list
[return]: https://www.w3schools.com/python/ref_keyword_return.asp
[ways to modify `lists`]: https://realpython.com/python-lists-tuples/#lists-are-mutable

## Hints
### Hint 1
All three are one line, and none of them needs a loop. Lists can be [constructed](https://devdocs.io/python~3.14/library/stdtypes#list) in several ways — the simplest is to write the elements out between square brackets, and elements may be *expressions*, not just literals. For the second and third, look at the [common sequence operations](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) table: one operator glues two sequences into a new one, and one operator answers "is this in there?".
### Hint 2
Task 1: you have the current round number and you need three consecutive numbers starting from it. Write the square brackets and put three arithmetic expressions inside them.

Task 2: `+` on two lists produces a **new** list with the left one's items followed by the right one's, and it leaves both originals alone. That is the whole function.

Task 3: `in` is a comparison operator, so `something in a_list` already *is* `True` or `False`. Do not wrap it in `if … return True else return False` — just return the expression. It also handles the empty list for free.
### Hint 3
Different data, same three moves — a port range, two lists of services, one membership check:

```python
port = 8080
[port, port + 1, port + 2]        # -> [8080, 8081, 8082]

healthy = ['api', 'db']
degraded = ['cache']
healthy + degraded                # -> ['api', 'db', 'cache']
healthy                           # -> ['api', 'db']    unchanged

'cache' in healthy + degraded     # -> True
'queue' in healthy + degraded     # -> False
```
