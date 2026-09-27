---
title: fix the last commit
kind: git
difficulty: easy
minutes: 6
prereqs: [339]
track: git
tags: [commits, history-rewriting]
---
# fix the last commit

*The tip commit is not history yet, not while it is still only yours. Fix it in place instead of apologizing for it in the next one.*

## Read first
- [git-commit](https://git-scm.com/docs/git-commit): `--amend`, replacing the last commit
- [git-add](https://git-scm.com/docs/git-add): staging what the amended commit should hold

## Why
A commit made in a hurry is often missing something obvious: a test that was written a minute later, a file that never got staged. As long as that commit has not been shared, there is no reason to carry the mistake forward in a second commit that says "actually, also this". `git commit --amend` replaces the tip commit with a new one: stage whatever should have been there, amend, and the message can change too. The result reads as if it had been right the first time.

## You get
A repository with two commits: a README, then a first pass at a small module, tracked under the message `wip`. Its test module sits on disk, untracked.

## You return
Still two commits; the second is `add the {app} parser` and holds both files.

## Rules
- exactly two commits, same as before
- the second commit's message is `add the {app} parser`
- the second commit holds both `{app}.py` and `test_{app}.py`
- the first commit, `start the project`, is unchanged

## Hints
### Hint 1
`wip` was never meant to be the final message. Nothing about the mistake needs a new commit to fix, the last one is still yours to change.

### Hint 2
Stage the file that is missing, then `git commit --amend -m "..."` with the message it should have had all along.

### Hint 3
The same fix on a different repository: a report script was committed without the config file it reads.

```sh
git add config.yaml
git commit --amend -m "add the report script"
```
