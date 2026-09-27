---
title: tidy a branch
kind: git
difficulty: hard
minutes: 15
prereqs: [341, 345]
track: git
tags: [rebase, history-rewriting]
---
# tidy a branch

*A branch that grew commit by commit doesn't have to ship that way. `rebase -i` can fold, reword and drop before it ever reaches main.*

## Read first
- [git-rebase](https://git-scm.com/docs/git-rebase): `-i`, the todo list's `pick`, `fixup`, `reword` and `drop`
- [git-rebase](https://git-scm.com/docs/git-rebase#_options): `GIT_SEQUENCE_EDITOR` and `GIT_EDITOR`, scripting the two editors it opens

## Why
A branch's real history, one commit at a time as work happened, is rarely the history worth keeping: a typo fixed two commits later, a debug print that never should have shipped, a message that doesn't say what the commit actually does once it's finished. `git rebase -i <base>` opens a todo list, one line per commit since `<base>`, oldest first; changing a line's word changes what happens to that commit. `fixup` folds a commit's change into the one above it and throws away its own message; `reword` keeps a commit but stops to let its message be rewritten; `drop` removes a commit and its change entirely. Scripting the two editors it opens, `GIT_SEQUENCE_EDITOR` for the todo list and `GIT_EDITOR` for a `reword`'s message, is what makes a rebase like this run without stopping.

## You get
A repository with one commit, a README. A feature branch adds a form module in progress: a first pass, a typo introduced then fixed two commits later, then a validation module, then a leftover debug print.

## You return
`feature/{form}` is exactly two commits on `main`: `add {form} form` holding the finished field list, then `validate the {form} form` holding `validate.py`; no `debug.py`; on the branch.

## Rules
- `feature/{form}` has exactly two commits since `main`
- the first, `add {form} form`, holds the finished field list with no typo
- the second is reworded to `validate the {form} form` and holds only `validate.py`
- `debug.py` is gone
- you end on `feature/{form}`

## Hints
### Hint 1
Three of these five commits don't deserve to survive on their own: two only fix what came before them, and one should never have been committed at all.

### Hint 2
`git rebase -i main` lists five `pick` lines, oldest first. Turn the typo commits into `fixup`, the debug print into `drop`, and the validation commit into `reword` to give it a better message; scripting both editors is what lets it all run without stopping.

### Hint 3
The same idea on a different repository: a branch adds a `parser` module, fixes a typo in it two commits later, adds a `tests` commit, then a stray `TODO.md` that should never have been added.

```sh
GIT_SEQUENCE_EDITOR="sed -i -e '2s/^pick/fixup/' -e '4s/^pick/drop/'" git rebase -i main
```
