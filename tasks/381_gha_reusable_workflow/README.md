---
title: "reusable workflows: write the one every service calls"
difficulty: hard
minutes: 25
prereqs: [376]
track: github-actions
tags: [reusable-workflows, inputs]
kind: workflow
edits: .github/workflows/build-image.yml
---
# reusable workflows: write the one every service calls

*Twenty services copying the same build job is twenty places to fix one bug. A reusable workflow is written once, called like a job, and takes inputs, secrets and outputs like a function.*

## Read first
- [Reuse workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows): `workflow_call`, inputs, secrets and outputs
- [Workflow syntax: on.workflow_call](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onworkflow_call): the declaration, field by field

## Why
A platform team owns how images are built: which registry, which tags, which cache. A **reusable workflow** is where that lives. It runs on `workflow_call`, and another workflow calls it as a job with `uses: ./.github/workflows/<file>` in place of `runs-on` and `steps`.

Its `workflow_call` block is its signature. `inputs` are typed parameters, `string`, `number` or `boolean`, and `required` makes the caller pass one. `secrets` are declared separately, since a secret is never an input: the caller hands them over under `secrets`, and the callee reads them through the `secrets` context under the name it declared. `outputs` hand a value back, and they climb in two steps: a step writes an output, the job exposes it under `jobs.<job>.outputs`, and `workflow_call.outputs` exposes the job's under a name the caller reads as `needs.<job>.outputs.<name>`.

Calling it wrong is a lint error rather than a failed run: actionlint reads the caller beside your file and checks every input, secret and output the caller uses against what yours declares.

## You get
An empty `.github/workflows/build-image.yml`, and beside it `.github/workflows/ci.yml`, read-only: the workflow that calls yours, and what it expects of it. Whatever you type is linted by actionlint, together with the caller, when you run it, offline. Nothing is run.

## You return
The reusable workflow `build-image` that `ci.yml` calls: it takes the image name and the build context as required string inputs and the registry password as a required secret, builds and pushes the image to `acmeshop.azurecr.io` tagged with the commit, and hands the pushed image's digest back as `digest`.

## Rules
- `name: build-image`, and `on` is exactly `workflow_call`
- `workflow_call.inputs` is exactly `image` and `context`, each `type: string` and `required: true`
- `workflow_call.secrets` is exactly `REGISTRY_PASSWORD`, `required: true`
- `workflow_call.outputs` is exactly `digest`, with `value: ${{{{ jobs.build.outputs.digest }}}}`
- exactly one job, `build`, on `ubuntu-latest`, whose `outputs` is exactly `digest: ${{{{ steps.push.outputs.digest }}}}`
- its steps, in order: `actions/checkout` at any version; `docker/login-action` at any version with exactly `registry: acmeshop.azurecr.io`, `username: acmeshop` and `password: ${{{{ secrets.REGISTRY_PASSWORD }}}}`; and, with `id: push`, `docker/build-push-action` at any version with exactly `context: ${{{{ inputs.context }}}}`, `push: true` and `tags: acmeshop.azurecr.io/${{{{ inputs.image }}}}:${{{{ github.sha }}}}`

## Hints
### Hint 1
The trigger is the signature. Inputs and secrets are declared in separate maps:

```yaml
on:
  workflow_call:
    inputs:
      image:
        type: string
        required: true
    secrets:
      REGISTRY_PASSWORD:
        required: true
```

### Hint 2
An output climbs from the step to the job to the workflow:

```yaml
    outputs:
      digest:
        value: ${{ jobs.build.outputs.digest }}
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.push.outputs.digest }}
```

### Hint 3
A step is named with `id` so its outputs can be read; `docker/build-push-action` sets `digest` itself:

```yaml
      - id: push
        uses: docker/build-push-action@v7
        with:
          context: ${{ inputs.context }}
          push: true
          tags: acmeshop.azurecr.io/${{ inputs.image }}:${{ github.sha }}
```
