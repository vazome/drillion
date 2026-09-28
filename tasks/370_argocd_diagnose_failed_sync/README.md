---
title: "diagnosis: the sync failed at its PreSync hook"
difficulty: medium
minutes: 15
prereqs: [361]
track: argocd
tags: [troubleshooting, hooks]
kind: manifest
---
# diagnosis: the sync failed at its PreSync hook

*When a hook fails, the sync stops and the old release keeps serving. The app looks Healthy and OutOfSync at once, and the reason is in the hook's logs.*

## Read first
- [Resource Hooks](https://argo-cd.readthedocs.io/en/stable/user-guide/resource_hooks/): what a failed PreSync hook does to the rest of the sync
- [argocd app get](https://argo-cd.readthedocs.io/en/stable/user-guide/commands/argocd_app_get/): the operation and its message
- [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/): how a pod finds a Service by name

## Why
A PreSync hook runs before anything else in a sync, and the sync goes on only if it succeeds. When it fails, Argo CD stops right there: nothing else is applied, so the Deployment still runs the old release. That is why a failed hook looks so calm. Health is Healthy, because the old pods are fine. Sync status is OutOfSync, because git has the new release and the cluster does not. The last operation is Failed, and its message says why.

With the delete policy from task 361, `BeforeHookCreation,HookSucceeded`, a failed Job is not deleted, so its logs are still there to read. Retrying the sync runs the same broken Job again; the fix is in git, and once it merges the next sync deletes the failed Job, creates the fixed one, and carries on.

## You get
This is what the on-call engineer saw after release 5.1.0 of `orders` merged. The output is written for this task in the shape the tools print, not captured from a cluster.

```
$ argocd app get orders
Name:               argocd/orders
Project:            default
Server:             https://kubernetes.default.svc
Namespace:          orders
Source:
- Repo:             https://github.com/acme/platform-gitops.git
  Target:           main
  Path:             apps/orders
Sync Policy:        Automated (Prune)
Sync Status:        OutOfSync from main (a81c3d0)
Health Status:      Healthy

Operation:          Sync
Sync Revision:      a81c3d0
Phase:              Failed
Message:            one or more synchronization tasks completed unsuccessfully, reason: Job has reached the specified backoff limit

GROUP  KIND        NAMESPACE  NAME            STATUS     HEALTH   HOOK     MESSAGE
batch  Job         orders     orders-migrate  Failed              PreSync  Job has reached the specified backoff limit
       Service     orders     orders          Synced     Healthy
apps   Deployment  orders     orders          OutOfSync  Healthy

$ kubectl -n orders logs job/orders-migrate
orders 5.1.0 migrate: connecting to postgres:5432
psql: error: could not translate host name "postgres" to address: Name or service not known

$ kubectl -n orders get services
NAME        TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)    AGE
orders      ClusterIP   10.0.141.27   none          80/TCP     41d
orders-db   ClusterIP   None          none          5432/TCP   41d
```

And this is `apps/orders/migrate.yaml` in git at `a81c3d0`:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: orders-migrate
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation,HookSucceeded
spec:
  backoffLimit: 2
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: ghcr.io/acme/orders:5.1.0
          args: ["migrate", "up"]
          env:
            - name: DATABASE_HOST
              value: postgres
```

## You return
The Job `orders-migrate` as it should be in git: the same manifest, with the one change that lets the migration reach its database.

## Rules
- one document, the Job `orders-migrate`
- everything in it is as in git at `a81c3d0`, except the one field that is broken
- it is still a PreSync hook with the same delete policy, and still runs `ghcr.io/acme/orders:5.1.0`

## Hints
### Hint 1
The operation failed, the app is Healthy, and only the Job's row says Failed. Whatever went wrong went wrong inside the Job, so its logs come first.

### Hint 2
"could not translate host name" is DNS: nothing in the cluster is called `postgres`. Inside a namespace, a Service's name is a host name. Which Services does `orders` have?

### Hint 3
The database's Service is `orders-db`. Change the value of `DATABASE_HOST` and nothing else.
