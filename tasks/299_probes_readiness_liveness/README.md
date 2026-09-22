---
title: "readiness and liveness: one decides traffic, the other decides restarts"
difficulty: medium
minutes: 15
prereqs: [268, 272]
track: kubernetes
tags: [kubernetes, deployment, probes, readiness, liveness]
kind: manifest
---
# readiness and liveness: one decides traffic, the other decides restarts

*A running container and a working one are different things. Probes are how Kubernetes tells them apart, and the two you meet first answer two different questions.*

## Read first
- [Liveness, Readiness, and Startup Probes](https://kubernetes.io/docs/concepts/workloads/pods/probes/): what each probe does when it fails

## Why
Without probes, Kubernetes knows one thing about your container: whether its process is still alive. A web server stuck on a deadlock is alive. A service still loading its cache is alive. Both get traffic, and both answer it badly.

A readiness probe asks "can this pod take requests right now?" When it fails, the pod is taken out of the Service's endpoints and nothing is sent to it, and nothing else happens. The container keeps running, and the moment the probe passes again the traffic comes back. That is the probe for a pod that is warming up, or briefly overloaded, or waiting on a database that went away.

A liveness probe asks "is this container broken beyond repair?" When it fails, the kubelet kills the container and starts it again. That is the right answer to a deadlock and the wrong answer to a slow dependency: restarting every pod because the database is down turns one outage into two.

So the two usually point at different endpoints. `/ready` checks what the app needs to serve, dependencies included. `/healthz` checks only the process itself, so that a dead database never gets a healthy pod restarted.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Deployment named `{name}`, running the image `{image}`, which listens on port `{port}`. It serves `/ready` for readiness and `/healthz` for liveness.

## Rules
- one Deployment, `apps/v1`, with a selector and a pod template whose labels agree
- exactly one container, running `{image}`, declaring `containerPort: {port}`
- a `readinessProbe` doing an HTTP GET of `/ready` on port `{port}`
- a `livenessProbe` doing an HTTP GET of `/healthz` on port `{port}`
- the probe's `port` can be the number, or the name you gave the container port

## Hints
### Hint 1
Probes live on the container, beside `image` and `ports`, not on the pod:

```yaml
      containers:
        - name: web
          image: some/image:tag
          ports:
            - containerPort: 8080
          readinessProbe:
            ...
```

### Hint 2
An HTTP probe is `httpGet` with a `path` and a `port`. The timing fields all have defaults, so the smallest probe is three lines:

```yaml
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
```

The liveness probe is the same shape under its own key, with its own path.

### Hint 3
Naming the port once and referring to it by name keeps the probes right when the port changes:

```yaml
          ports:
            - name: http
              containerPort: 8080
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
```
