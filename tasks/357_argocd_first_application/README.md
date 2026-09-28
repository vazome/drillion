---
title: "Applications: point Argo CD at a folder in git"
difficulty: easy
minutes: 10
prereqs: [268]
track: argocd
tags: [gitops]
kind: manifest
---
# Applications: point Argo CD at a folder in git

*An Argo CD Application says three things: where the manifests live in git, which cluster and namespace they go to, and which project is allowed to put them there.*

## Read first
- [Declarative Setup: Applications](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/#applications): the Application object, field by field
- [Application Specification](https://argo-cd.readthedocs.io/en/stable/user-guide/application-specification/): every field an Application can carry

## Why
With GitOps, nobody runs `kubectl apply` against production. The manifests live in a git repository, and a controller inside the cluster keeps the cluster looking like that repository. Argo CD is that controller, and an **Application** is how you tell it what to watch.

The Application itself is a Kubernetes object, and it lives in the namespace Argo CD runs in, `argocd`, whatever namespace it deploys to. Its `spec.source` names a repository, a revision (a branch, a tag or a commit) and a path inside it. Its `spec.destination` names a cluster and a namespace: `https://kubernetes.default.svc` is the API server of the cluster Argo CD itself runs in. And `spec.project` names the AppProject whose rules the Application has to stay inside; every install has one called `default`.

An Application with no `syncPolicy` only reports. Argo CD compares git with the cluster and shows Synced or OutOfSync, and nothing changes until someone presses Sync. That is where a team starts, so it can watch what Argo CD would do before it lets it.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against Argo CD's own schema when you run it, offline. Nothing is synced: there is no cluster.

## You return
One Application, `{name}`, that deploys the folder `{path}` of `{repo}` at `{revision}` into the namespace `{namespace}` of the cluster Argo CD runs in, and waits for someone to sync it.

## Rules
- `apiVersion: argoproj.io/v1alpha1`, `kind: Application`, `metadata.name: {name}`, `metadata.namespace: argocd`
- `spec.project: default`
- `spec.source` has `repoURL: {repo}`, `targetRevision: {revision}` and `path: {path}`, and there is no `spec.sources`
- `spec.destination` has `server: https://kubernetes.default.svc` and `namespace: {namespace}`, and no `name`
- no `spec.syncPolicy`: this one syncs when someone presses Sync

## Hints
### Hint 1
The skeleton is the same as any Kubernetes object. What makes it Argo's is the group and the version:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: checkout
  namespace: argocd
```

### Hint 2
The source says where the manifests are. `targetRevision` can be a branch, a tag or a commit SHA:

```yaml
spec:
  project: default
  source:
    repoURL: https://github.com/acme/platform-gitops.git
    targetRevision: main
    path: apps/checkout
```

### Hint 3
The destination says where they go. A cluster is named either by `server` or by `name`, never both, and the in-cluster API server is always at the same address:

```yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: checkout
```
