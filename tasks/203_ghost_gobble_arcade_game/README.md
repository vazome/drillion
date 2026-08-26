---
title: bools — the Pac-Man rulebook
minutes: 12
prereqs: [200]
tags: [exercism, bools, core]
source: exercism/python concept/ghost-gobble-arcade-game (MIT, adapted)
---
# bools — the Pac-Man rulebook

*and / or / not — four arcade-game rules built from booleans alone.*

## Why
You have taken over the rules engine of an arcade game. The graphics team already worked out where everything is on screen; every frame they hand the rules engine a handful of yes/no facts — is a power pellet active, is the player touching a ghost, has the player eaten the last dot — and the engine has to say what that means for the game: did the player score, did they eat the ghost, did they lose, did they win. Nothing here is arithmetic. It is four sentences of English turned into and / or / not, which is most of what business rules ever are.

## Introduction
Python represents true and false values with the [`bool`][bools] type, which is a subclass of `int`.
 There are only two values in this type: `True` and `False`.
  These values can be bound to a variable:

```python
>>> true_variable = True
>>> false_variable = False
```

We can evaluate Boolean expressions using the `and`, `or`, and `not` operators:

```python
>>> true_variable = True and True
>>> false_variable = True and False

>>> true_variable = False or True
>>> false_variable = False or False

>>> true_variable = not False
>>> false_variable = not True
```

[bools]: https://docs.python.org/3/library/stdtypes.html#typebool

## Instructions
In this exercise, you need to implement some rules from [Pac-Man][Pac-Man], the classic 1980s-era arcade-game.

You have four rules to implement, all related to the game states.

> _Do not worry about how the arguments are derived, just focus on combining the arguments to return the intended result._

### 1. Define if Pac-Man eats a ghost

Define the `eat_ghost()` function that takes two parameters (_if Pac-Man has a power pellet active_ and _if Pac-Man is touching a ghost_) and returns a Boolean value if Pac-Man is able to eat a ghost.
 The function should return `True` only if Pac-Man has a power pellet active and is touching a ghost.

```python
>>> eat_ghost(False, True)
...
False
```

### 2. Define if Pac-Man scores

Define the `score()` function that takes two parameters (_if Pac-Man is touching a power pellet_ and _if Pac-Man is touching a dot_) and returns a Boolean value if Pac-Man scored.
 The function should return `True` if Pac-Man is touching a power pellet or a dot.

```python
>>> score(True, True)
...
True
```

### 3. Define if Pac-Man loses

Define the `lose()` function that takes two parameters (_if Pac-Man has a power pellet active_ and _if Pac-Man is touching a ghost_) and returns a Boolean value if Pac-Man loses.
 The function should return `True` if Pac-Man is touching a ghost and does not have a power pellet active.

```python
>>> lose(False, True)
...
True
```

### 4. Define if Pac-Man wins

Define the `win()` function that takes three parameters (_if Pac-Man has eaten all of the dots_, _if Pac-Man has a power pellet active_, and _if Pac-Man is touching a ghost_) and returns a Boolean value if Pac-Man wins.
 The function should return `True` if Pac-Man has eaten all of the dots and has not lost based on the rules defined in part 3.

```python
>>> win(False, True, False)
...
False
```

[Pac-Man]: https://en.wikipedia.org/wiki/Pac-Man

## You get
Nothing. Every fact arrives as an argument to one of your functions, and every fact is already a plain `True` or `False` — you never work out where anything is.

> [!NOTE]
> Exercism has you define four top-level functions in `arcade_game.py`. Here there is one entry point: `solve()` takes **no arguments** and returns a dict that hands those four functions to the grader, keyed by name.

## You return
A dict with these four functions, all returning `True` or `False`.

| key | parameters | returns `True` when |
| --- | --- | --- |
| `"eat_ghost"` | `power_pellet_active`, `touching_ghost` | the player eats a ghost — only while a power pellet is active AND they are touching that ghost |
| `"score"` | `touching_power_pellet`, `touching_dot` | the player scores — they touch a power pellet or a dot; either one is enough |
| `"lose"` | `power_pellet_active`, `touching_ghost` | the player loses — they touch a ghost with no power pellet active |
| `"win"` | `has_eaten_all_dots`, `power_pellet_active`, `touching_ghost` | the player wins — every dot is eaten and they have not, at that same moment, lost by the rule above |

