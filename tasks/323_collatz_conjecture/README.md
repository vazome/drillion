---
title: collatz-conjecture — count the steps down to 1
minutes: 10
prereqs: [200, 206]
tags: [exercism, numbers, core]
source: exercism/python practice/collatz-conjecture (MIT, adapted)
---
# collatz-conjecture — count the steps down to 1

*collatz-conjecture — a loop whose length nobody can predict, and a guard for the input that would never end.*

## Why
This is the shape of every "keep going until it settles" loop you will write: a state, a rule that transforms it, and a counter of how many times you had to apply the rule. Convergence detectors, retry-until-healthy pollers, iterative solvers and back-pressure loops all look like this. The uncomfortable part is that the number of iterations is not something you can compute in advance — 27 takes 111 steps, and 26 takes 10 — so a `for` loop over a known range is the wrong tool and a `while` on the condition is the right one. And because a loop with no exit is the most expensive bug in the category, the input that would never terminate is rejected before the loop starts.

## Introduction
One evening, you stumbled upon an old notebook filled with cryptic scribbles, as though someone had been obsessively chasing an idea.
On one page, a single question stood out: **Can every number find its way to 1?**
It was tied to something called the **Collatz Conjecture**, a puzzle that has baffled thinkers for decades.

The rules were deceptively simple.
Pick any positive integer.

- If it's even, divide it by 2.
- If it's odd, multiply it by 3 and add 1.

Then, repeat these steps with the result, continuing indefinitely.

Curious, you picked number 12 to test and began the journey:

12 ➜ 6 ➜ 3 ➜ 10 ➜ 5 ➜ 16 ➜ 8 ➜ 4 ➜ 2 ➜ 1

Counting from the second number (6), it took 9 steps to reach 1, and each time the rules repeated, the number kept changing.
At first, the sequence seemed unpredictable — jumping up, down, and all over.
Yet, the conjecture claims that no matter the starting number, we'll always end at 1.

It was fascinating, but also puzzling.
Why does this always seem to work?
Could there be a number where the process breaks down, looping forever or escaping into infinity?
The notebook suggested solving this could reveal something profound — and with it, fame, [fortune][collatz-prize], and a place in history awaits whoever could unlock its secrets.

[collatz-prize]: https://mathprize.net/posts/collatz-conjecture/

## Instructions
Given a positive integer, return the number of steps it takes to reach 1 according to the rules of the Collatz Conjecture.

### Exception messages

Sometimes it is necessary to [raise an exception](https://docs.python.org/3/tutorial/errors.html#raising-exceptions). When you do this, you should always include a **meaningful error message** to indicate what the source of the error is. This makes your code more readable and helps significantly with debugging. For situations where you know that the error source will be a certain type, you can choose to raise one of the [built in error types](https://docs.python.org/3/library/exceptions.html#base-classes), but should still include a meaningful message.

The Collatz Conjecture is only concerned with **strictly positive integers**, so this exercise expects you to use the [raise statement](https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement) and "throw" a `ValueError` in your solution if the given value is zero or a negative integer. The tests will only pass if you both `raise` the `exception` and include a message with it.

To raise a `ValueError` with a message, write the message as an argument to the `exception` type:

```python
# example when argument is zero or a negative integer
raise ValueError("Only positive integers are allowed")
```

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

## Read first
- [Integers](https://docs.python.org/3/library/functions.html#int) — halving with `//` keeps the value an `int`; `/` turns it into a float
- [Arithmetic operations](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex) — `%`, `//` and the difference between them
- [while statements](https://docs.python.org/3/reference/compound_stmts.html#the-while-statement) — the loop for "until this is true", when the trip count is unknown
- [Raising exceptions](https://docs.python.org/3/tutorial/errors.html#raising-exceptions) — `raise ValueError("message")` before the loop, not inside it

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

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
