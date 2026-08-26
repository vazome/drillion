---
title: nth-prime — produce primes on demand and take the nth one
minutes: 15
prereqs: [200, 203, 206, 209, 212, 215, 221, 224, 227]
tags: [exercism, generators, data-structures]
source: exercism/python practice/nth-prime (MIT, adapted)
---
# nth-prime — produce primes on demand and take the nth one

*nth-prime — an endless sequence you generate lazily, stopping the moment you have enough.*

## Why
You cannot precompute this one, because nobody tells you how far to go: asked for the 10001st prime, you have no idea in advance where it lives. That is the same position you are in when you page through an API until you find the record you want, or read a log stream until the error appears — the source is effectively endless, so you produce values one at a time and stop when the condition is met. Doing it any other way means guessing an upper bound, and guessing an upper bound is how "it worked in staging" becomes "it ran out of memory in production".

## Instructions
Given a number n, determine what the nth prime is.

By listing the first six prime numbers: 2, 3, 5, 7, 11, and 13, we can see that the 6th prime is 13.

If your language provides methods in the standard library to deal with prime numbers, pretend they don't exist and implement them yourself.

### Exception messages

Sometimes it is necessary to [raise an exception](https://docs.python.org/3/tutorial/errors.html#raising-exceptions). When you do this, you should always include a **meaningful error message** to indicate what the source of the error is. This makes your code more readable and helps significantly with debugging. For situations where you know that the error source will be a certain type, you can choose to raise one of the [built in error types](https://docs.python.org/3/library/exceptions.html#base-classes), but should still include a meaningful message.

This particular exercise requires that you use the [raise statement](https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement) to "throw" a `ValueError` when the `prime()` function receives malformed input. Since this exercise deals only with _positive_ numbers, any number < 1 is malformed.  The tests will only pass if you both `raise` the `exception` and include a message with it.

To raise a `ValueError` with a message, write the message as an argument to the `exception` type:

```python
# when the prime function receives malformed input
raise ValueError('there is no zeroth prime')
```

## You get
`number` — which prime is wanted, counting from 1:

```python
solve(6)
```

It can be `0` or negative, which is an error, and it can be as large as `10001`, so brute force has to be at least reasonable.

> [!NOTE]
> Exercism's stub is `def prime(number)`. Here the function is `solve(number)`; nothing else about the task changes.

## You return
An `int` — the `number`th prime, with `solve(1)` being `2`.

```python
solve(1)   # -> 2
solve(6)   # -> 13
```

## Rules
- primes are counted from 1: the 1st is 2, the 2nd is 3, the 6th is 13
- `1` is not prime and never appears in the sequence
- do not import a primality helper from a library — the point is writing the test yourself
- any `number` below 1 raises `ValueError` with exactly this message:

```python
raise ValueError("there is no zeroth prime")
```

```python
solve(2)      # -> 3
solve(20)     # -> 71
solve(10001)  # -> 104743
solve(0)      # raises ValueError("there is no zeroth prime")
solve(-3)     # raises ValueError("there is no zeroth prime")
```

> [!WARNING]
> One of the graded cases is `solve(10001)`, the 10001st prime — `104743`. Testing a candidate by dividing it by every smaller number will not finish before the runner gives up. Stop at the square root: once nothing up to the square root of a candidate divides it, the candidate is prime — that one change is the difference between finishing and being killed on the clock.
>
> The `ValueError` message is compared character for character: lower case, no full stop, the word `zeroth` spelled exactly like that. Raise it before you do any work — a negative `number` must not send a loop off looking for a prime it will never reach.

## Read first
- [Generators](https://docs.python.org/3/tutorial/classes.html#generators) — `yield` produces a value and pauses, which is how an endless sequence stays affordable
- [itertools.count()](https://docs.python.org/3/library/itertools.html#itertools.count) — an endless counter, with a start and a step
- [itertools.islice()](https://docs.python.org/3/library/itertools.html#itertools.islice) — "take the first n of something endless" without building a list of everything
- [math.isqrt()](https://docs.python.org/3/library/math.html#math.isqrt) — testing divisors past the square root cannot find anything new
- [Raising exceptions](https://docs.python.org/3/tutorial/errors.html#raising-exceptions) — the guard clause at the top of the function

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Three pieces, and it is worth keeping them apart: the guard for bad input, a way to decide whether one number is prime, and a loop that keeps asking until it has counted far enough. Write the primality test on its own and try it on 1, 2, 3, 4, 9 and 11 before you build anything around it — 1 and 2 are where most first attempts get it wrong.
### Hint 2
For the primality test, you only ever need divisors up to the square root, and you only need the primes among them — which you already have, because you are collecting them as you go. Keep the primes you have found in a list, and test each new candidate against that list, stopping as soon as the prime you are looking at squared is larger than the candidate; if you get that far without a clean division, the candidate is prime. For the loop itself, count upwards from 2 and append; when the list is as long as `number`, the last one you appended is the answer. Skipping even candidates after 2 halves the work for one line of code.
### Hint 3
Different data, same "produce endlessly, stop when the count is reached" shape — pulling records from a paged API until you have twenty:

```python
from itertools import count, islice

def pages():
    for number in count(1):
        yield [f'record {number}-{i}' for i in range(3)]

def first(n):
    flat = (record for page in pages() for record in page)
    return list(islice(flat, n))

first(4)   # -> ['record 1-0', 'record 1-1', 'record 1-2', 'record 2-0']
```

`pages()` never ends and never needs to; `islice` stops asking after the fourth record, so page 3 is never fetched. Substitute "is this number prime?" for "is this record interesting?" and you have the task.
