---
title: resolve a conflict
kind: git
difficulty: medium
minutes: 15
prereqs: [345]
track: git
tags: [merging, conflicts]
---
# resolve a conflict

*Two branches can each have a good reason to touch the same line. git stops rather than guess which reason wins.*

## Read first
- [git-merge](https://git-scm.com/docs/git-merge): what a conflict leaves in the working tree and the index
- [git-status](https://git-scm.com/docs/git-status): reading what a conflicted merge is waiting on

## Why
When two branches change nearby lines differently, git has no way to know which version should win, so it stops the merge partway and marks the whole conflicting block in the file rather than guess; a line next to one that changed on both sides gets pulled into the same conflict, even if only one side touched it. Finishing the merge means editing the file down to what it should actually say, staging it, and running `git commit`; because the merge commit is already prepared and waiting, `--no-edit` just takes git's own message instead of opening an editor.

## You get
A repository with one commit, a server config with a port and a worker count. Since then, main raised the worker count and moved the port again, and a branch, split off before that, moved the port to a value of its own.

## You return
`feature/{topic}` merged into `main` with git's default message, `config.ini` exactly the three lines below, nothing left mid-merge.

```
[server]
port = {port}
workers = {workers}
```

## Rules
- `feature/{topic}` is merged into `main` with git's default merge message
- `config.ini` holds exactly `[server]`, `port = {port}`, `workers = {workers}`
- nothing is left mid-merge: no conflict markers, no pending commit

## Hints
### Hint 1
The port and worker settings sit on adjacent lines, and each branch touched at least one of them since they split; adjacent changes don't merge line by line, they conflict as a block.

### Hint 2
Merge, let it stop on the conflict, fix the file to say what it should, stage it, then `git commit --no-edit` to finish with git's own message.

### Hint 3
The same shape on a different repository: `main` and `feature/network` each changed a `TIMEOUT` setting since they split, and only `main` changed a `RETRIES` setting.

```sh
git merge feature/network || true
printf '%s\n' 'TIMEOUT = 20' 'RETRIES = 5' > settings.py
git add settings.py
git commit --no-edit
```
