---
title: undo commits, two different ways
kind: git
difficulty: medium
minutes: 12
prereqs: [341]
track: git
tags: [undo, history-rewriting]
---
# undo commits, two different ways

*`git reset` moves a branch backward. What it does with the difference depends on which flag you give it.*

## Read first
- [git-reset](https://git-scm.com/docs/git-reset): `--soft`, `--mixed`, `--hard`
- [git-switch](https://git-scm.com/docs/git-switch): moving between branches

## Why
`git reset HEAD~2` moves a branch back two commits either way, but what happens to the two commits' changes depends entirely on the flag. `--soft` leaves them staged, as if you had never committed at all, so a fresh `git commit` folds them into one. `--hard` throws them away completely, worktree and all, which is exactly what you want when a whole line of work turns out to be a dead end rather than something to keep in a different shape. Reaching for the wrong one turns "combine these" into "delete these" or the other way around, so the two need to stay separate in your head, the same as the two `git restore` flags do.

## You get
A repository with three commits on `main`: a start, then an export feature built in two steps, `export.py` first without the caller's rows and then with them, the second step also adding `test_export.py`. An `experiment` branch off the last of those adds one more commit trying a faster writer.

## You return
On `main`, the two export commits replaced by one, `add {format} export`, holding what they held together; `experiment`'s last commit gone and its file with it; on `main`.

## Rules
- `main` has one new commit in place of the two, `add {format} export`, holding both `export.py` and `test_export.py` as the two commits left them together
- `experiment` loses its last commit, and `fast.py` disappears with it
- you end on `main`

## Hints
### Hint 1
`--soft` keeps the two commits' changes staged, ready to become one. `--hard` on the other branch throws its last commit away for good, file included.

### Hint 2
On `main`: `git reset --soft HEAD~2`, then commit the combined change under one message. On `experiment`: `git reset --hard HEAD~1` drops its last commit outright. Switch back to `main` when done.

### Hint 3
The same shape on a different repository: `main` built a config loader in two commits that should become one, `add config loader`; a `spike` branch's last commit added a throwaway script that should be gone entirely.

```sh
git reset --soft HEAD~2
git commit -m "add config loader"
git switch spike
git reset --hard HEAD~1
git switch main
```
