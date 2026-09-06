---
title: classes — spawn a wave of aliens from a list of positions
difficulty: easy
tier: core
minutes: 12
prereqs: [35]
tags: [classes]
source: exercism/python concept/ellens-alien-game (MIT, adapted)
---
# classes — spawn a wave of aliens from a list of positions

*Classes — turning rows of data into objects, one call per row.*

## Read first
- [Classes (the Python tutorial)](https://devdocs.io/python~3.14/tutorial/classes) — the constructor call `Alien(2, -1)` is just the class name used like a function
- [Tuple unpacking](https://devdocs.io/python~3.14/tutorial/datastructures#tuples-and-sequences) — `x, y = position` splits a pair into two names in one line
- [Unpacking argument lists](https://devdocs.io/python~3.14/tutorial/controlflow#unpacking-argument-lists) — `Alien(*position)` spreads a tuple across the parameters, the shortest form of the same idea
- [List comprehensions](https://devdocs.io/python~3.14/tutorial/datastructures#list-comprehensions) — one expression per input item, and the result really is a `list`
- [Python Morsels: Classes](https://www.pythonmorsels.com/topics/classes/) — a refresher on what an instance is

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
The level designer hands the game a list of starting positions — plain coordinate pairs out of a level file. The game needs live alien objects, one per pair, in the same order. This little function is the seam every program has between "data that came from outside" and "objects the rest of the code talks to": the loader that turns rows from a database into records, the parser that turns YAML into config objects. It is three lines, and the only two things that can go wrong are forgetting that the constructor wants two arguments while the data arrives as one tuple, and returning a generator when the caller asked for a list.

## You get
The finished `Alien` class is already in the file above `solve`, marked `# given — do not edit`. It is exactly what task `035_ellens_alien_game` asks you to write: `Alien(x_coordinate, y_coordinate)`, a `health` that starts at 3, and a class-level `total_aliens_created` that counts up on every construction.

`positions` — a list of `(x, y)` tuples, in the order the aliens should appear:

```python
[(4, 7), (-1, 0), (3, 3)]
```

The list may be empty. Coordinates may be negative, and the same position may appear twice.

> [!NOTE]
> Exercism calls this function `new_aliens_collection(positions)` and asks for it alongside the class in one `classes.py`. Here **this task covers task 7 only** — the class itself is task `035_ellens_alien_game` — and the entry point is `solve(positions)`.

## You return
A `list` of `Alien` objects, one per position, in the same order as `positions`.

```python
aliens = solve([(4, 7), (-1, 0)])

len(aliens)                                       # -> 2
aliens[0].x_coordinate, aliens[0].y_coordinate    # -> (4, 7)
aliens[1].x_coordinate, aliens[1].y_coordinate    # -> (-1, 0)
aliens[0].health                                  # -> 3
solve([])                                         # -> []
```

## Rules
- one `Alien` per tuple, in order — the alien at index 0 must be built from `positions[0]`
- each alien is a **new** object: two positions that happen to be equal still give two separate aliens
- the return value is a `list`, so a generator expression or a `map(...)` object has to be wrapped in `list()`

> [!WARNING]
> A tuple is a *single* value, and the constructor takes *two* arguments — `Alien(position)` raises `TypeError: __init__() missing 1 required positional argument`. Unpack the pair before you pass it on.

## Hints
### Hint 1
One alien per position, in order, collected into a list — that is a `for` loop appending to a list, or the one-line form of the same thing. The only wrinkle: each item of `positions` is a tuple holding two numbers, but the constructor wants those two numbers as two separate arguments.
### Hint 2
Each item in `positions` is a **single** tuple, but `Alien` takes **two** parameters. So the only real question is how to get two arguments out of one tuple. Three routes work: index into it twice, unpack it into two names first, or let Python spread it for you at the call site — there is a prefix operator that does exactly that spreading, and it is the one most Python programmers reach for here.

Collect the results as you go. If you use the one-liner form, keep the square brackets: round brackets would build a generator, and the grader wants a `list`.
### Hint 3
Different data, same move. Rows out of a CSV becoming objects the rest of the program can use:

```python
class Host:
    def __init__(self, name, region):
        self.name = name
        self.region = region

rows = [("web-1", "eu-west-1"), ("db-1", "us-east-1")]
hosts = [Host(*row) for row in rows]

hosts[0].name, hosts[0].region     # -> ('web-1', 'eu-west-1')
len(hosts)                         # -> 2
```

`Host(*row)` is the whole trick: `row` is one tuple going in, two arguments coming out.
