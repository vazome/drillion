---
title: dicts — tally the words in a subtitle
difficulty: hard
tier: core
minutes: 15
prereqs: [88, 95, 96, 101, 106]
tags: [dicts]
source: exercism/python practice/word-count (MIT, adapted)
---
# dicts — tally the words in a subtitle

*word-count — cut messy text into words, then count them into a dict.*

## Why
Every "what are people actually saying?" question ends up here: the top terms in a week of support tickets, the most common error phrase in a log file, the words a search index should not bother storing. The counting is trivial — a dict of word to number. The work is deciding what a *word* is when the text is full of commas, tabs, capital letters and apostrophes, and getting that decision written down once instead of re-guessing it in five places.

## Introduction
You teach English as a foreign language to high school students.

You've decided to base your entire curriculum on TV shows.
You need to analyze which words are used, and how often they're repeated.

This will let you choose the simplest shows to start with, and to gradually increase the difficulty as time passes.

## Instructions
Your task is to count how many times each word occurs in a subtitle of a drama.

The subtitles from these dramas use only ASCII characters.

The characters often speak in casual English, using contractions like _they're_ or _it's_.
Though these contractions come from two words (e.g. _we are_), the contraction (_we're_) is considered a single word.

Words can be separated by any form of punctuation (e.g. ":", "!", or "?") or whitespace (e.g. "\t", "\n", or " ").
The only punctuation that does not separate words is the apostrophe in contractions.

Numbers are considered words.
If the subtitles say _It costs 100 dollars._ then _100_ will be its own word.

Words are case insensitive.
For example, the word _you_ occurs three times in the following sentence:

> You come back, you hear me? DO YOU HEAR ME?

The ordering of the word counts in the results doesn't matter.

Here's an example that incorporates several of the elements discussed above:

- simple words
- contractions
- numbers
- case insensitive words
- punctuation (including apostrophes) to separate words
- different forms of whitespace to separate words

`"That's the password: 'PASSWORD 123'!", cried the Special Agent.\nSo I fled.`

The mapping for this subtitle would be:

```text
123: 1
agent: 1
cried: 1
fled: 1
i: 1
password: 2
so: 1
special: 1
that's: 1
the: 2
```

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

## Exercism hints
### General

This exercise has many potential solutions and many paths you can take along the way.
No path is manifestly "better" than another, although a particular path may be more interesting or better suited to what you want to learn or explore right now.
Some paths may trade speed for clarity, others might take up more memory but be more scalable or maintainable.
We encourage you to try out more than one strategy to see what happens.

_______
-  Python has a robust set of tools to work with strings. [`str.split`][str.split] [`str.replace`][str.replace] [`str.lower`][str.lower] and [`str.strip`][str.strip] can be particularly helpful with this challenge.
-  String methods can be chained together (_as long as the method returns a `str`_))
-  While `str.split()` is very _specific_, `str.strip()` behaves differently, and allows multiple combinations.
-  The [`string`][string] module (as opposed to `str`) has some constants that can be useful for filtering and comparison when processing strings.
________

-  [Dictionaries][dict] can be helpful for tabulating when items (keys) appear more than once in a string.
-  [`dict.setdefault()`][dict.setdefault] can help in processing when a key might be missing from a dictionary.
-  The [Collections][collections] module implements some really useful subtypes to the core `dict` (dictionary), purpose-built to do things like [tally][collections.counter].
________
-  Exploring the [`re`][re] module and regular expressions can be fun, but is by no means necessary to solve this challenge.
-  [Regex101][regex101] is very helpful for experimenting with regular expression logic.
-  Both [`re.sub`][re.sub] and [`re.findall`][re.findall] can be interesting strategies to employ.
________
-  [Comprehensions][comprehensions] can often "flatten" loops where items are being appended to a list or inserted into a dictionary.
-  [Generator expressions][generator expressions] can often "stand in" for a list comprehension when an iterable is needed.
  Generator expressions are evaluated in a "lazy" fashion, and take up less space in memory than a corresponding list comprehension.


[collections.counter]: https://docs.python.org/3/library/collections.html#collections.Counter
[collections]: https://docs.python.org/3/library/collections.html#module-collections
[comprehensions]: https://treyhunner.com/2015/12/python-list-comprehensions-now-in-color/
[dict.setdefault]: https://docs.python.org/3/library/stdtypes.html#dict.setdefault
[dict]: https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
[generator expressions]: https://dbader.org/blog/python-generator-expressions
[re.findall]: https://docs.python.org/3/library/re.html?highlight=re#re.findall
[re.sub]: https://docs.python.org/3/library/re.html?highlight=re#re.sub
[re]: https://docs.python.org/3/library/re.html?highlight=re#module-re
[regex101]: https://regex101.com/
[str.lower]: https://docs.python.org/3/library/stdtypes.html#str.lower
[str.replace]: https://docs.python.org/3/library/stdtypes.html#str.replace
[str.split]: https://docs.python.org/3/library/stdtypes.html#str.split
[str.strip]: https://docs.python.org/3/library/stdtypes.html#str.strip
[string]: https://docs.python.org/3/library/string.html

## Read first
- [Mapping types: dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict) — what a dict guarantees and what it costs
- [collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter) — a dict subclass built for exactly this tally
- [re.findall()](https://docs.python.org/3/library/re.html#re.findall) — "give me every piece that looks like this", instead of "split on every separator I can think of"
- [str.lower()](https://docs.python.org/3/library/stdtypes.html#str.lower) — case folding before you count

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

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
