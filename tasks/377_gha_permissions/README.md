---
title: "permissions: a token that can do one thing"
difficulty: medium
minutes: 15
prereqs: [371]
track: github-actions
tags: [permissions, security]
kind: workflow
edits: .github/workflows/label.yml
---
# permissions: a token that can do one thing

*Every job gets a token for the repository, `GITHUB_TOKEN`. What it may do is set by `permissions`, and the safe default is almost nothing, granted back one scope at a time.*

## Read first
- [Controlling permissions for GITHUB_TOKEN](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/control-jobs-and-workflows#controlling-permissions-for-github_token): the scopes, and the workflow and job levels
- [Workflow syntax: permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions): what `read`, `write` and `none` mean

## Why
The token a job runs with is the blast radius of everything in it: every action it uses, every dependency it installs, every script. On an older repository its default can still be read and write on nearly everything, so a compromised dependency in a test job could push to `main`.

`permissions` at the top of the workflow sets the token for every job, and each scope named is granted at that level while every scope not named becomes `none`. So a workflow starts with `contents: read`, enough to check code out, and nothing else.

A job that needs more names its own `permissions`, and a job-level block **replaces** the workflow's entirely rather than adding to it: a job that labels pull requests and also needs to read the code lists both `contents: read` and `pull-requests: write`.

A job that does not check the code out has no repository on disk, so the `gh` CLI is told which repository to act on through `GH_REPO`, and which token to use through `GH_TOKEN`.

## You get
An empty `.github/workflows/label.yml`. Whatever you type is checked as YAML while you type it, and linted by actionlint when you run it, offline. Nothing is run.

## You return
A workflow named `label`, run when a pull request is opened, that gives its token only `contents: read`, and whose one job, `label`, may also write to pull requests and adds the label `{label}` to the pull request that started it.

## Rules
- `name: label`, and `on.pull_request.types` is exactly `[opened]`
- the workflow's `permissions` is exactly `contents: read`
- exactly one job, `label`, on `ubuntu-latest`, whose `permissions` is exactly `contents: read` and `pull-requests: write`
- its one step is `run: gh pr edit "$NUMBER" --add-label "{label}"`, with exactly three `env` entries: `GH_TOKEN: ${{{{ github.token }}}}`, `GH_REPO: ${{{{ github.repository }}}}` and `NUMBER: ${{{{ github.event.pull_request.number }}}}`

## Hints
### Hint 1
`types` narrows an event to some of its activities:

```yaml
on:
  pull_request:
    types: [opened]
permissions:
  contents: read
```

### Hint 2
A job's own block is the whole of what that job gets:

```yaml
jobs:
  label:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
```

### Hint 3
Values from the event reach the shell through `env`, never written into the command itself:

```yaml
    steps:
      - run: gh pr edit "$NUMBER" --add-label "needs-review"
        env:
          GH_TOKEN: ${{ github.token }}
          GH_REPO: ${{ github.repository }}
          NUMBER: ${{ github.event.pull_request.number }}
```
