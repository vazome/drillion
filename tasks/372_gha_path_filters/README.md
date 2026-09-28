---
title: "path filters and manual runs: one service's workflow in a monorepo"
difficulty: medium
minutes: 15
prereqs: [371]
track: github-actions
tags: [triggers, inputs]
kind: workflow
edits: .github/workflows/service.yml
---
# path filters and manual runs: one service's workflow in a monorepo

*In a repository that holds many services, each service's workflow should run when that service changes, and on demand, and not on every commit to anything.*

## Read first
- [Workflow syntax: on.push.paths](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onpushpull_requestpull_request_targetpathspaths-ignore): which files a push has to touch
- [Workflow syntax: on.workflow_dispatch.inputs](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onworkflow_dispatchinputs): a Run workflow button with a form

## Why
A monorepo with twenty services and one workflow per service would start twenty workflows on every commit. **Path filters** stop that: under `push` and `pull_request`, `paths` lists glob patterns, and the workflow runs only when the commit touches a file that matches one. `**` matches any depth, so `services/cart/**` is everything under that folder. List the workflow file itself too, so a change to how the service is built is tested by the build it changes.

`branches` and `paths` together must both match: a push to main that touches the service.

`workflow_dispatch` adds a Run workflow button, and its `inputs` become a form. A `choice` input offers fixed `options` and a `default`, so nobody can type `prodution`. The value is read as an expression, `inputs.environment`, and on a push or a pull request no form was filled in, so it is empty: `inputs.environment || 'staging'` falls back to staging. Passing it through `env` rather than writing the expression inside `run` keeps the shell from ever reading it as code.

## You get
An empty `.github/workflows/service.yml`. Whatever you type is checked as YAML while you type it, and linted by actionlint when you run it, offline. Nothing is run.

## You return
A workflow named `{svc}` that runs on pushes to `main` and on pull requests only when `services/{svc}/` or the workflow itself changes, and by hand with a choice of environment, and whose one job tests and deploys the service.

## Rules
- `name: {svc}`
- `on.push` has `branches: [main]` and `paths: ["services/{svc}/**", ".github/workflows/service.yml"]`
- `on.pull_request` has the same `paths` and nothing else
- `on.workflow_dispatch.inputs.environment` is `type: choice`, with `options: [staging, production]` and `default: staging`
- nothing else under `on`
- exactly one job, `build`, on `ubuntu-latest`, with three steps: `actions/checkout` at any version; `run: make -C services/{svc} test`; and `run: make -C services/{svc} deploy` with exactly one `env` entry, `TARGET: ${{{{ inputs.environment || 'staging' }}}}`

## Hints
### Hint 1
`paths` sits beside `branches` under the event. Quote a pattern that starts with `*` or holds one, to be safe:

```yaml
on:
  push:
    branches: [main]
    paths:
      - "services/cart/**"
      - ".github/workflows/service.yml"
```

### Hint 2
A choice input is a small form field:

```yaml
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, production]
        default: staging
```

### Hint 3
An expression in a value is written in `${{ }}`. `||` gives the right-hand side when the left is empty:

```yaml
      - run: make -C services/cart deploy
        env:
          TARGET: ${{ inputs.environment || 'staging' }}
```
