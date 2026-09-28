---
title: "concurrency: cancel the run a new push made pointless"
difficulty: medium
minutes: 12
prereqs: [373]
track: github-actions
tags: [concurrency, expressions]
kind: workflow
edits: .github/workflows/ci.yml
---
# concurrency: cancel the run a new push made pointless

*Push three fixups to a pull request in a minute and three full runs start, two of them testing code nobody will merge. A concurrency group cancels them; on `main`, it must not.*

## Read first
- [Control the concurrency of workflows and jobs](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/control-workflow-concurrency): groups, and `cancel-in-progress`

## Why
Runners are not free and neither is waiting. When a new commit lands on a pull request, the run for the commit before it tests code that is already out of date, and the useful thing to do is stop it.

`concurrency` at the top of a workflow puts every run in a **group**, named by an expression. Only one run per group is in progress at once; a new one waits, or, with `cancel-in-progress` true, cancels the one that is running. The group is the workflow's name and the ref, so each branch and each pull request has its own and never cancels anyone else's.

Cancelling is right for a pull request and wrong for `main`: a run on main may be the one that deploys, and killing it halfway leaves production half updated. `cancel-in-progress` takes an expression too, so it can be true for pull requests only: `github.event_name == 'pull_request'`.

## You get
An empty `.github/workflows/ci.yml`. Whatever you type is checked as YAML while you type it, and linted by actionlint when you run it, offline. Nothing is run.

## You return
A workflow named `CI`, run on pushes to `main` and on pull requests, in which a new run for the same branch or pull request cancels the one before it on a pull request and waits for it on main, and whose one job `test` runs `{command}`.

## Rules
- `name: CI`, and `on` is exactly `push` with `branches: [main]` and `pull_request` with nothing under it
- the workflow's `concurrency` is exactly `group: ${{{{ github.workflow }}}}-${{{{ github.ref }}}}` and `cancel-in-progress: ${{{{ github.event_name == 'pull_request' }}}}`
- exactly one job, `test`, on `ubuntu-latest`, with no `concurrency` of its own, whose steps are `actions/checkout` at any version and then `run: {command}`

## Hints
### Hint 1
The group is a string built from two contexts:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
```

### Hint 2
`cancel-in-progress` is usually `true` or `false`, and an expression that gives one works too:

```yaml
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

### Hint 3
This `concurrency` sits at the top level, beside `on` and `jobs`, so it governs whole runs rather than one job.
