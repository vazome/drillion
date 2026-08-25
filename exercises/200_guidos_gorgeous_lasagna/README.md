---
title: basics — Guido's lasagna kitchen timer
minutes: 12
prereqs: []
tags: [exercism, basics, core]
source: exercism/python concept/guidos-gorgeous-lasagna (MIT, adapted)
---
# basics — Guido's lasagna kitchen timer

*Constants and small functions — the shape every Python module has.*

## Why
You are writing the kitchen timer for a recipe app. The cook opens
the lasagna recipe, tells the app how many layers they are building and how
long the dish has already been in the oven, and the app has to answer two
questions: "how much longer does it bake?" and "how long have I been at
this?". The cookbook numbers never change — 40 minutes in the oven, 2
minutes of work per layer — so they belong in named constants at the top of
the file, not copy-pasted into every calculation. That is the whole habit
this drill is about.

## You get
nothing. You define the numbers and the functions yourself.

## You return
a dict with these four entries, wired to your own code.

  "EXPECTED_BAKE_TIME" — the plain number 40: how many minutes the cookbook
  says the lasagna spends in the oven, start to finish.

  "bake_time_remaining" — a function taking `elapsed_bake_time` (minutes
  already spent in the oven, e.g. 30) and returning how many minutes of
  baking are still to go.

  "preparation_time_in_minutes" — a function taking `number_of_layers`
  (e.g. 2) and returning the minutes of layering work, at 2 minutes a layer.

  "elapsed_time_in_minutes" — a function taking `number_of_layers` and
  `elapsed_bake_time` and returning the total minutes spent in the kitchen:
  the layering work plus the baking done so far.

## Rules
Every input is a whole number of minutes or layers; every function returns
a number. The dict keys are exactly the four strings above.

```python
bake_time_remaining(30)          ->  10   (40 - 30)
preparation_time_in_minutes(2)   ->   4   (2 layers x 2 minutes)
elapsed_time_in_minutes(3, 20)   ->  26   (3 x 2 of prep, plus 20 baked)
```

Nobody bakes past the cookbook time, so `bake_time_remaining` never has to
deal with a negative answer.

## Read first
- https://lerner.co.il/2019/06/18/understanding-python-assignment/  — what `name = value` actually binds, and why SCREAMING_SNAKE_CASE is a promise to yourself, not a lock
- https://docs.python.org/3/tutorial/controlflow.html#defining-functions  — def, parameters, return, and what a function hands back when you forget to return anything
- CONCEPT: basics — naming values, defining functions, comments and docstrings; internally everything in Python is an object, functions included.

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Two numbers in this recipe never change: 40 and 2. Bind each to a name once, above the functions, and let the functions read those names. The third function does not need to redo the per-layer arithmetic — one of your other functions already knows how to do it.
### Hint 2
Shape of the work: define the two constants, then define the three functions, then build the dict that maps each key string to the matching function. Put the function name in the dict WITHOUT parentheses — `{'bake_time_remaining': bake_time_remaining}` hands over the function itself so the caller can run it later; adding `()` would run it now, with no arguments, and store the result.
### Hint 3
Different data, same shape. A car wash charges a fixed 15-minute wash plus 3 minutes per extra service:

```python
WASH_TIME = 15
PER_EXTRA = 3
def extras_time(extras):
    return extras * PER_EXTRA
def total_time(extras):
    return WASH_TIME + extras_time(extras)
def handles():
    return {'WASH_TIME': WASH_TIME, 'total_time': total_time}
```

`handles()['total_time'](2)` is 21. Note `total_time` reusing `extras_time` instead of writing `extras * 3` a second time.
