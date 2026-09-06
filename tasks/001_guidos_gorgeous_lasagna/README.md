---
title: basics — Guido's lasagna kitchen timer
difficulty: easy
tier: core
minutes: 12
prereqs: []
tags: [functions]
source: exercism/python concept/guidos-gorgeous-lasagna (MIT, adapted)
---
# basics — Guido's lasagna kitchen timer

*Constants and small functions — the shape every Python module has.*

## Read first
- [Defining functions](https://devdocs.io/python~3.14/tutorial/controlflow#defining-functions) — `def`, parameters, `return`, and what a function hands back when you forget to return anything
- [Reuven Lerner: Understanding Python Assignment](https://lerner.co.il/2019/06/18/understanding-python-assignment/) — what `name = value` actually binds, and why `SCREAMING_SNAKE_CASE` is a promise to yourself, not a lock
- [Real Python: Commenting vs Documenting Code](https://realpython.com/documenting-python-code/#commenting-vs-documenting-code) — comments explain why, docstrings explain what
- [Python Morsels: Everything is an Object](https://www.pythonmorsels.com/everything-is-an-object/) — including functions, which is why one fits in a dict
- [Eli Bendersky: Python internals: how callables work](https://eli.thegreenplace.net/2012/03/23/python-internals-how-callables-work/) — what actually happens at `f()`
- [Sentdex (YouTube): Python 3 Programming Tutorial — Functions](https://www.youtube.com/watch?v=owglNL1KQf0) — the same material, spoken
- [dynamic typing and strong typing](https://stackoverflow.com/questions/11328920/is-python-strongly-typed) — why Python lets you rebind a name to another type but will not add an `int` to a `str`
- [type hints](https://devdocs.io/python~3.14/library/typing) — optional annotations, ignored at runtime
- [significant indentation](https://devdocs.io/python~3.14/reference/lexical_analysis#indentation) — the block rule that bites everyone once
- [DigitalOcean: How to Write Doctests in Python](https://www.digitalocean.com/community/tutorials/how-to-write-doctests-in-python) — docstrings that are also tests
- [Ned Batchelder: Is Python Interpreted or Compiled? Yes.](https://nedbatchelder.com/blog/201803/is_python_interpreted_or_compiled_yes.html) — what runs when you run a `.py`

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
You are writing the kitchen timer for a recipe app. The cook opens the lasagna recipe, tells the app how many layers they are building and how long the dish has already been in the oven, and the app has to answer two questions: "how much longer does it bake?" and "how long have I been at this?". The cookbook numbers never change — 40 minutes in the oven, 2 minutes of work per layer — so they belong in named constants at the top of the file, not copy-pasted into every calculation. That is the whole habit this task is about.

## You get
Nothing. You define the numbers and the functions yourself.

> [!NOTE]
> Exercism hands you a `lasagna.py` stub and checks the module-level names directly. Here there is one entry point: `solve()` takes **no arguments** and returns a dict that hands those same four names to the grader. Define the constants and functions wherever you like — module level or inside `solve` — as long as the dict points at them.

## You return
A dict with these four entries, wired to your own code.

| key | what it holds |
| --- | --- |
| `"EXPECTED_BAKE_TIME"` | the plain number 40: how many minutes the cookbook says the lasagna spends in the oven, start to finish |
| `"bake_time_remaining"` | a function taking `elapsed_bake_time` (minutes already spent in the oven, e.g. 30) and returning how many minutes of baking are still to go |
| `"preparation_time_in_minutes"` | a function taking `number_of_layers` (e.g. 2) and returning the minutes of layering work, at 2 minutes a layer |
| `"elapsed_time_in_minutes"` | a function taking `number_of_layers` and `elapsed_bake_time` and returning the total minutes spent in the kitchen: the layering work plus the baking done so far |

```python
answers = solve()
answers["EXPECTED_BAKE_TIME"]                    # -> 40
answers["bake_time_remaining"](30)               # -> 10   (40 - 30)
answers["preparation_time_in_minutes"](2)        # -> 4    (2 layers x 2 minutes)
answers["elapsed_time_in_minutes"](3, 20)        # -> 26   (3 x 2 of prep, plus 20 baked)
```

## Rules
Every input is a whole number of minutes or layers; every function returns a number. The dict keys are exactly the four strings above.

- the three function values are the functions **themselves**, not the result of calling them — `{"bake_time_remaining": bake_time_remaining}`, no parentheses
- `"EXPECTED_BAKE_TIME"` is the number, not a function
- Exercism's task 5 (docstrings) is not graded here, so write them for yourself or skip them

Nobody bakes past the cookbook time, so `bake_time_remaining` never has to deal with a negative answer.

## Hints
### Hint 1
Two numbers in this recipe never change: 40 and 2. [Name](https://realpython.com/python-variables/) each one and [assign](https://devdocs.io/python~3.14/reference/simple_stmts#assignment-statements) it an integer value once, above the functions, and let the functions read those names — that is how you avoid a ["magic number"](https://en.wikipedia.org/wiki/Magic_number_(programming)) sitting in the middle of your arithmetic. The third function does not need to redo the per-layer arithmetic: remember, you can always *call* a function you have defined previously.
### Hint 2
Shape of the work: define the two constants, then define the three functions, then build the dict that maps each key string to the matching function.

- `bake_time_remaining` — one parameter, the time elapsed so far; use the [mathematical operator for subtraction](https://devdocs.io/python~3.14/tutorial/introduction#numbers) and [return a value](https://devdocs.io/python~3.14/reference/simple_stmts#return).
- `preparation_time_in_minutes` — one parameter, the number of layers; use the operator for multiplication and return a value.
- `elapsed_time_in_minutes` — two parameters; [use the operator for addition](https://devdocs.io/python~3.14/tutorial/introduction#using-python-as-a-calculator) to sum the other two answers.

Put the function name in the dict WITHOUT parentheses — `{'bake_time_remaining': bake_time_remaining}` hands over the function itself so the caller can run it later; adding `()` would run it now, with no arguments, and store the result.
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
