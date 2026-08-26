---
title: list-methods — joining the coaster queue
difficulty: medium
tier: core
minutes: 12
prereqs: [97]
tags: [list-methods]
source: exercism/python concept/chaitanas-colossal-coaster (MIT, adapted)
---
# list-methods — joining the coaster queue

*`append`, `index`, `insert` — three methods that change the list you were handed.*

## Why
Chaitana's theme park has two queues and a steady stream of people who need putting into the right one, found inside it, or slotted in beside their friends. That is a work queue: jobs appended to the end, a job located by name, an urgent job inserted at a position. The detail that this task actually grades — and that bites people in real code — is that these methods change the list **in place** and hand back `None`, so `queue = queue.append(name)` silently throws your queue away. Building that reflex here costs ten minutes; not having it costs an afternoon.

## Introduction
A [`list`][list] is a mutable collection of items in _sequence_.
 Like most collections (_see the built-ins [`tuple`][tuple], [`dict`][dict] and [`set`][set]_), lists can hold reference to any (or multiple) data type(s) - including other lists.
 Lists can be copied in whole or in part via [slice notation][slice notation] or through the use of `<list>.copy()`.
 Like any [sequence][sequence type], elements within `lists` are referenced by `0-based index` number from the left, or `-1-based index` number from the right.

Lists support both [common][common sequence operations] and [mutable][mutable sequence operations] sequence operations such as `min(<list>)`/`max(<list>)`, `<list>.index()`, `<list>.append()` and `<list>.reverse()`.
 Elements inside a `list`  can be iterated over using the `for item in <list>` construct.
 `for index, item in enumerate(<list>)` can be used when both the element index and element value are needed.

Python also provides many useful [list-methods][list-methods] for working with lists.
 A selection of these `list methods` is covered below.


Note that when you manipulate a `list` with a `list-method`, **you alter the list** object that has been passed.
 If you do not wish to mutate the original `list`, you will need to at least make a `shallow copy` of it via slice or `<list>.copy()`.


### Adding Items

To add an item to the end or "right-hand side" of an existing list, use `<list>.append(<item>)`:

```python
>>> numbers = [1, 2, 3]
>>> numbers.append(9)

>>> numbers
[1, 2, 3, 9]
```

Rather than _appending_, `<list>.insert()` gives you the ability to add the item to a _specific index_ in the list.
It takes 2 parameters:

1. the `<index>` at which you want the item to be inserted.
2. the `<item>` to be inserted.

**Note**: If the given `index` is 0, the item will be added to the start ("left-hand side") of the `list`.
 If the supplied `index` is greater than the final `index` on the `list`, the item will be added in the final position -- the equivalent of using `<list>.append(<item>)`.


```python
>>> numbers = [1, 2, 3]
>>> numbers.insert(0, -2)

>>> numbers
[-2, 1, 2, 3]

>>> numbers.insert(1, 0)

>>> numbers
[-2, 0, 1, 2, 3]
```


`<list>.extend(<item>)` can be used to combine an existing list with the elements from another iterable (for example, a `set`, `tuple`, `str`, or `list`).
  The iterable is _unpacked_ and elements are appended in order (_Using `<list>.append(<item>)` in this circumstance would add the entire iterable as a **single item**._).


```python
>>> numbers = [1, 2, 3]
>>> other_numbers = [5, 6, 7]

>>> numbers.extend(other_numbers)

>>> numbers
[1, 2, 3, 5, 6, 7]

>>> numbers.extend([8, 9])

>>> numbers
[1, 2, 3, 5, 6, 7, 8, 9]

>>> numbers.append([8,9])

>>> numbers
[1, 2, 3, 5, 6, 7, 8, 9, [8, 9]]
```


### Removing Items

To delete an item from a list use `<list>.remove(<item>)`, passing the item to be removed as an argument.
 `<list>.remove(<item>)` will throw a `ValueError` if the item is not present in the `list`.


