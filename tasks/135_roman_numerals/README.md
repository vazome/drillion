---
title: tuples — write a number the way Rome would
difficulty: hard
tier: core
minutes: 15
prereqs: [11, 23]
tags: [tuples]
source: exercism/python practice/roman-numerals (MIT, adapted)
---
# tuples — write a number the way Rome would

*roman-numerals — a table of value/symbol pairs beats a wall of if statements.*

## Read first
- [Tuples](https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range) — a tuple of `(value, symbol)` pairs is the natural shape for a lookup table that never changes
- [The while statement](https://devdocs.io/python~3.14/reference/compound_stmts#the-while-statement) — "keep taking this unit while it still fits"
- [divmod()](https://devdocs.io/python~3.14/library/functions#divmod) — the other route: how many of this unit fit, and what is left over, in one call
- [str.join()](https://devdocs.io/python~3.14/library/stdtypes#str.join) — build the answer from a list of pieces rather than by repeated `+=`

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Nobody bills you for Roman numerals, but the shape of this problem is everywhere: convert a number into the largest units first and work down — 3661 seconds is `1h 1m 1s`, 1500000000 bytes is `1.5 GB`, 95 minutes is `1:35`. The naive version is a tower of `if` statements that you have to edit in three places whenever the units change. The version worth learning keeps the units in a table and walks it, so adding a unit means adding a row.

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
