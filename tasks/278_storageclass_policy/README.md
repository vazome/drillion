---
title: a StorageClass decides who provisions and what happens when you walk away
difficulty: hard
minutes: 20
prereqs: [277]
track: kubernetes
tags: [kubernetes, storageclass, persistentvolumeclaim, reclaim-policy]
kind: manifest
---
# a StorageClass decides who provisions and what happens when you walk away

*So far a volume had to exist before a claim could bind to it. A StorageClass makes volumes on demand, and the interesting decision is what becomes of the disk after the claim is gone.*

## Read first
- [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/): on-demand provisioning and `reclaimPolicy`

## Why
Hand-writing a PersistentVolume per claim, as the last task did, is how storage worked before it worked well. A StorageClass is the modern half: a named policy saying that when a claim names this class, a volume is provisioned for it on the spot by a `provisioner`, a controller that knows how to talk to some storage back end and cut a disk there. The claim never names a volume again; it names a class and the disk appears.

Two fields on the class are policy, and they are the task. `reclaimPolicy` says what happens to the backing disk when its claim is deleted. `Delete` tears the disk down with it, the right default for scratch and caches and everything a CI run ever created. `Retain` keeps the volume and its data alive, orphaned, for a human to deal with, which is the only safe answer for a database. This single field is the difference between "I deleted my test claim" and "the disk with three years of customer data is now unmanaged". It is also, by default, `Delete`: the safe answer is the one you have to ask for.

`volumeBindingMode` is the subtler half. `WaitForFirstConsumer` delays provisioning until a pod actually needs the claim, so the disk is cut where the pod can use it, in the right zone on a regional cloud. It is the default mode for a reason, and writing it out is writing what real classes carry.

And a class is not a core object: it lives at `storage.k8s.io/v1`, the same way a Deployment lived at `apps/v1`. The group name is the API's own map of who owns what.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
Two documents in one file: a StorageClass named `{name}`, provisioned by `{provisioner}`, with `reclaimPolicy: {policy}` and `volumeBindingMode: WaitForFirstConsumer`, and a PersistentVolumeClaim that asks it for `{capacity}`.

## Rules
- two YAML documents, separated by a line holding `---`. StorageClass first, the claim second
- the StorageClass is `apiVersion: storage.k8s.io/v1`, named `{name}`, with `provisioner: {provisioner}`
- `reclaimPolicy` is `{policy}`, written as given. There is no third answer
- `volumeBindingMode` is `WaitForFirstConsumer`
- the claim is `apiVersion: v1`, named `{claim}`, with `spec.storageClassName: {name}`, access mode `ReadWriteOnce`, and `resources.requests.storage` holding `{capacity}`
- no PersistentVolume in this file. That is the point: the class provisions, and a claim naming a class never names a volume

## Hints
### Hint 1
The class, four fields of policy:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: ebs.csi.aws.com
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
```

No `spec` at all: a class has no running state, so its policy sits directly under the object.

### Hint 2
The claim, which names the class and nothing else about the volume:

```yaml
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: media
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast
  resources:
    requests:
      storage: 5Gi
```

Compare it to last task's claim: same shape, one word different. `storageClassName: fast` used to be a filter over volumes that existed; now it is an order.

### Hint 3
The sentence worth carrying out of storage week. A PV is a disk that exists. A PVC is a request. A StorageClass is the policy for making both on demand, and `reclaimPolicy` is the answer to the only storage question that ends in tears: when the claim goes away, does the data? Default is Delete. For anything you would mourn, someone has to have written Retain on purpose.
