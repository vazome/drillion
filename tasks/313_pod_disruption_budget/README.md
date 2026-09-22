---
title: a PodDisruptionBudget keeps enough pods up while nodes are drained
difficulty: easy
minutes: 10
prereqs: [268]
track: kubernetes
tags: [kubernetes, poddisruptionbudget, availability, labels]
kind: manifest
---
# a PodDisruptionBudget keeps enough pods up while nodes are drained

*Nodes get drained for upgrades all the time. Without a budget, a drain can evict every replica of your app at once, and nothing about the Deployment stops it.*

## Read first
- [Disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/): voluntary and involuntary, and what a budget covers
- [Specifying a Disruption Budget](https://kubernetes.io/docs/tasks/run-application/configure-pdb/): `minAvailable`, `maxUnavailable`, and the selector

## Why
A cluster upgrade drains its nodes one by one: every pod on the node is evicted, and its controller starts a replacement somewhere else. If all three replicas of your API happen to sit on the node being drained, all three go at once, and the API is down until the replacements are ready. The Deployment only notices afterwards.

A PodDisruptionBudget is the rule the drain has to respect. It selects pods by label and says how many of them must stay up: `minAvailable: 2` means an eviction that would leave fewer than two running is refused, and the drain waits and retries until a replacement is ready elsewhere.

It covers voluntary disruptions only: drains, the cluster autoscaler removing a node, an eviction through the API. A node that loses power evicts nothing, it just stops, and no budget helps with that. That is what running several replicas across nodes is for.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One PodDisruptionBudget named `{name}`, for the pods labelled `app: {app}`, that never lets a voluntary disruption leave fewer than `{minimum}` of them running.

## Rules
- one PodDisruptionBudget, `apiVersion: policy/v1`
- `spec.selector.matchLabels` is `app: {app}`, and nothing else
- `spec.minAvailable: {minimum}`, as a number
- no `maxUnavailable`: a budget sets one or the other, never both

## Hints
### Hint 1
The budget is in the `policy` group, and its selector is the same shape as a Deployment's:

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api
spec:
  selector:
    matchLabels:
      app: api
```

### Hint 2
One more line under `spec`. It can also be a percentage in quotes, like `"50%"`; this task asks for the number:

```yaml
  minAvailable: 2
```

### Hint 3
The budget and the Deployment it protects share nothing but the label. It works for any pods with that label, whichever controller made them, so check the selector against the pod template's labels, not the Deployment's name.
