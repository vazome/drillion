---
title: set — second-highest distinct value
minutes: 8
prereqs: []
tags: [data-structures, rsample]
---
# set — second-highest distinct value

*Dedupe with a set — the runner-up trap.*

## Why
A performance review ranks people by score and the runner-up gets a
bonus. Two people tied for first. The naive "second item of the sorted
list" picks the other first-place person, not the real runner-up. The
business wants the second-highest distinct value, so duplicates have to
be treated as one value before picking. This is a well-known interview
trap.

## You get
`scores` — a list of numbers like [2, 3, 6, 6, 5], always with
at least two different values. The test creates it and hands it to you;
you never build it yourself.

## You return
one number: the second-highest value once duplicates are
ignored.

## Rules
Return the second-HIGHEST distinct score.

```
[2, 3, 6, 6, 5]  ->  5      (6 appears twice; it is still one value)
```

There are always at least two distinct values.

## Read first
- https://docs.python.org/3/tutorial/datastructures.html#sets  — what a set is, & | - operators
- https://realpython.com/python-sets/  — intersection() is what the take-home reranker used

> [!NOTE]
> **Take-home:** `query_words & content_words` in reranker.py

## Hints
### Hint 1
Sorting alone isn't enough: the top two slots can hold the same number twice. Duplicates have to disappear before you index anything.
### Hint 2
One built-in type refuses to hold duplicates. Convert, sort what's left, then pick a position.
### Hint 3
Different data, same shape:

```python
vals = [4, 9, 1, 9, 7]
uniq = sorted(set(vals))
print(uniq)        # [1, 4, 7, 9]
print(uniq[-2])    # 7  — second from the end
```

sorted() ascending plus a negative index, or reverse=True plus [1].
