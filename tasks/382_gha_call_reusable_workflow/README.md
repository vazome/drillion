---
title: "calling a reusable workflow: one release, two environments"
difficulty: medium
minutes: 15
prereqs: [381, 378]
track: github-actions
tags: [reusable-workflows, needs]
kind: workflow
edits: .github/workflows/release.yml
---
# calling a reusable workflow: one release, two environments

*The platform team wrote the deploy once. Your release calls it twice, staging then production, and hands it the permissions it needs.*

## Read first
- [Reuse workflows: calling a reusable workflow](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows#calling-a-reusable-workflow): `uses`, `with`, and `needs` between called jobs
- [Reuse workflows: access and permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/reusable-workflows#access-and-permissions-for-reusable-workflows): why the caller's token limits the callee's

## Why
A job that calls a reusable workflow has no `runs-on` and no `steps`. It has `uses`, the path of the workflow, and `with`, its inputs, and otherwise it behaves like any job: it can `needs` another, so production is only deployed once staging succeeded.

The one surprise is permissions. A called workflow runs with the caller's token, and it can only narrow it, never widen it. The deploy workflow beside your file asks for `id-token: write` to sign in to Azure with OIDC. If your workflow does not grant that, the called job asks for more than it was handed, and the run fails before it starts. So the caller grants, at the top, exactly what the callee needs: `contents: read` and `id-token: write`.

A release is started by pushing a tag, and `github.ref_name` is the tag's short name, `v2.4.0`, which is the image tag the build pushed.

## You get
An empty `.github/workflows/release.yml`, and beside it `.github/workflows/deploy.yml`, read-only: the reusable deploy your workflow calls. Whatever you type is linted by actionlint, together with the deploy workflow, when you run it, offline. Nothing is run.

## You return
A workflow named `release`, run when a tag starting with `v` is pushed, that grants its token what the deploy needs, and calls the deploy for `staging` and then, once that succeeded, for `production`, both with the pushed tag as the image tag.

## Rules
- `name: release`, and `on` is exactly `push` with `tags: ["v*"]`
- the workflow's `permissions` is exactly `contents: read` and `id-token: write`
- exactly two jobs, `staging` and `production`, each with `uses: ./.github/workflows/deploy.yml` and no `runs-on` or `steps`
- `staging`'s `with` is exactly `environment: staging` and `image-tag: ${{{{ github.ref_name }}}}`, and it needs nothing
- `production`'s `with` is exactly `environment: production` and `image-tag: ${{{{ github.ref_name }}}}`, and it has `needs: staging`

## Hints
### Hint 1
A tag filter sits under `push`, where `branches` would:

```yaml
on:
  push:
    tags: ["v*"]
permissions:
  contents: read
  id-token: write
```

### Hint 2
A calling job is three keys:

```yaml
jobs:
  staging:
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging
      image-tag: ${{ github.ref_name }}
```

### Hint 3
`needs` works between calling jobs as between any others.
