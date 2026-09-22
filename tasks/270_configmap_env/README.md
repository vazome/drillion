---
title: "two documents, one file: a ConfigMap and the Pod that reads it"
difficulty: easy
minutes: 15
prereqs: [269]
track: kubernetes
tags: [configmap, env, multi-document]
kind: manifest
---
# two documents, one file: a ConfigMap and the Pod that reads it

*Config does not live inside the container. It lives in its own object, and a Pod reaches into it by name at the moment it starts.*

## Read first
- [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/): keys and values that live outside the container
- [Configure a Pod to Use a ConfigMap](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/): env from a `configMapKeyRef`

## Why
A container image is built once and run everywhere, which is exactly why the things that change between everywhere do not go inside it. A ConfigMap is Kubernetes' envelope for that: keys and values that live separately from the pods that read them, so the same image runs with the log level it is given rather than the log level it was built with.

The wiring is where the lesson is. A Pod injects a ConfigMap entry as an environment variable with `valueFrom`, a block that points at another object: which ConfigMap by `name`, which entry in it by `key`. The trap sits one line away. `value` is the sibling field that holds a literal, and if both appear the literal wins and the ConfigMap is quietly ignored. Reading `LOG_LEVEL: value` as "the value named LOG_LEVEL" instead of "the string value" is the classic first week's bug.

This task is also the first file that holds two objects at once. Kubernetes manifests separate documents with a line holding three dashes, and the file is applied top to bottom, so the ConfigMap goes first and the Pod that names it goes second.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
Two documents in one file: a ConfigMap named `{name}` holding `LOG_LEVEL: {value}`, and a Pod whose container reads that entry in as an environment variable.

## Rules
- two YAML documents, separated by a line holding `---`. ConfigMap first, the Pod that reads it second
- the ConfigMap holds the entry under `data`
- the Pod's container has one `env` entry named `LOG_LEVEL`, and it reaches the value through `valueFrom` with a `configMapKeyRef` naming the ConfigMap and the key
- no `value` beside the `valueFrom`. The task is to point at the entry, and a literal beside the pointer is the bug this task exists to catch
- the container needs a `name` and an `image` as any other

## Hints
### Hint 1
The ConfigMap is the smaller object. `data` is a mapping, so its entries are plain `key: value` lines:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  LOG_LEVEL: debug
```

### Hint 2
Then a `---` line, then the Pod. The `env` entry has a name, which is the variable the container will see, and a `valueFrom` instead of a `value`:

```yaml
---
apiVersion: v1
kind: Pod
metadata:
  name: worker
spec:
  containers:
    - name: worker
      image: some/image:tag
      env:
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: LOG_LEVEL
```

The inner `name` is which ConfigMap, the inner `key` is which entry inside it. They are two lookups, and both have to be right.

### Hint 3
The same reach, one object over. A `secretKeyRef` is spelled identically and reads from a Secret, which is the next task. Once you can see that `valueFrom` is a pointer and `value` is a literal, the whole env family reads the same way.
