---
title: "workflows: run the tests on every push and pull request"
difficulty: easy
minutes: 10
prereqs: []
track: github-actions
tags: [triggers]
kind: workflow
edits: .github/workflows/ci.yml
---
# workflows: run the tests on every push and pull request

*A workflow is a YAML file in `.github/workflows/`. It says when it runs (`on`), where (`runs-on`), and what (`steps`), and GitHub runs it on a fresh virtual machine every time.*

## Read first
- [Workflow syntax: on](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#on): the events a workflow runs on
- [Workflow syntax: jobs](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobs): jobs, `runs-on` and `steps`

## Why
Continuous integration starts with one promise: nothing reaches `main` without the tests passing. GitHub Actions keeps it with a workflow that runs on every push and every pull request.

`on` names the events. `push` with `branches: [main]` runs on commits to main, and `pull_request` with nothing under it runs on every pull request against any branch. A workflow holds one or more **jobs**; each job runs on its own fresh machine, named by `runs-on`, and runs its `steps` in order. A step either runs a shell command with `run`, or runs a published **action** with `uses`, `owner/repo@version`, passing it inputs under `with`.

The machine starts empty, not even with your code on it. `actions/checkout` clones the commit being tested into the working directory, and `actions/setup-python` installs the Python version you name, so every run tests on the same interpreter whatever the runner image ships.

## You get
An empty `.github/workflows/ci.yml`. Whatever you type is checked as YAML while you type it, and linted by actionlint, the checker GitHub users run on their own workflows, when you run it, offline. Nothing is run: there is no runner.

## You return
A workflow named `CI` that runs on pushes to `main` and on every pull request, with one job, `test`, that checks out the code on `ubuntu-latest`, sets up Python {python}, installs `requirements.txt`, and runs `pytest`.

## Rules
- `name: CI`
- `on` has exactly two events: `push` limited to `branches: [main]`, and `pull_request` with nothing under it
- exactly one job, `test`, with `runs-on: ubuntu-latest`
- its steps, in order: `uses: actions/checkout` at any version; `uses: actions/setup-python` at any version, with `python-version: "{python}"` and no other input; `run: pip install -r requirements.txt`; `run: pytest`

## Hints
### Hint 1
`on` is a map of events. An event with no settings is written with nothing after its colon:

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
```

### Hint 2
A job is a key under `jobs`, and its steps are a list:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
```

### Hint 3
A version is a string: `3.10` unquoted is the number 3.1, so always quote it.

```yaml
      - uses: actions/setup-python@v7
        with:
          python-version: "3.13"
      - run: pip install -r requirements.txt
      - run: pytest
```
