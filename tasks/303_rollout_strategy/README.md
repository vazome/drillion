---
title: "a rollout with no gap: maxSurge, maxUnavailable, minReadySeconds"
difficulty: medium
minutes: 15
prereqs: [299]
track: kubernetes
tags: [deployment, rollout, probes]
kind: manifest
---
# a rollout with no gap: maxSurge, maxUnavailable, minReadySeconds

*By default a Deployment may take a quarter of your pods down while it rolls out a new version. For a service that is already at capacity, that quarter is an outage.*

## Read first
- [Deployments: rolling update](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#rolling-update-deployment): what the two numbers bound
- [minReadySeconds](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#min-ready-seconds): how long a new pod has to stay ready before it counts

## Why
Changing a Deployment's image replaces its pods a few at a time, and two numbers set the pace. `maxUnavailable` is how many of the wanted pods may be missing at once. `maxSurge` is how many extra pods may exist above the wanted count while the new ones come up. Both default to 25%.

With `maxUnavailable: 0`, capacity never drops: the Deployment has to start a new pod, wait for it to be ready, and only then stop an old one. `maxSurge` is what pays for that, in extra pods for the length of the rollout; at 0 as well, nothing could ever move, and the API refuses the pair.

"Ready" comes from the readiness probe, and a pod can pass it once and fall over ten seconds later. `minReadySeconds` makes the Deployment wait that long after a pod turns ready before it counts it as available and moves on. A bad version then stalls the rollout after its first pod, with the old pods still serving, instead of replacing all of them before anyone notices.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Deployment named `{name}`, running `{replicas}` replicas of `{image}`, that rolls out without ever dropping below `{replicas}` ready pods, bringing up at most `{surge}` extra at a time, and trusting a new pod only after it has been ready for `{wait}` seconds.

## Rules
- one Deployment, `apps/v1`, with a selector and a pod template whose labels agree, `replicas: {replicas}`, and one container running `{image}`
- `spec.strategy.type` is `RollingUpdate`
- `spec.strategy.rollingUpdate.maxUnavailable` is `0`, and `maxSurge` is `{surge}`
- `spec.minReadySeconds` is `{wait}`
- the container has a `readinessProbe` of any kind, since "ready" means nothing without one

## Hints
### Hint 1
`strategy` and `minReadySeconds` sit on the Deployment's own `spec`, beside `replicas`, not inside the pod template:

```yaml
spec:
  replicas: 4
  minReadySeconds: 10
  strategy:
    ...
  selector:
    ...
```

### Hint 2
The strategy is a type and, for a rolling update, the two numbers:

```yaml
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

Either number can also be a percentage in quotes, like `"25%"`.

### Hint 3
Any probe the kubelet can run will do here. A TCP probe only checks that the port opens:

```yaml
          readinessProbe:
            tcpSocket:
              port: 8080
```
