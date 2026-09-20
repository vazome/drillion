---
title: "one Pod, no controller: the smallest object that runs anything"
difficulty: easy
minutes: 10
prereqs: [268]
track: kubernetes
tags: [kubernetes, pod, containers]
kind: manifest
---
# one Pod, no controller: the smallest object that runs anything

*Every controller in Kubernetes exists to stamp out Pods. Before you let one, write a Pod yourself and see exactly what it is they have been abstracting away.*

## Read first
- [Pods](https://kubernetes.io/docs/concepts/workloads/pods/): the pod and what `spec.containers` needs
- [Pod API reference](https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/pod-v1/): the schema every field is checked against

## Why
A Pod is one address, one filesystem for its containers to share, and one localhost. Anything that runs on Kubernetes runs inside one, and every workload object you will ever write carries a Pod inside it as a template.

Written bare, a Pod is small enough to see whole. It has a name under `metadata`, and a `spec` whose `containers` is a list, because a Pod may hold several. Each container needs a `name` of its own, an `image` to run, and optionally a `ports` list saying which ports it listens on. That last part declares nothing and opens nothing; it is documentation other objects and other people read, and it is where the first type mistake happens, because a port is a number and the schema refuses the quoted kind.

One more thing worth noticing while it is fresh: `apiVersion` here is `v1` with no group in front of it. A Pod is a core object. A Deployment needed `apps/v1` because it lives in the apps group, and the object you write next decides its own answer.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Pod: named `{name}`, running the image `{image}`, declaring that it listens on port `{port}`.

## Rules
- one YAML document, one Pod, nothing else in the file
- `apiVersion` is `v1`. A Pod is a core object, so no group goes in front
- exactly one container, and it needs a `name` of its own as well as the `image`
- the container declares the port above under `ports`, as a `containerPort` with no quotes
- the Pod's name and the container's name may be the same word. Most real manifests make them so

## Hints
### Hint 1
Four keys at the top, and everything else hangs off the fourth:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ...
spec:
  ...
```

The only difference from a Deployment's skeleton is that `apiVersion` lost its group. Everything under `spec` is the pod itself.

### Hint 2
`containers` is a list, so its entries are dashes. One container, three fields:

```yaml
spec:
  containers:
    - name: something
      image: some/image:tag
      ports:
        - containerPort: 80
```

`containerPort` has no `port:` around it and no quotes around the number. It sits inside a `ports` list because a container may listen on several.

### Hint 3
The same list, one object over. When you wrote your Deployment, its `spec.template.spec.containers` was exactly this list, handed over unchanged. That is the pattern worth more than this task: a controller does not replace a pod spec, it wraps one and adds a counter around it.
