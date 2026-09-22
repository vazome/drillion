---
title: an init container prepares what the app finds when it starts
difficulty: hard
minutes: 20
prereqs: [269]
track: kubernetes
tags: [pod, volumes]
kind: manifest
---
# an init container prepares what the app finds when it starts

*Some work has to be finished before the app starts, and does not belong in the app's image. An init container runs it first, to completion, and hands the result over through a shared volume.*

## Read first
- [Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/): they run in order, each to completion, before any app container starts
- [emptyDir](https://kubernetes.io/docs/concepts/storage/volumes/#emptydir): a scratch directory that lives as long as the pod

## Why
A web server that serves files someone else builds. A service that needs a config file rendered from a template, or a schema migrated, or a certificate fetched, before it can take its first request. Putting those tools into the app's image makes it bigger and gives the running app tools it never uses again.

An init container is a container listed under `initContainers` instead of `containers`. The kubelet runs each one in turn, and only when every one has exited 0 does it start the app. If one fails, the pod starts it again and the app never runs on half-finished work.

The two containers share nothing by default: each has its own filesystem. A volume mounted into both is how the result gets across. An `emptyDir` is the plain case: an empty directory created with the pod and deleted with it. The init container writes into its mount, the app reads from its own mount of the same volume, and the two mount paths do not have to match.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Pod named `{name}`. Before its app container (`{image}`) starts, an init container running `busybox:1.37` writes an `index.html` into a shared `emptyDir`, which the app sees at `{path}`.

## Rules
- one Pod, `apiVersion: v1`
- exactly one init container, under `spec.initContainers`, running `busybox:1.37`, with a `command` that writes into the directory where the shared volume is mounted in it. Name that directory in the command itself
- exactly one app container, under `spec.containers`, running `{image}`
- one `emptyDir` volume, mounted into both containers. The app container mounts it at `{path}`

## Hints
### Hint 1
`initContainers` has exactly the shape of `containers`, and sits beside it:

```yaml
spec:
  initContainers:
    - name: fetch
      image: busybox:1.37
  containers:
    - name: web
      image: nginx:1.27
```

### Hint 2
A `command` is a list, and the shell form is the easy way to write a file:

```yaml
      command: ["sh", "-c", "echo hello > /work/index.html"]
```

### Hint 3
The volume is declared once, on the pod, and mounted by name in each container, at whatever path suits that container:

```yaml
  volumes:
    - name: content
      emptyDir: {}
```

```yaml
      volumeMounts:
        - name: content
          mountPath: /work
```
