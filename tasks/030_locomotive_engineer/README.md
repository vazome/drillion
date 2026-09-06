---
title: unpacking-and-multiple-assignment — packing and reordering wagons
difficulty: medium
tier: core
minutes: 13
prereqs: [25]
tags: [unpacking-and-multiple-assignment]
source: exercism/python concept/locomotive-engineer (MIT, adapted)
---
# unpacking-and-multiple-assignment — packing and reordering wagons

*`*args` on the way in, starred unpacking on the way out.*

## Read first
- [Trey Hunner: asterisks in Python](https://treyhunner.com/2018/10/asterisks-in-python-what-they-are-and-how-to-use-them/) — the one article that covers every use of `*` and `**`
- [Trey Hunner: tuple unpacking improves readability](https://treyhunner.com/2018/03/tuple-unpacking-improves-python-code-readability/) — why naming the parts beats indexing them
- [PEP 3132: extended iterable unpacking](https://peps.python.org/pep-3132/) — the `first, *rest = seq` form and why it exists
- [PEP 448: additional unpacking generalizations](https://peps.python.org/pep-0448/) — `[*a, *b]` and `{**a, **b}` in literals and calls
- [Stack Abuse: unpacking beyond parallel assignment](https://stackabuse.com/unpacking-in-python-beyond-parallel-assignment/) — worked examples of each form
- [Arbitrary argument lists](https://devdocs.io/python~3.14/tutorial/controlflow#arbitrary-argument-lists) — `*args` and `**kwargs` in a function definition

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Linus drives cargo trains and keeps the wagon numbers in his head, not in a system. The logistics program needs them as one tidy list, however many there happen to be that morning — and it needs yesterday's mistake fixed: two wagons were coupled to the front instead of the back, and a second list of forgotten IDs has to go in right behind the locomotive. Both jobs are the same Python idea seen from its two sides: a `*` in a parameter list gathers however many arguments turn up, and a `*` in an assignment or a literal spreads a collection back out.

## You get
Nothing. Wagon IDs arrive as arguments to your functions.

> [!NOTE]
> Exercism asks for five functions in one `locomotive_engineer.py`. Here the task is split in two: **this task covers tasks 1–2**, and tasks 3–5 are task `031_locomotive_engineer`. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your two functions to the grader, keyed by name.

## You return
A dict with these two functions.

| key | parameters | returns |
| --- | --- | --- |
| `"get_list_of_wagons"` | an **arbitrary number** of positional wagon IDs — `get_list_of_wagons(1, 7, 12)`, not a list argument | those IDs as a single list, in the order given |
| `"fix_list_of_wagons"` | `each_wagons_id` — the train as a list, with the locomotive (`1`) third; `missing_wagons` — a list of IDs to splice in | a new list: locomotive, the missing wagons, the rest of the train, then the two strays that were in front |

```python
train = solve()
train["get_list_of_wagons"](1, 7, 12, 3, 14, 8, 5)
# -> [1, 7, 12, 3, 14, 8, 5]
train["get_list_of_wagons"](1)
# -> [1]
train["fix_list_of_wagons"]([2, 5, 1, 7, 4, 12, 6, 3, 13], [3, 17, 6, 15])
# -> [1, 3, 17, 6, 15, 7, 4, 12, 6, 3, 13, 2, 5]
```

Reading that last one: `2` and `5` were the two wrongly-coupled wagons, `1` is the locomotive, `[3, 17, 6, 15]` are the forgotten IDs that belong straight behind it, and `7, 4, 12, 6, 3, 13` is the rest of the train, untouched.

## Rules
- this task implements **Exercism tasks 1 and 2 only** — `add_missing_stops`, `extend_route_information` and `fix_wagon_depot` belong to task `031_locomotive_engineer`
- `get_list_of_wagons` takes the IDs as **separate positional arguments**, not as one list; it must cope with none at all and with a dozen
- in `fix_list_of_wagons` the locomotive is always the **third** item of the train list (index `2`); the two items before it are the ones to move to the end, keeping their order
- the result order is: locomotive, then every missing wagon in the order given, then the remainder of the train in its order, then the two strays
- both functions return `list`s, not tuples
- the second list may be empty, and so may the remainder of the train

> [!NOTE]
> Exercism asks you to solve these with packing, unpacking and multiple assignment rather than with slicing, `insert()` and index arithmetic. The tests cannot tell the difference — but that is the point of the task.

## Hints
### Hint 1
Task 1 is about the function's **parameter list**, not its body: a `*` in front of a parameter name tells Python to collect however many positional arguments were passed into a single tuple, under that name. The body is then one conversion. Task 2 is the same star used the other way round — on the left of an `=` it soaks up "all the rest".
### Hint 2
For task 2, name the pieces you care about in **one assignment**: the two strays, the locomotive, and a starred name that swallows everything after it. That single line replaces every bit of indexing and slicing you were about to write, and it names the parts so the next line reads like the story.

Then build the answer as a list literal and *spread* the two collections into it with a `*` in front of each, in the order the story asks for: locomotive first, the forgotten wagons behind it, the remaining train, and the strays at the end. Inside a list literal, `*rest` means "and then all of these", not "multiply".
### Hint 3
Different data, same shape. A CSV header row that needs its key column moved to the front:

```python
def collect(*fields):
    return list(fields)

collect("id", "name", "email")     # -> ['id', 'name', 'email']

row = ["ts", "level", "msg", "svc", "host"]
first, second, key, *rest = row
[key, *rest, first, second]        # -> ['msg', 'svc', 'host', 'ts', 'level']
```

`collect` never mentions how many fields there are, and the reordering line never mentions an index.
