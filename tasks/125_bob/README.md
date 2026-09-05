---
title: conditionals — classify a message into one of five replies
difficulty: medium
tier: core
minutes: 10
prereqs: [5]
tags: [conditionals]
source: exercism/python practice/bob (MIT, adapted)
---
# conditionals — classify a message into one of five replies

*bob — five canned replies, and the order you test the rules in.*

## Read first
- [if statements](https://devdocs.io/python~3.14/tutorial/controlflow#if-statements) — if / elif / else: the first branch that matches wins, the rest never run
- [str.isupper()](https://devdocs.io/python~3.14/library/stdtypes#str.isupper) — `isupper()`, and the detail that decides this task: it is `False` for text containing no letters at all
- [str.strip()](https://devdocs.io/python~3.14/library/stdtypes#str.strip) — `strip()` and `endswith()`

*Adapted from [exercism/python](https://github.com/exercism/python) — MIT.*

## Why
An out-of-hours chat widget answers with one of five canned lines, and picking the right one is pure classification: shouted question, shouted statement, plain question, silence, everything else. The order you ask the questions in *is* the program — ask "is it a question?" before "is it shouted?" and the combined case can never be reached. Every routing rule and every alert filter you write later has this exact shape, so it is worth getting the reflex now.

## Introduction
Bob is a [lackadaisical][] teenager.
He likes to think that he's very cool.
And he definitely doesn't get excited about things.
That wouldn't be cool.

When people talk to him, his responses are pretty limited.

[lackadaisical]: https://www.collinsdictionary.com/dictionary/english/lackadaisical

## Instructions
Your task is to determine what Bob will reply to someone when they say something to him or ask him a question.

Bob only ever answers one of five things:

- **"Sure."**
  This is his response if you ask him a question, such as "How are you?"
  The convention used for questions is that it ends with a question mark.
- **"Whoa, chill out!"**
  This is his answer if you YELL AT HIM.
  The convention used for yelling is ALL CAPITAL LETTERS.
- **"Calm down, I know what I'm doing!"**
  This is what he says if you yell a question at him.
- **"Fine. Be that way!"**
  This is how he responds to silence.
  The convention used for silence is nothing, or various combinations of whitespace characters.
- **"Whatever."**
  This is what he answers to anything else.

## You get
`message` — the text someone typed, e.g. `"WATCH OUT!"`. It may be empty, may be nothing but spaces, tabs or newlines, and may have whitespace stuck on either end.

> [!NOTE]
> Exercism's stub is `def response(hey_bob)`. Here the function is `solve(message)`; nothing else about the task changes.

## You return
Exactly one of five strings, spelled and punctuated as below.

## Rules
Leading and trailing whitespace never counts — trim it first, then:

| the trimmed message is | reply |
| --- | --- |
| nothing at all | `"Fine. Be that way!"` |
| shouted AND a question | `"Calm down, I know what I'm doing!"` |
| shouted | `"Whoa, chill out!"` |
| a question | `"Sure."` |
| anything else | `"Whatever."` |

Shouted means: the text contains at least one letter and every letter in it is upper case, so `"1, 2, 3 GO!"` is shouting but `"1, 2, 3"` is not. A question means: after trimming, the text ends with `"?"`.

```python
solve("WATCH OUT!")              # -> "Whoa, chill out!"
solve("WHAT'S GOING ON?")        # -> "Calm down, I know what I'm doing!"
solve("You are, what, like 15?") # -> "Sure."
solve("\t\t\t")                  # -> "Fine. Be that way!"
```

> [!WARNING]
> The replies are compared character for character, full stop and exclamation mark included. `"Sure"` and `"sure."` both fail.

## Hints
### Hint 1
Four tests and a default. Two of the four can be true at the same time — find that pair and make sure you answer it before you answer either one on its own, or the combined reply becomes unreachable code.
### Hint 2
Trim the message once at the top and use that trimmed copy for every test afterwards. One `str` method answers 'is this text upper case?' and returns `False` when the text has no letters at all — which is exactly what you want for `'1, 2, 3'`. Another answers 'does it end with this?'. Silence is just the trimmed text being empty.
### Hint 3
Different data, same shape — routing an HTTP request:

```python
if not body:                     return 'empty'
if method == 'POST' and is_json: return 'json upload'
if method == 'POST':             return 'form post'
if is_json:                      return 'json read'
return 'plain'
```

Swap the second and third lines and 'json upload' never fires again. Same trap, same fix: most specific case first.
