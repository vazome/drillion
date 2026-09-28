---
title: "PreSync hooks: migrate the database before the new code starts"
difficulty: medium
minutes: 15
prereqs: [360, 309]
track: argocd
tags: [hooks, job]
kind: manifest
---
# PreSync hooks: migrate the database before the new code starts

*A hook is an object Argo CD runs at a fixed point in a sync instead of keeping it applied. A PreSync Job is how a schema migration runs before the release that needs it.*

## Read first
- [Resource Hooks](https://argo-cd.readthedocs.io/en/stable/user-guide/resource_hooks/): the phases, and the delete policies
- [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/): `backoffLimit` and `restartPolicy`

## Why
A new release often needs a new column. If the Deployment rolls out first, the new pods query a column that does not exist yet; if the migration is left to someone's laptop, it gets forgotten. A **hook** fixes the order inside the sync itself.

The annotation `argocd.argoproj.io/hook: PreSync` turns an object into a hook of the PreSync phase. Argo CD creates it before it applies anything else, waits for it to finish, and only if it succeeded goes on to apply the rest: the Deployment rolls out on a schema that is already migrated. If the Job fails, the sync stops there and the old pods keep serving.

A hook is not kept in sync like everything else, so it needs a rule for when it goes away: `argocd.argoproj.io/hook-delete-policy`, a comma-separated list. `HookSucceeded` deletes the Job once the sync has succeeded, so a cluster does not fill with finished migrations. A failed Job stays, with its pod and its logs, which is exactly what whoever is paged needs to read. `BeforeHookCreation` deletes the last run's Job before the next sync creates a new one. With no policy at all, Argo CD assumes `BeforeHookCreation`; name any policy and that default is gone, so a failed Job under the same name would still be there when the next sync tries to create it. Name both.

The migration runs the release's own image, so the migration code and the app code always come from the same build.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
Two documents: a PreSync Job `{name}-migrate` that runs `{image}` with the arguments `migrate up` against the database at `{db}`, retried at most {retries} times, deleted once it succeeds and replaced by the next sync, and the Deployment `{name}` it prepares for.

## Rules
- two documents: the Job, then the Deployment
- the Job is `apiVersion: batch/v1`, named `{name}-migrate`, with the annotations `argocd.argoproj.io/hook: PreSync` and `argocd.argoproj.io/hook-delete-policy: BeforeHookCreation,HookSucceeded`
- its `spec.backoffLimit` is {retries}, and its pod template has `restartPolicy: Never`
- its one container is named `migrate`, runs `{image}`, has `args: ["migrate", "up"]`, and exactly one environment variable, `DATABASE_HOST` with the value `{db}`
- the Deployment is `apiVersion: apps/v1`, named `{name}`, not a hook, with `replicas: 2`, and a selector and pod template labelled `app: {name}`
- its one container is named `{name}` and runs `{image}`, the same image as the migration

## Hints
### Hint 1
Both annotations go on the Job itself, not on its pod template:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: checkout-migrate
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation,HookSucceeded
```

### Hint 2
A Job's pod must not restart in place, and `backoffLimit` counts the new pods it may try instead:

```yaml
spec:
  backoffLimit: 2
  template:
    spec:
      restartPolicy: Never
```

### Hint 3
`args` replaces the image's `CMD` and keeps its `ENTRYPOINT`, so the release's own binary runs its migrate command:

```yaml
      containers:
        - name: migrate
          image: ghcr.io/acme/checkout:3.2.0
          args: ["migrate", "up"]
          env:
            - name: DATABASE_HOST
              value: checkout-db
```
