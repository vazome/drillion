---
title: pathlib.Path — walk and inspect a tree
difficulty: medium
tier: core
minutes: 12
prereqs: []
tags: [files-text]
---
# pathlib.Path — walk and inspect a tree

*pathlib turns path string-surgery into readable code — and interviewers notice.*

## Why
A company keeps one folder per service on a shared server, each with its own log and config subfolders. Before a migration the platform team asks for an inventory: the name of every log file anywhere under the root, the name (minus extension) of every config file, and whether someone already wrote a README at the top. Chopping path strings by hand is error-prone; you need to walk the whole tree and ask questions about each path.

## You get
`root` — a string with the path to the top folder, like `"/tmp/ex027_xyz"`. The test builds a small tree of folders and files under it and hands you the path; you never build it yourself.

## You return
a dict with three keys: `"logs"` (sorted list of log file names), `"conf_stems"` (sorted list of config file names without the extension) and `"has_readme"` (`True` or `False`).

## Rules
`root` is a directory path as a STRING. The tree under it looks like:

```text
root/
  api/
    logs/api-0.log
    conf/api.conf
    notes.txt
  web/
    logs/web-0.log
  README.md            <- sometimes absent
```

Build a `pathlib.Path` from it and return:

```python
solve(root)
# -> {"logs": ["api-0.log", "web-0.log"], "conf_stems": ["api"], "has_readme": True}
```

| key | what goes in it |
| --- | --- |
| `"logs"` | `.name` of every `*.log` anywhere under root, sorted |
| `"conf_stems"` | `.stem` of every `*.conf` anywhere under root, sorted |
| `"has_readme"` | does `root/README.md` exist |

Join paths with the `/` operator, not string concatenation. The `.log` and `.conf` files sit at any depth — search the whole tree, not just the top.

## Hints
### Hint 1
`pathlib` treats a path as an object, not a string: joining, searching and asking questions about it are all methods. `glob` looks in one directory only; it has a sibling that walks the entire tree. A `Path` also knows its own final component, and that component with the extension removed.
### Hint 2
`Path(root)` gets you into object-land. `rglob('*.log')` yields every match in the whole tree. `.name` is the final component, `.stem` is that minus the suffix. Join with the `/` operator and ask `.exists()` for the readme. Wrap both listings in `sorted` so the order is fixed.
### Hint 3
Different data, same moves:

```python
from pathlib import Path
etc = Path('/etc')
units = sorted(p.name for p in etc.rglob('*.timer'))
p = Path('/var/log/nginx/access.log')
print(p.name, p.stem, p.suffix)   # access.log access .log
print((etc / 'hosts').exists())   # True on most boxes
```

One object, and the string-splitting you used to do disappears.
