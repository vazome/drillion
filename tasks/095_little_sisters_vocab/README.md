---
title: strings — prefixes, suffixes and slices
difficulty: medium
tier: core
minutes: 15
prereqs: [88, 92]
tags: [strings]
source: exercism/python concept/little-sisters-vocab (MIT, adapted)
---
# strings — prefixes, suffixes and slices

*Concatenation, `join`, slicing and `split` — four word transforms and not one loop.*

## Why
Almost every name you touch in operations is a string with something bolted on the front, something to chop off the end, or one field buried in the middle: `prod-api-gateway`, `access.log.2026-08-25`, `arn:aws:s3:::bucket/key`. Your little sister's vocabulary homework is those same four moves in a friendlier costume — add a prefix to a word, stamp a prefix onto a whole list of words at once, strip a suffix off and repair the spelling underneath it, and pull one word out of a sentence by position. The interesting constraint is that none of the four needs a loop: the string methods already loop for you, and reaching for `for` here is the tell that you have not met `join` and `split` yet.

## Introduction
A `str` in Python is an [immutable sequence][text sequence] of [Unicode code points][unicode code points].
These could include letters, diacritical marks, positioning characters, numbers, currency symbols, emoji, punctuation, space and line break characters, and more.
 Being immutable, a `str` object's value in memory doesn't change; methods that appear to modify a string return a new copy or instance of that `str` object.


A `str` literal can be declared via single `'` or double `"` quotes. The escape `\` character is available as needed.


```python

>>> single_quoted = 'These allow "double quoting" without "escape" characters.'

>>> double_quoted = "These allow embedded 'single quoting', so you don't have to use an 'escape' character."

