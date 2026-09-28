---
title: "needs and if: lint, then test, then deploy only from main"
difficulty: medium
minutes: 15
prereqs: [371]
track: github-actions
tags: [needs, expressions]
kind: workflow
edits: .github/workflows/ci.yml
---
# needs and if: lint, then test, then deploy only from main

*Jobs run in parallel unless told otherwise. `needs` orders them, and `if` decides whether a job runs at all.*

## Read first
- [Workflow syntax: jobs.job_id.needs](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idneeds): order, and what happens when a needed job fails
- [Evaluate expressions in workflows and actions](https://docs.github.com/en/actions/reference/workflows-and-actions/expressions): operators and contexts

## Why
Every job in a workflow starts at once, each on its own machine. That is fast, and wrong for a pipeline: there is no point testing code that does not lint, and deploying code whose tests failed is the thing CI exists to prevent.

`needs` lists the jobs that must succeed first. A job that needs another waits for it, and is skipped if it failed. `needs: [lint, test]` waits for both.

`if` on a job is an expression, and the job runs only when it is true. The `github` context says what started the run: `github.ref` is the branch or tag as a full ref, `refs/heads/main`, and `github.event_name` is the event. A pull request from a branch into main has `github.ref` set to a merge ref, never `refs/heads/main`, so checking both the ref and the event keeps a pull request from ever reaching the deploy. On a job, `if` is always an expression, so it may be written bare, without the dollar-and-braces wrapper a value needs.

## You get
An empty `.github/workflows/ci.yml`. Whatever you type is checked as YAML while you type it, and linted by actionlint when you run it, offline. Nothing is run.

## You return
A workflow named `CI`, run on pushes to `main` and on pull requests, with three jobs on `ubuntu-latest`: `lint`, `test` once lint has passed, and `deploy` once both have passed, only for a push to main.

## Rules
- `name: CI`, and `on` is exactly `push` with `branches: [main]` and `pull_request` with nothing under it
- three jobs, `lint`, `test` and `deploy`, each on `ubuntu-latest`, each with `actions/checkout` at any version as its first step
- `lint`'s second and last step is `run: ruff check .`, and it has no `needs`
- `test` has `needs: lint`, and its second and last step is `run: pytest`
- `deploy` has `needs: [lint, test]`, `if: github.ref == 'refs/heads/main' && github.event_name == 'push'`, and its second and last step is `run: {deploy}`

## Hints
### Hint 1
One job waiting for another is one line; waiting for several is a list:

```yaml
  test:
    needs: lint
  deploy:
    needs: [lint, test]
```

### Hint 2
Strings in an expression take single quotes, and `&&` joins two conditions:

```yaml
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

### Hint 3
Each job starts on its own clean machine, so each checks the code out again:

```yaml
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - run: ruff check .
```
