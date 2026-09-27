---
title: rebase onto main
kind: git
difficulty: hard
minutes: 15
prereqs: [346, 348]
track: git
tags: [rebase, conflicts]
---
# rebase onto main

*A merge commit remembers that two histories forked and rejoined. Sometimes you'd rather main never knew the branch had fallen behind.*

## Read first
- [git-rebase](https://git-scm.com/docs/git-rebase): replaying commits onto a new base, resolving a conflict mid-rebase, `--continue`
- [git-merge](https://git-scm.com/docs/git-merge): `--ff-only`, landing a rebased branch without a merge commit

## Why
Merging main into a branch that's fallen behind keeps the fork visible forever, a merge commit with two parents recording that the branch and main once diverged. Rebasing replays the branch's own commits, one at a time, onto main's current tip instead, so when it's done the branch looks like it was written on top of main all along and can land with a plain fast-forward. A conflict during rebase stops on the one commit that doesn't apply cleanly, same as any conflict: fix the file, `git add` it, and `git rebase --continue` moves on to whatever's left, or finishes if that was the last one. A rebase still reconstructs each commit's message as it goes, so an editor opens for it; `GIT_EDITOR=true` accepts what's already there without changing it.

## You get
A repository with one commit, a page size setting and a README. A feature branch adds a module and raises the page size once. Since it split off, main added a health check and raised the same page size setting to a different value.

## You return
`feature/{feature}`'s two commits replayed on top of `main` with no merge commit, the conflict in `limits.py` resolved to exactly `PAGE_SIZE = {size}`; `main` fast-forwarded to it; the branch deleted; on `main`.

## Rules
- `feature/{feature}`'s commits are replayed onto `main`'s tip with no merge commit
- `limits.py` ends at exactly `PAGE_SIZE = {size}`
- `main` is fast-forwarded onto the rebased branch
- `feature/{feature}` is deleted
- you end on `main`

## Hints
### Hint 1
Both `main` and the branch changed the same setting since they split; replaying the branch's commits one at a time will stop on the one that touches it too.

### Hint 2
`git rebase main` on the branch, fix the conflicting file to what it should actually say, `git add` it, and `git rebase --continue` with a non-interactive editor to accept the regenerated message; once it lands, `main` can fast-forward onto it and the branch can go.

### Hint 3
The same shape on a different repository: a `cache` branch changed a `TTL` setting that main also changed since the branch split.

```sh
git switch feature/cache
git rebase main || true
printf 'TTL = 120\n' > settings.py
git add settings.py
GIT_EDITOR=true git rebase --continue
git switch main
git merge --ff-only feature/cache
git branch -d feature/cache
```
