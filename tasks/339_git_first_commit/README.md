---
title: the first commit, minus a secret
kind: git
difficulty: easy
minutes: 8
prereqs: []
track: git
tags: [staging, commits]
---
# the first commit, minus a secret

*A repository remembers everything you tell it, forever. Tell it a secret and it remembers that too.*

## Read first
- [git-add](https://git-scm.com/docs/git-add): staging what you mean to commit
- [gitignore](https://git-scm.com/docs/gitignore): telling git which files to leave alone

## Why
A new project starts as untracked files: git can see them, but nothing is remembered until you stage and commit. A file holding a password, a token or a key is easy to write and easy to forget you wrote, and once it is committed it stays in the history forever, readable by anyone who clones the repository, even after you delete it in a later commit. A `.gitignore` file tells git which paths to leave alone. Writing it before the first `git add` is the difference between a secret that is merely on disk and one that never enters history at all.

## You get
A repository with one commit, a README. Two more files sit on disk, untracked: a small module and its test. A third file, also untracked, holds a secret the app needs to run.

## You return
One new commit, `add the {app}`, holding `{app}.py`, `test_{app}.py` and a `.gitignore` whose only line is `{secret}`. Nothing is left to commit, and `{secret}` is never committed.

```
{secret}
```

## Rules
- exactly one new commit, `add the {app}`
- the commit holds `{app}.py`, `test_{app}.py` and `.gitignore`, nothing else
- `.gitignore` has exactly one line: `{secret}`
- `{secret}` is never staged or committed, and nothing else is left uncommitted

## Hints
### Hint 1
Write the ignore rule before you stage anything. Staging a file and then adding it to `.gitignore` does not undo the staging.

### Hint 2
`printf '%s\n' name > .gitignore` writes one line without you needing an editor. Then `git add` the files you want tracked, by name, and commit.

### Hint 3
The same shape on another project: a build tool drops a `dist/` folder full of generated files nobody should track.

```sh
printf '%s\n' 'dist/' > .gitignore
git add .gitignore main.py test_main.py
git commit -m "add the main script"
```
