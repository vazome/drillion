---
title: list-methods — thinning out the coaster queue
difficulty: medium
tier: core
minutes: 15
prereqs: [15]
tags: [list-methods]
source: exercism/python concept/chaitanas-colossal-coaster (MIT, adapted)
---
# list-methods — thinning out the coaster queue

*`remove`, `count`, `pop`, `sort` — and the copy that keeps the original intact.*

## Read first
- [more on lists (Python tutorial)](https://devdocs.io/python~3.14/tutorial/datastructures#more-on-lists) — `remove`, `pop`, `count`, `sort`, `copy`, each with its return value
- [mutable sequence operations](https://devdocs.io/python~3.14/library/stdtypes#typesseq-mutable) — the formal table: which methods mutate, and what they hand back
- [`sorted()`](https://devdocs.io/python~3.14/library/functions#sorted) — returns a new sorted list from any iterable and never touches the original
- [`list.sort()`](https://devdocs.io/python~3.14/library/stdtypes#list.sort) — sorts in place and returns `None`, deliberately, so you cannot use it by accident
- [sorting HOW TO](https://devdocs.io/python~3.14/howto/sorting) — `key=`, `reverse=`, and when to prefer which of the two
- [Timsort](https://en.wikipedia.org/wiki/Timsort) — the algorithm Python used until 3.11, when it switched to Powersort

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
The second half of the queue job is subtraction: eject the troublemaker by name, count how many people called Natasha are in line, take the last person off and hand them a voucher, and print an alphabetical roster for the office. That last one carries the lesson. `sort()` reorders the list you already have; `sorted()` — or a copy — gives you a new one and leaves the original alone. Confuse the two and you have just shuffled a live queue to make a report look tidy, which is the same bug as sorting a caller's list of hosts inside a logging helper.

## You get
Nothing. `solve()` takes **no arguments**; the grader calls your functions with the queues. A queue is a plain `list` of name strings, in the order people are standing, and the same name may appear more than once.

> [!NOTE]
> Exercism asks for all seven functions in one `list_methods.py`. Here the task is split in two: **this task covers tasks 4–7**, and tasks 1–3 are task `015_chaitanas_colossal_coaster`. There is one entry point — `solve()` returns a dict that hands your four functions to the grader, keyed by name.

## You return
A dict with these four functions.

| key | parameters | returns |
| --- | --- | --- |
| `"remove_the_mean_person"` | `queue`, `person_name` | the queue — **the same list object** — with that name gone |
| `"how_many_namefellows"` | `queue`, `person_name` | how many times the name appears in the queue, as an `int` |
| `"remove_the_last_person"` | `queue` | the name that was standing at the end, as a `str`; the queue is left one person shorter |
| `"sorted_names"` | `queue` | a **new** list holding the same names in alphabetical order; the queue itself keeps its original order |

```python
park = solve()
park["remove_the_mean_person"](["Natasha", "Steve", "Eltran", "Wanda"], "Eltran")
# -> ['Natasha', 'Steve', 'Wanda']
park["how_many_namefellows"](["Natasha", "Steve", "Eltran", "Natasha"], "Natasha")
# -> 2
park["how_many_namefellows"](["Natasha", "Steve", "Eltran"], "Bucky")
# -> 0
park["remove_the_last_person"](["Natasha", "Steve", "Rocket"])
# -> 'Rocket'
park["sorted_names"](["Natasha", "Steve", "Eltran", "Natasha", "Rocket"])
# -> ['Eltran', 'Natasha', 'Natasha', 'Rocket', 'Steve']
```

## Rules
- this task implements **Exercism tasks 4, 5, 6 and 7 only** — `add_me_to_the_queue`, `find_my_friend` and `add_me_with_my_friends` belong to task `015_chaitanas_colossal_coaster`
- the dict keys are exactly the four strings above, and each value is the function itself — no parentheses
- the mean person is always in the queue, and only their **first** appearance is removed — namefellows keep their places
- `how_many_namefellows` returns `0` for a name that is not there; it never raises
- `remove_the_last_person` returns the *name*, not the queue
- alphabetical means Python's own ascending string order, which is what `sort()` and `sorted()` do with no arguments

> [!WARNING]
> Three of the four are graded on what happened to the list you were handed. `remove_the_mean_person` must return that very list (`is`, not merely `==`). `remove_the_last_person` must leave the queue one person shorter. `sorted_names` must return a **different** object and leave the queue in its original order — sorting the caller's list in place produces the right names and still fails.

## Hints
### Hint 1
Four more list methods, one per task. You know the mean person's name, so you can remove them **by value** rather than by position. Counting how often a value occurs in a list is a method too. For the last person in line you *could* remove them by name, but popping them off the end is quicker and hands you the name at the same time. And for the office roster, remember that you need to avoid mutating the queue and losing its original order.
### Hint 2
The four you want are `remove()`, `count()`, `pop()` and `sort()` — or, for the last one, the built-in `sorted()`.

`remove()` and `sort()` change the list in place and evaluate to `None`, so call them on one line and return on the next. `count()` is pure: it changes nothing and gives you the number.

`pop()` is the interesting one. It changes the list **and** returns the item it took out, which is exactly the two things task 6 asks for in a single call — and with no argument it takes the last element.

For the roster you have two honest routes. Make a shallow copy first (`queue[:]` or `queue.copy()`) and sort *that*, or hand the queue to `sorted()`, which builds the new list for you. Either way the queue itself must come out of the function in the order it went in.
### Hint 3
Different data, same four methods — an alert list:

```python
alerts = ['disk', 'cpu', 'disk', 'net']
alerts.count('disk')       # -> 2
alerts.count('memory')     # -> 0

alerts.remove('cpu')
alerts                     # -> ['disk', 'disk', 'net']

alerts.pop()               # -> 'net'
alerts                     # -> ['disk', 'disk']

names = ['net', 'cpu']
sorted(names)              # -> ['cpu', 'net']    a new list
names                      # -> ['net', 'cpu']    untouched
names.sort()               # -> None              nothing came back
names                      # -> ['cpu', 'net']    but the list moved
```

The bottom four lines are the whole distinction: one of them gives you a list, the other gives you `None` and rearranges what you already had.
