---
title: your first Deployment, and the two labels that have to agree
difficulty: easy
minutes: 12
track: kubernetes
tags: [deployment, labels]
kind: manifest
---
# your first Deployment, and the two labels that have to agree

*A Deployment does not run your containers. It runs a template of them, and it finds them again by a label you have to write down twice.*

## Why
The first time you put a service on Kubernetes nobody hands you a form. You get an empty file and a cluster that will tell you what is wrong with it only after you have typed the whole thing.

A Deployment is the object that keeps N copies of your container running. The shape trips people up because it contains two things that look like duplication and are not. `spec.template` is the pod it stamps out, labels and all. `spec.selector` is how the Deployment finds the pods it already stamped out, so that it can count them. If those two disagree, the Deployment creates pods it cannot see, decides it still has zero, and creates more. The API server rejects that outright rather than let it happen, with a message about the selector not matching the template, which is the single most common first error.

The other half of this task is the part no tutorial mentions: a manifest is checked against a schema before anything runs it. A missing `selector`, a `replicas` given as `"3"` instead of `3`, an `apiVersion` of `v1` where `apps/v1` belongs, all of these are refused by the schema and never reach a cluster. Learning to read that refusal is most of learning to write YAML for Kubernetes.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Deployment: named `{name}`, running `{replicas}` replicas of the image `{image}`.

## Rules
- one YAML document, one Deployment, nothing else in the file
- `apiVersion` is `apps/v1`. A Deployment is not a core object and `v1` alone will not find it
- the name goes on the Deployment itself, under `metadata`
- `replicas` is a number, so it carries no quotes
- give the pod template a label, and give `spec.selector.matchLabels` the same label, with the same value. Any key works as long as both sides say it
- exactly one container, and its `image` is the one named above. The container needs a `name` of its own as well
- the container name and the label value are yours to choose. Reusing the Deployment's name for both is what most real manifests do

## Hints
### Hint 1
Four keys at the top, and everything else hangs off the fourth:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ...
spec:
  ...
```

Under `spec` you need exactly three things: `replicas`, `selector`, and `template`. The first is a number. The second is how the Deployment finds its pods. The third is the pod it makes.

### Hint 2
`template` is a pod with its `apiVersion` and `kind` left off, because the Deployment already knows what it is stamping out. So it has a `metadata` of its own and a `spec` of its own, and the containers live under that inner spec as a list:

```yaml
  template:
    metadata:
      labels:
        app: something
    spec:
      containers:
        - name: something
          image: some/image:tag
```

Now write `spec.selector.matchLabels` so that it says `app: something` too. Those two blocks are the pair that has to agree, and the indentation is where it usually goes wrong: `selector` is a sibling of `template`, not a child of it.

### Hint 3
The same shape, one object over, so that the pattern is worth more than this one task. A StatefulSet is a Deployment that keeps stable names and storage for its pods, and it is assembled from the identical pieces:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: ledger
spec:
  replicas: 3
  serviceName: ledger
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

Selector, template, matching labels, containers as a list. Once you can see those four, most of the workload objects read the same way and only the extra fields differ.
