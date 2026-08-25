---
title: generators — yield a filtered stream, lazily
minutes: 10
prereqs: []
tags: [core]
---
# generators — yield a filtered stream, lazily

*A generator hands over one item at a time, so a 10 GB log never lands in RAM.*

## Why
A log file on a production server is 10 GB. Support needs the
request ids of every failed request so they can look them up, and they
want the first one right away, not after the whole file has been read.
Loading the file into memory would crash the box. You need a way to hand
out results one at a time, reading only as far as needed for the next
answer.

## You get
`lines` — a stream of log lines like "api INFO req=a1", one
line per item, that you can walk through exactly once. The test creates
it and hands it to you; you never build it yourself.

## You return
not a list, but a generator: an object that hands out one
request id at a time, for ERROR lines only, doing the reading as it goes.

## Rules
Stream the request ids of the ERROR lines.

Each line looks like "<service> <LEVEL> req=<id>". Produce the <id> part
(a string) of every line whose LEVEL is ERROR, in order, nothing else.

```
["api INFO req=a1", "db ERROR req=b2", "api ERROR req=c3"]
->  yields "b2", then "c3"
```

What you return must be a generator, not a list. Two ways to make one: a
def with yield in its body, or a comprehension written with round brackets
instead of square ones.

The test checks with inspect.isgenerator, and it also checks that you are
lazy. It feeds you a stream that counts how many lines you pulled off it,
takes exactly one id from you, and then expects you to have read no
further than the line that id came from. Building a list first and yielding
from that fails the check even though the values would be right.

lines is any iterable of strings. Do not index it, do not call len on it,
just iterate it once.

## Hints
### Hint 1
A list comprehension does all the work up front and hands you the finished list; you cannot see item one until item ten thousand is done. A generator flips that: it does the least work needed to produce the next item, then stops and waits. Same values, different question — when does the work happen. On a log you are tailing, or a file bigger than memory, only one of the two is usable.
### Hint 2
Either write a def whose body loops over lines and yields the id when the level is ERROR — the moment a function contains yield anywhere, calling it runs none of the body and returns a generator instead. Or take the list comprehension you would have written and swap [ ] for ( ). For one line, line.split() gives the three fields; the id is the part of the third after the '='.
### Hint 3
Different data — even numbers, squared:

```python
def evens(nums):
    for n in nums:
        if n % 2 == 0:
            yield n * n

g = evens([1, 2, 3, 4])
print(g)          # <generator object evens at 0x...>  <- body not run yet
print(next(g))    # 4    <- only now does the loop start, and it stops again
print(list(g))    # [16] <- the 4 is already spent, a generator is one-shot

same = (n * n for n in [1, 2, 3, 4] if n % 2 == 0)   # identical, one line
```

Yours is the same shape: loop, test the level, yield the id.
