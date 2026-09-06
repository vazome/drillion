---
title: string-methods — the essay clean-up pass
difficulty: medium
tier: core
minutes: 12
prereqs: [10]
tags: [string-methods]
source: exercism/python concept/little-sisters-essay (MIT, adapted)
---
# string-methods — the essay clean-up pass

*`title()`, `endswith()`, `strip()`, `replace()` — four methods, four one-liners.*

## Read first
- [string methods](https://devdocs.io/python~3.14/library/stdtypes#string-methods) — the whole list; every task here is one entry from it
- [`str.title()`](https://devdocs.io/python~3.14/library/stdtypes#str.title) — capitalises the first letter of each word, and lower-cases the rest
- [`str.endswith()`](https://devdocs.io/python~3.14/library/stdtypes#str.endswith) — returns a `bool`, and accepts a tuple of suffixes when you need several
- [`str.strip()`](https://devdocs.io/python~3.14/library/stdtypes#str.strip) — with no argument it removes whitespace from both ends; with one it removes *any combination* of the characters you pass
- [`str.replace()`](https://devdocs.io/python~3.14/library/stdtypes#str.replace) — every occurrence by default, or the first N if you pass a count
- [common sequence operations](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — the indexing and slicing that `str` shares with `list` and `tuple`
- [strings and character data in Python (Real Python)](https://realpython.com/python-strings/) — the same methods with more worked examples
- [more string operations and functions (Programiz)](https://www.programiz.com/python-programming/string) — a short reference to skim

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
The boring half of every text pipeline is normalisation: trim the whitespace an editor left behind, check that a line really ends the way you assumed, title-case a heading for a report, swap one token for another. Your sister's essay needs exactly that pass before the teacher reads it, and so does every CSV column, every log line and every YAML value you will ever parse. The lesson is not that these are hard — it is that Python already ships all four, so hand-writing a loop to strip spaces is a code review comment waiting to happen.

## You get
Nothing. `solve()` takes **no arguments**; it hands the grader your four finished functions and the grader supplies the titles and sentences. This task covers all four Exercism tasks.

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

## Hints
### Hint 1
Each of the four is a single call on the string you were handed, and the whole task is finding the right method name. You can use a [string method](https://devdocs.io/python~3.14/library/stdtypes#string-methods) to capitalise a title properly, another to check the ending of a string, another to remove whitespace and another to replace words. Open that page and read the names.
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
