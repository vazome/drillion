---
title: bob — classify a message into one of five replies
minutes: 10
prereqs: [200, 209]
tags: [exercism, conditionals, core]
source: exercism/python practice/bob (MIT, adapted)
---
# bob — classify a message into one of five replies

*bob — five canned replies, and the order you test the rules in.*

## Why
An out-of-hours chat widget answers with one of five canned
lines, and picking the right one is pure classification: shouted
question, shouted statement, plain question, silence, everything else.
The order you ask the questions in *is* the program — ask "is it a
question?" before "is it shouted?" and the combined case can never be
reached. Every routing rule and every alert filter you write later has
this exact shape, so it is worth getting the reflex now.

## You get
`message` — the text someone typed, e.g. "WATCH OUT!". It may
be empty, may be nothing but spaces, tabs or newlines, and may have
whitespace stuck on either end.

## You return
exactly one of five strings, spelled and punctuated as
below.

## Rules
Leading and trailing whitespace never counts — trim it first, then:

  - nothing left at all      ->  "Fine. Be that way!"
  - shouted AND a question   ->  "Calm down, I know what I'm doing!"
  - shouted                  ->  "Whoa, chill out!"
  - a question               ->  "Sure."
  - anything else            ->  "Whatever."

Shouted means: the text contains at least one letter and every letter
in it is upper case, so "1, 2, 3 GO!" is shouting but "1, 2, 3" is not.
A question means: after trimming, the text ends with "?".

```python
solve("WATCH OUT!")             ->  "Whoa, chill out!"
solve("WHAT'S GOING ON?")       ->  "Calm down, I know what I'm doing!"
solve("You are, what, like 15?")->  "Sure."
solve("\t\t\t")                 ->  "Fine. Be that way!"
```

## Read first
- https://docs.python.org/3/tutorial/controlflow.html#if-statements  — if / elif / else: the first branch that matches wins, the rest never run
- https://docs.python.org/3/library/stdtypes.html#str.isupper  — isupper(), and the detail that decides this exercise: it is False for text containing no letters at all
- https://docs.python.org/3/library/stdtypes.html#str.strip  — strip() and endswith()

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Hints
### Hint 1
Four tests and a default. Two of the four can be true at the same time — find that pair and make sure you answer it before you answer either one on its own, or the combined reply becomes unreachable code.
### Hint 2
Trim the message once at the top and use that trimmed copy for every test afterwards. One str method answers 'is this text upper case?' and returns False when the text has no letters at all — which is exactly what you want for '1, 2, 3'. Another answers 'does it end with this?'. Silence is just the trimmed text being empty.
### Hint 3
Different data, same shape — routing an HTTP request:

```python
if not body:                 return 'empty'
if method == 'POST' and is_json: return 'json upload'
if method == 'POST':         return 'form post'
if is_json:                  return 'json read'
return 'plain'
```

Swap the second and third lines and 'json upload' never fires again. Same trap, same fix: most specific case first.
