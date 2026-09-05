---
title: conditionals — reactor meltdown control
difficulty: medium
tier: core
minutes: 15
prereqs: [17, 89]
tags: [conditionals]
source: exercism/python concept/meltdown-mitigation (MIT, adapted)
---
# conditionals — reactor meltdown control

*if / elif / else — three reactor decisions, each a different shape of branch.*

## Read first
- [Python Docs: Control flow tools](https://devdocs.io/python~3.14/tutorial/controlflow#more-control-flow-tools) — if / elif / else: the first branch whose test is `True` wins, and the rest are never even evaluated
- [Real Python: Conditional statements in Python](https://realpython.com/python-conditional-statements/) — chained comparisons (`0 <= x < 10`) and when a ladder of `elif` beats a pile of separate `if`s
- [Python Docs: Truth value testing](https://devdocs.io/python~3.14/library/stdtypes#truth-value-testing) — what counts as `True` when the test is not a comparison
- [Python Docs: Standard types — boolean operations](https://devdocs.io/python~3.14/library/stdtypes#boolean-operations-and-or-not) — `and` / `or` / `not` inside a condition
- [Python Docs: Comparisons](https://devdocs.io/python~3.14/library/stdtypes#comparisons) — the `<` / `<=` table this whole task turns on

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
You are writing the control software for a nuclear reactor. A reactor only produces power while it sits in a narrow band called criticality: below it the core gets damaged, above it you get a meltdown. The sensors feed you raw numbers — temperature, neutron count, voltage, current — and the control room needs three plain answers off them: is the core balanced right now, how efficiently is it running, and should the rods go in or out. Each answer is a different shape of decision: one yes/no, one four-way band, one three-way band. Getting the `<` versus `<=` right is the entire job; on this machine an off-by-one boundary is not a cosmetic bug.

## Introduction
### Conditionals

In Python, [`if`][if statement], `elif` (_a contraction of 'else and if'_) and `else` statements are used to [control the flow][control flow tools] of execution and make decisions in a program.
Unlike many other programming languages, Python versions 3.9 and below do not offer a formal case-switch statement, instead using multiple `elif` statements to serve a similar purpose.

Python 3.10 introduces a variant case-switch statement called `structural pattern matching`, which will be covered separately in another concept.

Conditional statements use expressions that must resolve to `True` or `False` -- either by returning a `bool` type directly, or by evaluating as ["truthy" or "falsy"][truth value testing].

```python
x = 10
y = 5

# The comparison '>' returns the bool 'True',
# so the statement is printed.
if x > y:
    print("x is greater than y")
...
>>> x is greater than y
```

When paired with `if`, an optional `else` code block will execute when the original `if` condition evaluates to `False`:

```python
x = 5
y = 10

# The comparison '>' here returns the bool 'False',
# so the 'else' block is executed instead of the 'if' block.
if x > y:
    print("x is greater than y")
else:
    print("y is greater than x")
...
>>> y is greater than x
```

`elif` allows for multiple evaluations/branches.

```python
x = 5
y = 10
z = 20

# The 'elif' statement allows for the checking of more conditions.
if x > y:
    print("x is greater than y and z")
elif y > z:
    print("y is greater than x and z")
else:
    print("z is greater than x and y")
...
>>> z is greater than x and y
```

[Boolean operations][boolean operations] and [comparisons][comparisons] can be combined with conditionals for more complex testing:

```python
>>> def classic_fizzbuzz(number):
        if number % 3 == 0 and number % 5 == 0:
            say = 'FizzBuzz!'
        elif number % 5 == 0:
            say = 'Buzz!'
        elif number % 3 == 0:
            say = 'Fizz!'
        else:
            say = str(number)

        return say

>>> classic_fizzbuzz(15)
'FizzBuzz!'

>>> classic_fizzbuzz(13)
'13'
```

[boolean operations]: https://devdocs.io/python~3.14/library/stdtypes#boolean-operations-and-or-not
[comparisons]: https://devdocs.io/python~3.14/library/stdtypes#comparisons
[control flow tools]: https://devdocs.io/python~3.14/tutorial/controlflow#more-control-flow-tools
[if statement]: https://devdocs.io/python~3.14/reference/compound_stmts#the-if-statement
[truth value testing]: https://devdocs.io/python~3.14/library/stdtypes#truth-value-testing

## Instructions
In this exercise, we'll develop a simple control system for a nuclear reactor.

For a reactor to produce the power it must be in a state of _criticality_.
If the reactor is in a state less than criticality, it can become damaged.
If the reactor state goes beyond criticality, it can overload and result in a meltdown.
We want to mitigate the chances of meltdown and correctly manage reactor state.

The following three tasks are all related to writing code for maintaining ideal reactor state.

### 1. Check for criticality

The first thing a control system has to do is check if the reactor is _balanced in criticality_.
A reactor is said to be balanced in criticality if it satisfies the following conditions:

- The temperature is less than 800 K.
- The number of neutrons emitted per second is greater than 500.
- The product of temperature and neutrons emitted per second is less than 500000.

Implement the function `is_criticality_balanced()` that takes `temperature` measured in kelvin and `neutrons_emitted` as parameters, and returns `True` if the criticality conditions are met, `False` if not.

```python
>>> is_criticality_balanced(750, 600)
True
```

### 2. Determine the Power output range

Once the reactor has started producing power its efficiency needs to be determined.
Efficiency can be grouped into 4 bands:

1. `green` -> efficiency of 80% or more,
2. `orange` -> efficiency of less than 80% but at least 60%,
3. `red` -> efficiency below 60%, but still 30% or more,
4. `black` ->  less than 30% efficient.

The percentage value can be calculated as `(generated_power/theoretical_max_power)*100`
where `generated_power` = `voltage` * `current`.
Note that the percentage value is usually not an integer number, so make sure to consider the
proper use of the `<` and `<=` comparisons.

Implement the function `reactor_efficiency(<voltage>, <current>, <theoretical_max_power>)`, with three parameters: `voltage`,
`current`, and `theoretical_max_power`.
This function should return the efficiency band of the reactor : 'green', 'orange', 'red', or 'black'.

```python
>>> reactor_efficiency(200,50,15000)
'orange'
```

### 3. Fail Safe Mechanism

Your final task involves creating a fail-safe mechanism to avoid overload and meltdown.
This mechanism will determine if the reactor is below, at, or above the ideal criticality threshold.
Criticality can then be increased, decreased, or stopped by inserting (or removing) control rods into the reactor.

Implement the function called `fail_safe()`, which takes 3 parameters: `temperature` measured in kelvin,
`neutrons_produced_per_second`, and `threshold`, and outputs a status code for the reactor.

- If `temperature * neutrons_produced_per_second` < 90% of `threshold`, output a status code of 'LOW'
  indicating that control rods must be removed to produce power.

- If the value `temperature * neutrons_produced_per_second` is within 10% of the `threshold` (so either 0-10% less than the threshold, at the threshold, or 0-10% greater than the threshold), the reactor is in _criticality_ and the status code of 'NORMAL' should be output, indicating that the reactor is in optimum condition and control rods are in an ideal position.

- If `temperature * neutrons_produced_per_second` is not in the above-stated ranges, the reactor is
  going into meltdown and a status code of 'DANGER' must be passed to immediately shut down the reactor.

```python
>>> fail_safe(temperature=1000, neutrons_produced_per_second=30, threshold=5000)
'DANGER'
```

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

## Exercism hints

### General

- The Python Docs on [Control Flow Tools][control flow tools] and the Real Python tutorial on [conditionals][real python conditionals] are great places to start.
- The Python Docs on [Boolean Operations][boolean operations] can be a great refresher on `bools`, as can the Real Python tutorial on [booleans][python booleans].
- The Python Docs on [Comparisons][comparisons] and [comparisons examples][python comparisons examples] can be a great refresher for comparisons.

### 1. Check for criticality

- Comparison operators ([comparisons][comparisons review]) and boolean operations ([concept:python/bools]()) can be combined and used with conditionals.
- Conditional expressions must evaluate to `True` or `False`.
- `else` can be used for a code block that will execute when all conditional tests return `False`.

  ```python
     >>> item = 'blue'
     >>> item_2 = 'green'
     
     >>>  if len(item) >= 3 and len(item_2) < 5:
            print('Both pass the test!')
          elif len(item) >= 3 or len(item_2) < 5:
            print('One passes the test!')
          else:
            print('None pass the test!')
    ...
    One passes the test!
  ```

### 2. Determine the Power output range

- Comparison operators can be combined and used with conditionals.
- Any number of `elif` statements can be used as decision "branches".
- Each "branch" can have a separate `return`, although it might be considered "bad form" by linting tools.
- If the linter complains, consider assigning the output of a branch to a common variable, and then `return`ing that variable.

### 3. Fail Safe Mechanism

- Comparison operators can be combined and used with conditionals.
- Any number of `elif` statements can be used as decision "branches".
- Each "branch" can have a separate `return`, although it might be considered "bad form" by linting tools.
- If the linter complains, consider assigning the output of a branch to a common variable, and then `return`ing that variable.


[boolean operations]: https://devdocs.io/python~3.14/library/stdtypes#boolean-operations-and-or-not
[comparisons review]: https://www.learnpython.dev/02-introduction-to-python/090-boolean-logic/20-comparisons/
[comparisons]: https://devdocs.io/python~3.14/library/stdtypes#comparisons
[control flow tools]: https://devdocs.io/python~3.14/tutorial/controlflow
[python booleans]: https://realpython.com/python-boolean/
[python comparisons examples]: https://www.tutorialspoint.com/python/comparison_operators_example.htm
[real python conditionals]: https://realpython.com/python-conditional-statements/

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
