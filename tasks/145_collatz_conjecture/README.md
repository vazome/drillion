---
title: numbers — count the steps down to 1
difficulty: easy
tier: core
minutes: 10
prereqs: [3]
tags: [numbers]
source: exercism/python practice/collatz-conjecture (MIT, adapted)
---
# numbers — count the steps down to 1

*collatz-conjecture — a loop whose length nobody can predict, and a guard for the input that would never end.*

## Read first
- [Integers](https://devdocs.io/python~3.14/library/functions#int) — halving with `//` keeps the value an `int`; `/` turns it into a float
- [Arithmetic operations](https://devdocs.io/python~3.14/library/stdtypes#numeric-types-int-float-complex) — `%`, `//` and the difference between them
- [while statements](https://devdocs.io/python~3.14/reference/compound_stmts#the-while-statement) — the loop for "until this is true", when the trip count is unknown
- [Raising exceptions](https://devdocs.io/python~3.14/tutorial/errors#raising-exceptions) — `raise ValueError("message")` before the loop, not inside it

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
This is the shape of every "keep going until it settles" loop you will write: a state, a rule that transforms it, and a counter of how many times you had to apply the rule. Convergence detectors, retry-until-healthy pollers, iterative solvers and back-pressure loops all look like this. The uncomfortable part is that the number of iterations is not something you can compute in advance — 27 takes 111 steps, and 26 takes 10 — so a `for` loop over a known range is the wrong tool and a `while` on the condition is the right one. And because a loop with no exit is the most expensive bug in the category, the input that would never terminate is rejected before the loop starts.

## You get
`number` — a starting integer, e.g.

```python
12
```

The grader passes positive integers, and also `0` and negative ones to check that you reject them.

> [!NOTE]
> Exercism's stub is `def steps(number)`. Here the function is `solve(number)`; nothing else about the task changes.

## You return
An `int`: how many times the rule had to be applied before the value became 1.

## Rules
- while the number is not 1, apply the rule and add one to the count
- even numbers are halved; odd numbers become `3 * number + 1`
- starting at 1 means zero steps — the loop never runs
- `0` and any negative number raise `ValueError("Only positive integers are allowed")`

```python
solve(1)        # -> 0
solve(16)       # -> 4    16 → 8 → 4 → 2 → 1
solve(12)       # -> 9    12 → 6 → 3 → 10 → 5 → 16 → 8 → 4 → 2 → 1
solve(1000000)  # -> 152
solve(0)        # raises ValueError("Only positive integers are allowed")
```

> [!WARNING]
> The message is compared character for character, capital `O` included: `Only positive integers are allowed`. And you are counting *steps*, not the numbers in the chain — the chain for 12 has ten numbers in it and the answer is 9.

## Hints
### Hint 1
Do 12 on paper first and count carefully — the answer is 9, not 10, because you count the arrows and not the numbers. Then notice that nothing about the loop depends on how big the input is: the same two-branch rule runs over and over until a single condition stops it. That condition, not a range, is what the loop should be written against.

### Hint 2
Reject the bad input first, in one `if` above everything else, so the loop can assume it is holding a positive number. Then keep two things alive: the current value and a counter that starts at zero. Loop while the value is still above 1; inside, ask whether it is even — `% 2` answers that — and replace the value using the matching rule, then bump the counter by one. When the loop ends the counter is the answer. Halve with `//` rather than `/`, or your "number" quietly becomes a float and stops looking like the integer the rules are about.

### Hint 3
Different data, same converge-and-count shape — how many halvings a cache budget needs before it fits in a memory limit:

```python
def shrinks(mb, limit):
    if mb <= 0:
        raise ValueError('size must be positive')
    count = 0
    while mb > limit:
        mb = mb // 2
        count += 1
    return count

shrinks(1000, 100)   # -> 4    1000 -> 500 -> 250 -> 125 -> 62
```

Guard, then a `while` on the stopping condition, then one counter incremented per iteration. The only thing this task adds is a second branch inside the loop.
