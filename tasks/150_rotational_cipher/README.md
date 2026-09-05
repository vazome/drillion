---
title: strings — ROT-n the letters, leave everything else alone
difficulty: easy
tier: core
minutes: 10
prereqs: [90, 95]
tags: [strings]
source: exercism/python practice/rotational-cipher (MIT, adapted)
---
# strings — ROT-n the letters, leave everything else alone

*rotational-cipher — shift letters around a 26-long circle and pass every other character straight through.*

## Read first
- [Text sequence type: str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str) — strings are immutable, so you build a new one rather than editing in place
- [string.ascii_lowercase / ascii_uppercase](https://docs.python.org/3/library/string.html#string.ascii_lowercase) — both alphabets, already written down
- [Arithmetic operations](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex) — `%`, and why it is what makes the shift wrap
- [str.join()](https://docs.python.org/3/library/stdtypes.html#str.join) — assembling the result from a list of characters instead of `+=` in a loop
- [ord() and chr()](https://docs.python.org/3/library/functions.html#ord) — the other route: characters as code points and back

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Two things worth owning live in this task. The first is modular arithmetic: `% 26` is what makes a shift wrap around instead of falling off the end of the alphabet, and it is the same `%` that makes ring buffers, round-robin load balancers, retry-slot assignment and hash bucketing work. The second is the discipline of transforming *only* what you were asked to transform — the letters — and passing punctuation, digits and spaces through untouched. Every text-processing bug you will ever debug is some version of a transformation that quietly ate a character it was not supposed to touch.

## Instructions
Create an implementation of the rotational cipher, also sometimes called the Caesar cipher.

The Caesar cipher is a simple shift cipher that relies on transposing all the letters in the alphabet using an integer key between `0` and `26`.
Using a key of `0` or `26` will always yield the same output due to modular arithmetic.
The letter is shifted for as many values as the value of the key.

The general notation for rotational ciphers is `ROT + <key>`.
The most commonly used rotational cipher is `ROT13`.

A `ROT13` on the Latin alphabet would be as follows:

```text
Plain:  abcdefghijklmnopqrstuvwxyz
Cipher: nopqrstuvwxyzabcdefghijklm
```

It is stronger than the Atbash cipher because it has 27 possible keys, and 25 usable keys.

Ciphertext is written out in the same formatting as the input including spaces and punctuation.

### Examples

- ROT5 `omg` gives `trl`
- ROT0 `c` gives `c`
- ROT26 `Cool` gives `Cool`
- ROT13 `The quick brown fox jumps over the lazy dog.` gives `Gur dhvpx oebja sbk whzcf bire gur ynml qbt.`
- ROT13 `Gur dhvpx oebja sbk whzcf bire gur ynml qbt.` gives `The quick brown fox jumps over the lazy dog.`

## You get
Two arguments:

```python
solve("Let's eat, Grandma!", 21)
```

- `text` — any string: mixed case, digits, spaces and punctuation
- `key` — an `int` from `0` to `26`, how far to shift

> [!NOTE]
> Exercism's stub is `def rotate(text, key)`. Here the function is `solve(text, key)`; nothing else about the task changes.

## You return
A `str` of exactly the same length as `text`, with the letters shifted and everything else identical.

## Rules
- lower-case letters shift within `a`–`z`, upper-case letters within `A`–`Z`; the case of each letter is preserved
- the shift wraps: with a key of 13, `n` becomes `a`
- a key of `0` or `26` gives the input back unchanged
- anything that is not an ASCII letter — spaces, digits, punctuation, apostrophes — is copied through in place
- the length and layout of the input are preserved exactly; nothing is stripped or grouped

```python
solve("a", 1)                     # -> "b"
solve("m", 13)                    # -> "z"
solve("n", 13)                    # -> "a"
solve("OMG", 5)                   # -> "TRL"
solve("Testing 1 2 3 testing", 4) # -> "Xiwxmrk 1 2 3 xiwxmrk"
solve("Let's eat, Grandma!", 21)  # -> "Gzo'n zvo, Bmviyhv!"
```

> [!WARNING]
> Case is not folded here — unlike the Atbash task, `"OMG"` must come back as `"TRL"`, in capitals. Shifting a capital with the lower-case alphabet's positions is the classic way to produce mojibake.

## Hints
### Hint 1
Handle one character at a time and sort it into exactly three cases: lower-case letter, upper-case letter, anything else. The third case is the easiest and the one people forget — it is not "skip", it is "keep as is". Start by writing the loop that copies every character unchanged, check the output equals the input, then add the shifting.

### Hint 2
For a letter, the shift is a move within a 26-long ring, so the work is: find its position in its own alphabet, add the key, take the remainder against 26 so the position wraps back to the start, and read the letter at that new position. `str.index` on `ascii_lowercase` gives you the position; the matching `ascii_uppercase` gives you the capitals with the same positions, which is why treating the two cases separately keeps the arithmetic identical. Collect the characters into a list and `join` them at the end. If you would rather avoid the two branches, `str.maketrans` can build one table for both alphabets at once and `translate` applies it in a single call.

### Hint 3
Different data, same wrap-with-`%` idea — handing out work to a fixed pool of workers, round-robin:

```python
workers = ['w0', 'w1', 'w2']
jobs = ['a', 'b', 'c', 'd', 'e']
[workers[i % len(workers)] for i, _ in enumerate(jobs)]
# -> ['w0', 'w1', 'w2', 'w0', 'w1']
```

Position plus offset, then `%` the size of the ring so it comes back round to the beginning. In this task the ring is the alphabet and the offset is the key.
