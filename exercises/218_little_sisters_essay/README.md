---
title: string-methods — the essay clean-up pass
minutes: 12
prereqs: [200, 215]
tags: [exercism, string-methods, core]
source: exercism/python concept/little-sisters-essay (MIT, adapted)
---
# string-methods — the essay clean-up pass

*`title()`, `endswith()`, `strip()`, `replace()` — four methods, four one-liners.*

## Why
The boring half of every text pipeline is normalisation: trim the whitespace an editor left behind, check that a line really ends the way you assumed, title-case a heading for a report, swap one token for another. Your sister's essay needs exactly that pass before the teacher reads it, and so does every CSV column, every log line and every YAML value you will ever parse. The lesson is not that these are hard — it is that Python already ships all four, so hand-writing a loop to strip spaces is a code review comment waiting to happen.

## Introduction
The `str` class offers [many useful methods][str methods] for working with and composing strings.
These include searching, cleaning, splitting, transforming, translating, and many other techniques.

Strings are [sequences][text sequence] of [Unicode code points][unicode code points] -- individual "characters" or code points (_strings of length 1_) can be referenced by `0-based index` number from the left, or `-1-based index` number from the right.
Strings implement all [common sequence operations][common sequence operations].

They can be iterated through using `for item in <str>` or `for index, item in enumerate(<str>)` syntax.
They can also be concatenated using `<str> + <other str>` or `<str>.join(<iterable>)`.

Strings are _immutable_, meaning the value of a `str` object in memory cannot change.
Functions or methods that operate on a `str` (_like the ones we are learning about here_) will return a new `instance` of that `str` object instead of modifying the original `str`.

Following is a small selection of Python string methods.
For a complete list, see the [str class][str methods] in the Python docs.


[`<str>.title()`][str-title] parses a string and capitalizes the first "character" of each "word" found.
In Python, this is very dependent on the [language codec][codecs] used and how the particular language represents words and characters.
There may also be [locale][locale] rules in place for a language or character set.


```python
man_in_hat_th = 'ผู้ชายใส่หมวก'
man_in_hat_ru = 'мужчина в шляпе'
man_in_hat_ko = '모자를 쓴 남자'
man_in_hat_en = 'the man in the hat.'

>>> man_in_hat_th.title()
'ผู้ชายใส่หมวก'

>>> man_in_hat_ru.title()
'Мужчина В Шляпе'

>>> man_in_hat_ko.title()
'모자를 쓴 남자'

>> man_in_hat_en.title()
'The Man In The Hat.'
```

[`<str>.endswith(<suffix>)`][str-endswith] returns `True` if the string ends with `<suffix>`, `False` otherwise.


```python
>>> 'My heart breaks. 💔'.endswith('💔')
True

>>> 'cheerfulness'.endswith('ness')
True

# Punctuation is part of the string, so needs to be included in any endswith match.
>>> 'Do you want to 💃?'.endswith('💃')
False

>> 'The quick brown fox jumped over the lazy dog.'.endswith('dog')
False
```

[`<str>.strip(<chars>)`][str-strip] returns a copy of the `str` with leading and trailing `<chars>` removed.
The code points specified in `<chars>` are not a prefix or suffix - **all combinations** of the code points will be removed starting from **both ends** of the string.
 If nothing is specified for `<chars>`, all combinations of whitespace code points will be removed.


 ```python
# This will remove "https://", because it can be formed from "/stph:". 
>>> 'https://unicode.org/emoji/'.strip('/stph:')
'unicode.org/emoji'

# Removal of all whitespace from both ends of the str.
>>> '   🐪🐪🐪🌟🐪🐪🐪   '.strip()
'🐪🐪🐪🌟🐪🐪🐪'

>>> justification = 'оправдание'
>>> justification.strip('еина')
'оправд'

# Prefix and suffix in one step.
>>> 'unaddressed'.strip('dnue')
'address'

>>> '  unaddressed  '.strip('dnue ')
'address'
```


[`<str>.replace(<substring>, <replacement substring>)`][str-replace] returns a copy of the string with all occurrences of `<substring>` replaced with `<replacement substring>`.

The quote used below is from [The Hunting of the Snark][The Hunting of the Snark] by [Lewis Carroll][Lewis Carroll]

