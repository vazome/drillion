---
title: "ignoreDifferences: stop fighting the autoscaler over replicas"
difficulty: medium
minutes: 12
prereqs: [358, 308]
track: argocd
tags: [drift, sync-policy]
kind: manifest
---
# ignoreDifferences: stop fighting the autoscaler over replicas

*When something in the cluster owns a field on purpose, Argo CD has to be told to leave it alone, both when it compares and when it syncs.*

## Read first
- [Diffing Customization](https://argo-cd.readthedocs.io/en/stable/user-guide/diffing/): `ignoreDifferences` and JSON pointers
- [Sync Options: Respect ignore differences](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/#respect-ignore-differences-configs): why the diff alone is not enough

## Why
A HorizontalPodAutoscaler changes a Deployment's `spec.replicas` all day, and that is its job. But the chart in git says `replicas: 2`, so the moment the autoscaler scales to 6 the app shows OutOfSync, and with `selfHeal` on, Argo CD scales it back to 2. The two controllers fight, and at peak load the one that wins is the wrong one.

Task 308 fixed this at the source: leave `replicas` out of the manifest. That is the right fix when the manifest is yours. When it is a chart that always renders `replicas`, the fix is on the Application: `spec.ignoreDifferences` names a kind (by group and kind, and optionally a name) and the JSON pointers inside it that Argo CD should not compare. `/spec/replicas` is the field, written as a path.

That only changes the **diff**. When a sync runs for any other reason, Argo CD still applies the manifest as written, replicas and all, and the autoscaler's choice is reset once more. The sync option `RespectIgnoreDifferences=true` makes the sync leave the ignored fields alone too.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against Argo CD's own schema when you run it, offline.

## You return
One Application, `{name}`, that deploys `{path}` of `{repo}` at `main` into `{namespace}`, syncs itself with prune and self-heal, and neither compares nor syncs the replicas of its Deployment `{name}`.

## Rules
- `apiVersion: argoproj.io/v1alpha1`, `kind: Application`, `metadata.name: {name}`, `metadata.namespace: argocd`, `spec.project: default`
- `spec.source`: `repoURL: {repo}`, `targetRevision: main`, `path: {path}`; `spec.destination`: `server: https://kubernetes.default.svc`, `namespace: {namespace}`
- `spec.syncPolicy.automated` has `prune: true` and `selfHeal: true`, and `syncOptions` is exactly `["RespectIgnoreDifferences=true"]`
- `spec.ignoreDifferences` is exactly one entry: `group: apps`, `kind: Deployment`, `name: {name}`, and `jsonPointers: ["/spec/replicas"]`

## Hints
### Hint 1
`ignoreDifferences` is a list under `spec`, one entry per kind of object:

```yaml
spec:
  ignoreDifferences:
    - group: apps
      kind: Deployment
      name: checkout
```

### Hint 2
A JSON pointer is a path from the top of the object, each step after a `/`. The group is the part of `apiVersion` before the slash, so a Deployment's is `apps`:

```yaml
      jsonPointers:
        - /spec/replicas
```

### Hint 3
The sync option goes in the same list as any other, spelt exactly:

```yaml
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - RespectIgnoreDifferences=true
```
