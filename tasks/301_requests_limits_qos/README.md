---
title: requests and limits, and the pods Kubernetes evicts last
difficulty: medium
minutes: 15
prereqs: [268]
track: kubernetes
tags: [kubernetes, deployment, resources, qos]
kind: manifest
---
# requests and limits, and the pods Kubernetes evicts last

*A request is what the scheduler promises you. A limit is where the kernel stops you. Set them equal and your pod is the last one thrown out when a node runs short.*

## Read first
- [Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/): what requests and limits each do
- [Pod Quality of Service Classes](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/): how the two decide who gets evicted

## Why
A container with no resources set runs on whatever the node has spare. The scheduler cannot plan around it, and when the node runs out of memory it is the first thing killed.

`requests` is a reservation. The scheduler only puts the pod on a node that has that much CPU and memory left unpromised, so the pod is guaranteed to get it. `limits` is a ceiling. A container that goes over its CPU limit is slowed down; one that goes over its memory limit is killed on the spot with `OOMKilled`.

How those two compare decides the pod's QoS class. None set: `BestEffort`, evicted first. Requests below limits: `Burstable`, somewhere in the middle. Every container with requests equal to limits, for both CPU and memory: `Guaranteed`, evicted last. A database or a payment service is usually run as Guaranteed on purpose: it gives up bursting in exchange for never being the pod the node gives up.

The units carry over from storage. CPU is in cores, and `500m` is half of one. Memory is in bytes with binary suffixes: `512Mi`, not `512M`.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Deployment named `{name}`, running `{image}`, whose pods land in the `Guaranteed` class with `{cpu}` of CPU and `{memory}` of memory.

## Rules
- one Deployment, `apps/v1`, with a selector and a pod template whose labels agree, and one container running `{image}`
- the container's `resources.requests` sets `cpu: {cpu}` and `memory: {memory}`
- its `resources.limits` sets exactly the same two values, so the pod is Guaranteed
- write the quantities in any form Kubernetes reads as the same amount: `500m` and `0.5` are equal, `1Gi` and `1024Mi` are equal, `1G` is not `1Gi`

## Hints
### Hint 1
`resources` sits on the container, beside `image`, and holds two maps:

```yaml
          resources:
            requests:
              cpu: ...
              memory: ...
            limits:
              cpu: ...
              memory: ...
```

### Hint 2
Quote nothing that is a plain number or a quantity with a suffix; YAML reads `500m` and `512Mi` as strings and Kubernetes parses them. A CPU of one whole core can be written `1` or `1000m`.

### Hint 3
Leave out `requests` and set only `limits`, and Kubernetes copies the limits into the requests for you, so that pod is Guaranteed as well. Writing both is clearer to the next person reading it, which is why the task asks for both.
