---
title: the first push
kind: git
difficulty: easy
minutes: 10
prereqs: [345]
track: git
tags: [remotes, branches]
---
# the first push

*A branch's first push has to say more than where the commits go. It has to say what `git pull` and a bare `git push` should mean from then on.*

## Read first
- [git-push](https://git-scm.com/docs/git-push): `-u`/`--set-upstream`, tracking a remote branch
- [git-switch](https://git-scm.com/docs/git-switch): `-c`, creating a branch as you move to it

## Why
`git push origin main` sends `main`'s commits to `origin` and nothing more. Without `-u` it never tells your local `main` which remote branch to compare itself to, so a later bare `git pull` or `git push` has nothing to default to, and asking what branch it tracks comes back empty. `-u` sets that link the first time a branch is pushed, and only needs doing once; every push and pull after that already knows where it goes. A brand new branch needs the same first push, with the same flag, before a plain `git push` on it means anything either.

## You get
A repository with two commits on `main` and an `origin` remote already configured, empty: nothing has been pushed to it yet.

## You return
`main` on `origin`, tracking `origin/main`; a new branch `docs/{topic}` from `main` with one commit, `describe {topic}`, adding `docs/{topic}.md` holding exactly the line `# {title}`, pushed and tracking `origin/docs/{topic}`; on `docs/{topic}`.

## Rules
- `main` is pushed to `origin` and tracks `origin/main`
- a new branch `docs/{topic}`, branched from `main`, adds `docs/{topic}.md` holding exactly `# {title}` in one commit, `describe {topic}`
- `docs/{topic}` is pushed to `origin` and tracks `origin/docs/{topic}`
- you end on `docs/{topic}`

## Hints
### Hint 1
The first push of any branch does not just send commits; without `-u` it leaves nothing for a later plain `git pull` or `git push` to default to.

### Hint 2
`git push -u origin main` first. Then branch, add the file, commit, and push the new branch the same way: `git push -u origin <branch>`.

### Hint 3
The same shape on a different repository: `main` has never been pushed, and a new branch `docs/onboarding` should add `docs/onboarding.md` holding exactly `# Onboarding`.

```sh
git push -u origin main
git switch -c docs/onboarding
mkdir -p docs
printf '%s\n' '# Onboarding' > docs/onboarding.md
git add docs/onboarding.md
git commit -m "describe onboarding"
git push -u origin docs/onboarding
```
