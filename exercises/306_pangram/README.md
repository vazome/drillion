---
title: pangram — a sentence that uses every letter
minutes: 10
prereqs: [200, 203, 209, 215]
tags: [exercism, strings, core]
source: exercism/python practice/pangram (MIT, adapted)
---
# pangram — a sentence that uses every letter

*pangram — does the sentence use all 26 letters? A subset check, not 26 ifs.*

## Why
A shop that sells fonts wants a different sample sentence each
time someone previews a typeface, and every sample has to show off all
26 letters — otherwise a customer never sees what the font's "q" looks
like. Sentences are crowdsourced, so submissions need screening. The
check itself ("does this thing contain everything on my required
list?") is the same one you run against required config keys or
required IAM permissions.

## You get
`sentence` — a string, e.g. "the quick brown fox jumps over
the lazy dog". It may be empty and may contain digits, underscores,
punctuation and mixed case.

## You return
`True` if every letter of the English alphabet appears at
least once, `False` otherwise. A real boolean.

## Rules
Case does not matter: "K" counts as "k". Only the 26 English letters
matter — digits, punctuation and underscores are neither required nor
a problem, and a letter appearing many times is no better than once.
An empty sentence is not a pangram.

```python
solve("the quick brown fox jumps over the lazy dog")   ->  True
solve("the_quick_brown_fox_jumps_over_the_lazy_dog")   ->  True
solve("five boxing wizards jump quickly at it")        ->  False  (no "h")
solve("abcdefghijklm ABCDEFGHIJKLM")                   ->  False  (13 letters twice)
```

## Read first
- https://docs.python.org/3/library/stdtypes.html#set  — sets, and `<=` / issubset: "is everything I need in there?"
- https://docs.python.org/3/library/string.html#string.ascii_lowercase  — the alphabet as a ready-made constant, so you never type it out
- https://docs.python.org/3/library/functions.html#all  — all(), the other way to say the same thing

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
You are asking one question 26 times: 'did the sentence contain this letter?'. Rather than write it 26 times, make one collection of what the sentence contains and one of what it must contain, and compare them in a single step.
### Hint 2
Fold the sentence to a single case, then turn it into a set of characters — duplicates and punctuation stop mattering the moment you do. `string.ascii_lowercase` is the 26 letters, ready made. Sets answer 'is every item of A also in B?' directly with `<=` (or `.issubset`); `all()` with a generator says the same thing one letter at a time.
### Hint 3
Different data, same check — validating a config:

```
required = {'host', 'port', 'token'}
required <= set(config)   ->  True when nothing is missing
```

Extra keys in `config` are irrelevant, exactly as extra punctuation is irrelevant to a pangram.
