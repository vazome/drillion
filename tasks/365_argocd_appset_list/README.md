---
title: "ApplicationSets: one template, an Application per environment"
difficulty: medium
minutes: 18
prereqs: [358]
track: argocd
tags: [generators, templates]
kind: manifest
---
# ApplicationSets: one template, an Application per environment

*An ApplicationSet is an Application template plus a generator that fills it in. A list generator turns three environments into three Applications that cannot drift apart.*

## Read first
- [List Generator](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Generators-List/): elements and the parameters they make
- [Go Template](https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/GoTemplate/): `goTemplate`, and why `missingkey=error`

## Why
The same service usually runs three times: in dev, in staging, in production, each on its own AKS cluster. Three hand-written Applications are three copies to keep in step, and sooner or later one of them points at the wrong folder. An **ApplicationSet** holds one `template` of an Application and a list of `generators`, and the ApplicationSet controller writes one Application for every set of parameters a generator produces.

The **list generator** is the plainest: its `elements` are written out by hand, and each element's keys become parameters. An element with `env` and `url` gives the template the parameters env and url, used in the template as Go template expressions: the variable, a dot and the key, in double curly braces.

Two settings make the templates safe. `goTemplate: true` switches on Go templates, the same language Helm uses. And `goTemplateOptions: ["missingkey=error"]` makes a misspelt parameter an error; without it, a typo quietly renders as an empty string, and an Application deploys to the namespace `-checkout` or the path `apps/checkout/envs/`.

The template also needs one Application name per element, so the environment has to be part of the name. Three elements with one name would be one Application overwritten three times.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against Argo CD's own schema when you run it, offline. The ApplicationSet is not expanded: the grader reads the generator and the template.

## You return
One ApplicationSet, `{app}`, whose list generator has the environments `dev`, `staging` and `prod` with their clusters, and whose template makes, for each, an Application `{name_tpl}` that deploys `{path_tpl}` of `{repo}` at `main` to that environment's cluster, in the namespace `{app}`, syncing itself.

## Rules
- `apiVersion: argoproj.io/v1alpha1`, `kind: ApplicationSet`, `metadata.name: {app}`, `metadata.namespace: argocd`
- `spec.goTemplate: true` and `spec.goTemplateOptions: ["missingkey=error"]`
- `spec.generators` is exactly one list generator, whose `elements` are exactly these three, each with the keys `env` and `url`:
  - `env: dev`, `url: {dev_url}`
  - `env: staging`, `url: {staging_url}`
  - `env: prod`, `url: {prod_url}`
- `spec.template.metadata.name: '{name_tpl}'`
- `spec.template.spec`: `project: default`, source `repoURL: {repo}`, `targetRevision: main`, `path: '{path_tpl}'`
- its destination is `server: '{{{{.url}}}}'` and `namespace: {app}`
- its `syncPolicy.automated` has `prune: true` and `selfHeal: true`, and `syncOptions` is exactly `["CreateNamespace=true"]`

## Hints
### Hint 1
The generator is a list of generators, and the list generator's elements are free-form maps:

```yaml
spec:
  goTemplate: true
  goTemplateOptions: ["missingkey=error"]
  generators:
    - list:
        elements:
          - env: dev
            url: https://aks-dev-weu.hcp.westeurope.azmk8s.io:443
```

### Hint 2
A value that starts with `{` must be quoted, or YAML reads it as the start of a map and the file does not parse:

```yaml
  template:
    metadata:
      name: '{{.env}}-checkout'
```

### Hint 3
`template.spec` is an Application's spec, with parameters wherever a value differs per element:

```yaml
    spec:
      project: default
      source:
        repoURL: https://github.com/acme/platform-gitops.git
        targetRevision: main
        path: 'apps/checkout/envs/{{.env}}'
      destination:
        server: '{{.url}}'
        namespace: checkout
```
