---
title: "least privilege: a ServiceAccount that can read one thing"
difficulty: hard
minutes: 20
prereqs: [269]
track: kubernetes
tags: [security, multi-document]
kind: manifest
---
# least privilege: a ServiceAccount that can read one thing

*A pod that talks to the Kubernetes API does it as a ServiceAccount. What that account may do is written in a Role, and a RoleBinding is what hands the Role to it.*

## Read first
- [Using RBAC Authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/): Role, RoleBinding, and how a rule is read
- [Service Accounts](https://kubernetes.io/docs/concepts/security/service-accounts/): the identity a pod runs as

## Why
Some apps need the Kubernetes API: a controller that watches ConfigMaps, a job that lists pods, a dashboard. The quick way to make that work is a ClusterRole with `"*"` everywhere, and then any bug in that app is a bug with the keys to the cluster.

RBAC splits the grant into three objects. A **ServiceAccount** is the identity, and a pod names it in `serviceAccountName`. A **Role** is a list of permissions inside one namespace: which API groups, which resources, which verbs. A **RoleBinding** says "this subject gets that Role". None of them does anything alone, and the split is what lets one Role be reused for many accounts.

A rule is read as a sentence: for these `apiGroups`, on these `resources`, allow these `verbs`. The core group, where pods, ConfigMaps and Secrets live, is written as the empty string `""`. Reading is three verbs: `get` one, `list` many, `watch` for changes. Anything else, `create`, `update`, `patch` or `delete`, is writing, and an app that only reads should never have it.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
Three documents in one file, in the namespace `{namespace}`: a ServiceAccount `{account}`, a Role `{role}` that may only read `{resource}`, and a RoleBinding `{role}` that gives that Role to that ServiceAccount.

## Rules
- three YAML documents, separated by `---`: the ServiceAccount, then the Role, then the RoleBinding. Each has `metadata.namespace: {namespace}`
- the ServiceAccount is `apiVersion: v1`, named `{account}`
- the Role is `apiVersion: rbac.authorization.k8s.io/v1`, named `{role}`, with exactly one rule: `apiGroups: [""]`, `resources: [{resource}]`, and the verbs `get`, `list` and `watch`, no others
- the RoleBinding is `apiVersion: rbac.authorization.k8s.io/v1`, named `{role}`. Its `roleRef` is `apiGroup: rbac.authorization.k8s.io`, `kind: Role`, `name: {role}`
- its `subjects` has exactly one entry: `kind: ServiceAccount`, `name: {account}`, `namespace: {namespace}`

## Hints
### Hint 1
The ServiceAccount is almost nothing, which is the point: it is a name.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: config-reader
  namespace: shop
```

### Hint 2
The Role's rules are a list, and each field in a rule is a list too:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: config-reader
  namespace: shop
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list", "watch"]
```

### Hint 3
The binding points at the Role with `roleRef`, which cannot be changed after the binding exists, and at the account with `subjects`. A ServiceAccount subject needs its namespace, even the binding's own:

```yaml
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: config-reader
subjects:
  - kind: ServiceAccount
    name: config-reader
    namespace: shop
```
