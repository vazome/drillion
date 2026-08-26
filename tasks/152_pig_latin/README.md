---
title: conditionals — translate English into a children's code
difficulty: medium
tier: core
minutes: 15
prereqs: [88, 89, 92]
tags: [conditionals]
source: exercism/python practice/pig-latin (MIT, adapted)
---
# conditionals — translate English into a children's code

*pig-latin — four rewrite rules, applied in the right order, to every word in a line.*

## Why
This is a rewrite engine in miniature, and rewrite engines are everywhere in operations: nginx rewrite rules, log scrubbers that mask secrets, slug generators that turn a title into a URL. They all share the same failure mode — several rules match the same input, and the answer depends entirely on which one you let win. Here the rules are small enough to hold in your head, so you can practise the part that actually bites: reading a specification as an ordered list of cases, and writing code where the order is visible instead of accidental.

## Introduction
Your parents have challenged you and your sibling to a game of two-on-two basketball.
Confident they'll win, they let you score the first couple of points, but then start taking over the game.
Needing a little boost, you start speaking in [Pig Latin][pig-latin], which is a made-up children's language that's difficult for non-children to understand.
This will give you the edge to prevail over your parents!

[pig-latin]: https://en.wikipedia.org/wiki/Pig_latin

## Instructions
Your task is to translate text from English to Pig Latin.
The translation is defined using four rules, which look at the pattern of vowels and consonants at the beginning of a word.
These rules look at each word's use of vowels and consonants:

- vowels: the letters `a`, `e`, `i`, `o`, and `u`
- consonants: the other 21 letters of the English alphabet

### Rule 1

If a word begins with a vowel, or starts with `"xr"` or `"yt"`, add an `"ay"` sound to the end of the word.

For example:

- `"apple"` -> `"appleay"` (starts with vowel)
- `"xray"` -> `"xrayay"` (starts with `"xr"`)
- `"yttria"` -> `"yttriaay"` (starts with `"yt"`)

### Rule 2

If a word begins with one or more consonants, first move those consonants to the end of the word and then add an `"ay"` sound to the end of the word.

For example:

- `"pig"` -> `"igp"` -> `"igpay"` (starts with single consonant)
- `"chair"` -> `"airch"` -> `"airchay"` (starts with multiple consonants)
- `"thrush"` -> `"ushthr"` -> `"ushthray"` (starts with multiple consonants)

### Rule 3

If a word starts with zero or more consonants followed by `"qu"`, first move those consonants (if any) and the `"qu"` part to the end of the word, and then add an `"ay"` sound to the end of the word.

For example:

- `"quick"` -> `"ickqu"` -> `"ickquay"` (starts with `"qu"`, no preceding consonants)
- `"square"` -> `"aresqu"` -> `"aresquay"` (starts with one consonant followed by `"qu`")

### Rule 4

If a word starts with one or more consonants followed by `"y"`, first move the consonants preceding the `"y"`to the end of the word, and then add an `"ay"` sound to the end of the word.

Some examples:

- `"my"` -> `"ym"` -> `"ymay"` (starts with single consonant followed by `"y"`)
- `"rhythm"` -> `"ythmrh"` -> `"ythmrhay"` (starts with multiple consonants followed by `"y"`)

## You get
`text` — one line of English, lower case, letters and single spaces only:

```python
"quick fast run"
```

It is one word or several. There is no punctuation, no upper case and no empty input.

> [!NOTE]
> Exercism's stub is `def translate(text)`. Here the function is `solve(text)`; nothing else about the task changes.

## You return
A `str`: the same words in the same order, each one translated, joined by single spaces.

```python
solve("pig")             # -> "igpay"
solve("quick fast run")  # -> "ickquay astfay unray"
```

## Rules
Split the line on whitespace, translate each word on its own, then join with `" "`. A word never changes length by more than the two letters `ay` plus the moved prefix.

The four rules overlap, so read them as an ordered list and let the first match win:

| the word starts with | example | becomes | why |
| --- | --- | --- | --- |
| a vowel | `equal` | `equalay` | rule 1 |
| `xr` or `yt` | `xray`, `yttria` | `xrayay`, `yttriaay` | rule 1 — these two pairs sound like vowels |
| consonants then `qu` | `square` | `aresquay` | rule 3 — the `u` travels with the `q` |
| consonants then `y` | `rhythm` | `ythmrhay` | rule 4 — `y` acts as the vowel |
| any other consonant run | `thrush` | `ushthray` | rule 2 |

- `y` is a consonant when it is the first letter and a vowel anywhere after that: `yellow` -> `ellowyay`, but `my` -> `ymay`
- `q` on its own, with no `u` after it, is just a consonant: `qat` -> `atqay`
- a `qu` that is not at the front is left alone: `liquid` -> `iquidlay`

```python
solve("xenon")    # -> "enonxay"
solve("yellow")   # -> "ellowyay"
solve("qat")      # -> "atqay"
solve("liquid")   # -> "iquidlay"
solve("school")   # -> "oolschay"
```

> [!WARNING]
> Checking "is the first letter a vowel?" before checking `xr`/`yt` is fine, but checking the plain consonant run before the `qu` rule is not: `square` would become `uaresqay` instead of `aresquay`. The `qu` case has to be tested first.

## Read first
- [str.split() and str.join()](https://docs.python.org/3/library/stdtypes.html#str.split) — the "split, map, join" shape that every line-of-words task uses
- [str.startswith()](https://docs.python.org/3/library/stdtypes.html#str.startswith) — accepts a tuple, so one call can test several prefixes
- [Slicing](https://docs.python.org/3/reference/expressions.html#slicings) — `word[n:] + word[:n]` is the whole of rule 2 once you know `n`
- [re.match()](https://docs.python.org/3/library/re.html#re.match) — optional: one anchored pattern with alternatives can express the ordering directly

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Write the one-word translator first and only wrap it in `split`/`join` at the very end — mixing the two makes both harder. For the single word, the whole job is finding one number: how many letters move from the front to the back. Rule 1 is that number being zero; every other rule is a different way of counting the prefix.
### Hint 2
Handle the vowel-sound cases first, because they are a flat list of prefixes to test. Then walk the word from the left while the letter is a consonant, and stop — but with two corrections built into the walk: if the letter you just passed was `q` and the next one is `u`, take the `u` as well; and treat `y` as a stopping point rather than a consonant unless it is the very first letter. When the walk ends at position `n`, the answer is the tail, then the head, then `ay`. Test `my`, `rhythm`, `yellow` and `square` by hand before you run anything — those four cover every corner.
### Hint 3
Different data, same "ordered rules, first match wins" shape — masking secrets in a log line:

```python
def mask(field):
    if field.startswith(('AKIA', 'ASIA')):
        return 'AWS_KEY'
    if field.startswith('eyJ'):
        return 'JWT'
    if field.isdigit() and len(field) == 16:
        return 'CARD'
    return field

mask('AKIAIOSFODNN7EXAMPLE')  # -> 'AWS_KEY'
mask('hello')                 # -> 'hello'
```

The rules are written in the order the specification lists them, each one returns immediately, and the fallback sits at the bottom. Reordering those three `if`s changes the output — which is exactly the trap in this task.