```python
>>> numbers = [1, 2, 3]
>>> numbers.remove(2)

>>> numbers
[1, 3]

# Trying to remove a value that is not in the list throws a ValueError
>>> numbers.remove(0)
ValueError: list.remove(x): x not in list
```


Alternatively, using the `<list>.pop(<index>)` method will both remove **and** `return` an element for use.


`<list>.pop(<index>)` takes one optional parameter: the `index` of the item to be removed and returned.
 If the (optional) `index` argument is not specified, the final element of the `list` will be removed and returned.
 If the `index` specified is higher than the final item `index`, an `IndexError` is raised.


```python
>>> numbers = [1, 2, 3]

>>> numbers.pop(0)
1

>>> numbers
[2, 3]

>>> numbers.pop()
3

>>> numbers
[2]

>>> numbers.pop(1)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
IndexError: pop index out of range
```

All elements can be removed from a `list` with `list.clear()`. It doesn't take any parameters.

```python
>>> numbers = [1, 2, 3]
>>> numbers.clear()

>>> numbers
[]
```

### Reversing and reordering

The `<list>.reverse()` method will reverse the order of elements **in-place**.


```python
>>> numbers = [1, 2, 3]
>>> numbers.reverse()

>>> numbers
[3, 2, 1]
```


A list can be re-ordered _**in place**_ with the help of [`<list>.sort()`][sort].
Default sort order is _ascending_ from the left.
The Python docs offer [additional tips and techniques for sorting][sorting how to].

> [!NOTE]
> From 2002 to 2022, Python used an algorithm called [`Timsort`][timsort] internally to arrange lists, but switched to [`Powersort`][powersort] from `Python 3.11` onward.

[powersort]: https://www.wild-inter.net/publications/munro-wild-2018
[timsort]: https://en.wikipedia.org/wiki/Timsort


```python
>>> names = ["Tony", "Natasha", "Thor", "Bruce"]

# The default sort order is *ascending*.
>>> names.sort()

>>> names
["Bruce", "Natasha", "Thor", "Tony"]
```

If a _descending_ order is desired, pass the `reverse=True` argument:

```python
>>> names = ["Tony", "Natasha", "Thor", "Bruce"]
>>> names.sort(reverse=True)

>>> names
["Tony", "Thor", "Natasha", "Bruce"]
```

For cases where mutating the original list is undesirable, the built-in [`sorted(<iterable>)`][sorted] function can be used to return a sorted **copy**.


```python
>>> names = ["Tony", "Natasha", "Thor", "Bruce"]

>>> sorted(names)
['Bruce', 'Natasha', 'Thor', 'Tony']
```


### Occurrences of an item in a list

The number of occurrences of an element in a list can be calculated with the help of `list.count(<item>)`.
 It takes the `item` to be counted as its argument and returns the total number of times that element appears in the `list`.


```python
>>> items = [1, 4, 7, 8, 2, 9, 2, 1, 1, 0, 4, 3]

>>> items.count(1)
3
```

### Finding the index of items

`<list>.index(<item>)` will return the `index` number of the _first occurrence_ of an item passed in.
 If there are no occurrences, a `ValueError` is raised.
 If the exact position of an item isn't needed, the built-in `in` operator is more efficient for checking if a list contains a given value.


Indexing is zero-based from the left, so the position of the "first" item is `0`.
Indexing will also work from the right, beginning with `-1`.


```python
>>> items = [7, 4, 1, 0, 2, 5]

>>> items.index(4)
1

>>> items.index(10)
ValueError: 10 is not in list
```

`start` and `end` indices can also be provided to narrow the search to a specific section of the `list`:

```python
>>> names = ["Tina", "Leo", "Thomas", "Tina", "Emily", "Justin"]

>>> names.index("Tina")
0

>>> names.index("Tina", 2, 5)
3
```

