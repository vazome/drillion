---
title: a StatefulSet is nothing without its headless Service
difficulty: hard
minutes: 25
prereqs: [268, 272]
track: kubernetes
tags: [kubernetes, statefulset, service, headless]
kind: manifest
---
# a StatefulSet is nothing without its headless Service

*A Deployment's pods are interchangeable. A StatefulSet's pods have names, and the names come from a Service that resolves to nobody in particular.*

## Read first
- [StatefulSet](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/): stable names for stateful workloads
- [Headless Services](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services): `clusterIP: None` and one DNS record per pod

## Why
Databases and queues are not interchangeable the way web servers are. The second replica of a database is not "another database", it is the follower of a specific first, and it has to find that first again after every restart. A StatefulSet is the controller for that: it gives its pods stable names, `ledger-0`, `ledger-1`, `ledger-2`, created in order and replaced by the same name when they die, so that storage and peer lists can be bolted onto the names.

The part that surprises everyone: the StatefulSet cannot hand out those names alone. It is required to be given a Service in `spec.serviceName`, and that Service must be headless, `clusterIP: None`. An ordinary Service would give the pods one shared address and hide them behind it, which is precisely what a StatefulSet exists to prevent. A headless Service resolves to the pods directly, one DNS record each, so `ledger-0.ledger` is a real address the followers can point at. No headless Service, no per-pod DNS, no peers, no cluster.

So this file holds two objects, and the order in it is the order you would apply them: the headless Service first, the StatefulSet that names it second. That dependence is also why the shape will feel familiar and strange at once. Selector, template, matching labels, containers: all of it is your Deployment's anatomy. The two new fields are `serviceName` pointing back at the first document, and the `None` that empties the Service out.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
Two documents in one file: a headless Service named `{name}`, and a StatefulSet named `{name}` running `{replicas}` replicas of `{image}`, whose `serviceName` points at that Service.

## Rules
- two YAML documents, separated by a line holding `---`. The Service first, the StatefulSet second
- the Service is `apiVersion: v1`, with `spec.clusterIP: None` unquoted, a selector of `app: {name}`, and one port entry whose `port` is `{port}`
- the StatefulSet is `apiVersion: apps/v1`, named `{name}`, with `spec.serviceName: {name}` naming the Service in the first document
- the StatefulSet runs `{replicas}` replicas, its selector and pod template labels agree on `app: {name}`, and its one container runs `{image}`
- the per-pod storage of a real StatefulSet, `volumeClaimTemplates`, is left out. That is the next storage task's business

## Hints
### Hint 1
The headless Service is the Service you have written twice already, with one field set to `None`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ledger
spec:
  clusterIP: None
  selector:
    app: ledger
  ports:
    - port: 5432
```

`clusterIP: None` is the whole trick. The Service stops being an address and becomes a directory.

### Hint 2
The StatefulSet, which is a Deployment's skeleton plus `serviceName`:

```yaml
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: ledger
spec:
  serviceName: ledger
  replicas: 3
  selector:
    matchLabels:
      app: ledger
  template:
    metadata:
      labels:
        app: ledger
    spec:
      containers:
        - name: ledger
          image: postgres:17
```

`serviceName` is what makes the pair a pair: it must spell the first document's Service name exactly.

### Hint 3
What the cluster does with the pair, so the fields have a story. The StatefulSet creates `ledger-0` first and waits for it before starting `ledger-1`, because a database follower must know its leader exists. Each pod gets DNS from the headless Service: `ledger-0.ledger` resolves to that one pod and no other. Delete the set and recreate it, and the names come back the same, which is why a volume attached to `ledger-0` last week can be reattached to `ledger-0` this week.
