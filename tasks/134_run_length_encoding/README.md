---
title: iteration — compress runs, and put them back
difficulty: medium
tier: core
minutes: 15
prereqs: [13, 90, 96, 101]
tags: [iteration, regular-expressions]
source: exercism/python practice/run-length-encoding (MIT, adapted)
---
# iteration — compress runs, and put them back

*run-length-encoding — a pair of functions that must undo each other exactly.*

## Read first
- [itertools.groupby()](https://devdocs.io/python~3.14/library/itertools#itertools.groupby) — hands you consecutive runs of equal items, which is the whole of `encode`
- [re.sub() with a function](https://devdocs.io/python~3.14/library/re#re.sub) — when the replacement is computed from the match, pass a function instead of a string
- [str.isdigit()](https://devdocs.io/python~3.14/library/stdtypes#str.isdigit) — the manual route for `decode`: accumulate digits until a non-digit arrives
- [Sequence operations](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — `"W" * 12` is the other half of `decode`

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Run-length encoding is the compression you meet before you meet compression: it is how fax machines, old bitmap formats and plenty of wire protocols shrink long stretches of the same value. The reason it is worth an hour is not the algorithm, it is the shape — two functions that have to be exact inverses. Serialise/deserialise, encrypt/decrypt, marshal/unmarshal: whenever you write one of a pair, the round trip is the test that finds the bug, and it finds it on the boring case (a run of length one) rather than the clever one.

## Instructions
Implement run-length encoding and decoding.

Run-length encoding (RLE) is a simple form of data compression, where runs (consecutive data elements) are replaced by just one data value and count.

For example we can represent the original 53 characters with only 13.

```text
"WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWB"  ->  "12WB12W3B24WB"
```

RLE allows the original data to be perfectly reconstructed from the compressed data, which makes it a lossless data compression.

```text
"AABCCCDEEEE"  ->  "2AB3CD4E"  ->  "AABCCCDEEEE"
```

For simplicity, you can assume that the unencoded string will only contain the letters A through Z (either lower or upper case) and whitespace.
This way data to be encoded will never contain any numbers and numbers inside data to be decoded always represent the count for the following character.

## You get
Nothing. Text arrives as an argument to your functions.

> [!NOTE]
> Exercism asks for two functions in one `run_length_encoding.py`. Here there is one entry point: `solve()` takes **no arguments** and returns a dict that hands both functions to the grader, keyed by name.

## You return
A dict with these two functions.

| key | parameter | returns |
| --- | --- | --- |
| `"encode"` | `text` — plain text: letters `A`–`Z`, `a`–`z` and whitespace, never digits | the compressed `str` |
| `"decode"` | `text` — a compressed `str` as produced by `encode` | the original `str` |

```python
codec = solve()
codec["encode"]("AABCCCDEEEE")   # -> "2AB3CD4E"
codec["decode"]("2AB3CD4E")      # -> "AABCCCDEEEE"
codec["encode"]("XYZ")           # -> "XYZ"
codec["encode"]("  hsqq qww  ")  # -> "2 hs2q q2w2 "
```

## Rules
- the dict keys are exactly `"encode"` and `"decode"`, and each value is the function itself — no parentheses
- a run of **one** character is written as the bare character, with no `1` in front of it
- a run of two or more is written as the count followed by the character, e.g. `12W`
- case is preserved and matters: `"zzz ZZ"` has two different runs
- whitespace is data like any other character — `"  "` encodes to `"2 "`
- both directions must handle the empty string and return `""`
- counts can be more than one digit, so `decode` must read `12W` as twelve `W`s, not as one `1` and two `W`s

```python
codec = solve()
codec["encode"]("WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWB")
# -> "12WB12W3B24WB"
codec["decode"]("12WB12W3B24WB")
# -> "WWWWWWWWWWWWBWWWWWWWWWWWWBBBWWWWWWWWWWWWWWWWWWWWWWWWB"
```

> [!WARNING]
> The grader round-trips your own output: `decode(encode(text)) == text` for randomly generated text. A `decode` that reads counts one digit at a time passes the small examples and fails the moment a run is ten or longer.

## Hints
### Hint 1
Write `encode` first and hand-run it on `"AABCCCDEEEE"`. Both functions have exactly one special case, and it is the same one seen from two sides: a run of length one carries no number. Decide what your code does with that case before you write the loop, not after.
### Hint 2
For `encode`, walk the text and track the current character and how many of it you have seen in a row; when the character changes, append `char` if the count is 1 and `f"{count}{char}"` otherwise — and remember to append the final run after the loop ends. `itertools.groupby` does that bookkeeping for you and turns the whole function into one comprehension. For `decode`, the safe move is to collect digits into a string until you hit a non-digit, then multiply: `char * int(digits or 1)`. A regular expression that matches "some digits followed by one non-digit" does the same in one call.
### Hint 3
Different data, same "runs of equal items" move — collapsing repeated log lines:

```python
from itertools import groupby

lines = ['timeout', 'timeout', 'timeout', 'ok', 'timeout']
[(line, len(list(group))) for line, group in groupby(lines)]
# -> [('timeout', 3), ('ok', 1), ('timeout', 1)]
```

Note that `groupby` only groups *neighbours* — the last `'timeout'` is its own group, which is exactly what run-length encoding needs and exactly what makes it wrong for counting.
