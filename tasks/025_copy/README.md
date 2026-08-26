---
title: shallow vs deep copy — predict the damage
minutes: 6
prereqs: []
tags: [data-structures]
---
# shallow vs deep copy — predict the damage

*One shared inner list has silently corrupted many config-cloning scripts.*

## Why
A classic interview question and a real production bug. A script takes the base config for one environment, copies it to make a second one, and edits the copy. Weeks later someone notices the ORIGINAL config changed too: a server added to staging showed up in prod. The copy only duplicated the outer container; the lists inside were still shared between both. You are asked to predict, line by line, which edits leak into which dict.

## You get
`cfg` — a dict with two keys, like

```python
{"servers": ["web-1", "db-2"], "ports": [80, 443]}
```

The test creates it and hands it to you; you never build it yourself.

## You return
a tuple of three dicts `(cfg, shallow, deep)` showing what each one looks like AFTER the snippet in the rules below has run. You work out the answer in your head and build the three dicts by hand.

## Rules
Predict, without running it, what this snippet leaves behind:

```python
import copy
shallow = cfg.copy()
deep = copy.deepcopy(cfg)
shallow["servers"].append("web-9")
shallow["region"] = "eu"
deep["ports"].append(9999)
```

`cfg` always has exactly two keys: `"servers"` (a list of names) and `"ports"` (a list of ints). Return a tuple `(cfg, shallow, deep)` — the three dicts as they look AFTER the snippet runs.

Build the three results by hand from the `cfg` you were given. The point is deciding which of the three mutations leaks where.

## Hints
### Hint 1
`cfg.copy()` copies only the outer dict — the lists inside are the very same objects, now reachable from two dicts. `deepcopy` clones all the way down. For each of the three mutations, ask: which actual object does this line touch, and who else can see that object.
### Hint 2
`shallow['servers']` is the same list object as `cfg['servers']`, so an append through one shows through the other. Assigning a brand-new key on `shallow` touches only the outer dict, which is NOT shared. `deep` shares nothing at all. Now apply that to the three lines.
### Hint 3
Different data, same mechanics:

```python
import copy
a = {'x': [1, 2]}
b = a.copy()
c = copy.deepcopy(a)
b['x'].append(3)
print(a)   # {'x': [1, 2, 3]}   b's append leaked into a
print(b)   # {'x': [1, 2, 3]}
print(c)   # {'x': [1, 2]}      the deep copy stayed clean
```

Same reasoning here, just three mutations instead of one.
