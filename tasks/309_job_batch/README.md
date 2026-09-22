---
title: a Job runs to the end, retries a few times, and cleans up after
difficulty: easy
minutes: 12
prereqs: [269]
track: kubernetes
tags: [kubernetes, job, batch]
kind: manifest
---
# a Job runs to the end, retries a few times, and cleans up after

*A Deployment restarts a container that exits, forever. A Job is for work that is supposed to exit: it counts the successful runs, gives up after enough failures, and can delete itself when done.*

## Read first
- [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/): completions, backoffLimit, and the restart policies a Job allows
- [Automatic cleanup for finished Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/ttlafterfinished/): `ttlSecondsAfterFinished`

## Why
A database migration, a nightly export, a batch of images to resize. Run one in a Deployment and it finishes, exits 0, and is started again, because a Deployment's whole job is to keep containers running.

A Job wants the opposite. It runs pods until `completions` of them have exited 0, then stops. A pod that fails is retried, and `backoffLimit` caps the retries so that a broken job fails for good instead of retrying all night. The pod template has to say `restartPolicy: Never` or `OnFailure`; the default, `Always`, is refused, because a container that always restarts never finishes.

A finished Job and its pods stay in the cluster so you can read the logs. That is useful for a day and clutter for a year. `ttlSecondsAfterFinished` deletes the Job, and its pods with it, that many seconds after it succeeds or fails.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
One Job named `{name}`, running `{image}`, that needs `{completions}` successful runs, gives up after `{retries}` failed retries, and is deleted `{ttl}` seconds after it finishes.

## Rules
- one Job, `apiVersion: batch/v1`
- `spec.completions: {completions}` and `spec.backoffLimit: {retries}`
- `spec.ttlSecondsAfterFinished: {ttl}`
- the pod template has exactly one container, running `{image}`, and a `command` of your choosing
- the pod template's `restartPolicy` is `Never` or `OnFailure`

## Hints
### Hint 1
A Job is in the `batch` group, and its `spec` wraps a pod template like a Deployment's, but with no selector to write: the Job labels its own pods.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: ...
spec:
  template:
    spec:
      containers:
        - ...
```

### Hint 2
`restartPolicy` belongs to the pod, so it goes in the template's `spec`, beside `containers`:

```yaml
    spec:
      restartPolicy: Never
      containers:
        - name: export
          image: some/image:tag
          command: ["python", "export.py"]
```

### Hint 3
The three numbers all sit on the Job's own `spec`, above `template`:

```yaml
spec:
  completions: 3
  backoffLimit: 4
  ttlSecondsAfterFinished: 3600
```
