---
title: strings — prefixes, suffixes and slices
difficulty: medium
tier: core
minutes: 15
prereqs: [5, 8]
tags: [strings]
source: exercism/python concept/little-sisters-vocab (MIT, adapted)
---
# strings — prefixes, suffixes and slices

*Concatenation, `join`, slicing and `split` — four word transforms and not one loop.*

## Read first
- [text sequence type — `str`](https://devdocs.io/python~3.14/library/stdtypes#text-sequence-type-str) — a string is an immutable sequence, so every "change" here really returns a new string
- [string methods](https://devdocs.io/python~3.14/library/stdtypes#string-methods) — the full menu; `join` and `split` are the two this task lives on
- [common sequence operations](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — indexing and slicing, shared by `str`, `list` and `tuple`
- [`str.join()`](https://devdocs.io/python~3.14/library/stdtypes#str.join) — the separator is the string you call it *on*, and it lands between elements, never at the ends
- [`str.split()`](https://devdocs.io/python~3.14/library/stdtypes#str.split) — with no argument it splits on any run of whitespace and hands back a list
- [strings and character data in Python (Real Python)](https://realpython.com/python-strings/) — a long worked tour of the same methods
- [string formatting best practices (Real Python)](https://realpython.com/python-string-formatting/) — where `+` stops being the right tool
- [`string` — common string operations](https://devdocs.io/python~3.14/library/string) — the module beside the type, constants such as `ascii_lowercase` included
- [The absolute minimum every developer must know about Unicode (Joel Spolsky)](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/) — why "character" is a slippery word

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
Almost every name you touch in operations is a string with something bolted on the front, something to chop off the end, or one field buried in the middle: `prod-api-gateway`, `access.log.2026-08-25`, `arn:aws:s3:::bucket/key`. Your little sister's vocabulary homework is those same four moves in a friendlier costume — add a prefix to a word, stamp a prefix onto a whole list of words at once, strip a suffix off and repair the spelling underneath it, and pull one word out of a sentence by position. The interesting constraint is that none of the four needs a loop: the string methods already loop for you, and reaching for `for` here is the tell that you have not met `join` and `split` yet.

## You get
Nothing. `solve()` takes **no arguments** — it hands the grader your four finished functions, and the grader calls them with the words and sentences. This task covers all four Exercism tasks.

> [!NOTE]
> Exercism asks for four separate functions in one `strings.py`. Here there is one entry point: `solve()` returns a dict keyed by those same four names.

## You return
A dict with these four functions.

| key | parameters | returns |
| --- | --- | --- |
| `"add_prefix_un"` | `word` — a root word such as `"happy"` | the same word with `un` glued to the front, as a new string |
| `"make_word_groups"` | `vocab_words` — a list whose **first** item is the prefix and whose remaining items are the words, e.g. `['en', 'close', 'joy']` | one string: the bare prefix, then every word with the prefix applied, all separated by `' :: '` |
| `"remove_suffix_ness"` | `word` — a word ending in `ness` | the root word: the last four characters gone, and a leftover final `i` turned back into a `y` |
| `"adjective_to_verb"` | `sentence`, `index` — a sentence, and the position of the adjective once the sentence is split on whitespace; `index` may be negative | that word as a verb: trailing full stop dropped, `en` added |

```python
words = solve()
words["add_prefix_un"]("happy")                                # -> 'unhappy'
words["make_word_groups"](['en', 'close', 'joy', 'lighten'])   # -> 'en :: enclose :: enjoy :: enlighten'
words["remove_suffix_ness"]("heaviness")                       # -> 'heavy'
words["remove_suffix_ness"]("sadness")                         # -> 'sad'
words["adjective_to_verb"]('I need to make that bright.', -1)  # -> 'brighten'
words["adjective_to_verb"]('It got dark as the sun set.', 2)   # -> 'darken'
```

## Rules
- the dict keys are exactly the four strings above, and each value is the function itself — no parentheses
- in `make_word_groups` the separator is `' :: '`, one space either side of the two colons, and the prefix at the very start appears **bare**, without a copy of itself in front of it
- `remove_suffix_ness` removes exactly four characters; only then does the spelling rule apply — if what is left ends in `i`, that one character becomes `y` (`'heaviness'` → `'heavi'` → `'heavy'`, while `'sadness'` → `'sad'` and nothing more happens)
- `adjective_to_verb` splits on whitespace, so `index` counts words, not characters, and a negative index counts from the right
- every word handed to `adjective_to_verb` is "regular": it never needs a spelling change, only the full stop removed when the word happens to end its sentence

> [!WARNING]
> The tests compare with `==`, so spelling and spacing are graded. `'en::enclose'` and `'en :: enclose '` both fail, and so does `'bright.en'` — drop the full stop *before* you add the suffix.

## Hints
### Hint 1
Three of the four are one line each and the fourth is two. Small strings concatenate with the `+` operator, so task 1 is over before it starts. For task 2, believe it or not, [`str.join()`](https://devdocs.io/python~3.14/library/stdtypes#str.join) is all you need — **a loop is not required**, and there is no need to alter the list you were handed if you can work out a good delimiter string.
### Hint 2
Remember that a delimiter goes *between* elements and glues them together, and that it can be any string you like — including one you build out of the data itself. Look hard at the shape you have to produce: the prefix appears once, bare, at the front, and then once glued to each following word. What single delimiter, inserted between the untouched list items, produces exactly that?

For task 3, strings slice from the right with negative indices: `'beautiful'[:-3] == 'beauti'`. Chop the suffix off first, then look at the last character of what is left.

For task 4, [`str.split()`](https://devdocs.io/python~3.14/library/stdtypes#str.split) returns a list and can be indexed straight away — `'Exercism rocks!'.split()[0] == 'Exercism'` — and a negative index works there just as it does on a string. Be careful of punctuation: once you split on whitespace the full stop is part of the word, and the same kind of slice removes it (`'dark.'[:-1] == 'dark'`).
### Hint 3
Different data, same three moves — turning a config into environment variable names and back:

```python
keys = ['APP', 'HOST', 'PORT', 'DEBUG']
joiner = ', ' + keys[0] + '_'
joiner.join(keys)              # -> 'APP, APP_HOST, APP_PORT, APP_DEBUG'

path = '/var/log/nginx/access.log'
path.split('/')[-1]            # -> 'access.log'
path.split('/')[-1][:-4]       # -> 'access'
```

Note that the joiner is built out of the list's own first item, and that nothing in either snippet is a loop.
