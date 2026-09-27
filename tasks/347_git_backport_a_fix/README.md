---
title: backport a fix
kind: git
difficulty: medium
minutes: 10
prereqs: [345]
track: git
tags: [branches, commits]
---
# backport a fix

*A fix made after a release branched off doesn't belong on every commit that came after it, just the one that actually fixes something.*

## Read first
- [git-cherry-pick](https://git-scm.com/docs/git-cherry-pick): replaying one commit's change elsewhere
- [git-log](https://git-scm.com/docs/git-log): `--grep` and `--format=%H` for finding a commit by its message

## Why
A release branch freezes a version in time; work that keeps happening on main after it splits off doesn't belong on it, except the fixes that do. Merging main into the release branch would drag every later commit along, not just the fix; `git cherry-pick` takes exactly the change one commit made and replays it as a new commit wherever you are, without touching anything else main did around it. `git log --grep` finds a commit by its message instead of by counting how many commits back it is, and `--format=%H` prints nothing but its hash, so it can be captured straight into the next command.

## You get
A repository with one commit, an app module. Main has since added a reports module, a fix under its own message, and an exports module. A release branch was cut right after the reports module landed, before the fix or the exports.

## You return
`release/1.{minor}` gains exactly one commit, `fix {bug}`, with that fix's change and nothing else; `main` unchanged; on `main`.

## Rules
- `release/1.{minor}` gains exactly one new commit, `fix {bug}`, holding only that fix's change
- `main` is unchanged
- you end on `main`

## Hints
### Hint 1
Merging main in would bring the exports module along for the ride too; only one of main's later commits is meant to land on the release branch.

### Hint 2
Find the fix commit's hash with `git log --grep`, switch to the release branch, and `git cherry-pick` just that hash.

### Hint 3
The same shape on a different repository: a `hotfix` commit landed on main after a `release/2.0` branch split off, among unrelated commits; the branch needs only that one fix.

```sh
git switch release/2.0
git cherry-pick "$(git log main --format=%H --grep='^fix the crash$')"
git switch main
```
