---
title: conditionals — reactor meltdown control
difficulty: medium
tier: core
minutes: 15
prereqs: [2]
tags: [conditionals]
source: exercism/python concept/meltdown-mitigation (MIT, adapted)
---
# conditionals — reactor meltdown control

*if / elif / else — three reactor decisions, each a different shape of branch.*

## Read first
- [Python Docs: Control flow tools](https://devdocs.io/python~3.14/tutorial/controlflow#tut-morecontrol) — if / elif / else: the first branch whose test is `True` wins, and the rest are never even evaluated
- [Real Python: Conditional statements in Python](https://realpython.com/python-conditional-statements/) — chained comparisons (`0 <= x < 10`) and when a ladder of `elif` beats a pile of separate `if`s
- [Python Docs: Truth value testing](https://devdocs.io/python~3.14/library/stdtypes#truth-value-testing) — what counts as `True` when the test is not a comparison
- [Python Docs: Standard types — boolean operations](https://devdocs.io/python~3.14/library/stdtypes#boolean-operations-and-or-not) — `and` / `or` / `not` inside a condition
- [Python Docs: Comparisons](https://devdocs.io/python~3.14/library/stdtypes#comparisons) — the `<` / `<=` table this whole task turns on

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
You are writing the control software for a nuclear reactor. A reactor only produces power while it sits in a narrow band called criticality: below it the core gets damaged, above it you get a meltdown. The sensors feed you raw numbers — temperature, neutron count, voltage, current — and the control room needs three plain answers off them: is the core balanced right now, how efficiently is it running, and should the rods go in or out. Each answer is a different shape of decision: one yes/no, one four-way band, one three-way band. Getting the `<` versus `<=` right is the entire job; on this machine an off-by-one boundary is not a cosmetic bug.

## You get
Nothing. Every reading arrives as an argument to one of your functions. Readings can be whole numbers or decimals.

> [!NOTE]
> Exercism has you define the three functions at the top of `conditionals.py`. Here there is one entry point: `solve()` takes **no arguments** and returns a dict that hands those three functions to the grader, keyed by name.

## You return
A dict with these three functions.

| key | parameters | returns |
| --- | --- | --- |
| `"is_criticality_balanced"` | `temperature` (kelvin, e.g. `750`), `neutrons_emitted` (per second, e.g. `600`) | `True` only when all three hold: temperature below 800, neutrons above 500, and the two multiplied together below 500000. Otherwise `False` |
| `"reactor_efficiency"` | `voltage`, `current`, `theoretical_max_power` (the output that would count as 100%) | the efficiency band as a string. Generated power is voltage times current; efficiency is that as a percentage of the theoretical max |
| `"fail_safe"` | `temperature`, `neutrons_produced_per_second`, `threshold` | a status string. Multiply the first two to get the reactor's output, then compare it with the threshold |

The bands, in the exact spelling the tests expect:

| `reactor_efficiency` | band |
| --- | --- |
| 80% or more | `'green'` |
| below 80%, at least 60% | `'orange'` |
| below 60%, at least 30% | `'red'` |
| below 30% | `'black'` |

| `fail_safe` | status |
| --- | --- |
| under 90% of the threshold — rods must come out | `'LOW'` |
| anywhere from 90% to 110% of the threshold | `'NORMAL'` |
| above 110% of the threshold — shut down now | `'DANGER'` |

```python
reactor = solve()
reactor["is_criticality_balanced"](750, 600)     # -> True
reactor["is_criticality_balanced"](800, 500)     # -> False     (800 is not below 800)
reactor["reactor_efficiency"](10, 799, 10000)    # -> 'orange'  (79.9%, just under green)
reactor["fail_safe"](10, 901, 10000)             # -> 'NORMAL'  (90.1% of threshold)
reactor["fail_safe"](10, 1101, 10000)            # -> 'DANGER'  (110.1%, over the band)
```

## Rules
- the dict keys are exactly the three strings above, and each value is the function itself — no parentheses
- thresholds and theoretical maxima are never zero
- the band strings are lower case (`'green'`) and the status strings upper case (`'LOW'`), exactly as printed above

> [!WARNING]
> Percentages are rarely whole numbers, so read every boundary carefully: "at least" includes the boundary, "below" does not. The tests sit right on the edges — 799 and 800, 90.1% and 110.1% — so a `<` where a `<=` belongs fails.

## Hints
### Hint 1
Three different shapes. The first is one condition made of three parts that must all hold — no branching needed at all, just the [comparison operators](https://devdocs.io/python~3.14/library/stdtypes#comparisons) combined with [boolean operations](https://devdocs.io/python~3.14/library/stdtypes#boolean-operations-and-or-not) into a single test. The other two are ladders: any number of `elif` statements can be used as decision "branches". Order them from one end of the scale to the other so that by the time you test a band, everything above it has already been ruled out and you only need ONE comparison per branch. `else` is the code block that runs when all the tests return `False`.
### Hint 2
Write the ladders top-down, highest band first, and each `elif` then only needs the lower edge of its band — the upper edge is already excluded by the branch above. The last band needs no test at all: `else` is everything left over, which is also what saves you when a reading is 0. Percentages: compute the percentage once into a variable before the ladder, so the arithmetic cannot drift between branches.

Each branch can have its own `return`, although some linting tools consider that bad form; if yours complains, assign the band to a common variable in each branch and `return` that variable at the end.
### Hint 3
Different data, same shape. Grading a support ticket's response time against a 60-minute SLA:

```python
used = (minutes_taken / 60) * 100
if used <= 50:
    band = 'fast'
elif used <= 100:
    band = 'ok'
else:
    band = 'breached'
return band
```

One ladder, one comparison per branch, one `else` for the rest. 'ok' covers 50 to 100 inclusive without either branch mentioning 50 twice.
