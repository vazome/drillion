---
title: bisect, find the first bad commit
kind: git
difficulty: hard
minutes: 15
prereqs: [344]
track: git
tags: [history-search, tagging]
---
# bisect, find the first bad commit

*Fifteen commits and one of them broke something. Checking each by hand is slow; a binary search, run by git itself, is not.*

## Read first
- [git-bisect](https://git-scm.com/docs/git-bisect): `start`, `run`, marking `refs/bisect/bad`, `reset`
- [git-tag](https://git-scm.com/docs/git-tag): naming a commit so the search never has to run twice

## Why
Checking fifteen commits one at a time to find where something broke is slow and easy to get wrong. `git bisect start <bad> <good>` bounds the search between a commit known to fail and one known to work, and `git bisect run <script>` hands git a script to run at each step instead of asking you to judge every commit yourself: exit `0` means good, anything else means bad, and git narrows the range on its own until one commit is left. That commit is left marked at `refs/bisect/bad`, which a tag turns into a name that outlives `git bisect reset`, the step that ends the search and returns `HEAD` to where it was before bisect left it detached partway through.

## You get
A repository with a `calc.py` module holding a rate, and a `check.sh` script that fails as soon as that rate changes. Fifteen more commits follow, each adding a note file, with one of them silently changing the rate along the way.

## You return
A tag named `first-bad` on the first commit where `sh check.sh` fails; the bisect finished; on `main`.

## Rules
- a tag named `first-bad` points at the first commit where `sh check.sh` fails
- the bisect is finished, `HEAD` is back on `main`, nothing left in progress

## Hints
### Hint 1
Checking fifteen commits by hand is slow and easy to get wrong partway through. Git can run the check itself at each step if you give it a script and let it narrow things down.

### Hint 2
`git bisect start HEAD <first-commit>`, then `git bisect run sh check.sh` does the whole search. `refs/bisect/bad` is left pointing at the answer; tag it before `git bisect reset` moves on.

### Hint 3
The same shape on a different repository: a `threshold.py` module and a `verify.sh` script that fails once a limit changes, across twenty commits that each touch an unrelated file.

```sh
git bisect start HEAD "$(git rev-list --max-parents=0 HEAD)"
git bisect run sh verify.sh
git tag first-bad refs/bisect/bad
git bisect reset
```
