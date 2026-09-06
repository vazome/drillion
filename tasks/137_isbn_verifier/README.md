---
title: strings — is this book number real, or a typo?
difficulty: medium
tier: core
minutes: 10
prereqs: [10]
tags: [strings]
source: exercism/python practice/isbn-verifier (MIT, adapted)
---
# strings — is this book number real, or a typo?

*isbn-verifier — a weighted checksum, and the one character that is not a digit.*

## Read first
- [str.replace()](https://devdocs.io/python~3.14/library/stdtypes#str.replace) — dropping the dashes in one call
- [str.isdigit()](https://devdocs.io/python~3.14/library/stdtypes#str.isdigit) — the per-character question that decides whether a piece is usable
- [enumerate()](https://devdocs.io/python~3.14/library/functions#enumerate) — position and character together; the position *is* the weight here
- [zip()](https://devdocs.io/python~3.14/library/functions#zip) — the other route: pair each character with a weight from `range(10, 0, -1)`
- [Text sequence type: str](https://devdocs.io/python~3.14/library/stdtypes#text-sequence-type-str) — slicing and indexing a string

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A shop's import job receives ten thousand rows of book data typed by humans and pasted from spreadsheets. Validating the identifier before the row reaches the database turns "mystery record nobody can find" into a rejected line with a reason, at the edge, for free. Every identifier you will meet at work — account numbers, IBANs, VAT numbers, container codes — carries a check digit for exactly this reason, and they all follow the shape below: weight each position, sum, test the total against one modulus.

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
