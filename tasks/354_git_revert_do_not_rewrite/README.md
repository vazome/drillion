---
title: revert, do not rewrite
kind: git
difficulty: medium
minutes: 10
prereqs: [353]
track: git
tags: [undo, remotes]
---
# revert, do not rewrite

*A commit sitting only in your own repository can be reset away and forgotten. One that has already reached origin cannot, not without a fight everyone else loses too.*

## Read first
- [git-revert](https://git-scm.com/docs/git-revert): `--no-edit`, undoing a commit with a new one
- [git-log](https://git-scm.com/docs/git-log): `--grep`, finding a commit by its message

## Why
Once a commit is pushed, resetting past it locally and pushing again either gets rejected, since your branch no longer contains a commit `origin` already has, or forces it through and rewrites history everyone who already pulled now disagrees with. `git revert` sidesteps the whole problem: it makes a new commit that undoes the change, so history only ever grows forward, and anyone's next `git pull` just picks up the new commit like any other. `--no-edit` accepts git's own default message, `Revert "<original message>"`, which already says exactly what it undoes.

## You get
A repository with three commits on `main`, already pushed to `origin`: a start, a flag turned on by default, and a metrics module added on top.

## You return
`enable {flag} by default` undone by a new commit with git's default message `Revert "enable {flag} by default"`, nothing else changed, and pushed to `origin`.

## Rules
- a new commit undoes exactly `enable {flag} by default`, titled `Revert "enable {flag} by default"`
- nothing else about the history changes: the metrics commit stays, and no commit is dropped or rewritten
- the revert is pushed to `origin`

## Hints
### Hint 1
The commit you're undoing is already on `origin`. Resetting past it locally and pushing again would either be rejected outright or force everyone who already has it to catch up.

### Hint 2
Find the commit with `git log --grep`, then `git revert --no-edit <sha>` to undo it with a new commit, and `git push` to send it on.

### Hint 3
The same shape on a different repository: a commit `switch to the new logger` is already on `origin` and needs undoing without touching anything committed after it.

```sh
git revert --no-edit "$(git log --format=%H --grep='^switch to the new logger$' -1)"
git push
```
