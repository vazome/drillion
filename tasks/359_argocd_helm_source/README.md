---
title: "Helm charts in Argo CD: a chart, a version and its values"
difficulty: medium
minutes: 15
prereqs: [358, 279]
track: argocd
tags: [values]
kind: manifest
---
# Helm charts in Argo CD: a chart, a version and its values

*Most of what runs on a cluster besides your own apps (cert-manager, external-secrets, the ingress controller) is someone else's Helm chart. Argo CD installs one straight from its Helm repository.*

## Read first
- [Helm](https://argo-cd.readthedocs.io/en/stable/user-guide/helm/): a chart as a source, `releaseName`, and values
- [Sync Options: Server-Side Apply](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/#server-side-apply): why big charts need it

## Why
A source does not have to be a folder in git. When `repoURL` is a Helm repository, `chart` names the chart in it and `targetRevision` is the chart's **version**, not a branch. Pin it: a chart that moves under you is an upgrade nobody reviewed.

Argo CD does not run `helm install`. It runs `helm template` and applies what comes out, so `helm list` shows nothing, and the release name only matters because charts put it into the names of what they create. `helm.releaseName` sets it; left out, it is the Application's name.

The values go in `helm.valuesObject`, as YAML under the key, rather than in `helm.values`, which is the same thing written as one string that no editor or schema can check.

Charts like these ship CustomResourceDefinitions, and a big CRD does not fit in the `last-applied-configuration` annotation a client-side apply writes, so the sync fails with "metadata.annotations: Too long". `ServerSideApply=true` has the API server track field ownership instead, and the problem goes away.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against Argo CD's own schema when you run it, offline.

## You return
One Application, `{chart}`, that installs the chart `{chart}` at version `{version}` from `{repo}` as the release `{chart}`, into the namespace `{chart}`, with `replicaCount` set to `{replicas}`, and syncs itself.

## Rules
- `apiVersion: argoproj.io/v1alpha1`, `kind: Application`, `metadata.name: {chart}`, `metadata.namespace: argocd`, `spec.project: default`
- `spec.source` has `repoURL: {repo}`, `chart: {chart}` and `targetRevision: {version}`, and no `path`
- `spec.source.helm.releaseName: {chart}`
- `spec.source.helm.valuesObject` is exactly `replicaCount: {replicas}`, and there is no `helm.values` string
- `spec.destination`: `server: https://kubernetes.default.svc`, `namespace: {chart}`
- `spec.syncPolicy.automated` has `prune: true` and `selfHeal: true`, and `syncOptions` is exactly `["CreateNamespace=true", "ServerSideApply=true"]`

## Hints
### Hint 1
A chart source has `chart` where a git source has `path`, and its `targetRevision` is the chart's version:

```yaml
  source:
    repoURL: https://charts.jetstack.io
    chart: cert-manager
    targetRevision: v1.18.2
```

### Hint 2
Values are written as YAML under `valuesObject`. A dotted key in the docs, `controller.replicaCount`, is a nested map here:

```yaml
    helm:
      releaseName: ingress-nginx
      valuesObject:
        controller:
          replicaCount: 2
```

### Hint 3
Both options go in the one list, each `Name=value`:

```yaml
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
```
