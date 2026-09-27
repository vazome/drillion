---
title: stash and switch
kind: git
difficulty: medium
minutes: 10
prereqs: [342]
track: git
tags: [stash, branches]
---
# stash and switch

*Unfinished work does not have to block a detour to another branch. git can hold it while you're away.*

## Read first
- [git-stash](https://git-scm.com/docs/git-stash): `push -u`, setting aside tracked and untracked changes
- [git-switch](https://git-scm.com/docs/git-switch): moving between branches

## Why
`git switch` refuses to leave a branch when the change in your way would be overwritten, and even when it does not refuse, carrying an unrelated, half-finished edit onto another branch is confusing at best. `git stash push` puts the tracked changes aside and gives you a clean tree; adding `-u` also sweeps up untracked files, so a new file you started does not get left behind or, worse, carried onto the other branch by mistake. The stash is a shelf, not a trash can: `git stash pop` takes the most recent entry back off it and reapplies it, exactly as it was, once you are back where you started.

## You get
A repository with one commit on `main`, a config file with two settings. A feature branch adds one more commit and leaves an unfinished edit to its own module and a new, untracked notes file, neither staged.

## You return
On `main`, one new commit `raise retries to {retries}` changing `RETRIES = 1` to `RETRIES = {retries}` in `config.py` and nothing else; back on `feature/{feature}` with both unfinished changes as they were, the edit and the new file, neither staged; the stash empty.

## Rules
- `main` has exactly one new commit, `raise retries to {retries}`, changing only `RETRIES = 1` to `RETRIES = {retries}`
- you end on `feature/{feature}`
- the feature branch's unstaged edit and untracked file are both back, unstaged, exactly as they were
- the stash is empty

## Hints
### Hint 1
Switching branches wants a clean tree. The untracked file needs sweeping up too, not just the tracked edit.

### Hint 2
`git stash push -u` first, then switch, fix, commit. Switch back, then `git stash pop` to bring everything back and clear the stash in the same step.

### Hint 3
The same shape on a different repository: a typo fix is needed on `main` while a `refactor/parser` branch has an unfinished edit and a new scratch file.

```sh
git stash push -u
git switch main
sed -i 's/pasre/parse/' parser.py
git commit -am "fix the typo"
git switch refactor/parser
git stash pop
```
