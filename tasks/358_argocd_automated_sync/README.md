---
title: "automated sync: let Argo CD apply git, prune and heal"
difficulty: medium
minutes: 12
prereqs: [357]
track: argocd
tags: [sync-policy, drift]
kind: manifest
---
# automated sync: let Argo CD apply git, prune and heal

*With automated sync, a merge to git is the deploy. `prune` removes what git no longer has, and `selfHeal` puts back what someone changed by hand.*

## Read first
- [Automated Sync Policy](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/): what `automated`, `prune` and `selfHeal` each do
- [Sync Options](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/): `CreateNamespace=true` and the rest
- [Application Specification](https://argo-cd.readthedocs.io/en/stable/user-guide/application-specification/): where `retry` sits

## Why
An Application with no `syncPolicy` only tells you it is OutOfSync. Once a team trusts it, `spec.syncPolicy.automated` makes Argo CD apply every new commit on its own, and from then on nobody deploys by hand.

Automated sync on its own is careful in two ways, and both are usually switched on. It never deletes: a Deployment removed from git keeps running in the cluster until `prune: true` lets Argo CD delete it. And it only reacts to git: if someone runs `kubectl scale` or edits a ConfigMap in the cluster, the app shows OutOfSync and stays that way, until `selfHeal: true` makes Argo CD put back what git says. That drift correction is what makes git the only way in.

Two more settings save a page at 3am. `CreateNamespace=true` in `syncOptions` creates the destination namespace when it does not exist, instead of failing the first sync with "namespace not found". And `retry` makes a failed sync try again with a growing wait, since the usual cause (a webhook that is not up yet, a CRD installed a moment later) goes away on its own.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against Argo CD's own schema when you run it, offline.

## You return
One Application, `{name}`, that deploys `{path}` of `{repo}` at `main` into the namespace `{namespace}` of the cluster Argo CD runs in, and keeps it synced on its own: it prunes, heals drift, creates the namespace, and retries a failed sync.

## Rules
- `apiVersion: argoproj.io/v1alpha1`, `kind: Application`, `metadata.name: {name}`, `metadata.namespace: argocd`, `spec.project: default`
- `spec.source`: `repoURL: {repo}`, `targetRevision: main`, `path: {path}`
- `spec.destination`: `server: https://kubernetes.default.svc`, `namespace: {namespace}`
- `spec.syncPolicy.automated` has `prune: true` and `selfHeal: true`
- `spec.syncPolicy.syncOptions` is exactly `["CreateNamespace=true"]`
- `spec.syncPolicy.retry` has `limit: {retries}`, and a `backoff` of `duration: 5s`, `factor: 2` and `maxDuration: 3m`

## Hints
### Hint 1
Everything about when and how Argo CD syncs lives under one key, beside `source` and `destination`:

```yaml
spec:
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Hint 2
Sync options are a list of strings, each written `Name=value`. A typo here is not a schema error, it is an option Argo CD silently ignores, so copy it exactly:

```yaml
    syncOptions:
      - CreateNamespace=true
```

### Hint 3
`retry` counts attempts with `limit` and spaces them with `backoff`: the first wait is `duration`, each next one is multiplied by `factor`, and none is longer than `maxDuration`. The durations are strings with a unit:

```yaml
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```
