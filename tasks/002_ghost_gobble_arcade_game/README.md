---
title: bools — the Pac-Man rulebook
difficulty: easy
tier: core
minutes: 12
prereqs: [1]
tags: [bools]
source: exercism/python concept/ghost-gobble-arcade-game (MIT, adapted)
---
# bools — the Pac-Man rulebook

*and / or / not — four arcade-game rules built from booleans alone.*

## Read first
- [boolean-operators](https://devdocs.io/python~3.14/library/stdtypes#boolean-operations-and-or-not) — the three operators, their precedence (`not` binds tightest, then `and`, then `or`)
- [Truth Value Testing](https://devdocs.io/python~3.14/library/stdtypes#truth) — why you never need to write `if flag == True`
- [boolean values](https://devdocs.io/python~3.14/library/stdtypes#bltin-boolean-values) — `True` and `False`, a subclass of `int`
- [bool() function](https://devdocs.io/python~3.14/library/functions#bool) — turning any object into one of the two
- [Comparisons in Python](https://devdocs.io/python~3.14/library/stdtypes#comparisons) — the operators that produce bools in the first place
- [Problem Solving with Python — Boolean Data Type](https://problemsolvingwithpython.com/04-Data-Types-and-Variables/04.02-Boolean-Data-Type/) — a gentler walk-through
- [Python Anti-Patterns: comparing things to True in the wrong way](https://docs.quantifiedcode.com/python-anti-patterns/readability/comparison_to_true.html) — the `== True` habit and why to drop it
- [PEP 285 — Adding a bool type](https://www.python.org/dev/peps/pep-0285/) — why `bool` subclasses `int`

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
You have taken over the rules engine of an arcade game. The graphics team already worked out where everything is on screen; every frame they hand the rules engine a handful of yes/no facts — is a power pellet active, is the player touching a ghost, has the player eaten the last dot — and the engine has to say what that means for the game: did the player score, did they eat the ghost, did they lose, did they win. Nothing here is arithmetic. It is four sentences of English turned into and / or / not, which is most of what business rules ever are.

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

## Hints
### Hint 1
Do not worry about how the arguments are *derived*, focus on combining the arguments to return the intended result. Read each rule out loud and mark the joining word: 'active AND touching' is `and`; 'a pellet OR a dot' is `or`; 'with NO pellet' is `not`. Each function is a single `return` of the arguments combined that way — no `if` statement is needed, because combining two bools with `and` already gives you a bool. This section of the Python documentation, [Truth Value Testing](https://devdocs.io/python~3.14/library/stdtypes#truth-value-testing), might help.
### Hint 2
All four rules are the same move: use the [Boolean](https://devdocs.io/python~3.14/library/stdtypes#truth) [operators](https://devdocs.io/python~3.14/library/stdtypes#boolean-operations-and-or-not) to combine the arguments into a result.

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
