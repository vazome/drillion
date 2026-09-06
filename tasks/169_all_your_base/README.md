---
title: comparisons — convert digits from one base to another
difficulty: medium
tier: core
minutes: 25
prereqs: [3, 6, 13]
tags: [comparisons]
source: exercism/python practice/all-your-base (MIT, adapted)
---
# comparisons — convert digits from one base to another

*all-your-base — collapse the digits into one number, then peel a new set of digits off it.*

## Read first
- [`divmod()`](https://devdocs.io/python~3.14/library/functions#divmod) — quotient and remainder in one call: the remainder is the next output digit, the quotient is what is left to convert
- [`any()`](https://devdocs.io/python~3.14/library/functions#any) — "is *any* digit out of range?" as a single expression
- [Raising exceptions](https://devdocs.io/python~3.14/tutorial/errors#raising-exceptions) — `raise ValueError("…")` with a message that has to match exactly

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Every identifier you have ever copied out of a system is a number in a costume: hex in a stack trace, base32 in a TOTP secret, base58 in a wallet address, base64 in a token. Converting between two of them looks like a solved problem until the library you reached for disagrees with the one on the other side about leading zeros, or about what an empty input means, and you are left staring at two ids that should be the same value. Doing the conversion once by hand — in, then out, with every awkward input given a deliberate answer — is what makes all of those APIs readable afterwards.

## You get
- `from_base` — the base the digits are currently written in, an `int`, e.g. `2`
- `digits` — the number as a list of `int`s, most significant digit first, e.g. `[1, 0, 1]`. It may be empty and it may carry leading zeros.
- `to_base` — the base to convert into, an `int`, e.g. `10`

The digits are numbers, not characters: `[2, 10]` in base 16 is the number written `2A` in hex.

> [!NOTE]
> Exercism's stub is `def rebase(input_base, digits, output_base)`. Here it is `solve(from_base, digits, to_base)` — same three arguments, same order.

## You return
A `list` of `int` — the same number written in `to_base`, most significant digit first, with no leading zeros. Zero itself is `[0]`.

## Rules
- the three checks run in this order — input base, then output base, then the digits — so when both bases are bad it is the input base that gets reported
- `from_base < 2` raises `ValueError("input base must be >= 2")`
- `to_base < 2` raises `ValueError("output base must be >= 2")`
- any digit `d` with `d < 0` or `d >= from_base` raises `ValueError("all digits must satisfy 0 <= d < input base")`
- an empty `digits`, or digits that are all zeros, converts to `[0]`
- leading zeros are accepted on the way in and never produced on the way out
- do the arithmetic yourself; `int(text, base)` and friends are not the task

```python
solve(2, [1, 0, 1, 0, 1, 0], 10)  # -> [4, 2]
solve(3, [1, 1, 2, 0], 16)        # -> [2, 10]
solve(7, [0, 6, 0], 10)           # -> [4, 2]
solve(2, [], 10)                  # -> [0]
solve(10, [0, 0, 0], 2)           # -> [0]
```

## Hints
### Hint 1
Do not try to go from one base straight to the other. There are two easy halves: turn the incoming digits into an ordinary Python `int` — which has no base at all, a number is just a number — and then turn that `int` into digits in the target base. Get the three guard clauses out of the way first, in the order their messages are listed, and what remains is those two halves.

### Hint 2
On the way in: read the digits left to right, and before adding each new one, multiply what you have so far by the input base. That is exactly what positional notation means, and it costs you no exponents. On the way out: repeatedly divide by the output base and collect the remainders — they come out least significant first, so the last thing you do is turn them around. Two edge cases then fall out of the loop instead of needing branches of their own: if the number is already zero the loop body never runs, so `[0]` is something you have to supply yourself, and leading zeros on the input contribute nothing on the way in and so cannot survive to the output.

### Hint 3
Different data, same shape — the same collapse-then-peel trick on a duration, where the "bases" are not even all the same size:

```python
total = ((1 * 24) + 9) * 60 + 5   # 1 day, 9 hours, 5 minutes -> 1985 minutes

parts = []
for size in (60, 24):             # minutes in an hour, then hours in a day
    total, remainder = divmod(total, size)
    parts.append(remainder)
parts.append(total)
parts.reverse()                   # -> [1, 9, 5]
```

Collapse to one quantity on the way in, peel it apart with `divmod` on the way out, reverse at the end. Base conversion is this with one repeated size instead of a list of different ones — and with `[0]` to remember, since a duration of zero would leave `parts` looking rather empty here too.
