---
title: find the commit
kind: git
difficulty: medium
minutes: 10
prereqs: [339]
track: git
tags: [history-search, tagging]
---
# find the commit

*A history nobody can search is just a pile of commits. `git log` can search by what changed, by who changed it, and by where.*

## Read first
- [git-log](https://git-scm.com/docs/git-log): `-S`, `--author`, and limiting to a path with `--`
- [git-tag](https://git-scm.com/docs/git-tag): naming a commit so you don't have to remember its hash

## Why
"Which commit added this line" is not a question `git log`'s default view answers, because a line can appear, disappear and reappear as a file is edited. `-S string` finds every commit where the number of times that exact string appears changed, added or removed, so more than one commit can match; the earliest of them is the one that introduced it. `--author` narrows a history to one person's commits, and a pathspec after `--` narrows it further to commits that touched a given directory, which matters when someone's most recent commit overall is not the one you actually want. Once a commit is found this way, a tag gives it a name, so nobody has to run the same search again just to point at it.

## You get
A repository with a dozen commits by three different authors, touching a small `src/` module and a `docs/` folder. One line of configuration was added partway through the history and changed again later.

## You return
A lightweight tag `introduced` on the commit that introduced `MAX_UPLOAD_MB = {limit}`, and a lightweight tag `last-docs` on the most recent commit by {author} that changed anything under `docs/`.

## Rules
- `introduced` points at the commit that first added the line, not a later commit that changed it
- `last-docs` points at {author}'s most recent commit that touched `docs/`, not merely their most recent commit overall
- both are ordinary, lightweight tags

## Hints
### Hint 1
`-S` can match more than one commit, once for adding a string and again for removing or changing it. "Introduced" means the earliest match, not the newest.

### Hint 2
`git log` prints newest first, so the last line of `-S`'s output is the oldest match. `$(...)` captures a command's output, and `git tag name sha` names that commit.

### Hint 3
The same search on a different repository: which commit first set `DEBUG = True` in `settings.py`, and one author's most recent commit under `migrations/`.

```sh
git tag introduced "$(git log -S 'DEBUG = True' --format=%H | tail -n 1)"
git tag last-migration "$(git log -1 --author='Ada Lovelace' --format=%H -- migrations/)"
```