```python
# The Hunting of the Snark, by Lewis Carroll
>>> quote = '''
"Just the place for a Snark!" the Bellman cried,
   As he landed his crew with care;
Supporting each man on the top of the tide
   By a finger entwined in his hair.

"Just the place for a Snark! I have said it twice:
   That alone should encourage the crew.
Just the place for a Snark! I have said it thrice:
   What I tell you three times is true."
'''

>>> quote.replace('Snark', '🐲')
...
'\n"Just the place for a 🐲!" the Bellman cried,\n   As he landed his crew with care;\nSupporting each man on the top of the tide\n   By a finger entwined in his hair.\n\n"Just the place for a 🐲! I have said it twice:\n   That alone should encourage the crew.\nJust the place for a 🐲! I have said it thrice:\n   What I tell you three times is true."\n'

>>> 'bookkeeper'.replace('kk', 'k k')
'book keeper'
```

[Lewis Carroll]: https://www.poetryfoundation.org/poets/lewis-carroll
[The Hunting of the Snark]: https://www.poetryfoundation.org/poems/43909/the-hunting-of-the-snark
[codecs]: https://docs.python.org/3/library/codecs.html
[common sequence operations]: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
[locale]: https://docs.python.org/3/library/locale.html#module-locale
[str methods]: https://docs.python.org/3/library/stdtypes.html#string-methods
[str-endswith]: https://docs.python.org/3/library/stdtypes.html#str.endswith
[str-replace]: https://docs.python.org/3/library/stdtypes.html#str.replace
[str-strip]: https://docs.python.org/3/library/stdtypes.html#str.strip
[str-title]: https://docs.python.org/3/library/stdtypes.html#str.title
[text sequence]: https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str
[unicode code points]: https://stackoverflow.com/questions/27331819/whats-the-difference-between-a-character-a-code-point-a-glyph-and-a-grapheme

## Instructions
In this exercise you are helping your younger sister edit her paper for school. The teacher is looking for correct punctuation, grammar, and excellent word choice.

You have four tasks to clean up and modify strings.

### 1. Capitalize the title of the paper

Any good paper needs a properly formatted title.
Implement the function `capitalize_title(<title>)` which takes a title `str` as a parameter and capitalizes the first letter of each word.
This function should return a `str` in title case.


```python
>>> capitalize_title("my hobbies")
"My Hobbies"
```

### 2. Check if each sentence ends with a period

You want to make sure that the punctuation in the paper is perfect.
Implement the function `check_sentence_ending()` that takes `sentence` as a parameter. This function should return a `bool`.


```python
>>> check_sentence_ending("I like to hike, bake, and read.")
True
```

### 3. Clean up spacing

To make the paper look professional, unnecessary spacing needs to be removed.
Implement the function `clean_up_spacing()` that takes  `sentence` as a parameter.
The function should remove extra whitespace at both the beginning and the end of the sentence, returning a new, updated sentence `str`.


```python
>>> clean_up_spacing(" I like to go on hikes with my dog.  ")
"I like to go on hikes with my dog."
```

### 4. Replace words with a synonym

To make the paper _even better_, you can replace some of the adjectives with their synonyms.
Write the function `replace_word_choice()` that takes `sentence`, `old_word`, and `new_word` as parameters.
This function should replace all instances of the `old_word` with the `new_word`, and return a new `str` with the updated sentence.


```python
>>> replace_word_choice("I bake good cakes.", "good", "amazing")
"I bake amazing cakes."
```

## You get
Nothing. `solve()` takes **no arguments**; it hands the grader your four finished functions and the grader supplies the titles and sentences. This drill covers all four Exercism tasks.

> [!NOTE]
> Exercism asks for four separate functions in one `string_methods.py`. Here there is one entry point: `solve()` returns a dict keyed by those same four names.

## You return
A dict with these four functions.

| key | parameters | returns |
| --- | --- | --- |
| `"capitalize_title"` | `title` — e.g. `"my hobbies"` | the same title with the first letter of every word upper case |
| `"check_sentence_ending"` | `sentence` | `True` when the sentence ends with a full stop, `False` otherwise |
| `"clean_up_spacing"` | `sentence` | the sentence with leading and trailing whitespace removed; the inside is left alone |
| `"replace_word_choice"` | `sentence`, `old_word`, `new_word` | the sentence with **every** occurrence of `old_word` swapped for `new_word` |

```python
essay = solve()
essay["capitalize_title"]("my hobbies")                            # -> 'My Hobbies'
essay["check_sentence_ending"]("I like to hike, bake, and read.")  # -> True
essay["check_sentence_ending"]("Fittonia are nice")                # -> False
essay["clean_up_spacing"](" I like to go on hikes with my dog.  ")
# -> 'I like to go on hikes with my dog.'
essay["replace_word_choice"]("I bake good cakes.", "good", "amazing")
# -> 'I bake amazing cakes.'
```

