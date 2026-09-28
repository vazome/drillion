---
title: "AppProjects: what a team's Applications are allowed to touch"
difficulty: hard
minutes: 20
prereqs: [357, 312]
track: argocd
tags: [security, multi-document]
kind: manifest
---
# AppProjects: what a team's Applications are allowed to touch

*An Application can deploy anything its project allows. The `default` project allows everything, so each team gets a project of its own that allows only what the team needs.*

## Read first
- [Projects](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/): source repositories, destinations, and the resource allow and deny lists
- [Declarative Setup: Projects](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/#projects): the AppProject object

## Why
Once teams write their own Applications, an Application is a way into the cluster: point one at any repository and any namespace, and Argo CD, which runs with cluster-admin rights, deploys whatever it finds. The **AppProject** is where that stops. Argo CD refuses to sync an Application that leaves its project's limits, whoever wrote it.

A project limits three things. `sourceRepos` lists the repositories its Applications may deploy from. `destinations` lists the clusters and namespaces they may deploy to, and a namespace may be a pattern, so `payments-*` covers `payments-dev` and `payments-prod` and nothing else. And two lists limit the kinds of object. Cluster-scoped kinds (Namespaces, ClusterRoles, CRDs) are an **allow** list, `clusterResourceWhitelist`: leave it out and the project may create none of them, which is right for a product team. Namespaced kinds are a **deny** list, `namespaceResourceBlacklist`: everything is allowed except what it names, and a team should not be able to delete the ResourceQuota and LimitRange the platform team put in its namespaces.

Because the project may create no Namespace, its Applications cannot use `CreateNamespace=true`: the platform team creates the namespaces, and the team deploys into them.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against Argo CD's own schema when you run it, offline.

## You return
Two documents: an AppProject `{team}` that may deploy only from `{repo}`, only into namespaces matching `{team}-*` in the cluster Argo CD runs in, no cluster-scoped objects, and never a ResourceQuota or LimitRange; and the team's Application `{app}` in that project, deploying `apps/{app}` at `main` into `{namespace}`.

## Rules
- two documents: the AppProject, then the Application
- the AppProject is `apiVersion: argoproj.io/v1alpha1`, named `{team}`, in `metadata.namespace: argocd`
- its `sourceRepos` is exactly `[{repo}]`
- its `destinations` is exactly one entry, `server: https://kubernetes.default.svc` and `namespace: {team}-*`
- it has no `clusterResourceWhitelist`, or an empty one
- its `namespaceResourceBlacklist` is exactly two entries, `group: ""` with `kind: ResourceQuota`, and `group: ""` with `kind: LimitRange`
- the Application is named `{app}`, in `metadata.namespace: argocd`, with `spec.project: {team}`, source `repoURL: {repo}`, `targetRevision: main`, `path: apps/{app}`, and destination `server: https://kubernetes.default.svc`, `namespace: {namespace}`
- the Application syncs itself with `prune: true` and `selfHeal: true`, and has no `CreateNamespace=true`

## Hints
### Hint 1
A project's lists are plain YAML lists. A destination names its cluster by `server` and its namespace by name or by pattern:

```yaml
spec:
  sourceRepos:
    - https://github.com/acme/payments-deploy.git
  destinations:
    - server: https://kubernetes.default.svc
      namespace: payments-*
```

### Hint 2
Each entry of a resource list is a group and a kind. The core group, where ResourceQuota lives, is the empty string:

```yaml
  namespaceResourceBlacklist:
    - group: ""
      kind: ResourceQuota
```

### Hint 3
The Application joins the project by name, and its destination has to fall inside the project's:

```yaml
spec:
  project: payments
  destination:
    server: https://kubernetes.default.svc
    namespace: payments-prod
```
