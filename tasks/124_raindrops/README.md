---
title: conditionals — sounds for the factors 3, 5 and 7
difficulty: easy
tier: core
minutes: 10
prereqs: [3, 5]
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
