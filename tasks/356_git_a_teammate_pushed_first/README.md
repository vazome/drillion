---
title: a teammate pushed first
kind: git
difficulty: hard
minutes: 15
prereqs: [343, 350, 353]
track: git
tags: [remotes, rebase, stash]
---
# a teammate pushed first

*Two problems can show up on `main` at once: origin moved without you, and you have an edit sitting in the way of catching up.*

## Read first
- [git-pull](https://git-scm.com/docs/git-pull): `--rebase`, `--autostash`
- [git-push](https://git-scm.com/docs/git-push): `--force-with-lease`, protecting a push that rewrites history

## Why
A teammate pushed to `main` while you were working, so your local `main` is now behind `origin/main`, and an uncommitted edit is sitting in your working tree besides. A plain `git pull` would try to merge and still refuse to run with that edit in the way. `git pull --rebase --autostash` handles both at once: it shelves the edit, replays your local commit on top of the teammate's, and brings the edit back, so `main` ends up as one straight line with no merge commit. Separately, you already amended a commit on a feature branch you had pushed before, which rewrote its history; pushing that branch plain would be rejected, since `origin` has a commit yours no longer contains. `--force-with-lease` pushes the rewrite through, but only if `origin` still holds what you last saw there, so it never silently overwrites a push you never fetched.

## You get
A repository with one commit on `main`, pushed to `origin`. A feature branch adds one commit, pushed, then amended locally to add docs, not yet pushed again. Back on `main`, a teammate has pushed a `ci` commit to `origin`, you have your own `changelog` commit on top of your local `main`, and an uncommitted edit to `notes.md` sits in your working tree.

## You return
`main`, here and on `origin`, is `teammate: add ci` then your `add changelog` on top, with no merge commit; your change to `notes.md` still there and not committed; `feature/{feature}` on `origin` replaced by your rewritten branch, pushed with `--force-with-lease`; on `main`.

## Rules
- `main`, locally and on `origin`, is `teammate: add ci` then `add changelog`, with no merge commit
- the uncommitted edit to `notes.md` is still there, unstaged
- `feature/{feature}` on `origin` matches your amended branch, pushed with `--force-with-lease`
- you end on `main`

## Hints
### Hint 1
`main` moved on `origin` since you last looked, and you also have an edit in the way; a plain `git pull` would try to merge and still balk at the edit sitting there.

### Hint 2
`git pull --rebase --autostash` shelves the edit, replays your commit on the teammate's, and restores the edit in one step. Push `main`, then force-with-lease the feature branch, since its old version on `origin` is not what you have locally anymore.

### Hint 3
The same shape on a different repository: `main` gained a teammate's `add rate limiting` commit while you had your own `fix pagination` commit and an uncommitted edit to `config.py`; a `feature/export` branch you had already pushed was amended locally and needs pushing again.

```sh
git pull --rebase --autostash
git push
git push --force-with-lease origin feature/export
```