## Rules
- the dict keys are exactly the four strings above, and each value is the function itself — no parentheses
- `clean_up_spacing` touches the two ends only: double spaces in the middle of the sentence survive
- `replace_word_choice` replaces *every* occurrence, not just the first, and matches plain substrings — there is no notion of word boundaries, so replacing `"cat"` would also hit `"category"`
- when `old_word` does not appear at all, the sentence comes back unchanged

> [!WARNING]
> `check_sentence_ending` is compared with `is True` / `is False`, so return a real boolean — `1` and `"yes"` fail. And strings are immutable: `sentence.strip()` on a line of its own changes nothing, you have to return (or reassign) the result.

## Exercism hints
### General

- [Python Documentation: String Methods][string-method-docs]
- [Python Documentation Tutorial: Text][tutorial-strings]

### 1. Capitalize the title of the paper

- You can use [string methods][title-method-docs] to capitalize the title properly.

### 2. Check if each sentence ends with a period

- You can use [string methods][endswith-method-docs] to check the ending of a string.

### 3. Clean up spacing

- You can use [string methods][strip-method-docs] to remove whitespace.

### 4. Replace words with a synonym

- You can use [string methods][replace-method-docs] to replace words.

[endswith-method-docs]: https://docs.python.org/3/library/stdtypes.html#str.endswith
[replace-method-docs]: https://docs.python.org/3/library/stdtypes.html#str.replace
[string-method-docs]: https://docs.python.org/3/library/stdtypes.html#string-methods
[strip-method-docs]: https://docs.python.org/3/library/stdtypes.html#str.strip
[title-method-docs]: https://docs.python.org/3/library/stdtypes.html#str.title
[tutorial-strings]: https://docs.python.org/3/tutorial/introduction.html#text

## Read first
- [string methods](https://docs.python.org/3/library/stdtypes.html#string-methods) — the whole list; every task here is one entry from it
- [`str.title()`](https://docs.python.org/3/library/stdtypes.html#str.title) — capitalises the first letter of each word, and lower-cases the rest
- [`str.endswith()`](https://docs.python.org/3/library/stdtypes.html#str.endswith) — returns a `bool`, and accepts a tuple of suffixes when you need several
- [`str.strip()`](https://docs.python.org/3/library/stdtypes.html#str.strip) — with no argument it removes whitespace from both ends; with one it removes *any combination* of the characters you pass
- [`str.replace()`](https://docs.python.org/3/library/stdtypes.html#str.replace) — every occurrence by default, or the first N if you pass a count
- [common sequence operations](https://docs.python.org/3/library/stdtypes.html#common-sequence-operations) — the indexing and slicing that `str` shares with `list` and `tuple`
- [strings and character data in Python (Real Python)](https://realpython.com/python-strings/) — the same methods with more worked examples
- [more string operations and functions (Programiz)](https://www.programiz.com/python-programming/string) — a short reference to skim

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Each of the four is a single call on the string you were handed, and the whole exercise is finding the right method name. You can use a [string method](https://docs.python.org/3/library/stdtypes.html#string-methods) to capitalise a title properly, another to check the ending of a string, another to remove whitespace and another to replace words. Open that page and read the names.
### Hint 2
The four you want are `title()`, `endswith()`, `strip()` and `replace()`.

Two details decide whether they work for you. First, `str` objects are immutable, so none of these methods edits the string in place — each returns a brand new one, and if you throw that return value away nothing happens. Second, `endswith()` already gives you `True` or `False`, so there is no `if` to write around it: return the call itself.

`replace()` takes the old substring and the new one, in that order, and quietly does nothing when the old one is absent — which is exactly the behaviour the "word not in the sentence" case wants.
### Hint 3
Different data, same four methods — tidying a log line before it goes into a report:

```python
line = "   nginx  ACCESS denied for 10.0.0.4   \n"
line.strip()                         # -> 'nginx  ACCESS denied for 10.0.0.4'
line.strip().endswith("10.0.0.4")    # -> True
line.strip().replace("ACCESS", "access")
# -> 'nginx  access denied for 10.0.0.4'
"weekly incident report".title()     # -> 'Weekly Incident Report'
```

Notice that `strip()` left the double space in the middle alone: it only ever works from the two ends inwards.
