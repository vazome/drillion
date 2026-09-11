---
title: longest common subsequence — what two releases still have in common
difficulty: hard
tier: advanced
minutes: 28
prereqs: [143, 188]
tags: [dynamic-programming, sequences]
source: TheAlgorithms/Python dynamic_programming/longest_common_subsequence.py (MIT, adapted)
---
# longest common subsequence — what two releases still have in common

*Two ordered lists, one answer: the longest run of steps that survives in both, in the same order, without having to be next to each other.*

## Read first
- [`len()` and sequences](https://devdocs.io/python~3.14/library/stdtypes#sequence-types-list-tuple-range) — the two lists you are comparing, and why order is the whole problem
- [`functools.cache`](https://devdocs.io/python~3.14/library/functools#functools.cache) — remembering an answer for a pair of positions you have already asked about
- [Tuples](https://devdocs.io/python~3.14/library/stdtypes#tuple) — a small immutable result you can build up and hand back

## Why
A release pipeline is an ordered list of steps, and the next release rewrites some of it: steps get dropped, new ones get inserted, a couple get moved. Before you sign the change off you want the honest answer to one question — what is still the same? Not "which step names appear in both", because a step that moved from before the migration to after it is a different pipeline even though the name is unchanged. What you want is the longest run of steps that appears in both, in the same order. That backbone is the part you already trust; everything either side of it is the part that needs reading. The same question is behind every diff you have ever looked at.

## You get
- `old` — the previous pipeline, a list of step names as `str`, in the order they ran, e.g. `["checkout", "build", "test", "deploy"]`.
- `new` — the current pipeline, the same shape. Names may repeat in either list, and either list may be empty.

## You return
a `list` of the step names that appear in both, in order — the longest such list there is.

## Rules
A step name may only be used once, and the names you return have to appear in that order in `old` and in that order in `new`.

- Both lists empty, or nothing at all in common, is `[]`.
- The lists are not the same length and neither is a prefix of the other.
- **Ties are decided for you.** More than one longest answer usually exists, so two rules make it a single one:
  - when the next name in `old` equals the next name in `new`, take it;
  - otherwise you either skip the next name in `old` or the next name in `new`, and when both choices lead to an equally long answer, **skip the one in `old`**.

```python
solve(["checkout", "build", "test", "deploy"],
      ["checkout", "lint", "build", "deploy"])     # -> ['checkout', 'build', 'deploy']
solve(["a", "b", "c"], ["c", "b", "a"])            # -> ['c']  (one name, and the tie rule picks which)
solve(["build"], [])                               # -> []
```

> [!WARNING]
> `[s for s in old if s in set(new)]` is not this. It keeps every shared name, in `old`'s order, and order is exactly what the question is about — on `["a", "b", "c"]` against `["c", "b", "a"]` it claims all three survived when the honest answer is one name long. The test compares against lists that were deliberately reordered, so that answer fails on the second case it sees.

> [!NOTE]
> Two nested loops over both lists is a few hundred steps. The plain recursion with no memory is two branches per step, which on the generated inputs does not finish. Cache on the pair of positions.

## Hints
### Hint 1
Ask the question from a pair of positions rather than about the whole list: *what is the longest shared run of `old[i:]` and `new[j:]`?* Running off the end of either list is the empty answer, and that is the whole stop condition.
### Hint 2
Two cases. If `old[i] == new[j]`, that name is in the answer and the rest of the answer is the same question asked at `(i + 1, j + 1)`. If they differ, one of them is not in the answer, so take the longer of `(i + 1, j)` and `(i, j + 1)` — and `>=` rather than `>` when you compare their lengths is what implements "skip the one in `old`".
### Hint 3
Same shape on characters instead of names:

```python
from functools import cache

def shared(a, b):
    @cache
    def best(i, j):
        if i == len(a) or j == len(b):
            return ()
        if a[i] == b[j]:
            return (a[i], *best(i + 1, j + 1))
        skip_a, skip_b = best(i + 1, j), best(i, j + 1)
        return skip_a if len(skip_a) >= len(skip_b) else skip_b
    return "".join(best(0, 0))

shared("programming", "gaming")     # 'gaming'
shared("physics", "smartphone")     # 'ph'
```

The cached function returns a tuple rather than a list, because `@cache` hands the same object back to every caller that asks the same question and a list one caller mutates would poison the answer for the next.

---
Adapted from TheAlgorithms/Python — MIT
