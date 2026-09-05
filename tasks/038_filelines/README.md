---
title: open() — stream a file line by line
difficulty: easy
tier: core
minutes: 10
prereqs: [37]
tags: [files-text]
---
# open() — stream a file line by line

*Every ops script starts by reading a file that is bigger than you would like.*

## Why
The overnight backup job failed. The log file it wrote is huge, far bigger than the machine's memory. Your manager wants only the ERROR messages, in the order they happened, so the team can see what broke first. You must read the file one line at a time, never the whole thing at once, or your own script will crash the box.

## You get
`path` — a string with the location of a log file on disk, like `"/tmp/ex026_abc.log"`. Every line in it is a level word, a space, then a message. The test writes the file and hands you the path; you never build it yourself.

## You return
a list of strings — the message part of every ERROR line, in file order, like `["disk full on node-7"]`. An empty list if there are no ERROR lines.

## Rules
`path` is a log file. Every line is a LEVEL, a space, then a message:

```text
INFO backup ok on node-3
ERROR disk full on node-7
WARN cert expiring on node-2
```

Open it with `encoding="utf-8"` and return the messages of the ERROR lines, in file order, newline stripped:

```python
solve(path)   # -> ["disk full on node-7"]
```

A file with no ERROR lines returns `[]`.

> [!TIP]
> Pretend the file is 40 GB. Do not call `.read()` or `.readlines()` — an open file object is already an iterable that yields one line at a time, in constant memory.

## Hints
### Hint 1
A file object is its own iterator: looping over it gives one line at a time and never holds the whole file. `.readlines()` builds the entire list in memory first — fine at 50 MB, fatal at 40 GB. One more thing: every line you get still ends with its newline character.
### Hint 2
Three pieces: `with` plus `open(path, encoding='utf-8')`, a `for` loop directly over the handle, and per line — strip the newline, test the level with `startswith`, cut the level off the front with a slice or `split`. Append matches to a list as you go.
### Hint 3
Different data, same skeleton — summing a column from a huge file:

```python
# each line of sizes.txt looks like: '512 backup.tar'
total = 0
with open('sizes.txt', encoding='utf-8') as f:
    for line in f:
        total += int(line.split()[0])
```

Open once, loop the handle, handle each line, never hold the whole file.