[common sequence operations]: https://docs.python.org/3/library/stdtypes.html#common-sequence-operations
[dict]: https://docs.python.org/3/library/stdtypes.html#dict
[list-methods]: https://docs.python.org/3/tutorial/datastructures.html#more-on-lists
[list]: https://docs.python.org/3/library/stdtypes.html#list
[mutable sequence operations]: https://docs.python.org/3/library/stdtypes.html#typesseq-mutable
[sequence type]: https://docs.python.org/3/library/stdtypes.html#sequence-types-list-tuple-range
[set]: https://docs.python.org/3/library/stdtypes.html#set
[slice notation]: https://docs.python.org/3/reference/expressions.html#slicings
[sort]: https://docs.python.org/3/library/stdtypes.html#list.sort
[sorted]: https://docs.python.org/3/library/functions.html#sorted
[sorting how to]: https://docs.python.org/3/howto/sorting.html
[tuple]: https://docs.python.org/3/library/stdtypes.html#tuple

## Instructions
Chaitana owns a very popular theme park.
 She only has one ride in the very center of beautifully landscaped grounds: The Biggest Roller Coaster in the World(TM).
 Although there is only this one attraction, people travel from all over the world and stand in line for hours for the opportunity to ride Chaitana's hypercoaster.

There are two queues for this ride, each represented as a `list`:

1. Normal Queue
2. Express Queue (_also known as the Fast-track_) - where people pay extra for priority access.


You have been asked to write some code to better manage the guests at the park.
 You need to implement the following functions as soon as possible before the guests (and your boss, Chaitana!) get cranky.
 Make sure you read carefully.
 Some tasks ask that you change or update the existing queue, while others ask you to make a copy of it.


### 1. Add me to the queue

Define the `add_me_to_the_queue()` function that takes 4 parameters `<express_queue>, <normal_queue>, <ticket_type>, <person_name>` and returns the appropriate queue updated with the person's name.


1. `<ticket_type>` is an `int` with 1 == express_queue and 0 == normal_queue.
2. `<person_name>` is the name (as a `str`) of the person to be added to the respective queue.


```python
>>> add_me_to_the_queue(express_queue=["Tony", "Bruce"], normal_queue=["RobotGuy", "WW"], ticket_type=1, person_name="RichieRich")
...
["Tony", "Bruce", "RichieRich"]

>>> add_me_to_the_queue(express_queue=["Tony", "Bruce"], normal_queue=["RobotGuy", "WW"], ticket_type=0, person_name="HawkEye")
....
["RobotGuy", "WW", "HawkEye"]
```

### 2. Where are my friends?

One person arrived late at the park but wants to join the queue where their friends are waiting.
 But they have no idea where their friends are standing and there isn't any phone reception to call them.

Define the `find_my_friend()` function that takes 2 parameters `queue` and  `friend_name` and returns the position in the queue of the person's name.


1. `<queue>` is the `list` of people standing in the queue.
2. `<friend_name>` is the name of the friend whose index (place in the queue) you need to find.

Remember:  Indexing starts at 0 from the left, and -1 from the right.


```python
>>> find_my_friend(queue=["Natasha", "Steve", "T'challa", "Wanda", "Rocket"], friend_name="Steve")
...
1
```


### 3. Can I please join them?

