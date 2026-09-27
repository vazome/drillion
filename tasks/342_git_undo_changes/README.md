---
title: undo changes, keep the right ones
kind: git
difficulty: easy
minutes: 8
prereqs: [339]
track: git
tags: [staging, undo]
---
# undo changes, keep the right ones

*Two files can both look "changed", and still need opposite fixes.*

## Read first
- [git-restore](https://git-scm.com/docs/git-restore): the worktree, the stage, or both

## Why
`git status` can show two files as modified for two different reasons. One might be a change you regret entirely and want gone. The other might be a change you meant to keep, just staged too early, before you were ready to commit it. `git restore path` throws away the worktree change and puts the file back to what is in the index. `git restore --staged path` does the opposite: it leaves the worktree alone and only unstages, so the edit is still there, just not queued for the next commit. Reaching for the wrong flag turns "unstage this" into "delete this", which is why the two need to stay separate in your head.

## You get
A repository with one commit, an app module and a notes file. Since then, the app module was edited carelessly, and a note was added to the notes file and staged.

## You return
`app.py` exactly as last committed; the note still in `notes.md`, changed but not staged; no new commit.

## Rules
- `app.py` matches the last commit exactly, nothing staged or unstaged on it
- `notes.md` still has the added note in the worktree, but it is not staged
- no new commit

## Hints
### Hint 1
These are two different problems. One file needs its edit thrown away. The other needs its edit kept, just taken back out of the stage.

### Hint 2
`git restore file` undoes the worktree. `git restore --staged file` undoes only the stage, and leaves the worktree as it is. Reach for the right one for each file.

### Hint 3
The same two problems on a different repository: a debug print was added and staged in `server.py`, and a config edit was made but not staged in `config.py`, and it is `config.py` you want to throw away this time.

```sh
git restore --staged server.py
git restore config.py
```
