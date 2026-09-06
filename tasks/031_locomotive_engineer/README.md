---
title: unpacking-and-multiple-assignment — routes and the wagon depot grid
difficulty: medium
tier: core
minutes: 15
prereqs: [30]
tags: [unpacking-and-multiple-assignment]
source: exercism/python concept/locomotive-engineer (MIT, adapted)
---
# unpacking-and-multiple-assignment — routes and the wagon depot grid

*`**kwargs`, `{**a, **b}` and transposing a grid with `zip(*rows)`.*

## Read first
- [Trey Hunner: asterisks in Python](https://treyhunner.com/2018/10/asterisks-in-python-what-they-are-and-how-to-use-them/) — the one article that covers every use of `*` and `**`
- [Trey Hunner: tuple unpacking improves readability](https://treyhunner.com/2018/03/tuple-unpacking-improves-python-code-readability/) — why naming the parts beats indexing them
- [PEP 3132: extended iterable unpacking](https://peps.python.org/pep-3132/) — the `first, *rest = seq` form and why it exists
- [PEP 448: additional unpacking generalizations](https://peps.python.org/pep-0448/) — `[*a, *b]` and `{**a, **b}` in literals and calls
- [Stack Abuse: unpacking beyond parallel assignment](https://stackabuse.com/unpacking-in-python-beyond-parallel-assignment/) — worked examples of each form
- [Arbitrary argument lists](https://devdocs.io/python~3.14/tutorial/controlflow#arbitrary-argument-lists) — `*args` and `**kwargs` in a function definition
- [Dan Bader: nested unpacking](https://dbader.org/blog/python-nested-unpacking) — unpacking a structure that is itself full of structures
- [zip()](https://devdocs.io/python~3.14/library/functions#zip) — pairs up the items of several iterables; with `*` in front of a list of rows it transposes them

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Same friend, harder paperwork. The routing records need the intermediate stops folded in — and nobody knows in advance how many stops a route has, so they arrive as keyword arguments. Other routes are missing details that differ from route to route: speed here, temperature there, so the merge has to be generic. And the wagon depot is stored wrong: the rows are grouped by colour when the *columns* should be. All three are the double-star half of unpacking, plus the one line of `zip` that turns rows into columns.

## You get
Nothing. Routes, extra details and depot rows arrive as arguments to your functions.

> [!NOTE]
> Exercism asks for five functions in one `locomotive_engineer.py`. Here the task is split in two: tasks 1–2 are task `030_locomotive_engineer`, and **this task covers tasks 3–5**. And there is one entry point: `solve()` takes **no arguments** and returns a dict that hands your three functions to the grader, keyed by name.

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
- this task implements **Exercism tasks 3, 4 and 5 only** — `get_list_of_wagons` and `fix_list_of_wagons` belong to task `030_locomotive_engineer`
- `add_missing_stops` receives the stops as **keyword arguments**, so its signature ends with a `**` parameter; only their *values* go into the `"stops"` list, and they keep the order they were passed in
- with no stops at all, `"stops"` is still there, holding an empty list
- `extend_route_information` merges the two dicts; the second dict's keys can be anything, and its value wins if a key appears in both
- both route functions build and return a **new** dict rather than mutating the one they were handed
- `fix_wagon_depot` is a transpose: the wagon at row *i*, column *j* ends up at row *j*, column *i*; the depot is always 3 rows of 3
- the rows it returns are `list`s of tuples — the `(id, colour)` pairs stay tuples, the rows do not

> [!NOTE]
> Exercism asks you to reach for packing, unpacking and multiple assignment here rather than for `dict` methods, slicing and index arithmetic. The tests cannot tell the difference — that is just what the task is for.

## Hints
### Hint 1
Two stars this time. `**kwargs` in a parameter list collects any number of `name=value` arguments into a dictionary; `{**a, **b}` in an expression pours two dictionaries into one new one, with the later one winning wherever the keys overlap. Between them they cover tasks 3 and 4 in about a line each.
### Hint 2
For task 3, the stops arrive as keyword arguments, so *inside* the function they are already a dict — you only need their values, in order, under one new key. Build the answer as a new dict literal that spreads the route in and then adds the extra key, rather than mutating the dict you were handed. [`<dict>.values()`](https://devdocs.io/python~3.14/library/stdtypes#dict.values) gives you the values, and `list(...)` fixes them as a list.

Task 5 is a transpose. `zip(*rows)` feeds each row to [`zip`](https://devdocs.io/python~3.14/library/functions#zip) as a separate argument, so `zip` pairs up first-of-each, second-of-each, third-of-each — which is exactly the swap the depot needs. `zip` yields tuples, though, and the depot wants each row as a *list* of tuples; a starred assignment target like `[*row] = ...` unpacks one of those into a list for you, and you can name all three rows in a single multiple assignment.
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
