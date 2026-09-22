---
title: a HorizontalPodAutoscaler, and the requests it measures against
difficulty: hard
minutes: 20
prereqs: [301]
track: kubernetes
tags: [availability, resources, multi-document]
kind: manifest
---
# a HorizontalPodAutoscaler, and the requests it measures against

*"Scale up at 70% CPU" means 70% of what each pod requested. A Deployment with no CPU request gives the autoscaler nothing to divide by, and it never scales at all.*

## Read first
- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/): how the controller decides the replica count
- [HorizontalPodAutoscaler walkthrough](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/): the `autoscaling/v2` object, end to end

## Why
Traffic is not flat. A fixed replica count is either too many pods at night or too few at noon. A HorizontalPodAutoscaler watches a metric across a Deployment's pods and changes the replica count to keep it near a target, between a floor and a ceiling you set.

For CPU, the target is a utilization: a percentage of each pod's CPU request. If the pods request `500m` and the target is 70%, the autoscaler adds pods when they average more than `350m`, and removes them when they average less. Without a CPU request there is no percentage to compute, and the autoscaler reports that it cannot read the metric and leaves the count alone. That is the first thing to check when an HPA "does nothing".

The second is quieter. If the Deployment's manifest also sets `replicas`, every `kubectl apply` of it resets the count to that number, undoing the autoscaler until it catches up again. Once an HPA owns a Deployment, leave `replicas` out of the Deployment and let the HPA's `minReplicas` be the floor.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
Two documents in one file: a Deployment named `{name}` running `{image}` with a CPU request of `{cpu}`, and a HorizontalPodAutoscaler for it that keeps between `{min}` and `{max}` pods at an average of `{target}`% CPU.

## Rules
- two YAML documents, separated by `---`. The Deployment first, the HorizontalPodAutoscaler second
- the Deployment is `apps/v1`, named `{name}`, with a selector and a pod template whose labels agree, and one container running `{image}` with `resources.requests.cpu: {cpu}`
- the Deployment sets no `spec.replicas`: the autoscaler owns that number
- the HPA is `autoscaling/v2`, and its `scaleTargetRef` is `apiVersion: apps/v1`, `kind: Deployment`, `name: {name}`
- `minReplicas: {min}` and `maxReplicas: {max}`
- exactly one metric: `type: Resource`, for `cpu`, with a target of `type: Utilization` and `averageUtilization: {target}`

## Hints
### Hint 1
The HPA points at its Deployment the way a human would: by API group, kind and name.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web
  minReplicas: 2
  maxReplicas: 10
```

### Hint 2
`metrics` is a list, because an HPA can watch several at once and follows whichever asks for the most pods. One CPU metric looks like this:

```yaml
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Hint 3
The request is on the Deployment's container, as in 301. Only `cpu` is needed for this task:

```yaml
          resources:
            requests:
              cpu: 250m
```
