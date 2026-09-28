---
title: "canary releases: a Rollout that moves traffic in steps"
difficulty: hard
minutes: 20
prereqs: [268]
track: argocd
tags: [canary, workloads]
kind: manifest
---
# canary releases: a Rollout that moves traffic in steps

*A Deployment replaces every pod as fast as it safely can. An Argo Rollout replaces them in steps you write down, and stops where you tell it to, so a bad release reaches a few users instead of all of them.*

## Read first
- [Canary Deployment Strategy](https://argoproj.github.io/argo-rollouts/features/canary/): steps, weights and pauses
- [Rollout Specification](https://argoproj.github.io/argo-rollouts/features/specification/): every field a Rollout has

## Why
A Deployment's rolling update only knows that pods are ready; it cannot know that the new version returns wrong prices. Progressive delivery puts the new version in front of a slice of traffic first, and moves on only when that slice looks healthy.

Argo Rollouts adds a **Rollout** object: a Deployment's `replicas`, `selector` and pod `template`, with a `strategy` a Deployment does not have. Under `strategy.canary.steps`, each step does exactly one thing. `setWeight` sends that percentage of traffic to the new version; `pause` with a `duration` waits that long, and a `pause` with no duration, an empty map, waits until someone promotes the rollout by hand, `kubectl argo rollouts promote`. After the last step, the new version takes all of it.

Without a service mesh or an ingress controller that can split traffic, a weight is carried out by pod counts: at 10 replicas, `setWeight: 20` runs 2 new pods beside 8 old ones. So choose replicas that divide into your weights. A weight is a percentage, 0 to 100, and Argo Rollouts refuses anything else; its schema does not, which is why the grader checks it.

The selector has to match the template's labels, exactly as for a Deployment, or the controller refuses the Rollout.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the Argo Rollouts schema when you run it, offline. Nothing rolls out: the steps are read, not run.

## You return
One Rollout, `{name}`, with {replicas} replicas of `{image}`, that sends {first}% of traffic to a new version, waits {pause}, sends {second}%, then waits for someone to promote it.

## Rules
- `apiVersion: argoproj.io/v1alpha1`, `kind: Rollout`, `metadata.name: {name}`
- `spec.replicas: {replicas}`, and a `spec.selector.matchLabels` of `app: {name}` that matches the pod template's labels
- the pod template has one container, named `{name}`, running `{image}`
- `spec.strategy.canary.steps` is exactly four steps, in this order: `setWeight: {first}`, a pause of `duration: {pause}`, `setWeight: {second}`, and a pause with no duration
- each step does exactly one thing, and every weight is between 0 and 100

## Hints
### Hint 1
The top of a Rollout is a Deployment's, with another `apiVersion` and `kind`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: checkout
spec:
  replicas: 10
  selector:
    matchLabels:
      app: checkout
```

### Hint 2
The steps are a list of one-key maps. A duration is a string with a unit:

```yaml
  strategy:
    canary:
      steps:
        - setWeight: 20
        - pause:
            duration: 5m
```

### Hint 3
An empty pause waits for a human. Written as a flow map, it is two characters:

```yaml
        - setWeight: 50
        - pause: {}
```
