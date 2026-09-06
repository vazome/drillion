---
title: list-methods — pick the rearrangements out of a word list
difficulty: medium
tier: core
minutes: 10
prereqs: [11, 18, 49]
tags: [list-methods]
source: exercism/python practice/anagram (MIT, adapted)
---
# list-methods — pick the rearrangements out of a word list

*anagram — same letters, different order: fingerprint a word and compare.*

## Read first
- [Sorting HOW TO](https://devdocs.io/python~3.14/howto/sorting) — `sorted()`, which turns any iterable into a list in a fixed order — including a string, character by character
- [More on lists](https://devdocs.io/python~3.14/tutorial/datastructures#more-on-lists) — list methods and list comprehensions, the shape this answer wants
- [collections.Counter](https://devdocs.io/python~3.14/library/collections#collections.Counter) — the other fingerprint: how many of each item
- [str.lower()](https://devdocs.io/python~3.14/library/stdtypes#str.lower) — the case fold that makes "Seton" comparable with "stone"

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
A daily word game ships a target word and a pile of guesses, and the server has to say which guesses are true rearrangements of it. Two rules trip people up: the comparison ignores capitals ("Silent" counts for "LISTEN") but the answer must give the guess back spelled exactly as it arrived, and a word is never an anagram of itself no matter how it is capitalised. The general skill is turning a value into a comparable fingerprint — the same move behind deduplicating records and grouping like with like.

## You get
`word` — the target word, e.g. `"listen"` — and `candidates`, a list of words to check:

```python
["enlists", "google", "inlets", "banana"]
```

> [!NOTE]
> Exercism's stub is `def find_anagrams(word, candidates)`. Here the function is `solve(word, candidates)`; nothing else about the task changes.

## You return
A list of the candidates that are anagrams of the target, in the order they appeared in `candidates`, each spelled exactly as it was given to you. No matches means an empty list.

## Rules
A candidate matches when it uses exactly the same letters as the target, each the same number of times — no letter left over on either side. Case is ignored when comparing. A candidate that *is* the target word (ignoring case) never counts.

```python
solve("stone", ["stone", "tones", "banana", "notes", "Seton"])
# -> ["tones", "notes", "Seton"]     ("stone" is itself, so it is out)
solve("good", ["dog", "goody"])
# -> []                              (subsets and supersets do not count)
solve("BANANA", ["Banana"])
# -> []
```

> [!WARNING]
> The result is compared with `==` against a list, so order matters: keep the candidates in the order they arrived, and return their original spelling, not the lower-cased one you compared with.

## Hints
### Hint 1
Two words are anagrams when they hold the same letters in the same quantities — order is exactly what you must stop caring about. So find a way to boil a word down to something that is equal for any rearrangement of it, then compare those. One extra rule then removes the target itself.
### Hint 2
`sorted(some_string)` gives you its characters in a fixed order, so any rearrangement produces the same list — lower-case the word first so capitals stop mattering. Compute the target's version once outside the loop, then keep each candidate whose version matches AND whose lower-cased spelling is not the target's. Keep the candidate's original spelling in what you return.
### Hint 3
Different data, same idea — grouping receipts that hold the same items:

```python
sorted(('milk', 'eggs')) == sorted(('eggs', 'milk'))   # -> True
```

`Counter` answers the same question and also keeps the counts, which is why it is the honest tool when duplicates matter:

```python
Counter('aab') == Counter('aba')  # -> True
Counter('aab') == Counter('ab')   # -> False
```
