---
title: a PV holds and a PVC asks, and 1Gi is not 1G
difficulty: medium
minutes: 20
track: kubernetes
tags: [kubernetes, persistentvolume, persistentvolumeclaim, storage]
kind: manifest
---
# a PV holds and a PVC asks, and 1Gi is not 1G

*Storage outlives every pod, so it gets its own objects: one that holds, one that asks, and a binding made when what is asked fits what is held.*

## Why
A pod's filesystem dies with the pod. The objects that outlive it are the two halves of Kubernetes storage. A PersistentVolume is a piece of storage that exists: a disk someone attached, a directory on a node, a network share. A PersistentVolumeClaim is a request for storage: this much, readable this way. The API binds a claim to a volume when the two agree, and from then on the claim is all a pod needs to know; the volume behind it can be a thumb drive today and a SAN volume tomorrow without anyone rewriting the pod.

The agreement has two terms, and both appear in both documents. `accessModes` says how the storage may be used: `ReadWriteOnce` for one node at a time, the normal shape for a database; `ReadWriteMany` for storage many nodes share, the shape of a shared file system. A claim binds only a volume whose modes cover its own. And the size is written in binary units: `1Gi`, which is 2 to the 30th, the number of bytes a machine actually counts. `1G` is 10 to the 9th, a decimal round number no disk was ever manufactured to. A claim for `1Gi` will not bind a volume holding `1G`, and the mismatch is invisible until something fills up early.

This file carries both documents, the volume first and the claim second, joined by `storageClassName`. The class is how a claim says which pool of volumes it is willing to bind to; two objects sharing a class name is the handshake.

## You get
An empty file, and the requirements below. Whatever you type is checked as YAML while you type it, and graded against the real Kubernetes schema when you run it, offline.

## You return
Two documents in one file: a PersistentVolume named `{name}` holding `{capacity}` with access mode `{accessMode}`, and a PersistentVolumeClaim asking it for exactly that, both stamped with the storage class `{storageClass}`.

## Rules
- two YAML documents, separated by a line holding `---`. PersistentVolume first, PersistentVolumeClaim second
- the PV is `apiVersion: v1`, with `spec.capacity.storage` holding the capacity above, written in binary units exactly as given
- the PV's `spec.accessModes` is a list holding the one mode above
- the PVC is also `apiVersion: v1`, and asks for the same: the same capacity under `spec.resources.requests.storage`, the same mode, the same class
- both documents carry `spec.storageClassName: {storageClass}`. That shared name is how the claim finds the volume
- the PV holds a directory on a node: `spec.hostPath.path: /mnt/data`. Real volumes point at disks and shares; the shape of the field is what is being learned

## Hints
### Hint 1
The PV, a capacity, a mode, and something to hold:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: cache-data
spec:
  capacity:
    storage: 2Gi
  accessModes:
    - ReadWriteOnce
  storageClassName: fast
  hostPath:
    path: /mnt/data
```

`capacity` is a mapping of one key, because a volume's size is the quantity everything else negotiates against.

### Hint 2
The claim, asking for the same three things:

```yaml
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cache-data
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast
  resources:
    requests:
      storage: 2Gi
```

The size hides one level deeper than in the PV: `requests` sits under `resources`, because a claim could one day negotiate a limit too.

### Hint 3
Where the units bite. `1Gi` is 1 073 741 824 bytes; `1G` is 1 000 000 000. Kubernetes quantities accept both spellings, so nothing rejects the wrong one, and a claim for `1G` simply never binds a volume holding `1Gi`, because 1G asks for less than the volume promises and the binding arithmetic is exact. When a dashboard ever shows you 73G used of 74Gi, that gap is this paragraph.
