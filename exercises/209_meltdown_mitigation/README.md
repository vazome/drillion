---
title: conditionals — reactor meltdown control
minutes: 15
prereqs: [200, 203]
tags: [exercism, conditionals, core]
source: exercism/python concept/meltdown-mitigation (MIT, adapted)
---
# conditionals — reactor meltdown control

*if / elif / else — three reactor decisions, each a different shape of branch.*

## Why
You are writing the control software for a nuclear reactor. A
reactor only produces power while it sits in a narrow band called
criticality: below it the core gets damaged, above it you get a meltdown.
The sensors feed you raw numbers — temperature, neutron count, voltage,
current — and the control room needs three plain answers off them: is the
core balanced right now, how efficiently is it running, and should the rods
go in or out. Each answer is a different shape of decision: one yes/no, one
four-way band, one three-way band. Getting the `<` versus `<=` right is the
entire job; on this machine an off-by-one boundary is not a cosmetic bug.

## You get
nothing. Every reading arrives as an argument to one of your
functions. Readings can be whole numbers or decimals.

## You return
a dict with these three functions.

  "is_criticality_balanced" — takes `temperature` (kelvin, e.g. 750) and
  `neutrons_emitted` (per second, e.g. 600). Returns True only when all
  three hold: temperature below 800, neutrons above 500, and the two
  multiplied together below 500000. Otherwise False.

  "reactor_efficiency" — takes `voltage`, `current` and
  `theoretical_max_power` (the output that would count as 100%). Generated
  power is voltage times current; efficiency is that as a percentage of the
  theoretical max. Returns the band as a string: 'green' at 80% or more,
  'orange' below 80% but at least 60%, 'red' below 60% but at least 30%,
  'black' below 30%.

  "fail_safe" — takes `temperature`, `neutrons_produced_per_second` and
  `threshold`. Multiply the first two to get the reactor's output. Returns
  'LOW' when that output is under 90% of the threshold (rods must come out),
  'NORMAL' while it is anywhere from 90% to 110% of the threshold, and
  'DANGER' above that (shut down now).

## Rules
The dict keys are exactly the three strings above. Thresholds and
theoretical maxima are never zero. Percentages are rarely whole numbers, so
read every boundary above carefully: "at least" includes the boundary,
"below" does not.

```python
is_criticality_balanced(750, 600)     ->  True
is_criticality_balanced(800, 500)     ->  False  (800 is not below 800)
reactor_efficiency(10, 799, 10000)    ->  'orange'  (79.9%, just under green)
fail_safe(10, 901, 10000)             ->  'NORMAL'  (90.1% of threshold)
fail_safe(10, 1101, 10000)            ->  'DANGER'  (110.1%, over the band)
```

## Read first
- https://docs.python.org/3/tutorial/controlflow.html#more-control-flow-tools  — if / elif / else: the first branch whose test is True wins, and the rest are never even evaluated
- https://realpython.com/python-conditional-statements/  — chained comparisons (`0 <= x < 10`) and when a ladder of elif beats a pile of separate ifs
- CONCEPT: conditionals — Python has no case/switch before 3.10; a chain of elif is how you write one, and every test must resolve to True or False.

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Three different shapes. The first is one condition made of three parts that must all hold — no branching needed at all, just the combined test. The other two are ladders: order the branches from one end of the scale to the other so that by the time you test a band, everything above it has already been ruled out and you only need ONE comparison per branch.
### Hint 2
Write the ladders top-down, highest band first, and each `elif` then only needs the lower edge of its band — the upper edge is already excluded by the branch above. The last band needs no test at all: `else` is everything left over, which is also what saves you when a reading is 0. Percentages: compute the percentage once into a variable before the ladder, so the arithmetic cannot drift between branches.
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
