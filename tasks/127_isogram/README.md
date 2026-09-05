---
title: strings — a word with no repeated letter
difficulty: easy
tier: core
minutes: 10
prereqs: [10, 51]
tags: [strings]
source: exercism/python practice/isogram (MIT, adapted)
---
# strings — a word with no repeated letter

*isogram — no letter twice: the set-length trick for spotting duplicates.*

## Read first
- [str.isalpha()](https://devdocs.io/python~3.14/library/stdtypes#str.isalpha) — `isalpha()` and `lower()`, the two methods that decide which characters count here
- [set](https://devdocs.io/python~3.14/library/stdtypes#set) — a set keeps one copy of each item; its length is therefore "how many distinct things did I see"
- [Real Python: strings](https://realpython.com/python-strings/) — walking a string character by character
- [len()](https://devdocs.io/python~3.14/library/functions#len) — the measuring half of the trick

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A crossword setter keeps a list of "non-pattern words" — words in which no letter appears twice — and submissions arrive from the public, so somebody has to screen them. Underneath the word game is the duplicate check you will run for the rest of your career: are these ids unique, did this CSV column repeat a key, did two hosts claim the same address. The measuring trick is always the same one.

## Instructions
Determine if a word or phrase is an isogram.

An isogram (also known as a "non-pattern word") is a word or phrase without a repeating letter, however spaces and hyphens are allowed to appear multiple times.

Examples of isograms:

- lumberjacks
- background
- downstream
- six-year-old

The word _isograms_, however, is not an isogram, because the s repeats.

## You get
`phrase` — a word or phrase, e.g. `"six-year-old"`. It may be empty, may mix upper and lower case, and may contain spaces and hyphens.

> [!NOTE]
> Exercism's stub is `def is_isogram(string)`. Here the function is `solve(phrase)`; nothing else about the task changes.

## You return
`True` if no letter repeats, `False` if one does. A real boolean.

## Rules
Only letters are compared, and case is ignored: `"Alphabet"` is not an isogram because of its two a's. Everything that is not a letter — spaces, hyphens, digits, punctuation — may repeat as often as it likes and never makes the answer `False`. An empty phrase is an isogram.

```python
solve("lumberjacks")   # -> True
solve("six-year-old")  # -> True   (hyphen repeats, letters do not)
solve("Alphabet")      # -> False  ('A' and 'a' are the same letter)
solve("up-to-date")    # -> False  ('t' appears twice)
```

> [!WARNING]
> The tests use `is True` / `is False`, so return the booleans themselves, not a truthy count.

## Hints
### Hint 1
Two separate questions here. First, which characters are even in the game — the hyphens in 'six-year-old' repeat and that is fine, spaces and hyphens are allowed to appear multiple times. Second, how do you notice a repeat at all? Think about a container that refuses to hold the same thing twice.
### Hint 2
Collect the characters that count — the alphabetic ones, all folded to a single case — into a list. Then compare how many you collected with how many *distinct* ones you collected. If those two numbers differ, some letter turned up more than once. `str.isalpha()` answers 'is this character a letter?' for one character at a time.
### Hint 3
Different data, same trick — checking a CSV column for duplicate ids:

```python
ids = ['a1', 'b2', 'a1']
len(set(ids)) != len(ids)   # -> True, so there is a duplicate
```

The set throws away the repeats; the length difference is what tells you they existed.
