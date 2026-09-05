---
title: recursion — recursive diff of two nested configs
difficulty: medium
tier: core
minutes: 30
prereqs: [2, 9]
tags: [recursion]
---
# recursion — recursive diff of two nested configs

*Whole-task task: what changed between two configs, at any depth.*

Combines topics 30 (nested dicts from JSON), 18 (dict lookups), 25 (copy).

## Read first
- [Mapping Types — dict](https://devdocs.io/python~3.14/library/stdtypes#mapping-types-dict) — the operations a recursive walk leans on

## Why
The staging environment works and production does not. Both were deployed from a config file, and someone on the platform team asks "what exactly is different between the two?" Reading two long files side by side by eye is slow and error-prone; a short list of added, removed and changed settings is what they want.

## You get
`old` — a nested dictionary (a dictionary whose values can themselves be dictionaries), like `{"replicas": 2, "db": {"host": "a"}}`. This is the config from the first environment.

`new` — the same kind of dictionary, from the second environment. The test builds both and hands them to you; you never build them yourself.

## You return
one dictionary with three keys: `"added"`, `"removed"` and `"changed"`. Each holds a dictionary of setting paths (like `"db.pool"`) and the values involved. All three keys are always present, even when there is nothing to list under one of them.

## Rules
Two configs came out of two environments. Report the difference.

`old` and `new` are nested dicts. Return exactly this shape, with dotted paths as keys:

```python
old = {"replicas": 2, "db": {"host": "a", "pool": 5}}
new = {"replicas": 3, "db": {"host": "a"}, "tls": True}

solve(old, new)
# -> {"added":   {"tls": True},
#     "removed": {"db.pool": 5},
#     "changed": {"replicas": (2, 3)}}
```

Rules:

| where the key turns up | it lands under | mapped to |
| --- | --- | --- |
| only in `new` | `"added"` | the new value |
| only in `old` | `"removed"` | the old value |
| in both, but different | `"changed"` | the tuple `(old_value, new_value)` |

- When both sides hold a dict, walk into it. Otherwise compare the values as they are, so a dict replaced by a string is one changed entry, not a subtree of them.
- Paths join keys with a dot. Top-level keys carry no dot.
- All three keys are always in the result, empty dict when nothing landed there.

> [!WARNING]
> Do not modify `old` or `new`. The test checks that.

> [!TIP]
> This is config drift, and it is a real on-call question. Narrate the walk out loud as you write it.

## Hints
### Hint 1
The input has the same shape at every level, so the code should too: a function that handles one level and calls itself for the next. The part people miss is the path — each level has to hand the prefix down, or you end up with bare key names and no idea where they came from.
### Hint 2
Write a helper walk(a, b, prefix) that appends into three dicts from the enclosing scope. For each key in a: missing from b means removed; both values dicts (isinstance(v, dict)) means recurse with prefix + key + '.'; otherwise compare with != and record the pair. Then a second small loop over b for the keys a never had. Read values, never assign into old or new.
### Hint 3
Different data — carrying a prefix down a recursive walk:

```python
def walk(d, prefix=''):
    for k, v in d.items():
        if isinstance(v, dict):
            walk(v, prefix + k + '.')
        else:
            print(prefix + k, '=', v)
walk({'a': 1, 'b': {'c': 2, 'd': {'e': 3}}})
# a = 1
# b.c = 2
# b.d.e = 3
```

Yours walks two dicts side by side instead of one, and records instead of printing.
