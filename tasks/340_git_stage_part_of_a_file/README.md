---
title: stage part of a file
kind: git
difficulty: medium
minutes: 12
prereqs: [339]
track: git
tags: [staging, commits]
---
# stage part of a file

*A commit is a story about one change. A file on disk does not care how many stories it is carrying at once.*

## Read first
- [git-add](https://git-scm.com/docs/git-add): `-p`, staging by hunk
- [git-commit](https://git-scm.com/docs/git-commit): `-a`, committing every tracked change

## Why
Sometimes you sit down to fix one small thing and notice another while you are in the file. The two edits land in the same working tree change, but they do not belong in the same commit: one is a bug fix, the other is unrelated. `git add` normally stages a whole file, hunk and all. `git add -p` instead walks the diff hunk by hunk and asks, for each one, whether to stage it. Answer yes to the hunk that belongs with this commit, no to the rest, and the file is only partly staged. Committing that gives a clean, single-purpose commit, and whatever is left in the file is still there, unstaged, for the next one.

## You get
A repository with one commit, a small settings module. Since then, two things about it have changed on disk: how a file is opened, and what one setting defaults to. Neither change is staged yet.

## You return
Two new commits: `read settings as UTF-8` changing only the `open(...)` line, then `set the default {name}` with the rest.

## Rules
- exactly two new commits, in this order
- the first commit's message is `read settings as UTF-8`, and it changes only the `open(...)` line
- the second commit's message is `set the default {name}`, and it holds the rest of the diff
- nothing left staged or unstaged afterwards

## Hints
### Hint 1
`git diff` shows both changes in one file. Read it before you stage anything: which lines belong to which story?

### Hint 2
`git add -p settings.py` shows one hunk at a time. `y` stages it, `n` leaves it for later. Commit what you staged, then `git commit -a` sweeps up whatever is still tracked and modified.

### Hint 3
The same shape in a different file: a function's docstring gets a typo fix, and a constant a few lines below gets a new value, in the same working tree change.

```sh
git add -p utils.py
# y for the docstring hunk, n for the constant
git commit -m "fix the typo in the docstring"
git commit -am "raise the retry limit"
```
