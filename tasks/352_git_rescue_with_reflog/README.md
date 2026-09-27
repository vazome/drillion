---
title: rescue with reflog
kind: git
difficulty: medium
minutes: 12
prereqs: [351]
track: git
tags: [undo, branches]
---
# rescue with reflog

*Deleting a branch or resetting past a commit only moves a name. The commit itself is still sitting there until git decides nothing points at it anymore.*

## Read first
- [git-reflog](https://git-scm.com/docs/git-reflog): the log of where `HEAD` has pointed, `--grep-reflog`
- [git-branch](https://git-scm.com/docs/git-branch): creating a branch at a specific commit

## Why
`HEAD`'s reflog remembers every commit it has ever pointed at, in this repository, on this machine, whatever branch was checked out at the time: every commit, every switch, every reset. Deleting a branch or hard-resetting past a commit only removes the name pointing at it; the commit itself stays reachable, and safe from garbage collection, as long as some reflog entry still names it. `git log -g --grep-reflog=<text>` searches those entries the same way `--grep` searches commit messages, so you can find the exact commit a `commit:` entry recorded without remembering its hash, then hand that hash to `git branch <name>` to bring a deleted branch back, or to `git reset --hard` to put a branch back where it was.

## You get
A repository with one commit on `main`. A feature branch is created, gets two commits, and is deleted after switching back to `main`. `main` then gets one more commit, which is undone with a hard reset that drops it.

## You return
`feature/{feature}` back where it was, at `add {feature} tests`; `main` back at `add {lost}`; nothing left to commit; on `main`.

## Rules
- `feature/{feature}` exists again, at the commit that added its tests
- `main` is back at the `add {lost}` commit
- nothing is left uncommitted
- you end on `main`

## Hints
### Hint 1
A branch's last commit does not vanish the moment the branch is deleted, and neither does one a hard reset moves past. `HEAD`'s reflog still remembers pointing at it.

### Hint 2
`git log -g -1 --format=%H --grep-reflog='commit: <message>' HEAD` finds the commit a `commit:` reflog entry recorded. Recreate the branch with `git branch <name> <sha>`, or put `main` back with `git reset --hard <sha>`.

### Hint 3
The same shape on a different repository: a `hotfix/timeout` branch was deleted after its one commit `raise the timeout`, and `main` was hard-reset past its own `wire up logging` commit.

```sh
git branch hotfix/timeout "$(git log -g -1 --format=%H --grep-reflog='commit: raise the timeout' HEAD)"
git reset --hard "$(git log -g -1 --format=%H --grep-reflog='commit: wire up logging' HEAD)"
```
