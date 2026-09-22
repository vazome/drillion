---
title: "a DaemonSet has no replicas: one per node, and that is the whole point"
difficulty: medium
minutes: 18
prereqs: [268]
track: kubernetes
tags: [workloads]
kind: manifest
---
# a DaemonSet has no replicas: one per node, and that is the whole point

*Log shippers, metric collectors, network agents: one of these has to run on every machine, and "how many?" is not a number you get to answer.*

## Read first
- [DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/): one pod per node, no replica count

## Why
Every controller so far answered the question "how many?". A Deployment counts replicas against `spec.replicas`. A StatefulSet does the same, with names. A DaemonSet refuses the question: it puts exactly one pod on every node in the cluster, and when a node joins, one starts there; when a node leaves, its pod goes with it. The size of the fleet is the size of the cluster, which is a number the controller reads from the world and never from the manifest.

Which is why the field you most want to write is not there. Copy a Deployment and add `spec.replicas: 3` to a DaemonSet, and the schema refuses the whole field: a DaemonSet's spec has no `replicas` key at all. That refusal is the task. The muscle to build is noticing that a controller's spec is a contract about what it decides, and a DaemonSet's contract is that you decide nothing about the count.

The rest of the anatomy you know cold, because it is the Deployment's: `selector` and `template` with matching labels, containers as a list. What the template holds changes with the job. DaemonSets run the per-node furniture of a cluster, the log shipper that tails every node's logs, the exporter that reports every node's metrics, and their images are agent images, small and always-on.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One DaemonSet: named `{name}`, putting one pod per node running the image `{image}`.

## Rules
- one YAML document, one DaemonSet, nothing else in the file
- `apiVersion` is `apps/v1`. Like a Deployment and a StatefulSet, it lives in the apps group
- no `replicas` anywhere in the file. There is no such field to set
- the selector and the pod template labels agree on `app: {name}`, as in every controller
- exactly one container, named `{name}`, running the image above

## Hints
### Hint 1
A Deployment's skeleton, minus the one field it does not have:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: ...
spec:
  selector: ...
  template: ...
```

If you are reaching for `replicas` after `spec:`, that reaching is the lesson. The kind decides what the spec may say.

### Hint 2
The template is the Deployment's, word for word:

```yaml
  selector:
    matchLabels:
      app: node-log
  template:
    metadata:
      labels:
        app: node-log
    spec:
      containers:
        - name: node-log
          image: fluent/fluentd:v1.17
```

Same agreement as always: the selector reads the labels the template writes.

### Hint 3
Why the agents live this way. A log shipper can only ship the logs of the machine it sits on, so "three of them somewhere" is useless; it must be one everywhere. The same holds for anything that touches the node itself: monitoring, networking, disk management. When a fourth node joins, nobody edits a manifest. The DaemonSet noticed, and the node has its agent before it finished joining.
