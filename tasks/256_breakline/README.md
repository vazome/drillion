---
title: word break — cut a run-together name into parts you recognise
difficulty: hard
tier: advanced
minutes: 25
prereqs: [188, 252]
tags: [dynamic-programming, strings]
---
# word break — cut a run-together name into parts you recognise

*Taking the longest part you recognise is not the same as taking the longest part that leaves something you can still finish.*

## Read first
- [`str` slicing](https://devdocs.io/python~3.14/library/stdtypes#common-sequence-operations) — `run[i:i + size]`, the candidate part starting at `i`
- [`frozenset`](https://devdocs.io/python~3.14/library/stdtypes#frozenset) — membership in one step instead of a scan down the list
- [`functools.cache`](https://devdocs.io/python~3.14/library/functools#functools.cache) — remembering the answer for a position you have already asked about
- [`range()` counting down](https://devdocs.io/python~3.14/library/functions#func-range) — `range(n, 0, -1)`, for trying the longest candidate first

## Why
An old system names its machines by gluing words together and nobody kept the separator: `logserver`, `webhookqueue`, `apicachenodes`. You have the vocabulary — the list of parts the naming convention was ever allowed to use — and you want the names split back apart so a report can group by role. The obvious pass takes the longest part you recognise at each position and moves on, and it is wrong in a way that looks right for weeks: `logserver` starts with `logs`, so the pass eats four characters and is left staring at `erver`, and reports the name as unrecognised. The name was fine. The greedy choice was not, and undoing it is the whole problem.

## You get
- `run` — one machine name, a non-empty `str` of lowercase letters with no separators, e.g. `"logserver"`.
- `parts` — the vocabulary, a list of non-empty lowercase `str`. Parts may be prefixes of each other, and a part may be used as many times as you like, or not at all. The list may be empty.

## You return
a `list` of the parts `run` is made of, in order, or `[]` when it cannot be made of them at all.

## Rules
The parts you return, joined back together with nothing between them, have to be exactly `run`.

- Every part you return has to be in `parts`. Repeats are fine.
- When no combination of parts spells `run`, return `[]`. An empty `parts` is always `[]`.
- **Ties are decided for you.** A name can often be cut more than one way, so one rule makes it a single answer: **take the longest part you can that still leaves a remainder you can finish**, and then apply the same rule to that remainder.

```python
solve("logserver", ["log", "logs", "server"])           # -> ['log', 'server']
solve("applepenapple", ["apple", "pen"])                # -> ['apple', 'pen', 'apple']
solve("cars", ["car", "ca", "rs"])                      # -> ['ca', 'rs']
solve("catsandog", ["cats", "dog", "sand", "and", "cat"])  # -> []
```

> [!WARNING]
> Longest match with no way back is the near-miss, and it is the answer most people submit. On `"logserver"` it takes `logs` and gives up; on `"cars"` it takes `car` and gives up. The tie rule says longest *that still leaves something finishable*, which is not a choice you can make looking at one position alone. Both of those names are in the test.

> [!NOTE]
> The remainder after a cut depends only on where you are, never on how you got there, so the same position gets asked about again and again down different paths. On the generated names that is the difference between instant and hopeless.

## Hints
### Hint 1
Ask it from a position rather than about the whole name: *can `run[i:]` be cut, and if so, how?* Reaching the end of `run` is a success with nothing left to cut, and that is the entire stop condition. Anything else tries each part that `run[i:]` starts with.
### Hint 2
Try the candidates at a position from longest down to shortest, and for each one that is in the vocabulary, ask the same question at `i + len(candidate)`. If that answer exists, you are done — the first success you find is the one the tie rule wants. If it does not, keep shrinking. Running out of candidates means this position cannot be cut, and that is a real answer worth remembering, so distinguish "cannot be cut" from "cut into nothing": `None` and `()` are not the same thing.
### Hint 3
The same shape on a smaller vocabulary, written so the failure has its own value:

```python
from functools import cache

def split(text, words):
    known = frozenset(words)
    longest = max((len(w) for w in known), default=0)

    @cache
    def at(i):
        if i == len(text):
            return ()
        for size in range(min(longest, len(text) - i), 0, -1):
            head = text[i:i + size]
            if head in known and (rest := at(i + size)) is not None:
                return (head, *rest)
        return None

    return list(at(0) or ())

split("queuestore", ["queue", "queues", "store"])   # ['queue', 'store']
split("queuestory", ["queue", "queues", "store"])   # []
```

`at` returns a tuple because `@cache` hands the same object to every caller asking the same question, and a list one caller mutates poisons the answer for the next.
