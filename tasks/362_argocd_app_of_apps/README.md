---
title: "app of apps: one Application that deploys the others"
difficulty: hard
minutes: 20
prereqs: [358, 360]
track: argocd
tags: [gitops, sync-waves]
kind: manifest
---
# app of apps: one Application that deploys the others

*An Application is a Kubernetes object, so Argo CD can deploy Applications too. One root Application pointed at a folder of them brings a whole cluster up from git.*

## Read first
- [Cluster Bootstrapping](https://argo-cd.readthedocs.io/en/stable/operator-manual/cluster-bootstrapping/): the app-of-apps pattern, and why children carry a finalizer
- [Resource Health: Argo CD App](https://argo-cd.readthedocs.io/en/stable/operator-manual/health/#argocd-app): what a wave between Applications does and does not wait for

## Why
A new cluster needs a dozen things before any product runs on it: cert-manager, the ingress controller, external-secrets, then the apps themselves. Creating a dozen Applications by hand is exactly the clicking GitOps was meant to end. Instead, one **root** Application points at a folder in git, `clusters/<cluster>`, and that folder holds the other Applications. Sync the root once and it creates the rest; add a file to the folder and a new app appears.

The root deploys Applications, and Applications live in `argocd`, so the root's destination namespace is `argocd`, whatever namespaces its children deploy into.

Each child carries the finalizer `resources-finalizer.argocd.argoproj.io`. Without it, deleting a child Application (or pruning its file from the folder) deletes only the Application object and leaves everything it deployed running with no owner. With it, Argo CD deletes the child's resources first.

Waves order the children the way they order any object: the platform piece in wave -1, the product in wave 0. One catch: since Argo CD 1.8 an Application's health is not assessed by default, so the wave orders the children but does not wait for the first to be healthy unless the cluster restores that health check in `argocd-cm`. Most app-of-apps setups do, and this task assumes it.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against Argo CD's own schema when you run it, offline.

## You return
Three Applications from `{repo}` at `main`, each syncing itself with prune and self-heal: the root `{root}` that deploys the folder `clusters/{cluster}`, and the two children that folder holds, `{infra}` from `platform/{infra}` into the namespace `{infra}` in wave -1, and `{app}` from `apps/{app}` into the namespace `{app}` in wave 0.

## Rules
- three documents, each `apiVersion: argoproj.io/v1alpha1`, `kind: Application`, `metadata.namespace: argocd`, `spec.project: default`, with `repoURL: {repo}` and `targetRevision: main` in `spec.source`, `server: https://kubernetes.default.svc` in `spec.destination`, and `spec.syncPolicy.automated` with `prune: true` and `selfHeal: true`
- the first is the root, `{root}`: source `path: clusters/{cluster}`, destination `namespace: argocd`, and no finalizer
- the second is `{infra}`: source `path: platform/{infra}`, destination `namespace: {infra}`, the annotation `argocd.argoproj.io/sync-wave: "-1"`, and `syncOptions` exactly `["CreateNamespace=true"]`
- the third is `{app}`: source `path: apps/{app}`, destination `namespace: {app}`, in wave 0, and `syncOptions` exactly `["CreateNamespace=true"]`
- both children have exactly one finalizer, `resources-finalizer.argocd.argoproj.io`

## Hints
### Hint 1
The root is an ordinary Application whose folder happens to hold Applications. Its destination is where those objects live:

```yaml
spec:
  source:
    path: clusters/aks-prod-weu
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
```

### Hint 2
The finalizer is a list under `metadata`, beside the annotations:

```yaml
metadata:
  name: cert-manager
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
  annotations:
    argocd.argoproj.io/sync-wave: "-1"
```

### Hint 3
A wave is a string even when it is negative, and wave 0 needs no annotation at all. Every child still needs its own `syncPolicy`: the root creating it does not sync it.
