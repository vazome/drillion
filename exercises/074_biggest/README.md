---
title: 'DRILL: N largest files under a directory tree'
minutes: 25
prereqs: [27]
tags: [whole-task]
practices: [27, 9, 40]
---
# DRILL: N largest files under a directory tree

Whole-task drill: the disk is full and someone wants the top offenders now.

Combines topics 27 (pathlib), 9 (sort key), 40 (tempfile).

## Why
A server's disk is almost full and the on-call engineer needs to
know, right now, which files are eating the space so they can delete or
move the biggest ones. "Show me the five largest files under /var" is
the question. A list sorted biggest-first is what they act on.

## You get
`root` — a folder path as text, like "/tmp/ex074_abc". The test
creates a small temporary folder tree with files of different sizes and
hands you the path; you never build it yourself.

`n` — a whole number, like 3: how many of the biggest files to report.

## You return
a list of pairs, biggest file first. Each pair is (the
file's path relative to root, its size in bytes), like
[("api/logs/app.log", 900), ("web/index.html", 400)].

## Rules
A disk is filling up. Find the n biggest files under `root`.

`root` is a directory path as a STRING. Return a list of
(relative_path, size_in_bytes) pairs, biggest first:

```python
root/
  api/logs/app.log      900 bytes
  api/logs/old.log      120 bytes
  web/index.html        400 bytes

solve(root, 2)  ->  [("api/logs/app.log", 900), ("web/index.html", 400)]
```

Details that matter:
  - Search the whole tree, at any depth. Directories are not files.
  - The path is relative to root, forward slashes, no leading "./".
  - Ties: same size, then smaller path first (plain string order).
  - Fewer than n files in the tree: return all of them.

Say the plan out loud before you type: collect, sort, slice.

## Hints
### Hint 1
Three steps, and only the middle one is interesting: collect every file with its size, sort, take the first n. Sorting is where people stall, because you want one direction for size and the other for the path. One key expression does both, no second sort pass.
### Hint 2
Path(root).rglob('*') walks the whole tree; p.is_file() drops the directories. p.stat().st_size is the size, p.relative_to(root).as_posix() is the name you report. Sort with key=lambda t: (-t[1], t[0]) — negating the number flips that field to descending while the string stays ascending. Then slice [:n].
### Hint 3
Different data, same two moves:

```python
rows = [('pod-b', 3), ('pod-a', 3), ('pod-c', 9)]
rows.sort(key=lambda t: (-t[1], t[0]))
print(rows)      # [('pod-c', 9), ('pod-a', 3), ('pod-b', 3)]

from pathlib import Path
p = Path('/var/log/nginx/access.log')
print(p.relative_to('/var/log').as_posix())   # nginx/access.log
```

A slice past the end is not an error, so [:n] handles the short tree for free.
