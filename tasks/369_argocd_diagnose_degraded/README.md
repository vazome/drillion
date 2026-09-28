---
title: "diagnosis: Synced, but Degraded"
difficulty: medium
minutes: 15
prereqs: [357, 299]
track: argocd
tags: [troubleshooting, probes]
kind: manifest
---
# diagnosis: Synced, but Degraded

*Synced means the cluster matches git. It says nothing about whether what git describes works. Read Argo CD's view of the app, follow it down to the pods, and fix the manifest.*

## Read first
- [Resource Health](https://argo-cd.readthedocs.io/en/stable/operator-manual/health/): what Healthy, Progressing and Degraded mean for a Deployment
- [argocd app get](https://argo-cd.readthedocs.io/en/stable/user-guide/commands/argocd_app_get/): the view below
- [Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/): events and logs

## Why
Argo CD reports two things about every app, and they answer different questions. **Sync status** compares the cluster with git: Synced or OutOfSync. **Health** asks whether what is running works: a Deployment is Healthy when its new pods are available, Progressing while they come up, and Degraded when the rollout has given up, after `progressDeadlineSeconds`.

Synced and Degraded together means git was applied faithfully and git is wrong. Syncing again changes nothing, and neither does restarting pods. The way in is to walk down: the app, then the resource that is not healthy, then its pods, their events and their logs. The fix goes where the mistake is, in git, and the next sync delivers it.

## You get
This is what the on-call engineer saw after release 2.8.0 of `catalog` merged. The output is written for this task in the shape the tools print, not captured from a cluster.

```
$ argocd app get catalog
Name:               argocd/catalog
Project:            default
Server:             https://kubernetes.default.svc
Namespace:          catalog
Source:
- Repo:             https://github.com/acme/platform-gitops.git
  Target:           main
  Path:             apps/catalog
Sync Policy:        Automated (Prune)
Sync Status:        Synced to main (4f2c9e1)
Health Status:      Degraded

GROUP  KIND        NAMESPACE  NAME     STATUS  HEALTH    HOOK  MESSAGE
       Service     catalog    catalog  Synced  Healthy         service/catalog unchanged
apps   Deployment  catalog    catalog  Synced  Degraded        Deployment "catalog" exceeded its progress deadline

$ kubectl -n catalog get pods
NAME                       READY   STATUS    RESTARTS   AGE
catalog-6d9f7c8b54-2xkqp   0/1     Running   0          11m
catalog-7b4d8f6c9d-hv5lm   1/1     Running   0          2d
catalog-7b4d8f6c9d-mz2nq   1/1     Running   0          2d
catalog-7b4d8f6c9d-w7rtc   1/1     Running   0          2d

$ kubectl -n catalog describe pod catalog-6d9f7c8b54-2xkqp
...
Events:
  Type     Reason     Age                 From     Message
  ----     ------     ----                ----     -------
  Warning  Unhealthy  1m (x64 over 11m)   kubelet  Readiness probe failed: HTTP probe failed with statuscode: 404

$ kubectl -n catalog logs catalog-6d9f7c8b54-2xkqp --tail 4
INFO  catalog 2.8.0 listening on :8080
INFO  readiness is served at /readyz and liveness at /healthz; /health was removed in 2.8.0
WARN  GET /health 404
WARN  GET /health 404
```

And this is `apps/catalog/deployment.yaml` in git at `4f2c9e1`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: catalog
spec:
  replicas: 3
  selector:
    matchLabels:
      app: catalog
  template:
    metadata:
      labels:
        app: catalog
    spec:
      containers:
        - name: catalog
          image: ghcr.io/acme/catalog:2.8.0
          ports:
            - containerPort: 8080
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            periodSeconds: 10
          livenessProbe:
            tcpSocket:
              port: 8080
            periodSeconds: 20
```

## You return
The Deployment `catalog` as it should be in git: the same manifest, with the one change that lets the new pods become ready.

## Rules
- one document, the Deployment `catalog`
- everything in it is as in git at `4f2c9e1`, except the one field that is broken
- it still runs `ghcr.io/acme/catalog:2.8.0`: the fix goes forward, not back to the old release

## Hints
### Hint 1
The new pod is Running with no restarts, yet 0/1 ready. Restarts are the liveness probe's doing and readiness is the readiness probe's, so only one of the two probes is failing. Which one, and what does it ask for?

### Hint 2
The event names the status code, 404: the probe reached the app, and the app does not have the page it asked for. The log says which pages 2.8.0 does have.

### Hint 3
Readiness is `/readyz` now. Change the readiness probe's `httpGet.path` and nothing else.
