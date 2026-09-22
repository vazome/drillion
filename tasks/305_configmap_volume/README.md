---
title: a ConfigMap mounted as files, for apps that read a config file
difficulty: medium
minutes: 15
prereqs: [270]
track: kubernetes
tags: [kubernetes, configmap, volumes, multi-document]
kind: manifest
---
# a ConfigMap mounted as files, for apps that read a config file

*Environment variables suit one setting at a time. An nginx.conf or a settings file wants to be a file, and a ConfigMap can be mounted as one.*

## Read first
- [Configure a Pod to Use a ConfigMap](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#add-configmap-data-to-a-volume): each key becomes a file
- [ConfigMaps: mounted ConfigMaps are updated automatically](https://kubernetes.io/docs/concepts/configuration/configmap/#mounted-configmaps-are-updated-automatically): and the one way to lose that

## Why
In 270 a ConfigMap handed the container one value through an environment variable. Most real software reads its configuration from a file instead: nginx, Prometheus, a Django settings module, anything with an `.ini`. Rebuilding the image for every config change is exactly what ConfigMaps exist to avoid.

Mounted as a volume, a ConfigMap becomes a directory with one file per key, the key as the file name and the value as its contents. A multi-line value, written with YAML's `|`, arrives as a multi-line file.

There is a second reason to prefer the mount. Environment variables are read once, when the container starts. A mounted ConfigMap is updated in place when the ConfigMap changes, within a minute or so, and an app that watches its config file picks the change up without a restart. That only holds for a whole-directory mount: mount a single key with `subPath` and the file is copied in once and never updated again.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
Two documents in one file: a ConfigMap named `{config}` holding a file `app.conf`, and a Pod named `{pod}`, running `{image}`, that finds that file in the directory `{dir}`.

## Rules
- two YAML documents, separated by `---`. The ConfigMap first, the Pod second
- the ConfigMap's `data` has a key `app.conf` with a non-empty value. Its contents are yours to choose
- the Pod has exactly one container, running `{image}`
- the Pod has a volume whose `configMap.name` is `{config}`, and the container mounts it at `{dir}`
- mount the whole directory: no `subPath`, which would freeze the file at whatever it held when the pod started

## Hints
### Hint 1
A key holding a whole file uses YAML's block scalar, and every line after the `|` is part of the value:

```yaml
data:
  app.conf: |
    listen 8080
    workers 4
```

### Hint 2
The volume refers to the ConfigMap by name. Everything else is the same volume-and-mount pair as any other volume:

```yaml
  volumes:
    - name: config
      configMap:
        name: app-config
```

### Hint 3
The mount path is the directory, not the file. With the ConfigMap above mounted at `/etc/app`, the file appears at `/etc/app/app.conf`:

```yaml
      volumeMounts:
        - name: config
          mountPath: /etc/app
```
