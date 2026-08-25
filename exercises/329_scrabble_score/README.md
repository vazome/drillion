---
title: scrabble-score — add up a word's letter values
minutes: 15
prereqs: [200, 215, 218, 221, 227, 236]
tags: [exercism, regular-expressions, core]
source: exercism/python practice/scrabble-score (MIT, adapted)
---
# scrabble-score — add up a word's letter values

*scrabble-score — a lookup table, a case fold, and one `sum`.*

## Why
"Score this thing by summing a per-item weight" is a whole genre: a risk score for a pull request, a cost estimate from a bill of materials, a priority number built from a set of labels, a relevance score for a search hit. The interesting decision is never the addition — it is where the weights live. Written as a chain of `if` statements they are unreadable and unchangeable; written as a table they are data, and data can be swapped for a different language, loaded from a file, or reviewed by someone who does not read Python. This drill is the smallest possible version of that choice.

## Introduction
[Scrabble][wikipedia] is a word game where players place letter tiles on a board to form words.
Each letter has a value.
A word's score is the sum of its letters' values.

[wikipedia]: https://en.wikipedia.org/wiki/Scrabble

## Instructions
Your task is to compute a word's Scrabble score by summing the values of its letters.

The letters are valued as follows:

| Letter                       | Value |
| ---------------------------- | ----- |
| A, E, I, O, U, L, N, R, S, T | 1     |
| D, G                         | 2     |
| B, C, M, P                   | 3     |
| F, H, V, W, Y                | 4     |
| K                            | 5     |
| J, X                         | 8     |
| Q, Z                         | 10    |

For example, the word "cabbage" is worth 14 points:

- 3 points for C
- 1 point for A
- 3 points for B
- 3 points for B
- 1 point for A
- 2 points for G
- 1 point for E

## You get
`word` — a single word of ASCII letters, in any mix of upper and lower case, possibly empty:

```python
"OxyphenButazone"
```

> [!NOTE]
> Exercism's stub is `def score(word)`. Here the function is `solve(word)`; nothing else about the task changes.

## You return
An `int` — the sum of the values of the word's letters. The empty string scores `0`.

## Rules
- case does not matter: `"a"` and `"A"` are both worth 1
- the score is the plain sum of every letter's value, with repeats counted every time
- the empty string scores `0`, because there is nothing to add up

```python
solve("a")                # -> 1
solve("f")                # -> 4
solve("at")               # -> 2
solve("zoo")              # -> 12
solve("quirky")           # -> 22
solve("OxyphenButazone")  # -> 41
solve("")                 # -> 0
```

> [!WARNING]
> Do not hard-code the seven groups as seven `if` branches. The grader will not catch you, but the whole point of the drill is the table — and the version with the table is the one you can still read next month.

## Read first
- [Mapping types: dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict) — a letter-to-value table is a dict, and lookup is the operation it is fastest at
- [sum()](https://docs.python.org/3/library/functions.html#sum) — adding up an iterable, including a generator expression, in one call
- [str.lower()](https://docs.python.org/3/library/stdtypes.html#str.lower) — fold the case once at the top rather than at every lookup
- [dict.get()](https://docs.python.org/3/library/stdtypes.html#dict.get) — a default instead of a `KeyError` when a character is not in the table
- [re.findall()](https://docs.python.org/3/library/re.html#re.findall) — the regular-expressions route, if you want to pick out the scoring characters by pattern

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
The instructions group letters by value because that is how a rule book reads, but that is not how your code will ask the question. Your code asks it one letter at a time: "what is *this* letter worth?" Write down the shape that answers that in one step, and then decide how to build it from the seven groups without typing twenty-six lines by hand.

### Hint 2
Build the table once, above the function, so it is not rebuilt on every call. You can spell out all twenty-six entries, or you can start from the seven groups and invert them the way the `etl` drill does — a small loop over `{1: "AEIOULNRST", 2: "DG", ...}` fills a dict of letter to value in a few lines. Then the function itself is three moves: fold the word to one case, look up each character, add the results. `sum` with a generator expression does the last two together, and an empty word makes `sum` return `0` on its own with no special case.

### Hint 3
Different data, same weight-table sum — costing a shopping basket from a price list:

```python
PRICES = {'apple': 3, 'bread': 2, 'cheese': 7}

def basket_cost(items):
    return sum(PRICES.get(item, 0) for item in items)

basket_cost(['apple', 'cheese', 'apple'])   # -> 13
basket_cost([])                             # -> 0
```

The weights are data in one place, the function is one `sum` over a lookup, and the empty case falls out for free. Changing a price is a one-character edit, not a code change.
