---
title: conditionals — sounds for the factors 3, 5 and 7
difficulty: easy
tier: core
minutes: 10
prereqs: [90, 92]
tags: [conditionals]
source: exercism/python practice/raindrops (MIT, adapted)
---
# conditionals — sounds for the factors 3, 5 and 7

*raindrops — build a string from the factors a number has, with a fallback.*

## Read first
- [if statements](https://devdocs.io/python~3.14/tutorial/controlflow#if-statements) — `if` / `elif` / `else`, and why three separate `if`s are not the same thing as one `if`/`elif` chain
- [Truth value testing](https://devdocs.io/python~3.14/library/stdtypes#truth-value-testing) — an empty string is falsy: that is how you ask "did I add anything?"
- [divmod()](https://devdocs.io/python~3.14/library/functions#divmod) — `%` and `divmod`, the two ways to ask for a remainder
- [operator.mod()](https://devdocs.io/python~3.14/library/operator#operator.mod) — the same `%` as a function
- [str()](https://devdocs.io/python~3.14/library/stdtypes#str) — turning the number into the fallback answer

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
This is FizzBuzz in a raincoat, and interviewers still hand it out because most candidates trip on the same two things: that several rules can fire for the same number (so it is three questions, not one choice of three), and that the fallback only applies when none of them fired. Picture a rain gauge whose display plays a chime per factor and only prints the raw reading when there is nothing to chime about.

## Introduction
Raindrops is a slightly more complex version of the FizzBuzz challenge, a classic interview question.

## Instructions
Your task is to convert a number into its corresponding raindrop sounds.

If a given number:

- is divisible by 3, add "Pling" to the result.
- is divisible by 5, add "Plang" to the result.
- is divisible by 7, add "Plong" to the result.
- **is not** divisible by 3, 5, or 7, the result should be the number as a string.

### Examples

- 28 is divisible by 7, but not 3 or 5, so the result would be `"Plong"`.
- 30 is divisible by 3 and 5, but not 7, so the result would be `"PlingPlang"`.
- 34 is not divisible by 3, 5, or 7, so the result would be `"34"`.

> [!NOTE]
> A common way to test if one number is evenly divisible by another is to compare the [remainder][remainder] or [modulus][modulo] to zero.
> Most languages provide operators or functions for one (or both) of these.

[remainder]: https://exercism.org/docs/programming/operators/remainder
[modulo]: https://en.wikipedia.org/wiki/Modulo_operation

### How this Exercise is Structured in Python

This exercise is best solved with Python's `%` ([modulo][modulo]) operator, which returns the remainder of positive integer division.
It has a method equivalent, `operator.mod()` in the [operator module][operator-mod].

Python also offers additional 'remainder' methods in the [math module][math-module].
[`math.fmod()`][fmod] behaves like `%`, but operates on floats.
[`math.remainder()`][remainder] implements a "step closest to zero" algorithm for the remainder of division.
While we encourage you to get familiar with these methods, neither of these will exactly match the result of `%`, and are not recommended for use with this exercise.

The built-in function [`divmod()`][divmod] will also give a remainder than matches `%` if used with two positive integers, but returns a `tuple` that needs to be unpacked.

[divmod]: https://devdocs.io/python~3.14/library/functions#divmod
[fmod]: https://devdocs.io/python~3.14/library/math#math.fmod
[math-module]: https://devdocs.io/python~3.14/library/math
[modulo]: https://www.programiz.com/python-programming/operators#arithmetic
[operator-mod]: https://devdocs.io/python~3.14/library/operator#operator.mod
[remainder]: https://devdocs.io/python~3.14/library/math#math.remainder

## You get
`number` — a positive whole number, e.g. `28`.

> [!NOTE]
> Exercism's stub is `def convert(number)`. Here the function is `solve(number)`; nothing else about the task changes.

## You return
A string. Either the chimes glued together, or the number written out as text.

## Rules
Start with nothing. If the number divides evenly by 3, add "Pling"; by 5, add "Plang"; by 7, add "Plong" — always in that order, and a number can add two or all three. If it divides by none of 3, 5 and 7, the answer is the number itself as a string.

| number divides by | result |
| --- | --- |
| 3 | `"Pling"` |
| 5 | `"Plang"` |
| 7 | `"Plong"` |
| none of them | the number as a string |

```python
solve(28)   # -> "Plong"            (7 only)
solve(30)   # -> "PlingPlang"       (3 and 5)
solve(105)  # -> "PlingPlangPlong"  (3, 5 and 7)
solve(34)   # -> "34"               (none of them)
```

> [!WARNING]
> The words are concatenated in the fixed order Pling, Plang, Plong — not in the order you happened to test the factors — and the fallback is `"34"`, the string, never the number `34`.

## Hints
### Hint 1
Three independent yes/no questions, not one choice between three answers — 15 has to produce two words. So build the answer up as you go, and only at the very end decide whether anything was added to it. A common way to test if one number is evenly divisible by another is to compare the remainder or modulus to zero.
### Hint 2
Start with an empty string. Ask about 3, then 5, then 7, each with its own `if`, appending a word when the remainder is zero — that ordering of the `if`s is what puts the words in the right order. Afterwards, if the string is still empty, return the number converted to text instead.
### Hint 3
Different data, same shape — Unix permission strings:

```python
out = ''
if readable:   out += 'r'
if writable:   out += 'w'
if executable: out += 'x'
return out or '-'
```

Three separate `if`s, one accumulator, and a fallback for 'nothing applied'.
