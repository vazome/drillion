---
title: list-methods — joining the coaster queue
difficulty: medium
tier: core
minutes: 12
prereqs: [12, 13]
tags: [list-methods]
source: exercism/python concept/chaitanas-colossal-coaster (MIT, adapted)
---
# list-methods — joining the coaster queue

*`append`, `index`, `insert` — three methods that change the list you were handed.*

## Read first
- [more on lists (Python tutorial)](https://devdocs.io/python~3.14/tutorial/datastructures#more-on-lists) — the method-by-method table: `append`, `insert`, `index` and the rest
- [mutable sequence operations](https://devdocs.io/python~3.14/library/stdtypes#typesseq-mutable) — the formal definition of what each mutating method does, and what it returns
- [the `list` type](https://devdocs.io/python~3.14/library/stdtypes#list) — the reference page for the type itself
- [`sorted()`](https://devdocs.io/python~3.14/library/functions#sorted) — the non-mutating counterpart you will meet in the next task
- [sorting HOW TO](https://devdocs.io/python~3.14/howto/sorting) — in-place versus copy, spelled out
- [Timsort](https://en.wikipedia.org/wiki/Timsort) — what Python used to sort lists between 2002 and 2022, for background

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Chaitana's theme park has two queues and a steady stream of people who need putting into the right one, found inside it, or slotted in beside their friends. That is a work queue: jobs appended to the end, a job located by name, an urgent job inserted at a position. The detail that this task actually grades — and that bites people in real code — is that these methods change the list **in place** and hand back `None`, so `queue = queue.append(name)` silently throws your queue away. Building that reflex here costs ten minutes; not having it costs an afternoon.

## You get
Nothing. `solve()` takes **no arguments**; the grader calls your functions with the queues. A queue is a plain `list` of name strings, in the order people are standing.

> [!NOTE]
> Exercism asks for all seven functions in one `list_methods.py`. Here the task is split in two: **this task covers tasks 1–3**, and tasks 4–7 are task `016_chaitanas_colossal_coaster`. There is one entry point — `solve()` returns a dict that hands your three functions to the grader, keyed by name.

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
- this task implements **Exercism tasks 1, 2 and 3 only** — `remove_the_mean_person`, `how_many_namefellows`, `remove_the_last_person` and `sorted_names` belong to task `016_chaitanas_colossal_coaster`
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- a new arrival always joins the **end** of the queue their ticket buys them; the other queue is not touched at all
- the friend is always somewhere in the queue, so `find_my_friend` never has to report "not found"
- an `index` past the end of the queue puts the person last, which is what `insert` already does — you do not have to special-case it

> [!WARNING]
> Two of these are graded on **identity**, not just on contents: the tests assert that the list you return `is` the queue you were given. `express_queue + [person_name]` produces the right names in a brand new list and still fails. Mutate the queue you were handed, then return that same object.

## Hints
### Hint 1
Each of the three is one or two lines, and each is a list method you can find in [more on lists](https://devdocs.io/python~3.14/tutorial/datastructures#more-on-lists). An `if`/`else` decides which queue you are dealing with in task 1, and then one method puts the person on the end of that queue. For task 2, one method searches a list for a value and gives you back its position. For task 3 you already know the position — one method drops a value in at a given index.
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
