---
title: loops — grade bands, rankings and the first perfect score
difficulty: hard
tier: core
minutes: 15
prereqs: [18]
tags: [loops]
source: exercism/python concept/making-the-grade (MIT, adapted)
---
# loops — grade bands, rankings and the first perfect score

*`range()` with a step, `enumerate()`, and the `break` that stops at the first hit.*

## Read first
- [`enumerate()`](https://devdocs.io/python~3.14/library/functions#enumerate) — `(index, value)` pairs, and the `start=` argument that lets you count from 1
- [the `range()` function](https://devdocs.io/python~3.14/tutorial/controlflow#the-range-function) — `start`, `stop` (exclusive) and `step`
- [`range()` is not an iterator (Trey Hunner)](https://treyhunner.com/2018/02/python-range-is-not-an-iterator/) — what a lazy sequence actually is
- [`break`, `continue` and loop `else`](https://devdocs.io/python~3.14/tutorial/controlflow#break-and-continue-statements-and-else-clauses-on-loops) — leaving a loop early, and the clause that runs when you did not
- [`round()`](https://devdocs.io/python~3.14/library/functions#round) — one argument gives an `int`, which is what keeps the band width whole
- [f-strings](https://devdocs.io/python~3.14/reference/lexical_analysis#formatted-string-literals) — assembling `'1. Joci: 100'` in one expression
- [`for` statements (Python tutorial)](https://devdocs.io/python~3.14/tutorial/controlflow#for-statements) — the loop all three tasks are built on
- [`enumerate()` in Python (Real Python)](https://realpython.com/python-enumerate/) — the long version, including when *not* to use it
- [Loop Like a Native (Ned Batchelder)](https://nedbatchelder.com/text/iter.html) — why indexing a list inside a loop is usually a smell
- [`StopIteration`](https://devdocs.io/python~3.14/library/exceptions#StopIteration) — the exception a `for` loop catches for you every time it ends

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
The same pile of exam scores, three harder questions. Grade bands are a counted loop with a computed step — the same arithmetic as bucketing latencies or sizing the ticks on a chart. The ranking is two lists that line up by position, which is `enumerate()`'s entire reason to exist and the thing you reach for whenever names and values arrive from two different places. And "did anyone score 100?" is the search that has to stop the moment it finds one, and still has a sensible answer when it finds nothing — the shape of every "is any host down?" check you will ever write.

## You get
Nothing. `solve()` takes **no arguments**; the grader calls your functions with the scores, the names and the pairs.

> [!NOTE]
> Exercism asks for all six functions in one `loops.py`. Here the task is split in two: **this task covers tasks 4–6**, and tasks 1–3 are task `018_making_the_grade`. There is one entry point — `solve()` returns a dict that hands your three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"letter_grades"` | `highest` — the top score anyone achieved, e.g. `100` | a list of **four** ints: the lowest score that still earns a `D`, a `C`, a `B` and an `A`, in that order |
| `"student_ranking"` | `student_scores`, `student_names` — the same length, both already sorted best first | a list of strings, one per student, formatted `'<rank>. <name>: <score>'`, with the rank starting at 1 |
| `"perfect_score"` | `student_info` — a list of `[name, score]` pairs, possibly empty | the **first** `[name, score]` pair whose score is `100`, or `[]` when nobody scored one |

```python
grades = solve()
grades["letter_grades"](100)     # -> [41, 56, 71, 86]
grades["letter_grades"](88)      # -> [41, 53, 65, 77]
grades["student_ranking"]([100, 99, 90], ['Joci', 'Sara', 'Kora'])
# -> ['1. Joci: 100', '2. Sara: 99', '3. Kora: 90']
grades["perfect_score"]([["Charles", 90], ["Tony", 80], ["Alex", 100]])
# -> ['Alex', 100]
grades["perfect_score"]([["Charles", 90], ["Tony", 80]])
# -> []
```

## Rules
- this task implements **Exercism tasks 4, 5 and 6 only** — `round_scores`, `count_failed_students` and `above_threshold` belong to task `018_making_the_grade`
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- a fail is `<= 40`, so the `D` band always starts at `41` and the first number in `letter_grades` is always `41`
- one band is `round((highest - 40) / 4)` wide, and the four thresholds step up from `41` by that width
- the ranking string has a full stop and a space after the rank and a colon and a space before the score: `'1. Joci: 100'`
- `perfect_score` hands back the pair itself — not the name, not the index — and an empty list, not `None`, when there is no perfect score

> [!WARNING]
> Exercism's own hint suggests `range(41, highest, increment)`. That is right for the sample exams, but for a few values of `highest` the increment rounds down and `range` yields **five** thresholds instead of four (try `highest = 90`). Four is the contract — `D`, `C`, `B`, `A` — so build exactly four.

## Hints
### Hint 1
The first task is arithmetic before it is a loop: these are *lower thresholds*, and the lower threshold for a `D` is `41`, because an `F` is anything `<= 40`. Work out how wide one band is, then start at `41` and step up.

The second task needs both a position and a value at the same time — Python has one built-in that hands you both. The third is a search: you cannot answer "nobody" until you have looked at everyone, but you must stop the moment you find someone.
### Hint 2
For the bands, `round()` without a second argument keeps the increment a whole number. From there, `range(<start>, <stop>, <step>)` generates a counted sequence you can append from — or you can build the four values straight from the start and the step. Either way, count what comes out: there must be exactly four.

For the ranking, `enumerate(<iterable>)` yields `(index, value)` pairs and the index starts at 0, so the rank is one more than it. If both lists are the same length and sorted the same way, the index from one retrieves the value from the other. An f-string assembles the whole line in a single expression, and `str()` around a number works too.

For the search, set the answer to the empty list **before** the loop, overwrite it when you find a 100, and `break` out; then return it after the loop. That way "nobody" is already the answer if the loop runs to the end. `continue` and `break` are the two keywords for moving past or escaping unwanted values.
### Hint 3
Different data, same three shapes — host uptimes and health checks:

```python
hosts = ['api-1', 'api-2', 'api-3']
uptimes = [99.9, 99.5, 97.2]
rows = []
for place, host in enumerate(hosts):
    rows.append(f'{place + 1}. {host}: {uptimes[place]}')
rows              # -> ['1. api-1: 99.9', '2. api-2: 99.5', '3. api-3: 97.2']

checks = [['api-1', 'ok'], ['api-2', 'down'], ['api-3', 'down']]
first_down = []
for check in checks:
    if check[1] == 'down':
        first_down = check
        break
first_down        # -> ['api-2', 'down']    api-3 was never looked at

start, step = 0, 25
[start + step * band for band in range(4)]   # -> [0, 25, 50, 75]
```

The last line is a comprehension, which you have not met yet — but the point is the arithmetic: four values, from a start and a width, and no chance of accidentally producing five.
