---
title: a hardened pod that passes the restricted security standard
difficulty: hard
minutes: 20
prereqs: [269]
track: kubernetes
tags: [pod, security, non-root]
kind: manifest
---
# a hardened pod that passes the restricted security standard

*Most containers run as root, with every capability, on a filesystem they can rewrite. None of that is needed to serve a web page, and a cluster set to `restricted` refuses a pod that asks for it.*

## Read first
- [Configure a Security Context for a Pod or Container](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/): the fields, and where each can go
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/#restricted): the list the `restricted` level enforces

## Why
A container is a process on a shared kernel. If it runs as root and something breaks into it, the attacker starts as root, with every Linux capability the runtime hands out, able to write anywhere in the image and to gain more privilege through a setuid binary. Each of those is one line to take away.

Kubernetes turns the list into a policy. A namespace labelled `pod-security.kubernetes.io/enforce: restricted` refuses any pod that does not:

- run as a user other than root: `runAsNonRoot: true`, and a `runAsUser` that is not 0
- forbid gaining privileges: `allowPrivilegeEscalation: false`
- drop every capability: `capabilities.drop: ["ALL"]`
- filter syscalls: `seccompProfile.type: RuntimeDefault`

`readOnlyRootFilesystem: true` is not on that list, and most hardening guides add it anyway: a process that cannot write to its own image cannot plant anything in it. The price is that the app has nowhere to write its temporary files, so you mount an `emptyDir` where it needs one. Hardening costs something, and paying it is part of the job.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Pod named `{name}`, running `{image}` as user `{uid}`, that the `restricted` standard admits, with a read-only root filesystem and a writable `/tmp`.

## Rules
- one Pod, `apiVersion: v1`, with exactly one container running `{image}`
- `runAsNonRoot: true` and `runAsUser: {uid}`, on the pod or on the container
- `seccompProfile.type: RuntimeDefault`, on the pod or on the container
- on the container's own `securityContext`: `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem: true`, and `capabilities.drop` holding `ALL`
- an `emptyDir` volume mounted into the container at `/tmp`

## Hints
### Hint 1
There are two `securityContext` blocks, and they take different fields. The pod's holds what applies to every container, like the user; the container's holds what only a container can have, like capabilities and the root filesystem:

```yaml
spec:
  securityContext:
    runAsNonRoot: true
  containers:
    - name: web
      image: some/image:tag
      securityContext:
        allowPrivilegeEscalation: false
```

### Hint 2
`capabilities` is a map with a list under it, and the one value that matters is the word `ALL`:

```yaml
        capabilities:
          drop: ["ALL"]
```

### Hint 3
A writable directory is a volume in the pod and a mount in the container, joined by name:

```yaml
  volumes:
    - name: tmp
      emptyDir: {}
```

```yaml
      volumeMounts:
        - name: tmp
          mountPath: /tmp
```
