---
title: difflib — a unified diff of two config versions, and a guess at the misspelt key
difficulty: medium
tier: core
minutes: 15
prereqs: [74]
tags: [files-text, stdlib-ops]
---
# difflib — a unified diff of two config versions, and a guess at the misspelt key

*`unified_diff` produces the `---`/`+++`/`@@` output every code review reads, and `get_close_matches` turns "no such key" into "did you mean".*

## Read first
- [`difflib`](https://devdocs.io/python~3.14/library/difflib) — the module and the several diffs it offers
- [`difflib.unified_diff`](https://devdocs.io/python~3.14/library/difflib#difflib.unified_diff) — the generator, its filenames and `lineterm`
- [`difflib.get_close_matches`](https://devdocs.io/python~3.14/library/difflib#difflib.get_close_matches) — `n` and `cutoff`

## Why
The deploy tool refuses a config change it does not understand, and the two things an operator needs at that moment are the same two things a reviewer needs: what actually changed between the running config and the proposed one, and — when they asked for a key that is not there — which key they probably meant. Printing both files side by side and letting the human find the difference is what people do when they have not met `difflib`, and it does not scale past twenty lines. Printing "unknown key: retrys" and stopping is technically true and wastes ten minutes of somebody's evening.

## You get
- `old` and `new`, each a list of config lines in `key = value` form. Every line ends with `\n`, the way `readlines()` hands them over.
- `wanted`, the key an operator asked for, possibly misspelt.

## You return
a tuple `(diff, suggestion)`.

- `diff` is a **list** of the unified-diff lines comparing `old` to `new`, labelled `config.old` and `config.new`.
- `suggestion` is the single closest key in `new` to `wanted`, as a string — or `None` when nothing is close enough.

## Rules
- The lines keep their trailing newlines all the way through the diff. Stripping them first produces output that runs together into one line and is the most common way this goes wrong.
- The diff is a list, not the generator you get back. Return it materialised.
- `fromfile` is `config.old` and `tofile` is `config.new`. Leave the context size alone.
- `suggestion` is one string or `None`, never a list, and never the empty string. A key spelt exactly right suggests itself.
- A key is the text before the first ` = ` on a line of `new`.

```python
old = ["retries = 3\n", "timeout = 30\n"]
new = ["retries = 5\n", "timeout = 30\n"]
diff, suggestion = solve(old, new, "retrys")
diff[:3]    # -> ['--- config.old\n', '+++ config.new\n', '@@ -1,2 +1,2 @@\n']
suggestion  # -> 'retries'
```

> [!NOTE]
> `get_close_matches` returns a list, ordered best first, and an **empty** list when nothing clears the similarity cutoff. Both of those have to become the one value you return.

## Hints
### Hint 1
`difflib.unified_diff` is a generator. `list(...)` around the call is the whole of "materialise it", and the `fromfile=` and `tofile=` keywords are what fill in the `---` and `+++` header lines.
### Hint 2
`lineterm` defaults to `'\n'`, which is correct when your input lines already end in `\n` — the header lines get one and the content lines keep theirs. That is why the newlines must not be stripped.
### Hint 3
Turning the match list into an answer:

```python
import difflib

keys = ["retries", "timeout", "endpoint"]
difflib.get_close_matches("retrys", keys, n=1)     # -> ['retries']
difflib.get_close_matches("banana", keys, n=1)     # -> []
```

`n=1` asks for at most one. What comes back is still a list, so index it only after checking that there is something in it.