>>> escapes = 'If needed, a \'slash\' can be used as an escape character within a string when switching quote styles won\'t work.'
```

Multi-line strings are declared with `'''` or `"""`.


```python
>>> triple_quoted =  '''Three single quotes or "double quotes" in a row allow for multi-line string literals.
  Line break characters, tabs and other whitespace are fully supported.

  You\'ll most often encounter these as "doc strings" or "doc tests" written just below the first line of a function or class definition.
    They\'re often used with auto documentation ✍ tools.
    '''
```

Strings can be concatenated using the `+` operator.
 This method should be used sparingly, as it is not very performant or easily maintained.


```python
language = "Ukrainian"
number = "nine"
word = "дев'ять"

sentence = word + " " + "means" + " " + number + " in " + language + "."

>>> print(sentence)
...
"дев'ять means nine in Ukrainian."
```

If a `list`, `tuple`, `set` or other collection of individual strings needs to be combined into a single `str`, [`<str>.join(<iterable>)`][str-join], is a better option:


```python
# str.join() makes a new string from the iterables elements.
>>> chickens = ["hen", "egg", "rooster"] # Lists are iterable.
>>> ' '.join(chickens)
'hen egg rooster'

# Any string can be used as the joining element.
>>> ' :: '.join(chickens)
'hen :: egg :: rooster'

>>> ' 🌿 '.join(chickens)
'hen 🌿 egg 🌿 rooster'


# Any iterable can be used as input.
>>> flowers = ("rose", "daisy", "carnation")  # Tuples are iterable.
>>> '*-*'.join(flowers)
'rose*-*daisy*-*carnation'

>>> flowers = {"rose", "daisy", "carnation"}  # Sets are iterable, but output order is not guaranteed.
>>> '*-*'.join(flowers)
'rose*-*carnation*-*daisy'

>>> phrase = "This is my string"  # Strings are iterable, but be careful!
>>> '..'.join(phrase)
'T..h..i..s.. ..i..s.. ..m..y.. ..s..t..r..i..n..g'


# Separators are inserted **between** elements, but can be any string (including spaces).
# This can be exploited for interesting effects.
>>> under_words = ['under', 'current', 'sea', 'pin', 'dog', 'lay']
>>> separator = ' ⤴️ under'
>>> separator.join(under_words)
'under ⤴️ undercurrent ⤴️ undersea ⤴️ underpin ⤴️ underdog ⤴️ underlay'

# The separator can be composed different ways, as long as the result is a string.
>>> upper_words = ['upper', 'crust', 'case', 'classmen', 'most', 'cut']
>>> separator = ' 🌟 ' + upper_words[0]
>>> separator.join(upper_words)
 'upper 🌟 uppercrust 🌟 uppercase 🌟 upperclassmen 🌟 uppermost 🌟 uppercut'
```

Code points within a `str` can be referenced by `0-based index` number from the left:


```python
creative = '창의적인'

>>> creative[0]
'창'

>>> creative[2]
'적'

>>> creative[3]
'인'
```

Indexing also works from the right, starting with a `-1-based index`:


```python
creative = '창의적인'

>>> creative[-4]
'창'

>>> creative[-2]
'적'

>>> creative[-1]
'인'

```

There is no separate “character” or "rune" type in Python, so indexing a string produces a new `str` of length 1:


```python

>>> website = "exercism"
>>> type(website[0])
<class 'str'>

>>> len(website[0])
1

>>> website[0] == website[0:1] == 'e'
True
```

Substrings can be selected via _slice notation_, using [`<str>[<start>:stop:<step>]`][common sequence operations] to produce a new string.
 Results exclude the `stop` index.
 If no `start` is given, the starting index will be 0.
 If no `stop` is given, the `stop` index will be the end of the string.


```python
moon_and_stars = '🌟🌟🌙🌟🌟⭐'
sun_and_moon = '🌞🌙🌞🌙🌞🌙🌞🌙🌞'

>>> moon_and_stars[1:4]
'🌟🌙🌟'

>>> moon_and_stars[:3]
'🌟🌟🌙'

>>> moon_and_stars[3:]
'🌟🌟⭐'

>>> moon_and_stars[:-1]
'🌟🌟🌙🌟🌟'

>>> moon_and_stars[:-3]
'🌟🌟🌙'

>>> sun_and_moon[::2]
'🌞🌞🌞🌞🌞'

>>> sun_and_moon[:-2:2]
'🌞🌞🌞🌞'

>>> sun_and_moon[1:-1:2]
'🌙🌙🌙🌙'
```

Strings can also be broken into smaller strings via [`<str>.split(<separator>)`][str-split], which will return a `list` of substrings.
 The list can then be further indexed or split, if needed.
 Using `<str>.split()` without any arguments will split the string on whitespace.


```python
>>> cat_ipsum = "Destroy house in 5 seconds mock the hooman."
>>> cat_ipsum.split()
...
['Destroy', 'house', 'in', '5', 'seconds', 'mock', 'the', 'hooman.']


>>> cat_ipsum.split()[-1]
'hooman.'


>>> cat_words = "feline, four-footed, ferocious, furry"
>>> cat_words.split(', ')
...
['feline', 'four-footed', 'ferocious', 'furry']
```

Separators for `<str>.split()` can be more than one character.
The **whole string** is used for split matching.


```python

>>> colors = """red,
orange,
green,
purple,
yellow"""

>>> colors.split(',\n')
['red', 'orange', 'green', 'purple', 'yellow']
```

Strings support all [common sequence operations][common sequence operations].
 Individual code points can be iterated through in a loop via `for item in <str>`.
 Indexes _with_ items can be iterated through in a loop via `for index, item in enumerate(<str>)`.


```python

>>> exercise = 'လေ့ကျင့်'

# Note that there are more code points than perceived glyphs or characters
>>> for code_point in exercise:
...    print(code_point)
...
လ
ေ
့
က
ျ
င
်
့

# Using enumerate will give both the value and index position of each element.
>>> for index, code_point in enumerate(exercise):
...    print(index, ": ", code_point)
...
0 :  လ
1 :  ေ
2 :  ့
3 :  က
4 :  ျ
5 :  င
6 :  ်
7 :  ့
```


[common sequence operations]: https://docs.python.org/3/library/stdtypes.html#common-sequence-operations
[str-join]: https://docs.python.org/3/library/stdtypes.html#str.join
[str-split]: https://docs.python.org/3/library/stdtypes.html#str.split
[text sequence]: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
[unicode code points]: https://stackoverflow.com/questions/27331819/whats-the-difference-between-a-character-a-code-point-a-glyph-and-a-grapheme

## Instructions
You are helping your younger sister with her English vocabulary homework, which she is finding very tedious.
 Her class is learning to create new words by adding _prefixes_ and _suffixes_.
 Given a set of words, the teacher is looking for correctly transformed words with correct spelling by adding the prefix to the beginning or the suffix to the ending.

The assignment has four activities, each with a set of text or words to work with.


### 1. Add a prefix to a word

One of the most common prefixes in English is `un`, meaning "not".
 In this activity, your sister needs to make negative, or "not" words by adding `un` to them.

Implement the `add_prefix_un(<word>)` function that takes `word` as a parameter and returns a new `un` prefixed word:


```python
>>> add_prefix_un("happy")
'unhappy'

>>> add_prefix_un("manageable")
'unmanageable'
```


### 2. Add prefixes to word groups

There are four more common prefixes that your sister's class is studying:
 `en` (_meaning to 'put into' or 'cover with'_),
 `pre` (_meaning 'before' or 'forward'_),
 `auto` (_meaning 'self' or 'same'_),
  and `inter` (_meaning 'between' or 'among'_).

 In this exercise, the class is creating groups of vocabulary words using these prefixes, so they can be studied together.
 Each prefix comes in a list with common words it's used with.
 The students need to apply the prefix and produce a string that shows the prefix applied to all of the words.

Implement the `make_word_groups(<vocab_words>)` function that takes a `vocab_words` as a parameter in the following form:
 `[<prefix>, <word_1>, <word_2> .... <word_n>]`, and returns a string with the prefix applied to each word that looks like:
  `'<prefix> :: <prefix><word_1> :: <prefix><word_2> :: <prefix><word_n>'`.

Creating a `for` or `while` loop to process the input is not needed here.
Think carefully about which string methods (and delimiters) you could use instead.


```python
>>> make_word_groups(['en', 'close', 'joy', 'lighten'])
'en :: enclose :: enjoy :: enlighten'

>>> make_word_groups(['pre', 'serve', 'dispose', 'position'])
'pre :: preserve :: predispose :: preposition'

>> make_word_groups(['auto', 'didactic', 'graph', 'mate'])
'auto :: autodidactic :: autograph :: automate'

>>> make_word_groups(['inter', 'twine', 'connected', 'dependent'])
'inter :: intertwine :: interconnected :: interdependent'
```


### 3. Remove a suffix from a word

`ness` is a common suffix that means _'state of being'_.
 In this activity, your sister needs to find the original root word by removing the `ness` suffix.
  But of course there are pesky spelling rules: If the root word originally ended in a consonant followed by a 'y', then the 'y' was changed to 'i'.
 Removing 'ness' needs to restore the 'y' in those root words. e.g. `happiness` --> `happi` --> `happy`.

Implement the `remove_suffix_ness(<word>)` function that takes in a `word`, and returns the root word without the `ness` suffix.


```python
>>> remove_suffix_ness("heaviness")
'heavy'

>>> remove_suffix_ness("sadness")
'sad'
```

### 4. Extract and transform a word

Suffixes are often used to change the part of speech a word is assigned to.
 A common practice in English is "verbing" or "verbifying" -- where an adjective _becomes_ a verb by adding an `en` suffix.

In this task, your sister is going to practice "verbing" words by extracting an adjective from a sentence and turning it into a verb.
 Fortunately, all the words that need to be transformed here are "regular" - they don't need spelling changes to add the suffix.

Implement the `adjective_to_verb(<sentence>, <index>)` function that takes two parameters.
 A `sentence` using the vocabulary word, and the `index` of the word, once that sentence is split apart.
 The function should return the extracted adjective as a verb.


```python
>>> adjective_to_verb('I need to make that bright.', -1 )
'brighten'

>>> adjective_to_verb('It got dark as the sun set.', 2)
'darken'
```

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

## Exercism hints
### General

- The Python Docs [Tutorial for strings][python-str-doc] has an overview of the Python `str` type.
- String methods [`str.join()`][str-join] and [`str.split()`][str-split] ar very helpful when processing strings.
- The Python Docs on [Sequence Types][common sequence operations] has a rundown of operations common to all sequences, including `strings`, `lists`, `tuples`, and `ranges`.

There's four activities in the assignment, each with a set of text or words to work with.

### 1. Add a prefix to a word

- Small strings can be concatenated with the `+` operator.

### 2. Add prefixes to word groups

- Believe it or not, [`str.join()`][str-join] is all you need here.  **A loop is not required**.
- The tests will be feeding your function a `list`.  There will be no need to alter this `list` if you can figure out a good delimiter string.
- Remember that delimiter strings go between elements and "glue" them together into a single string. Delimiters are inserted _without_ space, although you can include space characters within them.
- Like [`str.split()`][str-split], `str.join()` can process an arbitrary-length string, made up of any unicode code points. _Unlike_ `str.split()`, it can also process arbitrary-length iterables like `list`, `tuple`, and `set`.

### 3. Remove a suffix from a word

- Strings can be indexed or sliced from either the left (starting at 0) or the right (starting at -1).
- If you want the last code point of an arbitrary-length string, you can use `[-1]`.
- The last three letters in a string can be "sliced off" using a negative index. e.g. `beautiful'[:-3] == 'beauti`

### 4. Extract and transform a word

- Using [`str.split()`][str-split] returns a `list` of strings broken on white space.
- `lists` are sequences, and can be indexed.
- [`str.split()`][str-split] can be directly indexed: `'Exercism rocks!'.split()[0] == 'Exercism'`
- Be careful of punctuation! Periods can be removed via slice: `'dark.'[:-1] == 'dark'`


[common sequence operations]: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
[python-str-doc]: https://docs.python.org/3/tutorial/introduction.html#strings
[str-join]: https://docs.python.org/3/library/stdtypes.html#str.join
[str-split]: https://docs.python.org/3/library/stdtypes.html#str.split

## Read first
- [text sequence type — `str`](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str) — a string is an immutable sequence, so every "change" here really returns a new string
- [string methods](https://docs.python.org/3/library/stdtypes.html#string-methods) — the full menu; `join` and `split` are the two this task lives on
- [common sequence operations](https://docs.python.org/3/library/stdtypes.html#common-sequence-operations) — indexing and slicing, shared by `str`, `list` and `tuple`
- [`str.join()`](https://docs.python.org/3/library/stdtypes.html#str.join) — the separator is the string you call it *on*, and it lands between elements, never at the ends
- [`str.split()`](https://docs.python.org/3/library/stdtypes.html#str.split) — with no argument it splits on any run of whitespace and hands back a list
- [strings and character data in Python (Real Python)](https://realpython.com/python-strings/) — a long worked tour of the same methods
- [string formatting best practices (Real Python)](https://realpython.com/python-string-formatting/) — where `+` stops being the right tool
- [`string` — common string operations](https://docs.python.org/3/library/string.html) — the module beside the type, constants such as `ascii_lowercase` included
- [The absolute minimum every developer must know about Unicode (Joel Spolsky)](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/) — why "character" is a slippery word

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Three of the four are one line each and the fourth is two. Small strings concatenate with the `+` operator, so task 1 is over before it starts. For task 2, believe it or not, [`str.join()`](https://docs.python.org/3/library/stdtypes.html#str.join) is all you need — **a loop is not required**, and there is no need to alter the list you were handed if you can work out a good delimiter string.
### Hint 2
Remember that a delimiter goes *between* elements and glues them together, and that it can be any string you like — including one you build out of the data itself. Look hard at the shape you have to produce: the prefix appears once, bare, at the front, and then once glued to each following word. What single delimiter, inserted between the untouched list items, produces exactly that?

For task 3, strings slice from the right with negative indices: `'beautiful'[:-3] == 'beauti'`. Chop the suffix off first, then look at the last character of what is left.

For task 4, [`str.split()`](https://docs.python.org/3/library/stdtypes.html#str.split) returns a list and can be indexed straight away — `'Exercism rocks!'.split()[0] == 'Exercism'` — and a negative index works there just as it does on a string. Be careful of punctuation: once you split on whitespace the full stop is part of the word, and the same kind of slice removes it (`'dark.'[:-1] == 'dark'`).
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
