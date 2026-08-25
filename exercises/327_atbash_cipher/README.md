---
title: atbash-cipher — mirror the alphabet, then cut into five-letter blocks
minutes: 15
prereqs: [200, 209, 215, 218, 221, 224, 227]
tags: [exercism, string-methods, core]
source: exercism/python practice/atbash-cipher (MIT, adapted)
---
# atbash-cipher — mirror the alphabet, then cut into five-letter blocks

*atbash-cipher — normalise, substitute, group; and decoding is the same walk without the grouping.*

## Why
Two habits come out of this one. The first is normalising input before you transform it: strip what does not matter — case, spaces, punctuation — so the interesting code only ever sees one clean shape, instead of every function re-deciding what to do with a comma. The second is chunking a sequence into fixed-size groups, which you will write again for pagination, for batching API calls, for splitting a long token into readable segments, and for every "insert a space every four digits" card field. The cipher itself is a lookup table; the reusable parts are on either side of it.

## Instructions
Create an implementation of the Atbash cipher, an ancient encryption system created in the Middle East.

The Atbash cipher is a simple substitution cipher that relies on transposing all the letters in the alphabet such that the resulting alphabet is backwards.
The first letter is replaced with the last letter, the second with the second-last, and so on.

An Atbash cipher for the Latin alphabet would be as follows:

```text
Plain:  abcdefghijklmnopqrstuvwxyz
Cipher: zyxwvutsrqponmlkjihgfedcba
```

It is a very weak cipher because it only has one possible key, and it is a simple mono-alphabetic substitution cipher.
However, this may not have been an issue in the cipher's time.

Ciphertext is written out in groups of fixed length, the traditional group size being 5 letters, leaving numbers unchanged, and punctuation is excluded.
This is to make it harder to guess things based on word boundaries.
All text will be encoded as lowercase letters.

### Examples

- Encoding `test` gives `gvhg`
- Encoding `x123 yes` gives `c123b vh`
- Decoding `gvhg` gives `test`
- Decoding `gsvjf rxpyi ldmul cqfnk hlevi gsvoz abwlt` gives `thequickbrownfoxjumpsoverthelazydog`

## You get
Nothing. `solve()` takes **no arguments**; the text arrives as an argument to each of the functions you hand back.

> [!NOTE]
> Exercism asks for two functions, `encode(plain_text)` and `decode(ciphered_text)`, in one `atbash_cipher.py`. Here there is one entry point: `solve()` returns a dict that hands both to the grader, keyed by name.

## You return
A dict with these two functions.

| key | parameters | returns |
| --- | --- | --- |
| `"encode"` | `plain_text` — any string, mixed case, with punctuation and digits | the ciphertext as a `str`, lower case, in space-separated groups of five |
| `"decode"` | `ciphered_text` — ciphertext, with or without the grouping spaces | the plaintext as a `str`, lower case, with no spaces at all |

```python
cipher = solve()
cipher["encode"]("test")                    # -> "gvhg"
cipher["encode"]("x123 yes")                # -> "c123b vh"
cipher["encode"]("Truth is fiction.")       # -> "gifgs rhurx grlm"
cipher["decode"]("vcvix rhn")               # -> "exercism"
cipher["decode"]("gvhgr mt123 gvhgr mt")    # -> "testing123testing"
```

## Rules
Both directions start with the same clean-up: drop every character that is not a letter or a digit, lower-case what is left, then map each letter to its mirror.

| plain | cipher |
| --- | --- |
| `a` | `z` |
| `b` | `y` |
| `m` | `n` |
| `n` | `m` |
| `z` | `a` |

- the mapping is its own inverse — `a`↔`z`, `b`↔`y` — so encoding and decoding do exactly the same substitution
- digits pass through untouched, and they count as characters when you are measuring the groups of five
- spaces, punctuation and case in the input are discarded before anything else happens
- **encode** then inserts a single space after every fifth character; the last group may be shorter and never has a trailing space
- **decode** does not group at all — it returns one unbroken run of characters

```python
cipher = solve()
cipher["encode"]("mindblowingly")  # -> "nrmwy oldrm tob"
cipher["encode"]("O M G")          # -> "lnt"
cipher["decode"]("vc vix    r hn")  # -> "exercism"
```

> [!WARNING]
> The groups of five are counted over the *cleaned* text, not the original: `"Testing,1 2 3, testing."` encodes to `"gvhgr mt123 gvhgr mt"`, where the digits sit inside a group and the original spaces are gone.

## Read first
- [String methods](https://docs.python.org/3/library/stdtypes.html#string-methods) — `isalnum()`, `lower()` and `join()`, which is most of this exercise
- [str.maketrans() and str.translate()](https://docs.python.org/3/library/stdtypes.html#str.translate) — a whole substitution table applied in one call
- [Common sequence operations](https://docs.python.org/3/library/stdtypes.html#common-sequence-operations) — slicing, including `[::-1]` to build the reversed alphabet
- [string.ascii_lowercase](https://docs.python.org/3/library/string.html#string.ascii_lowercase) — the alphabet, already written down for you
- [range() with a step](https://docs.python.org/3/library/functions.html#func-range) — `range(0, len(text), 5)` is the index of every group's first character

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
`decode` is a strict subset of `encode`: same cleaning, same substitution, no grouping. So write one private helper that does the shared work and let both public functions call it — `decode` will be a single line, and `encode` will be that helper plus the chunking. Deciding this before you write anything saves you from two nearly identical functions that drift apart.

### Hint 2
For the substitution, you need "the letter at position *i* becomes the letter at position 25 − *i*". You can compute that with the alphabet's `index()`, or you can build the pairing once with `str.maketrans` over the alphabet and its reverse and then apply it to the whole string in one call. For the cleaning step, `isalnum()` decides what survives; keep the digits, they are part of the ciphertext. For the grouping, do not try to insert spaces while you build the string — finish the ciphertext first, then take slices of five by stepping a `range` across its length, and `join` those slices with a single space.

### Hint 3
Different data, same clean-then-chunk shape — printing a long API token in readable blocks of four:

```python
raw = 'sk-live 9f3a!2b7c 41de'
clean = ''.join(char for char in raw if char.isalnum())
blocks = [clean[i:i + 4] for i in range(0, len(clean), 4)]
' '.join(blocks)   # -> 'skli ve9f 3a2b 7c41 de'
```

Three separate steps, each doing one thing: throw away what is not data, cut at fixed positions with a stepped `range`, and join with the separator you want. Slicing past the end is safe, so the short final block needs no special case.
