---
title: roman-numerals — write a number the way Rome would
minutes: 15
prereqs: [200, 206, 209, 215, 218, 221, 224, 227, 233]
tags: [exercism, tuples, core]
source: exercism/python practice/roman-numerals (MIT, adapted)
---
# roman-numerals — write a number the way Rome would

*roman-numerals — a table of value/symbol pairs beats a wall of if statements.*

## Why
Nobody bills you for Roman numerals, but the shape of this problem is everywhere: convert a number into the largest units first and work down — 3661 seconds is `1h 1m 1s`, 1500000000 bytes is `1.5 GB`, 95 minutes is `1:35`. The naive version is a tower of `if` statements that you have to edit in three places whenever the units change. The version worth learning keeps the units in a table and walks it, so adding a unit means adding a row.

## Introduction
Today, most people in the world use Arabic numerals (0–9).
But if you travelled back two thousand years, you'd find that most Europeans were using Roman numerals instead.

To write a Roman numeral we use the following Latin letters, each of which has a value:

| M    | D   | C   | L   | X   | V   | I   |
| ---- | --- | --- | --- | --- | --- | --- |
| 1000 | 500 | 100 | 50  | 10  | 5   | 1   |

A Roman numeral is a sequence of these letters, and its value is the sum of the letters' values.
For example, `XVIII` has the value 18 (`10 + 5 + 1 + 1 + 1 = 18`).

There's one rule that makes things trickier though, and that's that **the same letter cannot be used more than three times in succession**.
That means that we can't express numbers such as 4 with the seemingly natural `IIII`.
Instead, for those numbers, we use a subtraction method between two letters.
So we think of `4` not as `1 + 1 + 1 + 1` but instead as `5 - 1`.
And slightly confusingly to our modern thinking, we write the smaller number first.
This applies only in the following cases: 4 (`IV`), 9 (`IX`), 40 (`XL`), 90 (`XC`), 400 (`CD`) and 900 (`CM`).

Order matters in Roman numerals!
Letters (and the special compounds above) must be ordered by decreasing value from left to right.

Here are some examples:

```text
 105 => CV
---- => --
 100 => C
+  5 =>  V
```

```text
 106 => CVI
---- => --
 100 => C
+  5 =>  V
+  1 =>   I
```

```text
 104 => CIV
---- => ---
 100 => C
+  4 =>  IV
```

And a final more complex example:

```text
 1996 => MCMXCVI
----- => -------
 1000 => M
+ 900 =>  CM
+  90 =>    XC
+   5 =>      V
+   1 =>       I
```

## Instructions
Your task is to convert a number from Arabic numerals to Roman numerals.

For this exercise, we are only concerned about traditional Roman numerals, in which the largest number is MMMCMXCIX (or 3,999).

> [!NOTE]
> There are lots of different ways to convert between Arabic and Roman numerals.
> We recommend taking a naive approach first to familiarise yourself with the concept of Roman numerals and then search for more efficient methods.
>
> Make sure to check out our Deep Dive video at the end to explore the different approaches you can take!

## You get
`number` — a whole number between 1 and 3999 inclusive, e.g. `1666`. Zero and negatives never arrive; neither does anything above 3999.

> [!NOTE]
> Exercism's stub is `def roman(number)`. Here the function is `solve(number)`; nothing else about the task changes.

## You return
A `str` of upper-case Latin letters, e.g. `"MDCLXVI"`. No spaces, no separators.

## Rules
Thirteen symbols cover every number in range — the seven letters plus the six subtraction pairs:

| value | symbol | value | symbol |
| --- | --- | --- | --- |
| 1000 | `M` | 90 | `XC` |
| 900 | `CM` | 50 | `L` |
| 500 | `D` | 40 | `XL` |
| 400 | `CD` | 10 | `X` |
| 100 | `C` | 9 | `IX` |
| | | 5 | `V` |
| | | 4 | `IV` |
| | | 1 | `I` |

- symbols come out in order of decreasing value, left to right
- a letter never appears more than three times in a row: 4 is `IV`, not `IIII`; 40 is `XL`, not `XXXX`
- the six subtraction pairs above are the only ones that exist — there is no `IL` for 49, it is `XLIX`

```python
solve(1)     # -> "I"
solve(4)     # -> "IV"
solve(48)    # -> "XLVIII"
solve(1666)  # -> "MDCLXVI"
solve(3999)  # -> "MMMCMXCIX"
```

> [!WARNING]
> `49` is the case that catches half-finished solutions: it is `XLIX` (40 + 9), not `IL` and not `XXXXVIIII`. If you treat the subtraction pairs as ordinary table rows in the right order, you get it for free.

## Read first
- [Tuples](https://docs.python.org/3/library/stdtypes.html#sequence-types-list-tuple-range) — a tuple of `(value, symbol)` pairs is the natural shape for a lookup table that never changes
- [The while statement](https://docs.python.org/3/reference/compound_stmts.html#the-while-statement) — "keep taking this unit while it still fits"
- [divmod()](https://docs.python.org/3/library/functions.html#divmod) — the other route: how many of this unit fit, and what is left over, in one call
- [str.join()](https://docs.python.org/3/library/stdtypes.html#str.join) — build the answer from a list of pieces rather than by repeated `+=`

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Start by asking what the *largest* symbol is that still fits inside your number, write it down, subtract its value, and ask the same question again about what is left. Do that by hand for 1666 and watch how many times you have to ask before you reach zero. The subtraction pairs like `CM` and `IV` are not exceptions to that process — they are simply more symbols with their own values.
### Hint 2
Keep the thirteen value/symbol pairs in one table, ordered from 1000 down to 1, and loop over it once. For each pair, `while number >= value:` append the symbol and subtract the value. Because `900` sits in the table above `500`, the number 900 never gets a chance to become `DCCCC`. When the loop over the table finishes, `number` is 0 and the joined pieces are the answer. There are no `if` statements in this solution at all.
### Hint 3
Different data, same greedy walk — turning seconds into a human duration:

```python
UNITS = ((3600, 'h'), (60, 'm'), (1, 's'))

def human(seconds):
    parts = []
    for size, name in UNITS:
        count, seconds = divmod(seconds, size)
        if count:
            parts.append(f'{count}{name}')
    return ' '.join(parts)

human(3661)   # -> '1h 1m 1s'
```

Largest unit first, take as many as fit, carry the remainder onwards. Adding a `86400, 'd'` row at the top is the entire change needed to support days.
