---
title: list-methods — pick the rearrangements out of a word list
difficulty: medium
tier: core
minutes: 10
prereqs: [88, 89, 92, 95, 96, 97, 99, 101]
tags: [list-methods]
source: exercism/python practice/anagram (MIT, adapted)
---
# list-methods — pick the rearrangements out of a word list

*anagram — same letters, different order: fingerprint a word and compare.*

## Why
A daily word game ships a target word and a pile of guesses, and the server has to say which guesses are true rearrangements of it. Two rules trip people up: the comparison ignores capitals ("Silent" counts for "LISTEN") but the answer must give the guess back spelled exactly as it arrived, and a word is never an anagram of itself no matter how it is capitalised. The general skill is turning a value into a comparable fingerprint — the same move behind deduplicating records and grouping like with like.

## Introduction
At a garage sale, you find a lovely vintage typewriter at a bargain price!
Excitedly, you rush home, insert a sheet of paper, and start typing away.
However, your excitement wanes when you examine the output: all words are garbled!
For example, it prints "stop" instead of "post" and "least" instead of "stale."
Carefully, you try again, but now it prints "spot" and "slate."
After some experimentation, you find there is a random delay before each letter is printed, which messes up the order.
You now understand why they sold it for so little money!

You realize this quirk allows you to generate anagrams, which are words formed by rearranging the letters of another word.
Pleased with your finding, you spend the rest of the day generating hundreds of anagrams.

## Instructions
Given a target word and one or more candidate words, your task is to find the candidates that are anagrams of the target.

An anagram is a rearrangement of letters to form a new word: for example `"owns"` is an anagram of `"snow"`.
A word is _not_ its own anagram: for example, `"stop"` is not an anagram of `"stop"`.

The target word and candidate words are made up of one or more ASCII alphabetic characters (`A`-`Z` and `a`-`z`).
Lowercase and uppercase characters are equivalent: for example, `"PoTS"` is an anagram of `"sTOp"`, but `"StoP"` is not an anagram of `"sTOp"`.
The words you need to find should be taken from the candidate words, using the same letter case.

Given the target `"stone"` and the candidate words `"stone"`, `"tones"`, `"banana"`, `"tons"`, `"notes"`, and `"Seton"`, the anagram words you need to find are `"tones"`, `"notes"`, and `"Seton"`.

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

## Read first
- [Sorting HOW TO](https://docs.python.org/3/howto/sorting.html) — `sorted()`, which turns any iterable into a list in a fixed order — including a string, character by character
- [More on lists](https://docs.python.org/3/tutorial/datastructures.html#more-on-lists) — list methods and list comprehensions, the shape this answer wants
- [collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter) — the other fingerprint: how many of each item
- [str.lower()](https://docs.python.org/3/library/stdtypes.html#str.lower) — the case fold that makes "Seton" comparable with "stone"

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

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
