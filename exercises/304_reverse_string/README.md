---
title: reverse-string — read the text back to front
minutes: 10
prereqs: [200, 203, 209, 215]
tags: [exercism, sequences, data-structures]
source: exercism/python practice/reverse-string (MIT, adapted)
---
# reverse-string — read the text back to front

*reverse-string — the slice everyone half-remembers, on real characters.*

## Why
Reading a string right-to-left comes up far more often than it
sounds: DNA reads have to be checked against their reverse, tail-style
log viewers show the newest line first, and palindrome checks are one
reversal plus one comparison. It is also the fastest way to find out
whether someone actually knows Python's slicing or just pattern-matches
on `for` loops — which is why it turns up in phone screens.

## You get
`text` — a string, e.g. "stressed". It may be empty, may hold
punctuation and spaces, and may hold characters outside ASCII such as
"子猫".

## You return
a new string with the same characters in the opposite
order. The original is left alone (strings cannot be changed anyway).

## Rules
Reverse by character, not by byte — a two-character string of Japanese
text comes back as two characters, not as mangled bytes. An empty
string reverses to an empty string.

```python
solve("stressed")    ->  "desserts"
solve("I'm hungry!") ->  "!yrgnuh m'I"
solve("racecar")     ->  "racecar"
solve("")            ->  ""
```

## Read first
- https://docs.python.org/3/library/stdtypes.html#common-sequence-operations  — strings are sequences: everything that works on a list works here too
- https://docs.python.org/3/reference/expressions.html#slicings  — the three-part slice [start:stop:step] and what it does when you leave parts out
- https://realpython.com/python-strings/  — indexing and slicing strings, with pictures

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
You need neither a loop nor an accumulator here. A string is a sequence, so the same bracket notation you use to take a piece of a list applies — and that notation takes one more number than most people ever use.
### Hint 2
The slice is text[start:stop:step]. Leave start and stop empty to mean 'the whole thing' and give step a value of -1 to walk it backwards. (The other route: reversed() hands you an iterator of characters, which you then have to join back into a string.)
### Hint 3
Different data, same slice:

```
[10, 20, 30][::-1]  ->  [30, 20, 10]
'abcdef'[::2]       ->  'ace'
'abcdef'[1:4]       ->  'bcd'
```

Same three slots every time — the third one is the step, and a negative step reverses the direction of travel.
