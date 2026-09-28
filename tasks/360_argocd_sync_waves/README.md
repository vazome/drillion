---
title: "sync waves: the database before the app that needs it"
difficulty: medium
minutes: 18
prereqs: [358, 275]
track: argocd
tags: [sync-waves, multi-document]
kind: manifest
---
# sync waves: the database before the app that needs it

*Argo CD applies everything in one sync in an order of its own. When one object has to be up before another starts, a sync wave says so.*

## Read first
- [Sync Phases and Waves](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/): how the order is decided, and what a wave waits for
- [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/): the database this task starts first

## Why
Inside one sync, Argo CD orders resources by kind: Namespaces first, then ConfigMaps and Secrets, then Services, then Deployments, and StatefulSets after Deployments. That is usually right, and here it is backwards. The API is a Deployment and its database is a StatefulSet, so the API starts first, finds nothing listening, and crash-loops until the database comes up.

A **sync wave** is an annotation, `argocd.argoproj.io/sync-wave`, holding a whole number. Every object without one is in wave 0. Argo CD applies the lowest wave first, waits until everything in it is healthy, and only then moves to the next. Kind order still decides the order inside one wave.

So the database's Service and StatefulSet stay in wave 0, and the API's Deployment goes in wave 1. Argo CD applies the Service and the StatefulSet, waits for the StatefulSet to report its pod ready, then applies the Deployment. A wave only waits for health, so an object that never turns healthy holds every later wave back, and that is the price of the guarantee.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline. Nothing is synced: the order is what the annotations say, assuming each wave turns healthy.

## You return
Three documents: the database's headless Service `{db}` and its StatefulSet `{db}` in wave 0, and the API's Deployment `{name}` in wave 1, which finds the database at the host `{db}`.

## Rules
- three documents, in this order: the Service, the StatefulSet, the Deployment
- the Service is `apiVersion: v1`, named `{db}`, headless (`clusterIP: None`), selects `app: {db}`, and has one port, `5432`
- the StatefulSet is `apiVersion: apps/v1`, named `{db}`, with `serviceName: {db}`, `replicas: 1`, and a selector and pod template labelled `app: {db}`. Its one container is named `{db}` and runs `{db_image}`
- neither the Service nor the StatefulSet has a sync-wave annotation other than `"0"`
- the Deployment is `apiVersion: apps/v1`, named `{name}`, with the annotation `argocd.argoproj.io/sync-wave: "1"`, `replicas: 2`, and a selector and pod template labelled `app: {name}`
- its one container is named `{name}`, runs `{image}`, and has exactly one environment variable, `DATABASE_HOST` with the value `{db}`

## Hints
### Hint 1
The wave is an annotation, and every annotation value is a string. `sync-wave: 1` is a number and the schema refuses it; quote it:

```yaml
metadata:
  name: checkout
  annotations:
    argocd.argoproj.io/sync-wave: "1"
```

### Hint 2
The database half is task 275 again, with one replica and a fixed port:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: checkout-db
spec:
  clusterIP: None
  selector:
    app: checkout-db
  ports:
    - port: 5432
```

### Hint 3
Inside a cluster, a Service's name is a host name, so the API reaches the database by it:

```yaml
      containers:
        - name: checkout
          image: ghcr.io/acme/checkout:3.2.0
          env:
            - name: DATABASE_HOST
              value: checkout-db
```
