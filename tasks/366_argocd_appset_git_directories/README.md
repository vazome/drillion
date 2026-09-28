---
title: "ApplicationSets from git: an Application for every folder"
difficulty: medium
minutes: 15
prereqs: [365]
track: argocd
tags: [generators, templates]
kind: manifest
---
# ApplicationSets from git: an Application for every folder

*The git directory generator reads the repository itself: every folder that matches a pattern becomes an Application, so adding a service is adding a folder.*

## Read first
- [Git Generator: directories](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Generators-Git/#git-generator-directories): the pattern, the exclude, and the path parameters

## Why
A list generator still needs someone to edit the list. The **git directory generator** needs no one: it scans a repository at a revision, and every directory that matches a `path` pattern yields one set of parameters. A team that wants a new service deployed opens a pull request adding `apps/<service>/`, and once it merges the ApplicationSet writes the Application for it. Deleting the folder removes the Application.

Each matched directory gives the template its path as parameters: `.path.path` is the whole path inside the repository, and `.path.basename` is its last segment, which makes a natural Application name and namespace.

A pattern like `apps/*` matches every folder, including the one that is half migrated or being retired. A second entry with `exclude: true` removes a folder from the match, and an exclude always wins over an include, whatever order they are written in.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against Argo CD's own schema when you run it, offline. The ApplicationSet is not expanded: the grader reads the generator and the template.

## You return
One ApplicationSet, `{name}`, that makes an Application for every folder under `{root}/` of `{repo}` at `main` except `{root}/{skipped}`. Each Application is named after its folder, deploys that folder into a namespace of the same name in the cluster Argo CD runs in, and syncs itself.

## Rules
- `apiVersion: argoproj.io/v1alpha1`, `kind: ApplicationSet`, `metadata.name: {name}`, `metadata.namespace: argocd`
- `spec.goTemplate: true` and `spec.goTemplateOptions: ["missingkey=error"]`
- `spec.generators` is exactly one git generator with `repoURL: {repo}` and `revision: main`
- its `directories` are exactly two: `path: {root}/*`, and `path: {root}/{skipped}` with `exclude: true`
- `spec.template.metadata.name: '{{{{.path.basename}}}}'`
- `spec.template.spec`: `project: default`, source `repoURL: {repo}`, `targetRevision: main`, `path: '{{{{.path.path}}}}'`
- its destination is `server: https://kubernetes.default.svc` and `namespace: '{{{{.path.basename}}}}'`
- its `syncPolicy.automated` has `prune: true` and `selfHeal: true`, and `syncOptions` is exactly `["CreateNamespace=true"]`

## Hints
### Hint 1
The git generator names the repository and revision it scans, then the patterns:

```yaml
  generators:
    - git:
        repoURL: https://github.com/acme/platform-gitops.git
        revision: main
        directories:
          - path: apps/*
```

### Hint 2
An exclude is a second entry in the same list, naming the folder:

```yaml
          - path: apps/legacy-billing
            exclude: true
```

### Hint 3
The folder's name serves twice, as the Application and as its namespace, and its full path is the source:

```yaml
  template:
    metadata:
      name: '{{.path.basename}}'
    spec:
      source:
        path: '{{.path.path}}'
      destination:
        namespace: '{{.path.basename}}'
```
