---
title: regular-expressions — squeeze a long name down to its initials
difficulty: medium
tier: core
minutes: 15
prereqs: [88, 95, 96, 101]
tags: [regular-expressions, files-text]
source: exercism/python practice/acronym (MIT, adapted)
---
# regular-expressions — squeeze a long name down to its initials

*acronym — first letter of every word, once you agree what a word is.*

## Why
Naming things is half of infrastructure work: a service called "Customer Identity And Access Management" becomes `ciam` in the repo name, the DNS entry, the IAM role and the dashboard title, and someone has to generate that consistently rather than by taste. The same three lines turn a ticket title into a slug or a column header into a short key. The interesting part is not the initials — it is that "word" has to be defined precisely enough that `metal-oxide` gives two letters and `Halley's` gives one.

## Instructions
Convert a phrase to its acronym.

Techies love their TLA (Three Letter Acronyms)!

Help generate some jargon by writing a program that converts a long name like Portable Network Graphics to its acronym (PNG).

Punctuation is handled as follows: hyphens are word separators (like whitespace); all other punctuation can be removed from the input.

For example:

| Input                     | Output |
| ------------------------- | ------ |
| As Soon As Possible       | ASAP   |
| Liquid-crystal display    | LCD    |
| Thank George It's Friday! | TGIF   |

## You get
`phrase` — a long name, e.g. `"Portable Network Graphics"`. Words may be separated by spaces or hyphens, may carry punctuation such as commas, exclamation marks or underscores, and may be lower case, capitalised or already in capitals.

> [!NOTE]
> Exercism's stub is `def abbreviate(words)`. Here the function is `solve(phrase)`; nothing else about the task changes.

## You return
A `str`: the first letter of every word, all upper case, with nothing between them.

## Rules
- hyphens separate words, exactly like spaces: `metal-oxide` is two words
- every other punctuation mark is thrown away before you look for words
- an apostrophe is thrown away too, so `Halley's` is one word and contributes one `H`
- runs of separators collapse: `Something - I made up` has no empty word between `Something` and `I`
- a word already in capitals still contributes only its first letter: `GNU Image` starts `GI`

| phrase | acronym |
| --- | --- |
| `As Soon As Possible` | `ASAP` |
| `Liquid-crystal display` | `LCD` |
| `Thank George It's Friday!` | `TGIF` |
| `The Road _Not_ Taken` | `TRNT` |

```python
solve("Portable Network Graphics")                # -> "PNG"
solve("First In, First Out")                      # -> "FIFO"
solve("Complementary metal-oxide semiconductor")  # -> "CMOS"
solve("Halley's Comet")                           # -> "HC"
```

> [!WARNING]
> `"Something - I made up from thin air"` must give `"SIMUFTA"`, not `"S-IMUFTA"`. A lone hyphen between spaces is a separator that produces no letter at all, so an empty piece must never reach `word[0]`.

## Read first
- [re.findall()](https://docs.python.org/3/library/re.html#re.findall) — pull out every run that matches a pattern instead of splitting on separators
- [re.sub()](https://docs.python.org/3/library/re.html#re.sub) — the other route: replace the characters you do not want, then `split()`
- [str.split()](https://docs.python.org/3/library/stdtypes.html#str.split) — with no argument it splits on runs of whitespace and drops empty pieces, which is exactly the collapsing you need
- [str.isalpha()](https://docs.python.org/3/library/stdtypes.html#str.isalpha) — "is this character a letter?", one character at a time

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Do the cleaning and the initials in two separate steps, and get the cleaning right first. Print the list of words you end up with for `"Something - I made up from thin air"` and for `"Halley's Comet"` before you take a single first letter. If those two lists are right, the rest is one line.
### Hint 2
Turn every character that is not a letter into a space, with one exception: delete apostrophes rather than replacing them, so `Halley's` stays glued together as a single word. Then `split()` with no argument gives you the words, collapsing runs of spaces and never handing you an empty string. Finally take `word[0]`, upper-case it, and `"".join(...)` the results. The `re` module can do the same cleaning in one call, but a comprehension over the characters is just as good.
### Hint 3
Different data, same shape — building a short key from a column header:

```python
header = 'Total Cost (USD), 2026'
cleaned = ''.join(ch if ch.isalnum() else ' ' for ch in header)
'_'.join(word.lower() for word in cleaned.split())   # -> 'total_cost_usd_2026'
```

Normalise first, split second, assemble third. Every slug generator you ever write is these three lines with different rules in step one.
