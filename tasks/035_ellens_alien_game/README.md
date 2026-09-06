---
title: classes — Ellen's alien, its own health and its own position
difficulty: medium
tier: core
minutes: 15
prereqs: [32]
tags: [classes]
source: exercism/python concept/ellens-alien-game (MIT, adapted)
---
# classes — Ellen's alien, its own health and its own position

*Classes — `__init__`, methods, instance attributes, and one class attribute.*

## Read first
- [Classes (the Python tutorial)](https://devdocs.io/python~3.14/tutorial/classes) — `class`, `__init__`, `self`, and the difference between a class attribute and an instance attribute
- [Python Morsels: Classes](https://www.pythonmorsels.com/topics/classes/) — a short rundown of what a class actually is
- [Real Python: OOP in Python 3](https://realpython.com/python3-object-oriented-programming/) — the same material at length, with worked examples
- [DigitalOcean: Class and instance variables](https://www.digitalocean.com/community/tutorials/understanding-class-and-instance-variables-in-python-3) — the exact distinction this task grades
- [DigitalOcean: Constructing classes and defining objects](https://www.digitalocean.com/community/tutorials/how-to-construct-classes-and-define-objects-in-python-3) — a gentler start if `self` is still strange
- [PyBites: when to use classes](https://pybit.es/articles/when-classes/) — and when a plain function or dict is the better answer
- [The `pass` statement](https://devdocs.io/python~3.14/reference/simple_stmts#the-pass-statement) — the placeholder body task 5 asks for

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A game has a thousand aliens on screen and each one has to remember where it is and how much damage it has taken. Keeping that in parallel lists — one for x, one for y, one for health, all indexed the same way — falls apart the first time an alien dies and the indexes shift. A class puts the three numbers and the four things you can do to them in one place, so "hit that alien" is one call and the alien is the only thing that knows how its own health works. The distinction the task really turns on is the one every code review asks about: health belongs to *one* alien, but the running total of aliens ever spawned belongs to the *class*, and putting either in the wrong place is a bug you only see at scale.

## You get
Nothing. `solve()` takes **no arguments** and hands back the `Alien` **class itself** — the class object, not an instance of it, so `return Alien` with no parentheses. The grader then builds aliens with it: `Alien(2, -1)`.

> [!NOTE]
> Exercism asks for the class plus a standalone `new_aliens_collection()` function in one `classes.py`. Here the task is split in two: **this task covers tasks 1–6**, the class itself. Task 7, the function that builds a list of aliens from a list of positions, is task `036_ellens_alien_game`.

## You return
The `Alien` class. The grader uses it exactly as Ellen's game would.

```python
Alien = solve()

alien = Alien(2, -1)         # x first, then y
alien.x_coordinate           # -> 2
alien.y_coordinate           # -> -1
alien.health                 # -> 3

alien.hit()
alien.health                 # -> 2
alien.is_alive()             # -> True

alien.teleport(5, -4)
alien.x_coordinate           # -> 5
alien.collision_detection(Alien(5, -4))   # -> None

Alien.total_aliens_created   # -> however many aliens have been built so far
```

| member | what it is |
| --- | --- |
| `Alien(x_coordinate, y_coordinate)` | the constructor: stores both coordinates on the instance and starts `health` at 3 |
| `alien.x_coordinate`, `alien.y_coordinate` | instance attributes holding this alien's position |
| `alien.health` | an instance attribute, starting at 3 |
| `alien.hit()` | takes one health point off **this** alien; returns nothing |
| `alien.is_alive()` | `True` while this alien still has health left, `False` once it is out |
| `alien.teleport(new_x_coordinate, new_y_coordinate)` | moves this alien; returns nothing |
| `alien.collision_detection(other)` | a placeholder Ellen will fill in later: it takes one argument, does nothing, returns `None` |
| `Alien.total_aliens_created` | a **class** attribute: how many aliens have been constructed, counting up by one every time a new one is built |

## Rules
- this task implements **Exercism tasks 1 to 6 only** — `new_aliens_collection` belongs to task `036_ellens_alien_game`
- `solve()` returns the class, not an instance: `return Alien`, never `return Alien()`
- the attribute names are checked by the grader exactly as spelled above (`x_coordinate`, not `x`)
- `health` must live on the instance: hitting one alien must not change another alien's health
- `total_aliens_created` must live on the class: every alien reports the same number, and reading it from the class directly (`Alien.total_aliens_created`) gives that number too
- `collision_detection` must be callable with one argument and return `None` — Python returns `None` from a function that never returns anything, so a body of `pass` is the whole job

> [!NOTE]
> Whether `hit()` stops at zero or lets health go negative is genuinely up to you: Exercism's own tests accept both, and so does this grader. Just make sure `is_alive()` agrees with whichever you picked.

## Hints
### Hint 1
Every method here takes `self` as its first parameter, including the constructor — and the constructor's name has two underscores on **both** sides: `__init__`. Anything you want an alien to remember about itself gets stored as `self.<name> = ...` inside `__init__`; anything you want *all* aliens to share sits directly in the class body, above the methods. Exactly one of the members in the table belongs in that second group — find it before you start typing.
### Hint 2
Shape of the work:

- class body, before any `def`: `total_aliens_created = 0`. That line runs once, when the class is defined, so the counter is shared by every alien.
- `__init__(self, x_coordinate, y_coordinate)`: store both coordinates on `self`, set `self.health = 3`, and bump the shared counter. Bump it through the **class name** — `Alien.total_aliens_created += 1` — because `self.total_aliens_created += 1` would quietly create a per-alien copy and the count would stick at 1 forever.
- `hit(self)`: `self.health -= 1`. You may clamp it at zero instead; both pass.
- `is_alive(self)`: return the comparison itself, `self.health > 0`, not an `if`/`else` around it.
- `teleport(self, new_x_coordinate, new_y_coordinate)`: reassign the two instance attributes.
- `collision_detection(self, other)`: a body of `pass`. It has to accept the argument and return nothing.

Then `solve()` returns the class object: the bare name `Alien`.
### Hint 3
Different data, same shape. A build agent that remembers its own queue and how many agents exist:

```python
class Agent:
    total_agents_started = 0          # shared by every agent

    def __init__(self, name, region):
        Agent.total_agents_started += 1
        self.name = name              # this agent's own
        self.region = region
        self.jobs_left = 5

    def take_job(self):
        self.jobs_left -= 1

    def is_free(self):
        return self.jobs_left > 0

    def move(self, new_region):
        self.region = new_region

    def on_failure(self, error):
        pass                          # to be written when we know what to log

one, two = Agent("a", "eu"), Agent("b", "us")
one.take_job()
one.jobs_left, two.jobs_left          # -> (4, 5)   jobs_left is per agent
Agent.total_agents_started            # -> 2        the counter is per class
```

Move `jobs_left = 5` up next to `total_agents_started` and `one.take_job()` would drain every agent at once — that one line is the whole instance-versus-class distinction.
