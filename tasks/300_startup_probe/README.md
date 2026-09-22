---
title: a startup probe, so a slow boot is not mistaken for a hang
difficulty: medium
minutes: 15
prereqs: [299]
track: kubernetes
tags: [deployment, probes]
kind: manifest
---
# a startup probe, so a slow boot is not mistaken for a hang

*A liveness probe cannot tell a container that is still starting from one that is stuck. Give it a delay long enough for the first and it is too slow for the second.*

## Read first
- [Protect slow starting containers with startup probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/#define-startup-probes): the budget is `failureThreshold` times `periodSeconds`

## Why
Some services take minutes to boot: a JVM warming up, a search index loading from disk, a migration that runs before the port opens. A liveness probe that expects an answer in thirty seconds kills that container before it ever finishes, the replacement is killed the same way, and the pod sits in `CrashLoopBackOff` with nothing wrong with it.

The first fix everyone reaches for is `initialDelaySeconds: 300` on the liveness probe. It works on the day, and it costs you forever after: a container that deadlocks at hour three now also waits five minutes to be restarted after every crash, and the number has to grow every time the boot does.

A startup probe is the right tool. While it runs, liveness and readiness are held off. It gets a budget of `failureThreshold × periodSeconds` seconds to succeed once; after that it stops for good and the liveness probe takes over at its own quick pace. The slow start gets its patience, and the running container keeps a fast restart.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Deployment named `{name}`, running `{image}` on port `{port}`. The app answers `/healthz` once it is up, and on a bad day it takes `{boot}` seconds to get there.

## Rules
- one Deployment, `apps/v1`, with a selector and a pod template whose labels agree, and one container running `{image}` on `containerPort: {port}`
- a `startupProbe` doing an HTTP GET of `/healthz` on that port, whose `failureThreshold × periodSeconds` covers at least `{boot}` seconds. `periodSeconds` is 10 when you leave it out
- a `livenessProbe` doing an HTTP GET of `/healthz` on that port
- no `initialDelaySeconds` on the liveness probe: waiting out the boot is the startup probe's job

## Hints
### Hint 1
A startup probe is the same shape as the liveness probe you wrote in 299, under its own key:

```yaml
          startupProbe:
            httpGet:
              path: /healthz
              port: 8080
```

### Hint 2
The budget is the two numbers multiplied. For a boot of up to five minutes with a check every ten seconds, that is thirty tries:

```yaml
            failureThreshold: 30
            periodSeconds: 10
```

Round up. A budget one try short restarts a healthy container on its slowest day.

### Hint 3
The liveness probe can stay small and quick, because nothing asks it anything until the startup probe has succeeded:

```yaml
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            periodSeconds: 10
            failureThreshold: 3
```
