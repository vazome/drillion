---
title: fixup commits
kind: git
difficulty: medium
minutes: 12
prereqs: [348]
track: git
tags: [rebase, commits]
---
# fixup commits

*A fix for an earlier commit doesn't have to be typed as history-rewriting by hand. `--fixup` and `--autosquash` do the bookkeeping for you.*

## Read first
- [git-commit](https://git-scm.com/docs/git-commit): `--fixup=<commit>`, what it names the new commit
- [git-rebase](https://git-scm.com/docs/git-rebase): `--autosquash`, what it does with a `fixup!` commit

## Why
Editing an earlier commit by hand means an interactive rebase, finding the right line, marking it `fixup`, and trusting the sed or the memory is right. `git commit --fixup=<commit>` skips the finding-the-line part: it makes an ordinary commit whose message is `fixup! <that commit's message>`, so it's clear at a glance what it's meant to fold into. `git rebase --autosquash` reads that prefix itself, moves the fixup commit right after the one it names and marks it `fixup` in the todo list automatically; an editor that just accepts the list unchanged still runs the fold, since autosquash already wrote it correctly.

## You get
A repository with one commit, a README. A feature branch adds a parser and its test, two commits; since then, the parser module was edited on disk, a fix to how it splits its input, not yet staged.

## You return
Still two commits on the branch, `add parser` now holding the stripped version, made with `commit --fixup` and folded with `--autosquash`.

## Rules
- the branch still holds exactly two commits
- `add parser` holds the fixed, stripped-input version of `parser.py`
- `add parser tests` is unchanged
- no third commit is left over

## Hints
### Hint 1
The parser needs the exact same fix as before, just applied without cracking open the todo list by hand.

### Hint 2
`git commit --fixup=<hash>` names the commit to fold into by writing `fixup! <message>`; `git rebase --autosquash` finds that prefix on its own and reorders the todo list, so an editor that changes nothing still finishes the fold.

### Hint 3
The same idea on a different repository: a `format` function was fixed on disk after its own commit, and one more commit landed after it; fold the fix into the original without touching the todo list by hand.

```sh
git commit -a --fixup="$(git log --format=%H --grep='^add the formatter$' -1)"
GIT_SEQUENCE_EDITOR=true git rebase -i --autosquash main
```
