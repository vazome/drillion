---
title: grains — doubling on every chessboard square
minutes: 10
prereqs: [200, 206]
tags: [exercism, numbers, core]
source: exercism/python practice/grains (MIT, adapted)
---
# grains — doubling on every chessboard square

*grains — one exponent instead of a loop, and a `ValueError` when the square does not exist.*

## Why
Doubling is the growth curve behind retry backoff, cache sizing, partition splitting and every capacity estimate that turns out badly. People are reliably wrong about it: "sixty-four squares" sounds small, and the answer is more wheat than has ever been grown. Writing it out once, in code that says `2 ** (n - 1)` rather than looping a billion times, is the cheap way to build the intuition — and to notice that Python's integers do not overflow at 64 bits the way most languages' do. The second half of the task is the boring half that matters in production: reject the input that makes no sense, with a message that says why.

## Introduction
There once was a wise servant who saved the life of a prince.
The king promised to pay whatever the servant could dream up.
Knowing that the king loved chess, the servant told the king he would like to have grains of wheat.
One grain on the first square of a chessboard, with the number of grains doubling on each successive square.

## Instructions
Calculate the number of grains of wheat on a chessboard.

A chessboard has 64 squares.
Square 1 has one grain, square 2 has two grains, square 3 has four grains, and so on, doubling each time.

Write code that calculates:

- the number of grains on a given square
- the total number of grains on the chessboard

### Exception messages

Sometimes it is necessary to [raise an exception](https://docs.python.org/3/tutorial/errors.html#raising-exceptions). When you do this, you should always include a **meaningful error message** to indicate what the source of the error is. This makes your code more readable and helps significantly with debugging. For situations where you know that the error source will be a certain type, you can choose to raise one of the [built in error types](https://docs.python.org/3/library/exceptions.html#base-classes), but should still include a meaningful message.

This particular exercise requires that you use the [raise statement](https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement) to "throw" a `ValueError` when the square input is out of range. The tests will only pass if you both `raise` the `exception` and include a message with it.

To raise a `ValueError` with a message, write the message as an argument to the `exception` type:

```python
# when the square value is not in the acceptable range
raise ValueError("square must be between 1 and 64")
```

## You get
Nothing. `solve()` takes **no arguments**; the square number arrives as an argument to one of the functions you hand back.

> [!NOTE]
> Exercism asks for two functions, `square(number)` and `total()`, in one `grains.py`. Here there is one entry point: `solve()` returns a dict that hands both functions to the grader, keyed by name.

## You return
A dict with these two functions.

| key | parameters | returns |
| --- | --- | --- |
| `"square"` | `number` — which square, counting from 1 | the `int` number of grains on that square |
| `"total"` | none | the `int` number of grains on the whole board |

```python
board = solve()
board["square"](1)   # -> 1
board["square"](4)   # -> 8
board["square"](64)  # -> 9223372036854775808
board["total"]()     # -> 18446744073709551615
board["square"](0)   # raises ValueError("square must be between 1 and 64")
```

## Rules
- square 1 holds one grain and every square after it holds twice the one before, so square `n` holds `2 ** (n - 1)`
- the board has 64 squares; the total is every square added together, which is `2 ** 64 - 1`
- `"square"` raises `ValueError("square must be between 1 and 64")` for any `number` below 1 or above 64 — `0`, `-1` and `65` all get that same message
- the results are exact `int` values, not floats: `2 ** 63` is fine in Python, `2.0 ** 63` loses digits

> [!WARNING]
> The message is compared character for character: lower case, no full stop, `square must be between 1 and 64`.

## Read first
- [Integers](https://docs.python.org/3/library/functions.html#int) — Python `int` is arbitrary precision, so 64 doublings do not overflow
- [Arithmetic operations](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex) — `**`, and why `2 ** 64` stays exact while `2.0 ** 64` does not
- [Operator precedence](https://docs.python.org/3/reference/expressions.html#operator-precedence) — `**` binds tighter than `-`, so `2 ** 64 - 1` is the number you meant
- [Raising exceptions](https://docs.python.org/3/tutorial/errors.html#raising-exceptions) — `raise ValueError("message")`, and why the message is the useful part

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Write the first four squares down: 1, 2, 4, 8. Then write the powers of two next to them: 2⁰, 2¹, 2², 2³. The offset between "square number" and "exponent" is the entire arithmetic part of this task, and getting it wrong by one is the classic way to fail square 1. Do the validation first, though — a function that rejects bad input before computing anything is easier to read than one that computes and then apologises.

### Hint 2
Guard, then compute. The guard is a single `if` covering both ends of the range at once, and it raises rather than returning anything, so nothing below it has to think about bad input again. The computation is one expression with `**`; no loop and no accumulator. For the board total, resist writing a loop that adds 64 powers: the sum of the first *n* powers of two is one less than the next power of two, so the whole board is a single expression too. Check that claim on a tiny board — squares 1, 2 and 3 hold 1 + 2 + 4 = 7, and the next power of two is 8.

### Hint 3
Different data, same guard-then-formula shape — capped exponential backoff for a retry loop:

```python
def backoff(attempt):
    if attempt < 1 or attempt > 10:
        raise ValueError('attempt must be between 1 and 10')
    return min(2 ** (attempt - 1), 60)

backoff(1)   # -> 1
backoff(5)   # -> 16
backoff(9)   # -> 60
```

The range check is one `if` with an `or`, the doubling is one `**` with the off-by-one already folded into the exponent, and the caller never sees a half-computed answer.
