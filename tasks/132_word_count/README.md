---
title: dicts — tally the words in a subtitle
difficulty: hard
tier: core
minutes: 15
prereqs: [11, 25, 49, 61]
tags: [dicts]
source: exercism/python practice/word-count (MIT, adapted)
---
# dicts — tally the words in a subtitle

*word-count — cut messy text into words, then count them into a dict.*

## Read first
- [Mapping types: dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — what a dict guarantees and what it costs
- [collections.Counter](https://devdocs.io/python~3.14/library/collections#collections.Counter) — a dict subclass built for exactly this tally
- [re.findall()](https://devdocs.io/python~3.14/library/re#re.findall) — "give me every piece that looks like this", instead of "split on every separator I can think of"
- [str.lower()](https://devdocs.io/python~3.14/library/stdtypes#str.lower) — case folding before you count

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Every "what are people actually saying?" question ends up here: the top terms in a week of support tickets, the most common error phrase in a log file, the words a search index should not bother storing. The counting is trivial — a dict of word to number. The work is deciding what a *word* is when the text is full of commas, tabs, capital letters and apostrophes, and getting that decision written down once instead of re-guessing it in five places.

## You get
`subtitle` — one line of subtitle text, e.g.

```python
"That's the password: 'PASSWORD 123'!"
```

It is ASCII only. It may contain any punctuation, tabs and newlines, and it mixes upper and lower case freely.

> [!NOTE]
> Exercism's stub is `def count_words(sentence)`. Here the function is `solve(subtitle)`; nothing else about the task changes.

## You return
A `dict` mapping each word (lower case `str`) to how many times it occurs (`int`). Order does not matter — dicts compare by content. A `collections.Counter` is a dict and is accepted.

## Rules
A word is a run of ASCII letters and digits, optionally with one apostrophe inside it followed by more letters — that is what makes `don't` one word and not two.

| in the text | words found |
| --- | --- |
| `one,two,three` | `one`, `two`, `three` |
| `testing, 1, 2 testing` | `testing`, `1`, `2`, `testing` |
| `go Go GO` | `go`, `go`, `go` |
| `'can't'` | `can't` — the quotes around it are not part of the word |
| `my_spacebar_is_broken` | `my`, `spacebar`, `is`, `broken` — `_` separates |

- fold everything to lower case before counting
- digits are words: `100` counts like any other word
- an apostrophe that is not between letters (a quote mark) is a separator, not part of a word
- a word never appears with a count of zero; only words that occur are keys

```python
solve("one fish two fish red fish")  # -> {"one": 1, "fish": 3, "two": 1, "red": 1}
solve("go Go GO Stop stop")          # -> {"go": 3, "stop": 2}
solve("can, can't, 'can't'")         # -> {"can": 1, "can't": 2}
solve("hey,my_spacebar_is_broken")   # -> {"hey": 1, "my": 1, "spacebar": 1, "is": 1, "broken": 1}
```

> [!WARNING]
> `"''hey''"` must give `{"hey": 1}`, not `{"'hey'": 1}` — stripping punctuation only from the outside of each split piece is not enough, because `don't` has to survive.

## Hints
### Hint 1
There are two halves and they are independent. Half one: turn the line into a list of words. Half two: turn that list into counts. Half two is four lines at most — and one import makes it one line. Spend your thinking on half one, and in particular on `don't`: describe out loud which apostrophes belong to a word and which do not.
### Hint 2
Splitting is the wrong instinct here, because you would have to enumerate every separator. Turn the question around: instead of saying what separates words, say what a word *looks like*, and let `re.findall` pull out every match. A word is one or more letters or digits, optionally followed by an apostrophe and more letters. Lower-case the whole line first, so the pattern only has to think about one case. Then hand the list of matches to `collections.Counter`, or build the dict yourself with `counts[word] = counts.get(word, 0) + 1`.
### Hint 3
Different data, same two halves — counting HTTP status codes in an access log:

```python
import re
from collections import Counter

log = '10.0.0.1 - GET /a 200\n10.0.0.2 - GET /b 404\n10.0.0.1 - GET /a 200'
codes = re.findall(r'\b[1-5]\d\d$', log, flags=re.MULTILINE)
Counter(codes)   # -> Counter({'200': 2, '404': 1})
```

Describe the shape you want, collect every match, then tally. The messy part is always the pattern, never the counting.
