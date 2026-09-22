---
title: "the default Service: a selector finds the pods, and two ports do two jobs"
difficulty: medium
minutes: 15
prereqs: [269]
track: kubernetes
tags: [service, labels]
kind: manifest
---
# the default Service: a selector finds the pods, and two ports do two jobs

*Pods are born and die with new IPs every time. A Service is the stable address in front of them, and a label is how it finds them.*

## Read first
- [Service](https://kubernetes.io/docs/concepts/services-networking/service/): the stable address, its selector, and the two ports

## Why
A Pod's IP belongs to the Pod, and the Pod is mortal. Any client that memorised the IP is memorising a corpse's address. A Service is the fixed virtual IP that outlives them, forwarding to whichever pods are alive, and it finds those pods the way a Deployment does: a `selector` matching labels, the same agreement you wrote in your first Deployment, this time read from the other side.

The two ports are where the thinking is. `port` is the number clients call, the one the Service answers on inside the cluster. `targetPort` is where it forwards on the container, and the two need not be the same, because the outside-facing number and the container's own listening port are decisions made by different people at different times. Most confused first Services set one and assume the other.

And the kind of a Service is chosen by leaving it alone. `spec.type` defaults to `ClusterIP`, an address reachable only from inside the cluster, which is the right default: most traffic is internal. Writing the type out is not wrong, but the default is the lesson, because knowing what a Service is when nobody named a type is knowing what a Service is.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Service: named `{name}`, selecting pods labelled `app: {name}`, answering on port `{port}` and forwarding to the containers on `{targetPort}`.

## Rules
- one YAML document, one Service, nothing else in the file
- `apiVersion` is `v1`. A Service is a core object
- leave `spec.type` off. ClusterIP is the default, and the default is the point of the task
- `spec.selector` labels the pods this Service forwards to, and `app: {name}` is the label to use
- one entry under `spec.ports`, carrying both `port` and `targetPort` from above
- the selector finds nothing in this task, since no pods are in the file. That is fine: a Service forwards to whatever matches at runtime, and the schema has no opinion about it

## Hints
### Hint 1
The skeleton, core `apiVersion` and all:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ...
spec:
  selector: ...
  ports: ...
```

Two things hang off `spec`: who to forward to, and how the ports line up.

### Hint 2
The selector is a mapping of labels, exactly like `matchLabels` was:

```yaml
  selector:
    app: checkout
  ports:
    - port: 80
      targetPort: 8080
```

Read a request to it out loud to keep the two ports straight: "call the Service on 80, and it hands the request to whatever is listening on 8080 inside a pod it selected".

### Hint 3
Where the pods went. Your Deployment from earlier stamps out pods carrying `app: checkout` in `spec.template.metadata.labels`, and this Service's selector reads the very same labels from the outside. One agreement, two objects on opposite ends of it, which is why the label key is `app` on both sides and why a rename on one side only leaves the Service forwarding to nothing.