```python
rules = solve()
rules["eat_ghost"](False, True)   # -> False  (touching a ghost, but no pellet)
rules["score"](True, False)       # -> True   (a power pellet still counts)
rules["lose"](True, True)         # -> False  (the pellet saves you)
rules["win"](True, True, True)    # -> True   (all dots eaten, and not lost)
rules["win"](True, False, True)   # -> False  (all dots eaten, but lost anyway)
```

## Rules
- the dict keys are exactly the four strings above, and each value is the function itself — no parentheses
- every parameter arrives as a real `True`/`False`; return booleans, not `1`/`0` or a string (the tests compare with `==`, so an int would pass here — but neighbouring tasks check `is True`)
- the parameters are positional and in the order given above

## Exercism hints

### General

- For an overview, this section of the Python documentation: [Truth Value Testing][stdlib-bools] might help.
- Don't worry about how the arguments are _derived_, focus on combining the arguments to return the intended result.

### 1. Define if Pac-Man can eat a ghost

- You can use the [Boolean][boolean] [operators][Boolean-operators] to combine arguments for a result.

### 2. Define if Pac-Man scores

- You can use the [Boolean][boolean] [operators][Boolean-operators] to combine arguments for a result.

### 3. Define if Pac-Man loses

- You can use the [boolean][Boolean] [operators][Boolean-operators] to combine arguments for a result.

### 4. Define if Pac-Man wins

- You can use the [Boolean][boolean] [operators][Boolean-operators] to combine arguments for a result.

[Boolean-operators]: https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not
[boolean]: https://docs.python.org/3/library/stdtypes.html#truth
[stdlib-bools]: https://docs.python.org/3/library/stdtypes.html#truth-value-testing

## Read first
- [boolean-operators](https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not) — the three operators, their precedence (`not` binds tightest, then `and`, then `or`)
- [Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth) — why you never need to write `if flag == True`
- [boolean values](https://docs.python.org/3/library/stdtypes.html#bltin-boolean-values) — `True` and `False`, a subclass of `int`
- [bool() function](https://docs.python.org/3/library/functions.html#bool) — turning any object into one of the two
- [Comparisons in Python](https://docs.python.org/3/library/stdtypes.html#comparisons) — the operators that produce bools in the first place
- [Problem Solving with Python — Boolean Data Type](https://problemsolvingwithpython.com/04-Data-Types-and-Variables/04.02-Boolean-Data-Type/) — a gentler walk-through
- [Python Anti-Patterns: comparing things to True in the wrong way](https://docs.quantifiedcode.com/python-anti-patterns/readability/comparison_to_true.html) — the `== True` habit and why to drop it
- [PEP 285 — Adding a bool type](https://www.python.org/dev/peps/pep-0285/) — why `bool` subclasses `int`

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Do not worry about how the arguments are *derived*, focus on combining the arguments to return the intended result. Read each rule out loud and mark the joining word: 'active AND touching' is `and`; 'a pellet OR a dot' is `or`; 'with NO pellet' is `not`. Each function is a single `return` of the arguments combined that way — no `if` statement is needed, because combining two bools with `and` already gives you a bool. This section of the Python documentation, [Truth Value Testing](https://docs.python.org/3/library/stdtypes.html#truth-value-testing), might help.
### Hint 2
All four rules are the same move: use the [Boolean](https://docs.python.org/3/library/stdtypes.html#truth) [operators](https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not) to combine the arguments into a result.

`win` is the interesting one: it is 'all dots eaten AND not lost'. You already wrote the losing rule as its own function, so call it rather than restating 'touching a ghost without a pellet' a second time — that way one bug fix fixes both. Precedence: `not` binds tighter than `and`, so `not a and b` reads as `(not a) and b`; add parentheses whenever you have to stop and think about it.
### Hint 3
Different data, same shape. A door lock: it opens when the badge is valid and the building is not in lockdown; it alarms when someone pushes the door while it is not open.

```python
def opens(badge_valid, lockdown):
    return badge_valid and not lockdown
def alarms(pushed, badge_valid, lockdown):
    return pushed and not opens(badge_valid, lockdown)
```

`alarms` reuses `opens` instead of repeating its condition — that is exactly the relationship `win` has with the losing rule.
