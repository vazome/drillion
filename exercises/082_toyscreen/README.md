---
title: 'DRILL: palindrome, anagram, top-N words'
minutes: 30
prereqs: [19]
tags: [whole-task]
practices: [28, 19, 22]
---
# DRILL: palindrome, anagram, top-N words

Whole-task drill: the three warm-ups that open half of all phone screens.

Combines topics 28 (str methods), 19 (Counter), 22 (sets and sorting).

## Why
Many phone screens for ops roles open with two or three tiny
warm-up questions before the real work: is this phrase the same read
backwards, are these two words made of the same letters, what are the
most common words in this text. They are not about the job; they check
that you can state a rule clearly and then write it. Here all three are
bundled into one function so you can practise them together.

## You get
`phrase` — a string like "Nurses, run." to test for reading the
same backwards.

`pair` — two strings packed together, like ("Dirty room", "Dormitory"),
to test whether they use the same letters.

`text` — a string of words like "pod pod, POD deploy Deploy node".

`n` — a whole number, like 2: how many of the most common words to
report. The test builds all four and hands them to you.

## You return
a dictionary with three keys: "palindrome" (True or False),
"anagram" (True or False) and "top_words" (a list of (word, count)
pairs, most common first).

## Rules
Three small questions, one dict back:

```
{"palindrome": True,
 "anagram": True,
 "top_words": [("pod", 3), ("deploy", 2)]}
```

palindrome — is `phrase` the same read backwards, ignoring case and

```
anything that is not a letter or a digit.

    "Nurses, run."  ->  True
```

anagram — `pair` is (a, b). Same letters rearranged, ignoring case and

```
spaces.

    ("Dirty room", "Dormitory")  ->  True
```

top_words — the n most common words in `text`. Lowercase them and

```
strip the characters .,!?;:'" off both ends of each word. Sort by
count descending, then by the word alphabetically, so the answer
never depends on which word you happened to see first. Return
(word, count) tuples.

    "pod pod, POD deploy Deploy node", 2
    ->  [("pod", 3), ("deploy", 2)]
```

Each one is five lines. The grading here is on how cleanly you say the
rule before you write it, so narrate all three out loud.

## Hints
### Hint 1
Three unrelated questions, so resist making them share code. Every one is the same two beats: normalise, then compare. Every bug lives in the normalise beat — which characters you drop, and whether you dropped them on both sides.
### Hint 2
Palindrome: build a cleaned string with a comprehension over phrase keeping c.isalnum(), lowercased, then compare it to s[::-1]. Anagram: sorted() of each side, lowercased with spaces removed, and compare the two lists. Top words: Counter over text.lower().split() with w.strip('.,!?;:\'"') on each word, then sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n] — most_common would leave ties in whatever order they arrived.
### Hint 3
Different data, both normalising moves:

```python
from collections import Counter
words = [w.strip('.,;') for w in 'Red, red; blue GREEN green red'.lower().split()]
counts = Counter(words)
print(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:2])
# [('red', 3), ('green', 2)]

s = ''.join(c.lower() for c in 'Ab, ba.' if c.isalnum())
print(s, s == s[::-1])          # abba True
print(sorted('cat') == sorted('act'))    # True
```

Note the sort key: minus the count sorts big first, the word sorts A to Z, one pass.
