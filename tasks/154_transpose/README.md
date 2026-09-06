---
title: unpacking-and-multiple-assignment — turn the rows of a block of text into its columns
difficulty: hard
tier: core
minutes: 15
prereqs: [11, 30]
tags: [unpacking-and-multiple-assignment]
source: exercism/python practice/transpose (MIT, adapted)
---
# unpacking-and-multiple-assignment — turn the rows of a block of text into its columns

*transpose — rotate a ragged block of text, padding on the left but never on the right.*

## Read first
- [str.splitlines()](https://devdocs.io/python~3.14/library/stdtypes#str.splitlines) — cut the block into rows; note how it treats the empty string
- [zip()](https://devdocs.io/python~3.14/library/functions#zip) — `zip(*rows)` is the transpose itself, once the rows are the right length
- [Unpacking argument lists](https://devdocs.io/python~3.14/tutorial/controlflow#unpacking-argument-lists) — what the `*` in `zip(*rows)` actually does
- [str.ljust()](https://devdocs.io/python~3.14/library/stdtypes#str.ljust) — pads on the right to a given width, which is how you make rows equal length

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Rotating a table is a daily chore: a metrics export arrives with one row per host and one column per day, and the dashboard wants it the other way round; a CSV has to be pivoted before it can be joined; a fixed-width report needs reading down instead of across. `zip(*rows)` does the easy half in one expression. The interesting half is what happens when the rows are not all the same length — and that is where this task lives, because the rule is deliberately asymmetric: pad on the left, never on the right.

## Instructions
Given an input text output it transposed.

Roughly explained, the transpose of a matrix:

```text
ABC
DEF
```

is given by:

```text
AD
BE
CF
```

Rows become columns and columns become rows.
See [transpose][].

If the input has rows of different lengths, this is to be solved as follows:

- Pad to the left with spaces.
- Don't pad to the right.

Therefore, transposing this matrix:

```text
ABC
DE
```

results in:

```text
AD
BE
C
```

And transposing:

```text
AB
DEF
```

results in:

```text
AD
BE
 F
```

In general, all characters from the input should also be present in the transposed output.
That means that if a column in the input text contains only spaces on its bottom-most row(s), the corresponding output row should contain the spaces in its right-most column(s).

[transpose]: https://en.wikipedia.org/wiki/Transpose

## You get
`text` — a block of text, rows separated by `"\n"`, with no trailing newline:

```python
"ABC\n123"
```

The rows may have different lengths, the text may be a single line, and it may be `""`.

> [!NOTE]
> Exercism's stub is `def transpose(text)`. Here the function is `solve(text)`; nothing else about the task changes.

## You return
A `str`: the transposed block, again with rows joined by `"\n"` and no trailing newline.

```python
solve("ABC\n123")  # -> "A1\nB2\nC3"
solve("")          # -> ""
```

## Rules
- output row `i` is made of character `i` of each input row, top to bottom
- there are as many output rows as there are characters in the longest input row
- a row that is shorter than a **later** row is padded with spaces up to that later row's length — those spaces do appear in the output
- a row that is shorter than only **earlier** rows is not padded; its column simply ends

```python
solve("ABC\nDE")   # -> "AD\nBE\nC"
solve("AB\nDEF")   # -> "AD\nBE\n F"
solve("A1")        # -> "A\n1"
solve("A\n1")      # -> "A1"
```

The asymmetry is easier to see on the triangle:

| input | output |
| --- | --- |
| `T` | `TEASER` |
| `EE` | `_EASER` |
| `AAA` | `__ASER` |
| `SSSS` | `___SER` |
| `EEEEE` | `____ER` |
| `RRRRRR` | `_____R` |

(each `_` in that table is a real space in the output)

> [!WARNING]
> Padding every row to the width of the longest one and transposing is *almost* right, but it adds trailing spaces to the output rows. `"ABC\nDE"` must give `"AD\nBE\nC"` — three characters on the last row would be wrong, and so would `"C "`.

## Hints
### Hint 1
Try `zip(*text.splitlines())` in a REPL on `"ABC\n123"` and then on `"ABC\nDE"`. The first is already the answer; the second silently loses the `C`, because `zip` stops at the shortest row. Everything left to do is deciding how long each row should be *before* the rotation.
### Hint 2
Ask, for each row, "is there a longer row below me?" — if yes, pad to that length; if no, leave the row alone. Walking the rows from the bottom upwards makes this cheap: keep a running maximum of the lengths you have seen so far and pad each row to it. After that pass, rotate. Since the rows are now ragged only on their right-hand ends, `zip` is no longer safe — build each output row by taking character `i` from every row that is long enough to have one.
### Hint 3
Different data, same "pad, then rotate" shape — flipping a small table of readings:

```python
rows = [[1, 2, 3], [4, 5, 6]]
list(zip(*rows))            # -> [(1, 4), (2, 5), (3, 6)]

ragged = ['ab', 'cde']
width = max(len(row) for row in ragged)
padded = [row.ljust(width) for row in ragged]
[''.join(col) for col in zip(*padded)]   # -> ['ac', 'bd', ' e']
```

The `' e'` shows the padding surviving into the output, which is what the left-padding rule asks for — the task only adds the extra condition that padding a row is allowed for later rows and forbidden for earlier ones.
