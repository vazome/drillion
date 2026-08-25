---
title: dict.get — count without KeyError
minutes: 8
prereqs: []
tags: [data-structures]
---
# dict.get — count without KeyError

*Counting into a dict by hand — the KeyError that bites every beginner.*

## Why
A deploy log is a stream of action words: "deploy", "rollback",
"pod", "node". Your manager asks "how many of each happened this week?"
You need a tally: each distinct word and its count. Interviewers often
ask for this "without imports" to see whether you can handle the first
time a new word shows up, when there is no count to add to yet.

## You get
`words` — a list of strings like ["a", "b", "a"]. The test
creates it and hands it to you; you never build it yourself.

## You return
a plain dict mapping each word to how many times it
appeared.

## Rules
Count how many times each word appears. Return a plain dict.

```
["a", "b", "a"]  ->  {"a": 2, "b": 1}
```

Do it with a loop and a dict — no Counter here. This is the version
interviewers make you write when they say "without imports".

## Hints
### Hint 1
counts[word] += 1 explodes the first time a word appears, because += has to READ the old value before adding — and there isn't one yet.
### Hint 2
dict has a method that reads a key but returns a fallback instead of exploding when the key is missing. Look up `dict.get`.
### Hint 3
Different data, same shape:

```python
tally = {}
for c in 'hello':
    tally[c] = tally.get(c, 0) + 1
print(tally)     # {'h': 1, 'e': 1, 'l': 2, 'o': 1}
```

The 0 is what .get hands back when the key is new.