Now that their friends have been found (in task #2 above), the late arriver would like to join them at their place in the queue.
Define the `add_me_with_my_friends()` function that takes 3 parameters `queue`, `index`, and  `person_name`.


1. `<queue>` is the `list` of people standing in the queue.
2. `<index>` is the position at which the new person should be added.
3. `<person_name>` is the name of the person to add at the index position.

Return the queue updated with the late arrivals name.


```python
>>> add_me_with_my_friends(queue=["Natasha", "Steve", "T'challa", "Wanda", "Rocket"], index=1, person_name="Bucky")
...
["Natasha", "Bucky", "Steve", "T'challa", "Wanda", "Rocket"]
```

### 4. Mean person in the queue

You just heard from the queue that there is a really mean person shoving, shouting, and making trouble.
 You need to throw that miscreant out for bad behavior!


Define the `remove_the_mean_person()` function that takes 2 parameters `queue` and `person_name`.


1. `<queue>` is the `list` of people standing in the queue.
2. `<person_name>` is the name of the person that needs to be kicked out.

Return the queue updated without the mean person's name.

```python
>>> remove_the_mean_person(queue=["Natasha", "Steve", "Eltran", "Wanda", "Rocket"], person_name="Eltran")
...
["Natasha", "Steve", "Wanda", "Rocket"]
```


### 5. Namefellows

You may not have seen two unrelated people who look exactly the same, but you have _definitely_ seen unrelated people with the exact same name (_namefellows_)!
 Today, it looks like there are a lot of them in attendance.
  You want to know how many times a particular name occurs in the queue.

Define the `how_many_namefellows()` function that takes 2 parameters `queue` and  `person_name`.

1. `<queue>` is the `list` of people standing in the queue.
2. `<person_name>` is the name you think might occur more than once in the queue.


Return the number of occurrences of `person_name`, as an `int`.


```python
>>> how_many_namefellows(queue=["Natasha", "Steve", "Eltran", "Natasha", "Rocket"], person_name="Natasha")
...
2
```

### 6. Remove the last person

Sadly, it's overcrowded at the park today and you need to remove the last person in the normal line (_you will give them a voucher to come back in the fast-track on another day_).
 You will have to define the function `remove_the_last_person()` that takes 1 parameter `queue`, which is the list of people standing in the queue.

You should update the `list` and also `return` the name of the person who was removed, so you can write them a voucher.


```python
>>> remove_the_last_person(queue=["Natasha", "Steve", "Eltran", "Natasha", "Rocket"])
...
'Rocket'
```

### 7. Sort the Queue List

For administrative purposes, you need to get all the names in a given queue in alphabetical order.


Define the `sorted_names()` function that takes 1 argument,  `queue`, (the `list` of people standing in the queue), and returns a `sorted` copy of the `list`.


```python
>>> sorted_names(queue=["Natasha", "Steve", "Eltran", "Natasha", "Rocket"])
...
['Eltran', 'Natasha', 'Natasha', 'Rocket', 'Steve']
```

## You get
Nothing. `solve()` takes **no arguments**; the grader calls your functions with the queues. A queue is a plain `list` of name strings, in the order people are standing.

> [!NOTE]
> Exercism asks for all seven functions in one `list_methods.py`. Here the task is split in two: **this task covers tasks 1–3**, and tasks 4–7 are task `100_chaitanas_colossal_coaster`. There is one entry point — `solve()` returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"add_me_to_the_queue"` | `express_queue`, `normal_queue`, `ticket_type` (`1` = express, `0` = normal), `person_name` | the queue the person joined — **that same list object** — with the name now at the end of it |
| `"find_my_friend"` | `queue`, `friend_name` | the friend's position in the queue as an `int`, counting from `0` at the front |
| `"add_me_with_my_friends"` | `queue`, `index`, `person_name` | the queue — **the same list object** — with the name now sitting at `index` and everyone from there back shifted one place |

```python
park = solve()
park["add_me_to_the_queue"](["Tony", "Bruce"], ["RobotGuy", "WW"], 1, "RichieRich")
# -> ['Tony', 'Bruce', 'RichieRich']
park["add_me_to_the_queue"](["Tony", "Bruce"], ["RobotGuy", "WW"], 0, "HawkEye")
# -> ['RobotGuy', 'WW', 'HawkEye']
park["find_my_friend"](["Natasha", "Steve", "Wanda", "Rocket"], "Steve")
# -> 1
park["add_me_with_my_friends"](["Natasha", "Steve", "Wanda"], 1, "Bucky")
# -> ['Natasha', 'Bucky', 'Steve', 'Wanda']
```

## Rules
- this task implements **Exercism tasks 1, 2 and 3 only** — `remove_the_mean_person`, `how_many_namefellows`, `remove_the_last_person` and `sorted_names` belong to task `100_chaitanas_colossal_coaster`
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- a new arrival always joins the **end** of the queue their ticket buys them; the other queue is not touched at all
- the friend is always somewhere in the queue, so `find_my_friend` never has to report "not found"
- an `index` past the end of the queue puts the person last, which is what `insert` already does — you do not have to special-case it

> [!WARNING]
> Two of these are graded on **identity**, not just on contents: the tests assert that the list you return `is` the queue you were given. `express_queue + [person_name]` produces the right names in a brand new list and still fails. Mutate the queue you were handed, then return that same object.

## Exercism hints

### General

- Make sure you have a good understanding of how to create and update lists.
- The Python [documentation on `lists`][python lists] can be really helpful.
- The Python [tutorial section on `lists`][more on lists] is also a good resource.

### 1. Add Me to the queue

- An `if-else` statement can help you find which ticket type you are dealing with.
- You can then `append()` the person to the queue based on the ticket type.

### 2. Where are my friends

- You need to find the `index()` of the friend name from the queue.

### 3. Can I please join them?

- Since you know the `index()`, you can `insert()` the friend into the queue at that point.

### 4. Mean person in the queue

- You know the mean persons name, so you can `remove()` them from the queue.

### 5. Namefellows

-  `count()`-ing the occurrences of the `name` in the queue could be a good strategy here.

### 6. Remove the last person

- Although you could `remove()` the person by name, `pop()`-ing them out might be quicker.

### 7. Sort the Queue List

- Don't forget that You need to avoid mutating the queue and losing its original order.
- Once you have a `copy()`, `sort()`-ing should be straightforward.
- We're looking for an _ascending_ sort, or _alphabetical from a-z_.

[python lists]: https://docs.python.org/3.11/library/stdtypes.html#list
[more on lists]: https://docs.python.org/3.11/tutorial/datastructures.html#more-on-lists

## Read first
- [more on lists (Python tutorial)](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists) — the method-by-method table: `append`, `insert`, `index` and the rest
- [mutable sequence operations](https://docs.python.org/3/library/stdtypes.html#typesseq-mutable) — the formal definition of what each mutating method does, and what it returns
- [the `list` type](https://docs.python.org/3/library/stdtypes.html#list) — the reference page for the type itself
- [`sorted()`](https://docs.python.org/3/library/functions.html#sorted) — the non-mutating counterpart you will meet in the next task
- [sorting HOW TO](https://docs.python.org/3/howto/sorting.html) — in-place versus copy, spelled out
- [Timsort](https://en.wikipedia.org/wiki/Timsort) — what Python used to sort lists between 2002 and 2022, for background

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Each of the three is one or two lines, and each is a list method you can find in [more on lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists). An `if`/`else` decides which queue you are dealing with in task 1, and then one method puts the person on the end of that queue. For task 2, one method searches a list for a value and gives you back its position. For task 3 you already know the position — one method drops a value in at a given index.
### Hint 2
The three you want are `append()`, `index()` and `insert()`. `insert()` takes the index first and the item second.

The trap is what they return. `append()` and `insert()` change the list and evaluate to `None`, so `return queue.append(person_name)` returns `None` and fails the test. Call the method on one line, return the list on the next.

For task 1, pick the queue first and give it a name, then append to that name and return it — the name still points at the caller's list, which is exactly what the identity check wants. `index()` is the odd one out here: it changes nothing and returns the position.
### Hint 3
Different data, same three methods — a job queue:

```python
jobs = ['reindex', 'backfill']
jobs.append('vacuum')
jobs                          # -> ['reindex', 'backfill', 'vacuum']

jobs.index('backfill')        # -> 1

jobs.insert(0, 'hotfix')
jobs                          # -> ['hotfix', 'reindex', 'backfill', 'vacuum']

jobs.append('audit') is None  # -> True    the call returns nothing; the list changed
```

The last line is the whole warning in one expression: the value of `jobs.append('audit')` is `None`, and the useful result is in `jobs`.
