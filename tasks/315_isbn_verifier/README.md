---
title: isbn-verifier — is this book number real, or a typo?
minutes: 10
prereqs: [200, 203, 209, 215]
tags: [exercism, strings, core]
source: exercism/python practice/isbn-verifier (MIT, adapted)
---
# isbn-verifier — is this book number real, or a typo?

*isbn-verifier — a weighted checksum, and the one character that is not a digit.*

## Why
A shop's import job receives ten thousand rows of book data typed by humans and pasted from spreadsheets. Validating the identifier before the row reaches the database turns "mystery record nobody can find" into a rejected line with a reason, at the edge, for free. Every identifier you will meet at work — account numbers, IBANs, VAT numbers, container codes — carries a check digit for exactly this reason, and they all follow the shape below: weight each position, sum, test the total against one modulus.

## Instructions
The [ISBN-10 verification process][isbn-verification] is used to validate book identification numbers.
These normally contain dashes and look like: `3-598-21508-8`

### ISBN

The ISBN-10 format is 9 digits (0 to 9) plus one check character (either a digit or an X only).
In the case the check character is an X, this represents the value '10'.
These may be communicated with or without hyphens, and can be checked for their validity by the following formula:

```text
(d₁ * 10 + d₂ * 9 + d₃ * 8 + d₄ * 7 + d₅ * 6 + d₆ * 5 + d₇ * 4 + d₈ * 3 + d₉ * 2 + d₁₀ * 1) mod 11 == 0
```

If the result is 0, then it is a valid ISBN-10, otherwise it is invalid.

### Example

Let's take the ISBN-10 `3-598-21508-8`.
We plug it in to the formula, and get:

```text
(3 * 10 + 5 * 9 + 9 * 8 + 8 * 7 + 2 * 6 + 1 * 5 + 5 * 4 + 0 * 3 + 8 * 2 + 8 * 1) mod 11 == 0
```

Since the result is 0, this proves that our ISBN is valid.

### Task

Given a string the program should check if the provided string is a valid ISBN-10.
Putting this into place requires some thinking about preprocessing/parsing of the string prior to calculating the check digit for the ISBN.

The program should be able to verify ISBN-10 both with and without separating dashes.

### Caveats

Converting from strings to numbers can be tricky in certain languages.
Now, it's even trickier since the check digit of an ISBN-10 may be 'X' (representing '10').
For instance `3-598-21507-X` is a valid ISBN-10.

[isbn-verification]: https://en.wikipedia.org/wiki/International_Standard_Book_Number

## You get
`isbn` — a candidate ISBN-10 as a string, e.g. `"3-598-21508-8"`. Dashes may appear anywhere or not at all, the string may be any length, and it may contain characters that are neither digits nor dashes.

> [!NOTE]
> Exercism's stub is `def is_valid(isbn)`. Here the function is `solve(isbn)`; nothing else about the task changes.

## You return
`True` if the string is a valid ISBN-10, `False` otherwise. A real boolean — never a raised exception, whatever the input looks like.

## Rules
- remove the dashes first; nothing else is removed
- what is left must be **exactly 10 characters**, no more, no fewer
- the first nine must be digits `0`–`9`
- the tenth may be a digit or an `X`, where `X` counts as 10 — and `X` is legal **only** in that last position
- multiply the first character by 10, the second by 9, and so on down to the tenth by 1; the ISBN is valid when the total is divisible by 11

| input | verdict | why |
| --- | --- | --- |
| `3-598-21508-8` | `True` | the weighted sum is 264, and 264 = 11 × 24 |
| `3-598-21508-9` | `False` | wrong check digit |
| `3-598-21507-X` | `True` | the check "digit" 10, written `X` |
| `3-598-2X507-9` | `False` | `X` outside the last position |
| `359821507` | `False` | nine characters |
| `3598215078X` | `False` | eleven characters |
| `""` | `False` | no characters |

```python
solve("3-598-21508-8")  # -> True
solve("3598215088")     # -> True
solve("359821507X")     # -> True
solve("00")             # -> False
```

> [!WARNING]
> Check the length **and** the characters — both, and independently. `"3132P34035"` is ten characters long and still invalid; `"3598P215088"` has a valid-looking body and is eleven characters long. And the grader compares with `is True` / `is False`, so return the booleans themselves.

## Read first
- [str.replace()](https://docs.python.org/3/library/stdtypes.html#str.replace) — dropping the dashes in one call
- [str.isdigit()](https://docs.python.org/3/library/stdtypes.html#str.isdigit) — the per-character question that decides whether a piece is usable
- [enumerate()](https://docs.python.org/3/library/functions.html#enumerate) — position and character together; the position *is* the weight here
- [zip()](https://docs.python.org/3/library/functions.html#zip) — the other route: pair each character with a weight from `range(10, 0, -1)`
- [Text sequence type: str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str) — slicing and indexing a string

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Two gates and then a sum. Gate one is about length, gate two is about which characters are allowed where — and the second gate is not "are they all digits", because of `X`. Write down, in words, exactly what makes `"3-598-2X507-9"` different from `"3-598-21507-X"` before you write any code; that sentence is your gate.
### Hint 2
Strip the dashes, then bail out with `False` if the length is not 10. Walk the ten characters with their positions: a digit contributes `int(char)`, an `X` at position 9 (the last one) contributes 10, and anything else means an immediate `False`. Multiply each contribution by `10 - position` and add it to a running total. At the end, the answer is `total % 11 == 0`. Returning early on the first bad character keeps the whole thing at about eight lines.
### Hint 3
Different data, same weighted-sum-then-modulus move — a two-digit check on an account number:

```python
digits = '4417123456'
weights = [7, 3, 1] * 4
total = sum(int(d) * w for d, w in zip(digits, weights))
total % 10 == 0   # -> False here: the total is 175
```

Pick the weights, pair them with the characters, sum, test one modulus. Every check-digit scheme you meet is this with a different weight list and a different modulus — and always with a gate in front that rejects the wrong length.
