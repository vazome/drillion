---
title: merge a branch
kind: git
difficulty: easy
minutes: 10
prereqs: [339]
track: git
tags: [branches, merging]
---
# merge a branch

*Two finished branches don't land the same way: one can just move main forward, the other needs a commit of its own to remember there were two.*

## Read first
- [git-merge](https://git-scm.com/docs/git-merge): `--ff-only`, `--no-ff`
- [git-branch](https://git-scm.com/docs/git-branch): `-d`, deleting a branch git can prove is merged

## Why
When main hasn't moved since a branch split off, landing that branch is just moving main's pointer forward to where the branch already is; `git merge --ff-only` refuses to do anything else, which is a promise that no merge commit appears where none was needed. Once main has moved past where a second branch split off, a fast-forward isn't possible anymore, and letting git pick whichever way happens to work would hide that the two branches were ever separate; `git merge --no-ff` always makes a merge commit, even on the rare case a fast-forward would have worked, so the branch's shape is remembered. A branch already folded into main serves no future purpose: `git branch -d` only deletes one git can prove is merged in.

## You get
A repository with one commit on `main`. Two feature branches split from it: one holds two commits ready to land, the other holds one commit made independently, at the same point main was.

## You return
`main` holds `feature/{a}`'s two commits with no merge commit, then a merge commit bringing in `feature/{b}` with git's default message `Merge branch 'feature/{b}'`; both branches deleted; on `main`.

## Rules
- `main` fast-forwards onto `feature/{a}`'s two commits, with no merge commit
- `feature/{b}` is merged in with a merge commit, message `Merge branch 'feature/{b}'`
- both `feature/{a}` and `feature/{b}` are deleted
- you end on `main`

## Hints
### Hint 1
One of these branches can just move `main` forward; forcing a merge commit onto it would remember a fork that never happened. Check which branch actually moved since `main` did before merging both the same way.

### Hint 2
`git merge --ff-only` for the branch `main` can just move onto; `git merge --no-ff` for the one it can't. `--no-edit` accepts git's own message. Delete both once they're in with `git branch -d`.

### Hint 3
The same shape on a different repository: `hotfix/logging` only extends where `main` already is, and `feature/export` was started independently, at the same point.

```sh
git merge --ff-only hotfix/logging
git merge --no-ff --no-edit feature/export
git branch -d hotfix/logging feature/export
```
