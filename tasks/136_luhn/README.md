---
title: classes — the checksum that catches a mistyped card number
difficulty: hard
tier: core
minutes: 15
prereqs: [96, 115]
tags: [classes]
source: exercism/python practice/luhn (MIT, adapted)
---
# classes — the checksum that catches a mistyped card number

*luhn — double every second digit from the right, and mind which digits those are.*

## Read first
- [Classes tutorial](https://devdocs.io/python~3.14/tutorial/classes) — `__init__`, `self`, and where instance state lives
- [str.replace()](https://devdocs.io/python~3.14/library/stdtypes#str.replace) — removing the spaces in one call
- [str.isdigit()](https://devdocs.io/python~3.14/library/stdtypes#str.isdigit) — asks the "is this all digits?" question about a whole string, not just one character
- [reversed()](https://devdocs.io/python~3.14/library/functions#reversed) — walk from the right so "every second digit from the right" needs no length arithmetic
- [enumerate()](https://devdocs.io/python~3.14/library/functions#enumerate) — position and character together, which is how you know whether to double

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Before a payment form talks to a bank, before an IMEI reaches a carrier, before a national insurance number hits a database, a two-line check catches most typos and every single-digit slip — for free, offline, in microseconds. That is what a checksum buys: cheap rejection of nonsense at the edge, so the expensive system downstream only sees plausible input. Validating early and locally is a habit worth having, and Luhn is the cleanest example of it.

## Introduction
At the Global Verification Authority, you've just been entrusted with a critical assignment.
Across the city, from online purchases to secure logins, countless operations rely on the accuracy of numerical identifiers like credit card numbers, bank account numbers, transaction codes, and tracking IDs.
The Luhn algorithm is a simple checksum formula used to help identify mistyped numbers.

A batch of identifiers has just arrived on your desk.
All of them must pass the Luhn test to ensure they're legitimate.
If any fail, they'll be flagged as invalid, preventing mistakes such as incorrect transactions or failed account verifications.

Can you ensure this is done right? The integrity of many services depends on you.

## Instructions
Determine whether a number is valid according to the [Luhn formula][luhn].

The number will be provided as a string.

### Validating a number

Strings of length 1 or less are not valid.
Spaces are allowed in the input, but they should be stripped before checking.
All other non-digit characters are disallowed.

### Examples

#### Valid credit card number

The number to be checked is `4539 3195 0343 6467`.

The first step of the Luhn algorithm is to start at the end of the number and double every second digit, beginning with the second digit from the right and moving left.

```text
4539 3195 0343 6467
↑ ↑  ↑ ↑  ↑ ↑  ↑ ↑  (double these)
```

If the result of doubling a digit is greater than 9, we subtract 9 from that result.
We end up with:

```text
8569 6195 0383 3437
```

Finally, we sum all digits.
If the sum is evenly divisible by 10, the original number is valid.

```text
8 + 5 + 6 + 9 + 6 + 1 + 9 + 5 + 0 + 3 + 8 + 3 + 3 + 4 + 3 + 7 = 80
```

80 is evenly divisible by 10, so number `4539 3195 0343 6467` is valid!

#### Invalid Canadian SIN

The number to be checked is `066 123 478`.

We start at the end of the number and double every second digit, beginning with the second digit from the right and moving left.

```text
066 123 478
 ↑  ↑ ↑  ↑  (double these)
```

If the result of doubling a digit is greater than 9, we subtract 9 from that result.
We end up with:

```text
036 226 458
```

We sum the digits:

```text
0 + 3 + 6 + 2 + 2 + 6 + 4 + 5 + 8 = 36
```

36 is not evenly divisible by 10, so number `066 123 478` is not valid!

[luhn]: https://en.wikipedia.org/wiki/Luhn_algorithm

## You get
Nothing to start — you return a **class**. The grader builds it as `Luhn(card_num)`, where `card_num` is the identifier as a string, e.g. `"4539 3195 0343 6467"`. It may contain spaces anywhere, including at the front, and it may contain characters that make it invalid.

> [!NOTE]
> Exercism's stub is a `class Luhn` in `luhn.py`. Here the entry point is `solve()`, which takes **no arguments** and returns the class itself — not an instance.

## You return
The class. The grader uses it like this:

```python
Luhn = solve()
Luhn("4539 3195 0343 6467").valid()  # -> True
Luhn("8273 1232 7352 0569").valid()  # -> False
```

So it needs `__init__(self, card_num)` and a method `valid(self)` returning a real `bool`.

## Rules
- spaces are stripped before anything else is decided; they may appear anywhere and never make a number invalid
- after stripping spaces, **any** non-digit character makes the number invalid — letters, `-`, `:`, `#`, `%`, all of them. Return `False`; do not raise
- a string with **one digit or fewer** is invalid, even `"0"`, even `"  "`
- doubling starts at the **second digit from the right** and moves left, so which digits get doubled depends on the length
- if doubling gives more than 9, subtract 9 from the result
- the number is valid when the sum of all the digits (doubled ones counted after the subtraction) is divisible by 10

```python
Luhn = solve()
Luhn("059").valid()          # -> True
Luhn("055 444 285").valid()  # -> True
Luhn("055 444 286").valid()  # -> False   last digit changed
Luhn("055-444-285").valid()  # -> False   hyphens are not spaces
Luhn("0000 0").valid()       # -> True    five digits, sum 0
Luhn(" 0").valid()           # -> False   one digit after stripping
```

> [!WARNING]
> The grader compares with `is True` / `is False`, so return the booleans themselves. It also calls `valid()` **twice on the same object** and expects the same answer both times — do not consume or mutate the digits inside `valid()`.

## Hints
### Hint 1
Three jobs, in this order: clean the input, reject what cannot possibly be a number, then compute. Keep them apart — most wrong answers here come from computing a checksum over a string that still had a space or a letter in it. Do the arithmetic by hand on `"059"` and check you get 10 before writing any code.
### Hint 2
"Every second digit from the right" is much easier if you actually walk from the right: `for index, char in enumerate(reversed(digits))` gives you index 0 for the last digit, and the ones you double are exactly the odd indices. Double, and if the result is over 9 subtract 9 — which is the same as adding its two digits together. Sum everything and test `total % 10 == 0`. Put the cleaning in `__init__` or in `valid()`, but if you put it in `valid()` make sure it works the second time it is called.
### Hint 3
Different data, same "the position decides what happens to the value" pattern — a parity check over a byte string:

```python
bits = '1011001'
total = sum(int(bit) * (2 if index % 2 else 1)
            for index, bit in enumerate(reversed(bits)))
total % 2 == 0   # -> False, so this word fails its parity check
```

Walk from the end, let the index decide the weight, sum, then test the total against one modulus. Luhn is this with weights 1 and 2, a "subtract 9 if over 9" step, and `% 10` at the finish.
